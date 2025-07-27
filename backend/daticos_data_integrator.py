#!/usr/bin/env python3
"""
Integrador de datos de Daticos a MongoDB con enriquecimiento automático
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional
import uuid
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DaticosDataIntegrator:
    """
    Integrador que toma datos extraídos de Daticos y los procesa para MongoDB
    con enriquecimiento automático de información
    """
    
    def __init__(self):
        # Conexión MongoDB usando variable de entorno
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = 'daticos_db'
        self.client = None
        self.db = None
        
        # Configuración de colecciones
        self.collections = {
            'personas': 'personas',
            'empresas': 'empresas',
            'raw_data': 'daticos_raw',
            'extraction_log': 'extraction_logs'
        }
        
    async def initialize_db(self):
        """Inicializar conexión a MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            
            # Probar conexión
            await self.client.admin.command('ping')
            logger.info("✅ Conexión exitosa a MongoDB")
            
            # Crear índices necesarios
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise
    
    async def create_indexes(self):
        """Crear índices optimizados para búsquedas"""
        try:
            personas_col = self.db[self.collections['personas']]
            empresas_col = self.db[self.collections['empresas']]
            
            # Índices para personas
            await personas_col.create_index("cedula", unique=True)
            await personas_col.create_index("nombre")
            await personas_col.create_index("apellidos")
            await personas_col.create_index("telefono")
            await personas_col.create_index("provincia")
            await personas_col.create_index([("nombre", "text"), ("apellidos", "text")])
            
            # Índices para empresas
            await empresas_col.create_index("cedula_juridica", unique=True)
            await empresas_col.create_index("nombre_empresa")
            await empresas_col.create_index([("nombre_empresa", "text")])
            
            logger.info("✅ Índices creados exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
    
    async def load_daticos_extraction(self, file_path: str = '/app/backend/daticos_complete_extraction.json') -> Dict:
        """Cargar datos extraídos de Daticos"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"📂 Cargados datos de extracción: {data.get('total_records', 0)} registros")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error cargando datos de extracción: {e}")
            return {}
    
    async def process_and_integrate_data(self) -> Dict:
        """Procesar e integrar todos los datos extraídos de Daticos"""
        try:
            # Cargar datos de extracción
            extraction_data = await self.load_daticos_extraction()
            if not extraction_data:
                return {'success': False, 'error': 'No data to process'}
            
            # Inicializar DB
            await self.initialize_db()
            
            # Procesar datos por categoría
            integration_stats = {
                'total_processed': 0,
                'personas_added': 0,
                'empresas_added': 0,
                'duplicates_skipped': 0,
                'errors': 0,
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
            # Guardar datos raw para respaldo
            await self.save_raw_extraction(extraction_data)
            
            # Procesar cada categoría de endpoints
            for category, endpoints in extraction_data.get('endpoints_explored', {}).items():
                logger.info(f"🔄 Procesando categoría: {category}")
                
                for endpoint_name, endpoint_data in endpoints.items():
                    extracted_records = endpoint_data.get('extracted_records', [])
                    
                    if extracted_records:
                        logger.info(f"📝 Procesando {len(extracted_records)} registros de {endpoint_name}")
                        
                        for record in extracted_records:
                            try:
                                processed_record = await self.process_single_record(
                                    record, category, endpoint_name
                                )
                                
                                if processed_record:
                                    result = await self.save_processed_record(processed_record)
                                    
                                    if result['success']:
                                        integration_stats['total_processed'] += 1
                                        if processed_record.get('tipo_persona') == 'fisica':
                                            integration_stats['personas_added'] += 1
                                        elif processed_record.get('tipo_persona') == 'juridica':
                                            integration_stats['empresas_added'] += 1
                                    else:
                                        if 'duplicate' in result.get('reason', ''):
                                            integration_stats['duplicates_skipped'] += 1
                                        else:
                                            integration_stats['errors'] += 1
                                            
                            except Exception as e:
                                logger.error(f"Error procesando registro: {e}")
                                integration_stats['errors'] += 1
                                continue
            
            # Registrar estadísticas de integración
            await self.log_integration_stats(integration_stats)
            
            logger.info(f"🎉 Integración completada:")
            logger.info(f"   📊 Total procesados: {integration_stats['total_processed']}")
            logger.info(f"   👤 Personas añadidas: {integration_stats['personas_added']}")
            logger.info(f"   🏢 Empresas añadidas: {integration_stats['empresas_added']}")
            logger.info(f"   ⏭️ Duplicados omitidos: {integration_stats['duplicates_skipped']}")
            logger.info(f"   ❌ Errores: {integration_stats['errors']}")
            
            return {'success': True, 'stats': integration_stats}
            
        except Exception as e:
            logger.error(f"❌ Error durante integración: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    async def save_raw_extraction(self, extraction_data: Dict):
        """Guardar datos de extracción raw para respaldo"""
        try:
            raw_col = self.db[self.collections['raw_data']]
            
            raw_record = {
                'extraction_id': str(uuid.uuid4()),
                'timestamp': extraction_data.get('extraction_timestamp'),
                'credentials_used': extraction_data.get('credentials_used'),
                'total_records': extraction_data.get('total_records', 0),
                'data': extraction_data,
                'imported_at': datetime.utcnow().isoformat()
            }
            
            await raw_col.insert_one(raw_record)
            logger.info("📦 Datos raw guardados para respaldo")
            
        except Exception as e:
            logger.error(f"Error guardando datos raw: {e}")
    
    async def process_single_record(self, record: Dict, category: str, endpoint_name: str) -> Optional[Dict]:
        """Procesar un registro individual y enriquecerlo"""
        try:
            processed_record = {
                'id': str(uuid.uuid4()),
                'source_category': category,
                'source_endpoint': endpoint_name,
                'raw_data': record,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            # Extraer y normalizar información según el tipo de registro
            if self.contains_cedula_data(record):
                processed_record.update(await self.extract_cedula_info(record))
            
            if self.contains_personal_data(record):
                processed_record.update(await self.extract_personal_info(record))
            
            if self.contains_contact_data(record):
                processed_record.update(await self.extract_contact_info(record))
            
            if self.contains_location_data(record):
                processed_record.update(await self.extract_location_info(record))
            
            if self.contains_business_data(record):
                processed_record.update(await self.extract_business_info(record))
            
            # Determinar tipo de persona (física/jurídica)
            processed_record['tipo_persona'] = self.determine_person_type(processed_record)
            
            # Enriquecer con información adicional
            processed_record = await self.enrich_record_data(processed_record)
            
            return processed_record
            
        except Exception as e:
            logger.error(f"Error procesando registro individual: {e}")
            return None
    
    def contains_cedula_data(self, record: Dict) -> bool:
        """Verificar si el registro contiene datos de cédula"""
        cedula_fields = ['cedula', 'documento', 'id', 'identificacion']
        text_content = str(record).lower()
        
        return any(field in text_content for field in cedula_fields) or \
               any(re.search(r'\b\d{1,2}-\d{4}-\d{4}\b', str(value)) for value in record.values())
    
    def contains_personal_data(self, record: Dict) -> bool:
        """Verificar si contiene datos personales"""
        personal_fields = ['nombre', 'apellido', 'name', 'surname']
        return any(field in str(record).lower() for field in personal_fields)
    
    def contains_contact_data(self, record: Dict) -> bool:
        """Verificar si contiene datos de contacto"""
        contact_fields = ['telefono', 'phone', 'email', 'correo']
        text_content = str(record).lower()
        
        return any(field in text_content for field in contact_fields) or \
               any(re.search(r'\b\d{4}-\d{4}\b|\b\d{8}\b', str(value)) for value in record.values())
    
    def contains_location_data(self, record: Dict) -> bool:
        """Verificar si contiene datos de ubicación"""
        location_fields = ['provincia', 'canton', 'distrito', 'direccion', 'address']
        return any(field in str(record).lower() for field in location_fields)
    
    def contains_business_data(self, record: Dict) -> bool:
        """Verificar si contiene datos empresariales"""
        business_fields = ['empresa', 'company', 'sociedad', 'comercio', 'negocio']
        return any(field in str(record).lower() for field in business_fields)
    
    async def extract_cedula_info(self, record: Dict) -> Dict:
        """Extraer información de cédula"""
        cedula_info = {}
        
        # Buscar cédulas en diferentes formatos
        for key, value in record.items():
            if isinstance(value, str):
                # Formato X-XXXX-XXXX (físicas) o 3-XXX-XXXXXX (jurídicas)
                cedula_match = re.search(r'\b(\d{1,2}-\d{3,4}-\d{4,6})\b', value)
                if cedula_match:
                    cedula_info['cedula'] = cedula_match.group(1)
                    break
                
                # Formato sin guiones
                cedula_match = re.search(r'\b(\d{9,12})\b', value)
                if cedula_match and 'cedula' in key.lower():
                    cedula_raw = cedula_match.group(1)
                    cedula_info['cedula'] = self.format_cedula(cedula_raw)
                    break
        
        return cedula_info
    
    def format_cedula(self, cedula_raw: str) -> str:
        """Formatear cédula sin guiones a formato estándar"""
        if len(cedula_raw) == 9:  # Cédula física
            return f"{cedula_raw[0]}-{cedula_raw[1:5]}-{cedula_raw[5:9]}"
        elif len(cedula_raw) >= 10:  # Cédula jurídica
            return f"{cedula_raw[0]}-{cedula_raw[1:4]}-{cedula_raw[4:]}"
        return cedula_raw
    
    async def extract_personal_info(self, record: Dict) -> Dict:
        """Extraer información personal (nombres, apellidos)"""
        personal_info = {}
        
        for key, value in record.items():
            if isinstance(value, str) and value.strip():
                key_lower = key.lower()
                
                if 'nombre' in key_lower or 'name' in key_lower:
                    personal_info['nombre'] = value.strip().title()
                elif 'apellido' in key_lower or 'surname' in key_lower:
                    personal_info['apellidos'] = value.strip().title()
        
        # Si hay nombres completos, intentar separar
        for key, value in record.items():
            if isinstance(value, str) and len(value.split()) > 1:
                if 'nombre' in key.lower() and 'apellidos' not in personal_info:
                    parts = value.strip().split()
                    if len(parts) >= 2:
                        personal_info['nombre'] = parts[0].title()
                        personal_info['apellidos'] = ' '.join(parts[1:]).title()
                        break
        
        return personal_info
    
    async def extract_contact_info(self, record: Dict) -> Dict:
        """Extraer información de contacto"""
        contact_info = {}
        
        for key, value in record.items():
            if isinstance(value, str):
                key_lower = key.lower()
                
                # Teléfonos
                if 'telefono' in key_lower or 'phone' in key_lower:
                    contact_info['telefono'] = value.strip()
                
                # Email
                elif 'email' in key_lower or 'correo' in key_lower:
                    contact_info['email'] = value.strip().lower()
                
                # Buscar números de teléfono en el texto
                elif not contact_info.get('telefono'):
                    phone_match = re.search(r'\b(\d{4}-\d{4}|\d{8})\b', value)
                    if phone_match:
                        contact_info['telefono'] = phone_match.group(1)
        
        return contact_info
    
    async def extract_location_info(self, record: Dict) -> Dict:
        """Extraer información de ubicación"""
        location_info = {}
        
        for key, value in record.items():
            if isinstance(value, str) and value.strip():
                key_lower = key.lower()
                
                if 'provincia' in key_lower or 'province' in key_lower:
                    location_info['provincia'] = value.strip().title()
                elif 'canton' in key_lower or 'county' in key_lower:
                    location_info['canton'] = value.strip().title()
                elif 'distrito' in key_lower or 'district' in key_lower:
                    location_info['distrito'] = value.strip().title()
                elif 'direccion' in key_lower or 'address' in key_lower:
                    location_info['direccion'] = value.strip()
        
        return location_info
    
    async def extract_business_info(self, record: Dict) -> Dict:
        """Extraer información empresarial"""
        business_info = {}
        
        for key, value in record.items():
            if isinstance(value, str) and value.strip():
                key_lower = key.lower()
                
                if 'empresa' in key_lower or 'company' in key_lower:
                    business_info['nombre_empresa'] = value.strip().title()
                elif 'actividad' in key_lower or 'activity' in key_lower:
                    business_info['actividad_comercial'] = value.strip()
                elif 'sector' in key_lower:
                    business_info['sector'] = value.strip()
        
        return business_info
    
    def determine_person_type(self, record: Dict) -> str:
        """Determinar si es persona física o jurídica"""
        cedula = record.get('cedula', '')
        
        if cedula.startswith('3-') or 'juridica' in str(record).lower():
            return 'juridica'
        elif cedula and not cedula.startswith('3-'):
            return 'fisica'
        elif record.get('nombre_empresa'):
            return 'juridica'
        else:
            return 'fisica'
    
    async def enrich_record_data(self, record: Dict) -> Dict:
        """Enriquecer registro con información adicional"""
        # Agregar metadata de enriquecimiento
        record['enrichment'] = {
            'data_quality_score': self.calculate_data_quality_score(record),
            'completeness_percentage': self.calculate_completeness_percentage(record),
            'last_enriched': datetime.utcnow().isoformat()
        }
        
        # Agregar categorización automática
        record['categories'] = self.categorize_record(record)
        
        return record
    
    def calculate_data_quality_score(self, record: Dict) -> float:
        """Calcular score de calidad de datos (0-1)"""
        quality_factors = []
        
        # Factor 1: Existencia de cédula
        quality_factors.append(1.0 if record.get('cedula') else 0.0)
        
        # Factor 2: Información personal completa
        if record.get('nombre') and record.get('apellidos'):
            quality_factors.append(1.0)
        elif record.get('nombre') or record.get('apellidos'):
            quality_factors.append(0.5)
        else:
            quality_factors.append(0.0)
        
        # Factor 3: Información de contacto
        quality_factors.append(1.0 if record.get('telefono') else 0.0)
        
        # Factor 4: Información de ubicación
        location_score = 0.0
        if record.get('provincia'): location_score += 0.4
        if record.get('canton'): location_score += 0.3
        if record.get('distrito'): location_score += 0.3
        quality_factors.append(location_score)
        
        return sum(quality_factors) / len(quality_factors)
    
    def calculate_completeness_percentage(self, record: Dict) -> int:
        """Calcular porcentaje de completitud de campos importantes"""
        important_fields = [
            'cedula', 'nombre', 'apellidos', 'telefono', 
            'provincia', 'canton', 'distrito'
        ]
        
        filled_fields = sum(1 for field in important_fields if record.get(field))
        return int((filled_fields / len(important_fields)) * 100)
    
    def categorize_record(self, record: Dict) -> List[str]:
        """Categorizar registro automáticamente"""
        categories = []
        
        if record.get('tipo_persona') == 'juridica':
            categories.append('empresa')
        else:
            categories.append('persona_fisica')
        
        if record.get('telefono'):
            categories.append('con_telefono')
        
        if record.get('provincia'):
            categories.append(f"provincia_{record['provincia'].lower().replace(' ', '_')}")
        
        if record.get('enrichment', {}).get('data_quality_score', 0) > 0.7:
            categories.append('alta_calidad')
        
        return categories
    
    async def save_processed_record(self, record: Dict) -> Dict:
        """Guardar registro procesado en la colección apropiada"""
        try:
            # Determinar colección según tipo de persona
            if record.get('tipo_persona') == 'juridica':
                collection = self.db[self.collections['empresas']]
                unique_field = 'cedula'  # Para empresas, usar cédula jurídica
            else:
                collection = self.db[self.collections['personas']]
                unique_field = 'cedula'  # Para personas físicas, usar cédula
            
            # Verificar si ya existe (evitar duplicados)
            if record.get(unique_field):
                existing = await collection.find_one({unique_field: record[unique_field]})
                if existing:
                    # Actualizar registro existente con nueva información
                    update_result = await collection.update_one(
                        {unique_field: record[unique_field]},
                        {
                            '$set': {
                                'updated_at': datetime.utcnow().isoformat(),
                                'additional_sources': existing.get('additional_sources', []) + [record['source_endpoint']]
                            },
                            '$addToSet': {
                                'raw_data_history': record['raw_data']
                            }
                        }
                    )
                    return {'success': True, 'action': 'updated', 'reason': 'duplicate_cedula'}
            
            # Insertar nuevo registro
            record['created_at'] = datetime.utcnow().isoformat()
            record['updated_at'] = record['created_at']
            record['additional_sources'] = [record['source_endpoint']]
            
            await collection.insert_one(record)
            return {'success': True, 'action': 'inserted'}
            
        except Exception as e:
            logger.error(f"Error guardando registro: {e}")
            return {'success': False, 'error': str(e)}
    
    async def log_integration_stats(self, stats: Dict):
        """Registrar estadísticas de integración"""
        try:
            log_col = self.db[self.collections['extraction_log']]
            
            log_record = {
                'log_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'process_type': 'daticos_integration',
                'stats': stats
            }
            
            await log_col.insert_one(log_record)
            logger.info("📝 Estadísticas de integración registradas")
            
        except Exception as e:
            logger.error(f"Error registrando estadísticas: {e}")
    
    async def close_connection(self):
        """Cerrar conexión a MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔚 Conexión MongoDB cerrada")

# Función principal para ejecutar la integración
async def run_data_integration():
    """Ejecutar proceso completo de integración de datos"""
    integrator = DaticosDataIntegrator()
    
    try:
        logger.info("🚀 Iniciando integración de datos Daticos a MongoDB...")
        
        result = await integrator.process_and_integrate_data()
        
        if result['success']:
            logger.info("🎉 ¡Integración de datos completada exitosamente!")
            return result['stats']
        else:
            logger.error(f"❌ Error en integración: {result['error']}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error durante integración: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        await integrator.close_connection()

if __name__ == "__main__":
    # Ejecutar integración
    result = asyncio.run(run_data_integration())
    if result:
        print(f"\n🎯 INTEGRACIÓN COMPLETADA:")
        print(f"   📊 Total procesados: {result.get('total_processed', 0)}")
        print(f"   👤 Personas añadidas: {result.get('personas_added', 0)}")
        print(f"   🏢 Empresas añadidas: {result.get('empresas_added', 0)}")
        print(f"   ⏭️ Duplicados omitidos: {result.get('duplicates_skipped', 0)}")
        print(f"   ❌ Errores: {result.get('errors', 0)}")
    else:
        print("\n❌ Integración falló")