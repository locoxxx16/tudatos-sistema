#!/usr/bin/env python3
"""
SCRIPT DE MIGRACIÓN A OBJECTROCKET (HEROKU)
Migra todos los datos de MongoDB local a ObjectRocket MongoDB
"""

import pymongo
import os
import subprocess
import json
from tqdm import tqdm
import time

# Configuración local
LOCAL_MONGO = "mongodb://localhost:27017"
LOCAL_DB = "test_database"

def get_heroku_config():
    """Obtiene la URL de ObjectRocket desde Heroku"""
    try:
        print("🔍 Obteniendo credenciales de Heroku...")
        
        # Ejecutar heroku config para obtener las variables
        result = subprocess.run(['heroku', 'config', '--app', 'datatico-db', '--json'], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Error ejecutando heroku config:")
            print(result.stderr)
            return None
            
        config = json.loads(result.stdout)
        
        # Buscar la URL de ObjectRocket
        objectrocket_url = None
        for key, value in config.items():
            if 'OBMONGO' in key and 'URL' in key:
                objectrocket_url = value
                print(f"✅ Encontrada URL: {key}")
                break
                
        return objectrocket_url
        
    except FileNotFoundError:
        print("❌ Heroku CLI no encontrado. Instalando...")
        return None
    except Exception as e:
        print(f"❌ Error obteniendo config: {e}")
        return None

def migrate_database():
    print("🚀 INICIANDO MIGRACIÓN A OBJECTROCKET")
    print("=" * 50)
    
    # Obtener URL de ObjectRocket
    objectrocket_url = get_heroku_config()
    
    if not objectrocket_url:
        print("❌ No se pudo obtener la URL de ObjectRocket")
        print("📋 Intenta manualmente con:")
        print("   heroku config --app datatico-db")
        return
    
    print(f"🔗 URL ObjectRocket: {objectrocket_url[:50]}...")
    
    # Conectar a bases de datos
    print("🔌 Conectando a MongoDB local...")
    local_client = pymongo.MongoClient(LOCAL_MONGO)
    local_db = local_client[LOCAL_DB]
    
    print("🔌 Conectando a ObjectRocket...")
    objectrocket_client = pymongo.MongoClient(objectrocket_url)
    
    # Extraer nombre de base de datos de la URL
    # URL format: mongodb://user:pass@host/database_name
    database_name = objectrocket_url.split('/')[-1].split('?')[0]
    if database_name in ['', 'YOUR_DATABASE_NAME']:
        database_name = "datatico_cr"  # nombre por defecto
    
    objectrocket_db = objectrocket_client[database_name]
    
    print(f"📊 Base de datos ObjectRocket: {database_name}")
    
    # Colecciones importantes (ordenadas por prioridad)
    important_collections = [
        'personas_fisicas_fast2m',      # 4M registros - PRIORIDAD ALTA
        'personas_juridicas_fast2m',    # 1M registros - PRIORIDAD ALTA
        'tse_datos_hibridos',          # 591K registros
        'personas_fisicas',            # 310K registros
        'ultra_deep_extraction',       # 19K registros
        'personas_juridicas',          # 800 registros
        'daticos_datos_masivos'        # 396 registros
    ]
    
    total_migrated = 0
    
    for collection_name in important_collections:
        print(f"\n📊 Migrando colección: {collection_name}")
        
        local_collection = local_db[collection_name]
        objectrocket_collection = objectrocket_db[collection_name]
        
        # Contar documentos
        total_docs = local_collection.count_documents({})
        print(f"   Documentos a migrar: {total_docs:,}")
        
        if total_docs == 0:
            print("   ⏭️  Colección vacía, saltando...")
            continue
            
        # Verificar si la colección ya existe en ObjectRocket
        existing_docs = objectrocket_collection.count_documents({})
        if existing_docs > 0:
            print(f"   ⚠️  Ya existen {existing_docs:,} documentos")
            choice = input("   ¿Limpiar y reemplazar? (s/n): ").lower()
            if choice == 's':
                print("   🧹 Limpiando colección destino...")
                objectrocket_collection.delete_many({})
            else:
                print("   ⏭️  Saltando colección...")
                continue
        
        # Migrar en lotes optimizados
        batch_size = 500  # Menor para ObjectRocket
        migrated_count = 0
        
        with tqdm(total=total_docs, desc=f"   {collection_name}") as pbar:
            cursor = local_collection.find().batch_size(batch_size)
            batch = []
            
            for doc in cursor:
                batch.append(doc)
                
                if len(batch) >= batch_size:
                    try:
                        objectrocket_collection.insert_many(batch, ordered=False)
                        migrated_count += len(batch)
                        total_migrated += len(batch)
                        batch = []
                        pbar.update(batch_size)
                        
                        # Pausa pequeña para no sobrecargar
                        time.sleep(0.1)
                        
                    except Exception as e:
                        print(f"\n   ❌ Error insertando lote: {e}")
                        # Intentar documento por documento
                        for single_doc in batch:
                            try:
                                objectrocket_collection.insert_one(single_doc)
                                migrated_count += 1
                                total_migrated += 1
                            except:
                                pass
                        batch = []
                        pbar.update(batch_size)
            
            # Insertar último lote
            if batch:
                try:
                    objectrocket_collection.insert_many(batch, ordered=False)
                    migrated_count += len(batch)
                    total_migrated += len(batch)
                    pbar.update(len(batch))
                except Exception as e:
                    print(f"\n   ❌ Error en último lote: {e}")
                    for single_doc in batch:
                        try:
                            objectrocket_collection.insert_one(single_doc)
                            migrated_count += 1
                            total_migrated += 1
                        except:
                            pass
                    pbar.update(len(batch))
        
        print(f"   ✅ {collection_name}: {migrated_count:,} documentos migrados")
        
        # Verificar migración
        final_count = objectrocket_collection.count_documents({})
        print(f"   📊 Verificación: {final_count:,} documentos en ObjectRocket")
    
    print("\n🎉 MIGRACIÓN COMPLETADA")
    print(f"📊 Total documentos migrados: {total_migrated:,}")
    print("✅ Tu base de datos está ahora en ObjectRocket (Heroku)")
    print(f"🔗 Base de datos ObjectRocket: {database_name}")
    
    # Cerrar conexiones
    local_client.close()
    objectrocket_client.close()

if __name__ == "__main__":
    migrate_database()