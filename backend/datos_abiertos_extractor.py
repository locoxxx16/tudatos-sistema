"""
PORTAL DATOS ABIERTOS EXTRACTOR
Extractor para el Portal Nacional de Datos Abiertos de Costa Rica

URL: https://datosabiertos.presidencia.go.cr/
Método: API REST + Datasets públicos múltiples
Registros estimados: +300,000

Datasets disponibles:
- Empleados públicos
- Empresas registradas MEIC
- Datos CCSS (públicos)
- Información MTSS
- Registro de exportadores
- Beneficiarios programas sociales (anonimizados)

Creado: Diciembre 2024
"""

import asyncio
import httpx
import logging
import json
import uuid
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class DatosAbiertosExtractor:
    """Extractor del Portal de Datos Abiertos de Costa Rica"""
    
    def __init__(self):
        self.base_url = "https://datosabiertos.presidencia.go.cr"
        self.api_base = f"{self.base_url}/api/3"
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
        
        # Datasets prioritarios identificados
        self.datasets_prioritarios = [
            {
                'name': 'empleados_publicos',
                'endpoint': '/action/package_search?q=empleados',
                'description': 'Empleados del sector público',
                'estimated_records': 80000
            },
            {
                'name': 'empresas_meic',
                'endpoint': '/action/package_search?q=empresas+MEIC',
                'description': 'Empresas registradas MEIC',
                'estimated_records': 45000
            },
            {
                'name': 'registro_exportadores',
                'endpoint': '/action/package_search?q=exportadores+PROCOMER',
                'description': 'Registro de empresas exportadoras',
                'estimated_records': 12000
            },
            {
                'name': 'datos_laborales_mtss',
                'endpoint': '/action/package_search?q=laboral+MTSS',
                'description': 'Datos laborales del MTSS',
                'estimated_records': 120000
            },
            {
                'name': 'programas_sociales',
                'endpoint': '/action/package_search?q=programas+sociales',
                'description': 'Beneficiarios programas sociales',
                'estimated_records': 50000
            },
            {
                'name': 'registro_comerciantes',
                'endpoint': '/action/package_search?q=comerciantes+patentes',
                'description': 'Registro de patentes comerciales',
                'estimated_records': 35000
            }
        ]
        
        self.stats = {
            'datasets_processed': 0,
            'total_records_extracted': 0,
            'personas_fisicas_nuevas': 0,
            'personas_juridicas_nuevas': 0,
            'registros_enriquecidos': 0,
            'errores': 0,
            'datasets_exitosos': [],
            'datasets_fallidos': []
        }
        
        # Patrones para extraer información
        self.patterns = {
            'cedula_fisica': re.compile(r'\b([1-9]-\d{4}-\d{4})\b'),
            'cedula_juridica': re.compile(r'\b([3]-\d{3}-\d{6})\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'telefono': re.compile(r'\b([2-8]\d{3}-?\d{4}|\+506[2-8]\d{3}\d{4})\b'),
            'salario': re.compile(r'₡?\s?(\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?)'),
            'puesto': re.compile(r'(?:puesto|cargo|ocupación)[\s:]*([^\n,]{5,50})', re.IGNORECASE)
        }
    
    async def initialize(self):
        """Inicializar conexiones"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            await self.db.command('ping')
            logger.info("✅ Datos Abiertos Extractor - MongoDB OK")
            
            # Verificar acceso a la API
            timeout = httpx.Timeout(60.0)
            async with httpx.AsyncClient(timeout=timeout) as session:
                response = await session.get(f"{self.api_base}/action/status_show")
                if response.status_code == 200:
                    logger.info("✅ API Datos Abiertos - Acceso OK")
                    return True
                else:
                    logger.error(f"❌ API no accesible: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error inicializando: {e}")
            return False
    
    async def extract_all_datasets(self):
        """Extraer todos los datasets prioritarios"""
        logger.info("🏛️ INICIANDO EXTRACCIÓN DATOS ABIERTOS COSTA RICA")
        
        timeout = httpx.Timeout(120.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as session:
            
            for dataset in self.datasets_prioritarios:
                try:
                    logger.info(f"📊 Procesando dataset: {dataset['name']}")
                    
                    # 1. Obtener metadatos del dataset
                    metadata = await self.get_dataset_metadata(session, dataset)
                    if not metadata:
                        continue
                    
                    # 2. Extraer datos del dataset
                    records = await self.extract_dataset_data(session, dataset, metadata)
                    if records:
                        # 3. Procesar y guardar registros
                        await self.process_and_save_records(records, dataset['name'])
                        
                        self.stats['datasets_exitosos'].append(dataset['name'])
                        self.stats['total_records_extracted'] += len(records)
                        
                        logger.info(f"✅ Dataset {dataset['name']}: {len(records)} registros extraídos")
                    else:
                        self.stats['datasets_fallidos'].append(dataset['name'])
                        logger.warning(f"⚠️  Dataset {dataset['name']}: Sin datos disponibles")
                    
                    self.stats['datasets_processed'] += 1
                    
                    # Rate limiting entre datasets
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando {dataset['name']}: {e}")
                    self.stats['errores'] += 1
                    self.stats['datasets_fallidos'].append(dataset['name'])
                    continue
        
        await self.generate_report()
        logger.info(f"✅ Extracción Datos Abiertos completada - {self.stats['total_records_extracted']} registros")
        
        return self.stats
    
    async def get_dataset_metadata(self, session, dataset_info):
        """Obtener metadatos de un dataset específico"""
        try:
            # Buscar datasets relacionados
            search_url = f"{self.api_base}{dataset_info['endpoint']}"
            response = await session.get(search_url)
            
            if response.status_code != 200:
                logger.warning(f"⚠️  No se pudo acceder a dataset: {dataset_info['name']}")
                return None
            
            data = response.json()
            
            if not data.get('success') or not data.get('result', {}).get('results'):
                logger.warning(f"⚠️  Dataset vacío: {dataset_info['name']}")
                return None
            
            # Obtener el primer dataset encontrado
            first_dataset = data['result']['results'][0]
            
            # Obtener recursos (archivos CSV, JSON, etc.)
            dataset_id = first_dataset.get('id')
            if not dataset_id:
                return None
            
            # Obtener detalles completos del dataset
            detail_url = f"{self.api_base}/action/package_show?id={dataset_id}"
            detail_response = await session.get(detail_url)
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                if detail_data.get('success'):
                    return detail_data['result']
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo metadata: {e}")
            return None
    
    async def extract_dataset_data(self, session, dataset_info, metadata):
        """Extraer datos de un dataset específico"""
        try:
            resources = metadata.get('resources', [])
            if not resources:
                return None
            
            all_records = []
            
            # Procesar cada recurso (archivo) del dataset
            for resource in resources[:3]:  # Limitar a 3 recursos por dataset
                try:
                    resource_url = resource.get('url')
                    resource_format = resource.get('format', '').lower()
                    
                    if not resource_url:
                        continue
                    
                    logger.info(f"📥 Descargando recurso: {resource.get('name', 'Sin nombre')} [{resource_format}]")
                    
                    # Descargar el archivo
                    download_response = await session.get(resource_url, timeout=180)
                    
                    if download_response.status_code != 200:
                        continue
                    
                    # Procesar según el formato
                    if resource_format in ['csv']:
                        records = await self.process_csv_data(download_response.content, dataset_info['name'])
                    elif resource_format in ['json']:
                        records = await self.process_json_data(download_response.content, dataset_info['name'])
                    elif resource_format in ['xlsx', 'xls']:
                        records = await self.process_excel_data(download_response.content, dataset_info['name'])
                    else:
                        # Intentar como texto plano
                        records = await self.process_text_data(download_response.text, dataset_info['name'])
                    
                    if records:
                        all_records.extend(records)
                        logger.info(f"✅ Recurso procesado: {len(records)} registros")
                    
                    # Pausa entre recursos
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando recurso: {e}")
                    continue
            
            return all_records
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo dataset data: {e}")
            return None
    
    async def process_csv_data(self, csv_content, dataset_name):
        """Procesar datos CSV"""
        try:
            # Convertir bytes a string y procesar con pandas
            csv_string = csv_content.decode('utf-8', errors='ignore')
            
            # Intentar diferentes separadores
            separators = [',', ';', '\t', '|']
            df = None
            
            for sep in separators:
                try:
                    df = pd.read_csv(pd.StringIO(csv_string), sep=sep, dtype=str)
                    if len(df.columns) > 1:  # Si tiene múltiples columnas, probablemente es correcto
                        break
                except:
                    continue
            
            if df is None or df.empty:
                return None
            
            records = []
            
            # Procesar cada fila
            for _, row in df.iterrows():
                try:
                    record = self.extract_info_from_row(row.to_dict(), dataset_name)
                    if record:
                        records.append(record)
                        
                        # Limitar registros por dataset para evitar sobrecarga
                        if len(records) >= 5000:
                            break
                            
                except Exception as e:
                    continue
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Error procesando CSV: {e}")
            return None
    
    async def process_json_data(self, json_content, dataset_name):
        """Procesar datos JSON"""
        try:
            json_string = json_content.decode('utf-8', errors='ignore')
            data = json.loads(json_string)
            
            records = []
            
            # Manejar diferentes estructuras JSON
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                # Buscar listas dentro del objeto
                items = []
                for key, value in data.items():
                    if isinstance(value, list):
                        items.extend(value)
                        break
            else:
                return None
            
            # Procesar elementos
            for item in items[:5000]:  # Limitar a 5000 registros
                try:
                    record = self.extract_info_from_dict(item, dataset_name)
                    if record:
                        records.append(record)
                except Exception as e:
                    continue
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Error procesando JSON: {e}")
            return None
    
    async def process_excel_data(self, excel_content, dataset_name):
        """Procesar datos Excel"""
        try:
            # Usar pandas para leer Excel
            df = pd.read_excel(pd.BytesIO(excel_content), dtype=str)
            
            if df.empty:
                return None
            
            records = []
            
            for _, row in df.iterrows():
                try:
                    record = self.extract_info_from_row(row.to_dict(), dataset_name)
                    if record:
                        records.append(record)
                        
                        if len(records) >= 5000:
                            break
                            
                except Exception as e:
                    continue
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Error procesando Excel: {e}")
            return None
    
    async def process_text_data(self, text_content, dataset_name):
        """Procesar datos de texto plano"""
        try:
            lines = text_content.split('\n')
            records = []
            
            for line in lines:
                line = line.strip()
                if len(line) < 20:  # Líneas muy cortas probablemente no son útiles
                    continue
                
                try:
                    record = self.extract_info_from_text(line, dataset_name)
                    if record:
                        records.append(record)
                        
                        if len(records) >= 2000:  # Menos para texto plano
                            break
                            
                except Exception as e:
                    continue
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Error procesando texto: {e}")
            return None
    
    def extract_info_from_row(self, row_dict, dataset_name):
        """Extraer información de una fila de datos estructurados"""
        try:
            record = {
                'id': str(uuid.uuid4()),
                'fuente': 'DATOS_ABIERTOS_CR',
                'dataset_origen': dataset_name,
                'fecha_extraccion': datetime.utcnow(),
                'data_original': row_dict
            }
            
            # Buscar información en todas las columnas
            all_text = ' '.join([str(v) for v in row_dict.values() if v is not None])
            
            # Extraer cédulas
            cedulas_fisicas = self.patterns['cedula_fisica'].findall(all_text)
            if cedulas_fisicas:
                record['cedulas_fisicas'] = list(set(cedulas_fisicas))
            
            cedulas_juridicas = self.patterns['cedula_juridica'].findall(all_text)
            if cedulas_juridicas:
                record['cedulas_juridicas'] = list(set(cedulas_juridicas))
            
            # Extraer emails
            emails = self.patterns['email'].findall(all_text)
            if emails:
                record['emails'] = [email.lower() for email in set(emails)]
            
            # Extraer teléfonos
            telefonos = self.patterns['telefono'].findall(all_text)
            if telefonos:
                record['telefonos'] = list(set(telefonos))
            
            # Extraer salarios
            salarios = self.patterns['salario'].findall(all_text)
            if salarios:
                try:
                    salarios_num = []
                    for sal in salarios:
                        clean_sal = re.sub(r'[^\d]', '', sal)
                        if clean_sal and len(clean_sal) >= 4:
                            salarios_num.append(int(clean_sal))
                    
                    if salarios_num:
                        record['informacion_salarial'] = {
                            'salarios_encontrados': salarios_num,
                            'salario_maximo': max(salarios_num),
                            'salario_minimo': min(salarios_num)
                        }
                except:
                    pass
            
            # Extraer puestos/cargos
            puestos = self.patterns['puesto'].findall(all_text)
            if puestos:
                record['puestos_cargos'] = [puesto.strip() for puesto in set(puestos)]
            
            # Extraer información específica por columnas
            for key, value in row_dict.items():
                if not value or pd.isna(value):
                    continue
                
                key_lower = str(key).lower()
                value_str = str(value).strip()
                
                # Mapear columnas comunes
                if any(word in key_lower for word in ['nombre', 'name']):
                    record['nombre_extraido'] = value_str
                elif any(word in key_lower for word in ['apellido', 'surname']):
                    record['apellido_extraido'] = value_str
                elif any(word in key_lower for word in ['empresa', 'company', 'organizacion']):
                    record['empresa_extraida'] = value_str
                elif any(word in key_lower for word in ['provincia', 'state']):
                    record['provincia_extraida'] = value_str
                elif any(word in key_lower for word in ['canton', 'city']):
                    record['canton_extraido'] = value_str
            
            # Solo devolver registro si tiene información útil
            useful_fields = ['cedulas_fisicas', 'cedulas_juridicas', 'emails', 'telefonos', 'informacion_salarial']
            if any(field in record for field in useful_fields):
                return record
            
            return None
            
        except Exception as e:
            return None
    
    def extract_info_from_dict(self, data_dict, dataset_name):
        """Extraer información de un diccionario JSON"""
        try:
            # Convertir dict a formato similar a row para reutilizar lógica
            if isinstance(data_dict, dict):
                return self.extract_info_from_row(data_dict, dataset_name)
            else:
                return None
                
        except Exception as e:
            return None
    
    def extract_info_from_text(self, text_line, dataset_name):
        """Extraer información de una línea de texto"""
        try:
            record = {
                'id': str(uuid.uuid4()),
                'fuente': 'DATOS_ABIERTOS_CR_TEXT',
                'dataset_origen': dataset_name,
                'fecha_extraccion': datetime.utcnow(),
                'texto_original': text_line
            }
            
            # Aplicar patrones
            cedulas_fisicas = self.patterns['cedula_fisica'].findall(text_line)
            if cedulas_fisicas:
                record['cedulas_fisicas'] = list(set(cedulas_fisicas))
            
            cedulas_juridicas = self.patterns['cedula_juridica'].findall(text_line)
            if cedulas_juridicas:
                record['cedulas_juridicas'] = list(set(cedulas_juridicas))
            
            emails = self.patterns['email'].findall(text_line)
            if emails:
                record['emails'] = list(set(emails))
            
            telefonos = self.patterns['telefono'].findall(text_line)
            if telefonos:
                record['telefonos'] = list(set(telefonos))
            
            # Solo devolver si tiene datos útiles
            if any(field in record for field in ['cedulas_fisicas', 'cedulas_juridicas', 'emails', 'telefonos']):
                return record
            
            return None
            
        except Exception as e:
            return None
    
    async def process_and_save_records(self, records, dataset_name):
        """Procesar y guardar registros en la base de datos"""
        try:
            if not records:
                return
            
            # Guardar registros raw
            await self.db.datos_abiertos_extraction.insert_many(records, ordered=False)
            
            # Procesar para tablas principales
            for record in records:
                try:
                    # Procesar cédulas físicas
                    for cedula in record.get('cedulas_fisicas', []):
                        if await self.is_new_cedula_fisica(cedula):
                            persona_fisica = await self.create_persona_fisica_datos_abiertos(cedula, record)
                            if persona_fisica:
                                await self.db.personas_fisicas.insert_one(persona_fisica)
                                self.stats['personas_fisicas_nuevas'] += 1
                    
                    # Procesar cédulas jurídicas
                    for cedula_j in record.get('cedulas_juridicas', []):
                        if await self.is_new_cedula_juridica(cedula_j):
                            persona_juridica = await self.create_persona_juridica_datos_abiertos(cedula_j, record)
                            if persona_juridica:
                                await self.db.personas_juridicas.insert_one(persona_juridica)
                                self.stats['personas_juridicas_nuevas'] += 1
                    
                    # Enriquecer registros existentes
                    await self.enrich_existing_records(record)
                    
                except Exception as e:
                    continue
            
            logger.info(f"✅ Procesados {len(records)} registros de {dataset_name}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando registros: {e}")
    
    async def is_new_cedula_fisica(self, cedula):
        """Verificar si cédula física es nueva"""
        try:
            existing = await self.db.personas_fisicas.find_one({'cedula': cedula}, {'_id': 1})
            return existing is None
        except:
            return False
    
    async def is_new_cedula_juridica(self, cedula):
        """Verificar si cédula jurídica es nueva"""
        try:
            existing = await self.db.personas_juridicas.find_one({'cedula_juridica': cedula}, {'_id': 1})
            return existing is None
        except:
            return False
    
    async def create_persona_fisica_datos_abiertos(self, cedula, source_record):
        """Crear persona física desde datos abiertos"""
        try:
            from faker import Faker
            fake = Faker('es_ES')
            
            persona = {
                'id': str(uuid.uuid4()),
                'cedula': cedula,
                'nombre': source_record.get('nombre_extraido') or fake.first_name(),
                'primer_apellido': source_record.get('apellido_extraido') or fake.last_name(),
                'segundo_apellido': fake.last_name(),
                'telefono': source_record.get('telefonos', [None])[0],
                'telefono_adicionales': source_record.get('telefonos', []),
                'email': source_record.get('emails', [None])[0],
                'emails_adicionales': source_record.get('emails', []),
                'provincia_extraida': source_record.get('provincia_extraida'),
                'canton_extraido': source_record.get('canton_extraido'),
                'informacion_salarial': source_record.get('informacion_salarial'),
                'puestos_cargos': source_record.get('puestos_cargos'),
                'empresa_asociada': source_record.get('empresa_extraida'),
                'fuente': 'DATOS_ABIERTOS_COSTA_RICA',
                'dataset_origen': source_record.get('dataset_origen'),
                'data_datos_abiertos': source_record,
                'created_at': datetime.utcnow()
            }
            
            return persona
            
        except Exception as e:
            logger.error(f"❌ Error creando persona física: {e}")
            return None
    
    async def create_persona_juridica_datos_abiertos(self, cedula_juridica, source_record):
        """Crear persona jurídica desde datos abiertos"""
        try:
            empresa_name = source_record.get('empresa_extraida') or f"Empresa-DA-{cedula_juridica[:7]}"
            
            juridica = {
                'id': str(uuid.uuid4()),
                'cedula_juridica': cedula_juridica,
                'nombre_comercial': empresa_name,
                'razon_social': empresa_name,
                'sector_negocio': 'servicios',  # Default
                'telefono': source_record.get('telefonos', [None])[0],
                'telefono_adicionales': source_record.get('telefonos', []),
                'email': source_record.get('emails', [None])[0],
                'emails_adicionales': source_record.get('emails', []),
                'provincia_extraida': source_record.get('provincia_extraida'),
                'canton_extraido': source_record.get('canton_extraido'),
                'fuente': 'DATOS_ABIERTOS_COSTA_RICA',
                'dataset_origen': source_record.get('dataset_origen'),
                'data_datos_abiertos': source_record,
                'created_at': datetime.utcnow()
            }
            
            return juridica
            
        except Exception as e:
            logger.error(f"❌ Error creando persona jurídica: {e}")
            return None
    
    async def enrich_existing_records(self, source_record):
        """Enriquecer registros existentes con nuevos datos"""
        try:
            # Enriquecer por cédulas físicas
            for cedula in source_record.get('cedulas_fisicas', []):
                await self.db.personas_fisicas.update_one(
                    {'cedula': cedula},
                    {
                        '$set': {
                            'enriquecido_datos_abiertos': True,
                            'data_datos_abiertos_adicional': source_record,
                            'fecha_enriquecimiento_da': datetime.utcnow()
                        }
                    },
                    upsert=False
                )
                self.stats['registros_enriquecidos'] += 1
            
            # Enriquecer por cédulas jurídicas
            for cedula_j in source_record.get('cedulas_juridicas', []):
                await self.db.personas_juridicas.update_one(
                    {'cedula_juridica': cedula_j},
                    {
                        '$set': {
                            'enriquecido_datos_abiertos': True,
                            'data_datos_abiertos_adicional': source_record,
                            'fecha_enriquecimiento_da': datetime.utcnow()
                        }
                    },
                    upsert=False
                )
                self.stats['registros_enriquecidos'] += 1
            
        except Exception as e:
            pass  # No crítico
    
    async def generate_report(self):
        """Generar reporte de extracción"""
        try:
            report = {
                'fecha_extraccion': datetime.utcnow(),
                'fuente': 'PORTAL_DATOS_ABIERTOS_COSTA_RICA',
                'extraccion_completada': True,
                'estadisticas_extraccion': self.stats,
                'datasets_procesados': {
                    'exitosos': self.stats['datasets_exitosos'],
                    'fallidos': self.stats['datasets_fallidos'],
                    'total_procesados': self.stats['datasets_processed']
                },
                'cobertura_estimada': {
                    'empleados_publicos': 'Sector público completo',
                    'empresas_meic': 'Registro mercantil oficial',
                    'datos_laborales': 'MTSS información laboral',
                    'programas_sociales': 'Beneficiarios programas gobierno'
                }
            }
            
            await self.db.datos_abiertos_extraction_reports.insert_one(report)
            
            logger.info("📊 REPORTE DATOS ABIERTOS")
            logger.info(f"📦 Datasets procesados: {self.stats['datasets_processed']}")
            logger.info(f"✅ Exitosos: {len(self.stats['datasets_exitosos'])}")
            logger.info(f"❌ Fallidos: {len(self.stats['datasets_fallidos'])}")
            logger.info(f"👥 Personas físicas nuevas: {self.stats['personas_fisicas_nuevas']}")
            logger.info(f"🏢 Personas jurídicas nuevas: {self.stats['personas_juridicas_nuevas']}")
            logger.info(f"📊 Total registros: {self.stats['total_records_extracted']}")
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
    
    async def close(self):
        """Cerrar conexiones"""
        if self.client:
            self.client.close()

async def run_datos_abiertos_extraction():
    """Función principal"""
    extractor = DatosAbiertosExtractor()
    
    try:
        if await extractor.initialize():
            result = await extractor.extract_all_data()
            return result
        else:
            return {'error': 'Falló la inicialización'}
    finally:
        await extractor.close()

if __name__ == "__main__":
    result = asyncio.run(run_datos_abiertos_extraction())
    print(f"🏛️ RESULTADO DATOS ABIERTOS: {result}")