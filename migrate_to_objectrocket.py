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


# URLs de ObjectRocket obtenidas de Heroku
OBJECTROCKET_RS_URL = "mongodb://iad2-c19-0.mongo.objectrocket.com:52752,iad2-c19-1.mongo.objectrocket.com:52752,iad2-c19-2.mongo.objectrocket.com:52752/?replicaSet=592734bd19354a7d81c1402dd6eed9f4&ssl=true"
OBJECTROCKET_URL = "mongodb://iad2-c19-0.mongo.objectrocket.com:52752?ssl=true"

def get_objectrocket_credentials():
    """Solicita las credenciales de ObjectRocket"""
    print("🔍 NECESITAMOS LAS CREDENCIALES DE OBJECTROCKET")
    print("=" * 50)
    print("Las URLs de ObjectRocket no incluyen usuario y contraseña.")
    print("Necesitas obtenerlas desde ObjectRocket directamente.")
    print("")
    print("Opciones:")
    print("1. Ir a: https://app.objectrocket.com")
    print("2. Login con tu cuenta")
    print("3. Ir a tu instancia MongoDB")
    print("4. Buscar 'Database Users' o 'Users'")
    print("5. Crear un usuario si no existe")
    print("")
    
    username = input("👤 Usuario de ObjectRocket: ").strip()
    password = input("🔐 Contraseña de ObjectRocket: ").strip()
    database = input("🗄️  Nombre de la base de datos (presiona Enter para 'datatico_cr'): ").strip()
    
    if not database:
        database = "datatico_cr"
    
    # Construir URL completa con credenciales
    if username and password:
        # Usar la URL con replica set para mejor performance
        url_with_creds = OBJECTROCKET_RS_URL.replace("mongodb://", f"mongodb://{username}:{password}@")
        # Agregar el nombre de la base de datos
        url_with_creds = url_with_creds.replace("/?", f"/{database}?")
        return url_with_creds, database
    else:
        print("❌ Credenciales vacías")
        return None, None

def test_connection(url, database):
    """Testa la conexión a ObjectRocket"""
    try:
        print("🔌 Probando conexión a ObjectRocket...")
        client = pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)
        
        # Test de conexión
        client.admin.command('ping')
        
        # Test de acceso a la base de datos
        db = client[database]
        collections = db.list_collection_names()
        
        print(f"✅ Conexión exitosa!")
        print(f"📊 Base de datos: {database}")
        print(f"📁 Colecciones existentes: {len(collections)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Verifica:")
        print("   - Usuario y contraseña correctos")
        print("   - Nombre de base de datos correcto")
        print("   - Permisos de acceso configurados")
        return False

def migrate_database():
    print("🚀 INICIANDO MIGRACIÓN A OBJECTROCKET")
    print("=" * 50)
    
    # Obtener credenciales de ObjectRocket
    objectrocket_url, database_name = get_objectrocket_credentials()
    
    if not objectrocket_url:
        print("❌ No se pudieron obtener las credenciales de ObjectRocket")
        return
    
    # Probar conexión antes de continuar
    if not test_connection(objectrocket_url, database_name):
        print("❌ No se pudo conectar a ObjectRocket")
        print("💡 Verifica las credenciales e intenta nuevamente")
        return
    
    print(f"🔗 URL ObjectRocket: {objectrocket_url[:50]}...")
    
    # Conectar a bases de datos
    print("🔌 Conectando a MongoDB local...")
    local_client = pymongo.MongoClient(LOCAL_MONGO)
    local_db = local_client[LOCAL_DB]
    
    print("🔌 Conectando a ObjectRocket...")
    objectrocket_client = pymongo.MongoClient(objectrocket_url)
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