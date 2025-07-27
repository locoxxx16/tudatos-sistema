#!/usr/bin/env python3
"""
Script para exportar TODA la base de datos para migración a hosting externo
"""

import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import zipfile

async def export_complete_database():
    """Exportar toda la base de datos a archivos JSON"""
    
    # Conectar a MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['daticos_db']
    
    print("🚀 Iniciando exportación completa de la base de datos...")
    
    # Crear directorio de exportación
    export_dir = f"/app/database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(export_dir, exist_ok=True)
    
    # Colecciones a exportar
    collections_to_export = [
        'personas',
        'empresas', 
        'personas_fisicas',
        'personas_juridicas',
        'provincias',
        'cantones',
        'distritos',
        'daticos_raw',
        'extraction_logs',
        'representantes_legales',
        'sms_campaigns',
        'update_statistics'
    ]
    
    export_summary = {
        'export_timestamp': datetime.utcnow().isoformat(),
        'total_collections': 0,
        'total_documents': 0,
        'collections_exported': {},
        'export_files': []
    }
    
    for collection_name in collections_to_export:
        try:
            collection = db[collection_name]
            
            # Contar documentos
            doc_count = await collection.count_documents({})
            
            if doc_count > 0:
                print(f"📄 Exportando {collection_name}: {doc_count} documentos...")
                
                # Obtener todos los documentos
                documents = await collection.find({}).to_list(None)
                
                # Convertir ObjectIds a strings para JSON
                for doc in documents:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                
                # Guardar a archivo JSON
                file_path = f"{export_dir}/{collection_name}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(documents, f, indent=2, ensure_ascii=False, default=str)
                
                export_summary['collections_exported'][collection_name] = doc_count
                export_summary['total_documents'] += doc_count
                export_summary['export_files'].append(f"{collection_name}.json")
                
                print(f"✅ {collection_name}: {doc_count} documentos exportados")
            else:
                print(f"⚪ {collection_name}: colección vacía")
                
        except Exception as e:
            print(f"❌ Error exportando {collection_name}: {e}")
            continue
    
    export_summary['total_collections'] = len(export_summary['collections_exported'])
    
    # Guardar resumen de exportación
    summary_file = f"{export_dir}/export_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(export_summary, f, indent=2, ensure_ascii=False)
    
    export_summary['export_files'].append('export_summary.json')
    
    # Crear archivo ZIP con todo
    zip_file = f"/app/database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(export_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, export_dir)
                zipf.write(file_path, arc_name)
    
    print(f"\n🎉 EXPORTACIÓN COMPLETA:")
    print(f"   📊 Total colecciones: {export_summary['total_collections']}")
    print(f"   📄 Total documentos: {export_summary['total_documents']}")
    print(f"   📁 Directorio: {export_dir}")
    print(f"   💾 Archivo ZIP: {zip_file}")
    print(f"   📋 Archivos creados: {len(export_summary['export_files'])}")
    
    # Cerrar conexión
    client.close()
    
    return {
        'success': True,
        'export_directory': export_dir,
        'zip_file': zip_file,
        'summary': export_summary
    }

async def create_import_script():
    """Crear script para importar datos en nuevo hosting"""
    
    import_script = '''#!/usr/bin/env python3
"""
Script para IMPORTAR la base de datos exportada en tu nuevo hosting
Instrucciones:
1. Instalar dependencias: pip install motor pymongo
2. Configurar MONGO_URL en tu nuevo servidor
3. Ejecutar: python import_database.py
"""

import asyncio
import json
import os
import glob
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def import_database():
    """Importar base de datos desde archivos JSON exportados"""
    
    # CONFIGURAR ESTA URL CON TU NUEVA BASE DE DATOS
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['daticos_db']  # Cambia el nombre si necesitas
    
    print("🚀 Iniciando importación de base de datos...")
    
    # Buscar archivos JSON para importar
    json_files = glob.glob("*.json")
    json_files = [f for f in json_files if f != 'export_summary.json']
    
    import_summary = {
        'import_timestamp': datetime.utcnow().isoformat(),
        'collections_imported': {},
        'total_documents_imported': 0,
        'errors': []
    }
    
    for json_file in json_files:
        try:
            collection_name = json_file.replace('.json', '')
            
            print(f"📄 Importando {collection_name}...")
            
            # Leer archivo JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            if documents:
                # Limpiar colección existente (opcional)
                # await db[collection_name].delete_many({})
                
                # Insertar documentos
                result = await db[collection_name].insert_many(documents)
                
                imported_count = len(result.inserted_ids)
                import_summary['collections_imported'][collection_name] = imported_count
                import_summary['total_documents_imported'] += imported_count
                
                print(f"✅ {collection_name}: {imported_count} documentos importados")
            else:
                print(f"⚪ {collection_name}: archivo vacío")
                
        except Exception as e:
            error_msg = f"Error importando {json_file}: {str(e)}"
            print(f"❌ {error_msg}")
            import_summary['errors'].append(error_msg)
            continue
    
    print(f"\\n🎉 IMPORTACIÓN COMPLETA:")
    print(f"   📊 Colecciones: {len(import_summary['collections_imported'])}")
    print(f"   📄 Total documentos: {import_summary['total_documents_imported']}")
    print(f"   ❌ Errores: {len(import_summary['errors'])}")
    
    # Crear índices importantes
    try:
        await db.personas.create_index("cedula", unique=True)
        await db.empresas.create_index("cedula_juridica", unique=True) 
        await db.personas_fisicas.create_index("cedula", unique=True)
        await db.personas_juridicas.create_index("cedula_juridica", unique=True)
        print("✅ Índices creados exitosamente")
    except Exception as e:
        print(f"⚠️  Error creando índices: {e}")
    
    client.close()
    return import_summary

if __name__ == "__main__":
    result = asyncio.run(import_database())
    print("\\n🎯 Importación finalizada!")
'''
    
    with open('/app/import_database.py', 'w', encoding='utf-8') as f:
        f.write(import_script)
    
    print("📝 Script de importación creado: /app/import_database.py")

if __name__ == "__main__":
    # Ejecutar exportación
    result = asyncio.run(export_complete_database())
    
    if result['success']:
        # Crear script de importación
        asyncio.run(create_import_script())
        
        print(f"\n🎯 EXPORTACIÓN LISTA PARA MIGRACIÓN:")
        print(f"📁 Todos tus datos están en: {result['zip_file']}")
        print(f"📄 {result['summary']['total_documents']} registros exportados")
        print(f"📋 Incluye script de importación para tu nuevo servidor")
    else:
        print("❌ Error en la exportación")