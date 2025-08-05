#!/usr/bin/env python3
"""
SCRIPT DE MIGRACIÓN COMPLETA
Migra todos los datos de MongoDB local a MongoDB Atlas M10
"""

import pymongo
import os
from tqdm import tqdm
import time

# Configuración
LOCAL_MONGO = "mongodb://localhost:27017"
LOCAL_DB = "test_database"

# Atlas connection (será actualizada con tu string real)
ATLAS_MONGO = "mongodb+srv://tudatos_admin:PASSWORD@tudatos-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority"
ATLAS_DB = "tudatos_system"

def migrate_database():
    print("🚀 INICIANDO MIGRACIÓN DE 5.9M REGISTROS")
    print("=" * 50)
    
    # Conectar a bases de datos
    local_client = pymongo.MongoClient(LOCAL_MONGO)
    local_db = local_client[LOCAL_DB]
    
    atlas_client = pymongo.MongoClient(ATLAS_MONGO)
    atlas_db = atlas_client[ATLAS_DB]
    
    # Obtener colecciones importantes
    important_collections = [
        'personas_fisicas_fast2m',      # 4M registros
        'personas_juridicas_fast2m',    # 1M registros  
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
        atlas_collection = atlas_db[collection_name]
        
        # Contar documentos
        total_docs = local_collection.count_documents({})
        print(f"   Documentos a migrar: {total_docs:,}")
        
        if total_docs == 0:
            print("   ⏭️  Colección vacía, saltando...")
            continue
            
        # Limpiar colección destino
        atlas_collection.delete_many({})
        
        # Migrar en lotes de 1000
        batch_size = 1000
        with tqdm(total=total_docs, desc=f"   {collection_name}") as pbar:
            cursor = local_collection.find().batch_size(batch_size)
            batch = []
            
            for doc in cursor:
                batch.append(doc)
                
                if len(batch) >= batch_size:
                    atlas_collection.insert_many(batch)
                    batch = []
                    pbar.update(batch_size)
                    total_migrated += batch_size
            
            # Insertar último lote
            if batch:
                atlas_collection.insert_many(batch)
                pbar.update(len(batch))
                total_migrated += len(batch)
        
        print(f"   ✅ {collection_name}: {total_docs:,} documentos migrados")
    
    print("\n🎉 MIGRACIÓN COMPLETADA")
    print(f"📊 Total documentos migrados: {total_migrated:,}")
    print("✅ Tu base de datos está ahora en MongoDB Atlas M10")

if __name__ == "__main__":
    migrate_database()