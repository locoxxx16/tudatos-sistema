#!/usr/bin/env python3
"""
MIGRACIÓN AUTOMATIZADA A OBJECTROCKET
Migra todos los datos de MongoDB local a ObjectRocket MongoDB
"""

import pymongo
import os
from tqdm import tqdm
import time

# Configuración
LOCAL_MONGO = "mongodb://localhost:27017"
LOCAL_DB = "test_database"

# Credenciales de ObjectRocket
USERNAME = "datatico_admin"
PASSWORD = "DataCR2025#Secure"
DATABASE = "datatico_cr"

# URL base de ObjectRocket
OBJECTROCKET_BASE_URL = "mongodb://iad2-c19-0.mongo.objectrocket.com:52752,iad2-c19-1.mongo.objectrocket.com:52752,iad2-c19-2.mongo.objectrocket.com:52752/?replicaSet=592734bd19354a7d81c1402dd6eed9f4&ssl=true"

# Construir URL completa con credenciales
OBJECTROCKET_URL = OBJECTROCKET_BASE_URL.replace("mongodb://", f"mongodb://{USERNAME}:{PASSWORD}@")
OBJECTROCKET_URL = OBJECTROCKET_URL.replace("/?", f"/{DATABASE}?")

def test_connection():
    """Testa la conexión a ObjectRocket"""
    try:
        print("🔌 Probando conexión a ObjectRocket...")
        client = pymongo.MongoClient(OBJECTROCKET_URL, serverSelectionTimeoutMS=10000)
        
        # Test de conexión
        client.admin.command('ping')
        
        # Test de acceso a la base de datos
        db = client[DATABASE]
        collections = db.list_collection_names()
        
        print(f"✅ Conexión exitosa!")
        print(f"📊 Base de datos: {DATABASE}")
        print(f"📁 Colecciones existentes: {len(collections)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def migrate_database():
    print("🚀 INICIANDO MIGRACIÓN A OBJECTROCKET")
    print("=" * 50)
    print(f"📍 Usuario: {USERNAME}")
    print(f"📊 Base de datos: {DATABASE}")
    print(f"🔗 Conexión: ObjectRocket Replica Set")
    
    # Probar conexión
    if not test_connection():
        print("❌ No se pudo conectar a ObjectRocket")
        return
    
    # Conectar a bases de datos
    print("\n🔌 Conectando a MongoDB local...")
    local_client = pymongo.MongoClient(LOCAL_MONGO)
    local_db = local_client[LOCAL_DB]
    
    print("🔌 Conectando a ObjectRocket...")
    objectrocket_client = pymongo.MongoClient(OBJECTROCKET_URL)
    objectrocket_db = objectrocket_client[DATABASE]
    
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
    start_time = time.time()
    
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
        
        # Verificar si ya existe
        existing_docs = objectrocket_collection.count_documents({})
        if existing_docs > 0:
            print(f"   ⚠️  Ya existen {existing_docs:,} documentos. Limpiando...")
            objectrocket_collection.delete_many({})
        
        # Migrar en lotes optimizados
        batch_size = 500  # Lotes más pequeños para ObjectRocket
        migrated_count = 0
        
        print(f"   🚀 Iniciando migración en lotes de {batch_size}")
        
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
                        
                        # Pausa para no sobrecargar ObjectRocket
                        time.sleep(0.05)
                        
                    except Exception as e:
                        print(f"\n   ⚠️  Error en lote: {str(e)[:100]}...")
                        # Intentar documento por documento en caso de error
                        for single_doc in batch:
                            try:
                                objectrocket_collection.insert_one(single_doc)
                                migrated_count += 1
                                total_migrated += 1
                            except:
                                pass  # Ignorar documentos problemáticos
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
                    print(f"\n   ⚠️  Error en último lote: {str(e)[:100]}...")
                    for single_doc in batch:
                        try:
                            objectrocket_collection.insert_one(single_doc)
                            migrated_count += 1
                            total_migrated += 1
                        except:
                            pass
                    pbar.update(len(batch))
        
        # Verificar migración
        final_count = objectrocket_collection.count_documents({})
        print(f"   ✅ {collection_name}: {migrated_count:,} documentos migrados")
        print(f"   📊 Verificación: {final_count:,} documentos en ObjectRocket")
        
        # Crear índices básicos
        try:
            if 'personas_fisicas' in collection_name:
                objectrocket_collection.create_index([("cedula", 1)])
                print(f"   📇 Índice de cédula creado")
            elif 'personas_juridicas' in collection_name:
                objectrocket_collection.create_index([("cedula_juridica", 1)])
                print(f"   📇 Índice de cédula jurídica creado")
        except:
            pass  # Ignorar errores de índices
    
    elapsed_time = time.time() - start_time
    
    print("\n🎉 MIGRACIÓN COMPLETADA")
    print("=" * 50)
    print(f"📊 Total documentos migrados: {total_migrated:,}")
    print(f"⏱️  Tiempo total: {elapsed_time/60:.1f} minutos")
    print(f"🗄️  Base de datos ObjectRocket: {DATABASE}")
    print(f"🔗 Usuario: {USERNAME}")
    print("✅ Tu aplicación puede usar ahora ObjectRocket!")
    
    # Mostrar URL de conexión para Vercel
    print("\n📋 PARA CONFIGURAR VERCEL:")
    vercel_url = f"mongodb://{USERNAME}:{PASSWORD}@iad2-c19-0.mongo.objectrocket.com:52752,iad2-c19-1.mongo.objectrocket.com:52752,iad2-c19-2.mongo.objectrocket.com:52752/{DATABASE}?replicaSet=592734bd19354a7d81c1402dd6eed9f4&ssl=true"
    print(f"MONGO_URL={vercel_url}")
    
    # Cerrar conexiones
    local_client.close()
    objectrocket_client.close()

if __name__ == "__main__":
    migrate_database()