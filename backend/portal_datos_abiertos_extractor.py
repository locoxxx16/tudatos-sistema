"""
PORTAL DATOS ABIERTOS EXTRACTOR
Extractor para datos del Portal de Datos Abiertos de Costa Rica

Fuentes principales:
- https://www.datosabiertos.go.cr/
- https://api.datosabiertos.go.cr/
- Datasets públicos del gobierno costarricense
- APIs RESTful de ministerios y instituciones

Datos objetivo:
- Registros de funcionarios públicos
- Empresas contratistas del estado
- Licencias y permisos gubernamentales
- Datos demográficos oficiales
- Registros educativos y de salud (públicos)

Creado: Diciembre 2024
"""

import asyncio
import httpx
import logging
import re
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class PortalDatosAbiertosExtractor:
    """Extractor del Portal de Datos Abiertos de Costa Rica"""
    
    def __init__(self):
        self.base_url = "https://www.datosabiertos.go.cr"
        self.api_base = "https://api.datosabiertos.go.cr"
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
        
        # APIs y endpoints descubiertos
        self.endpoints_api = {
            'funcionarios_publicos': '/api/v1/funcionarios',
            'empresas_contratistas': '/api/v1/contrataciones',
            'licencias_comerciales': '/api/v1/licencias',
            'permisos_construccion': '/api/v1/permisos',
            'registros_educativos': '/api/v1/educacion',
            'centros_salud': '/api/v1/salud',
            'datos_demograficos': '/api/v1/demografia',
            'empresas_zona_franca': '/api/v1/zonafranca',
            'cooperativas': '/api/v1/cooperativas',
            'ong_fundaciones': '/api/v1/organizaciones'
        }
        
        # Datasets específicos identificados
        self.datasets_prioritarios = [
            {'id': 'funcionarios-gobierno-central', 'tipo': 'personas'},
            {'id': 'empresas-contratistas-estado', 'tipo': 'empresas'},
            {'id': 'licencias-comerciales-municipales', 'tipo': 'licencias'},
            {'id': 'registro-cooperativas-cr', 'tipo': 'cooperativas'},
            {'id': 'permisos-funcionamiento', 'tipo': 'permisos'},
            {'id': 'centros-educativos-mei', 'tipo': 'educacion'},
            {'id': 'establecimientos-salud', 'tipo': 'salud'},
            {'id': 'organizaciones-no-gubernamentales', 'tipo': 'ong'}
        ]
        
        self.stats = {
            'funcionarios_extraidos': 0,
            'empresas_contratistas_extraidas': 0,
            'licencias_extraidas': 0,
            'cooperativas_extraidas': 0,
            'ong_extraidas': 0,
            'centros_educativos_extraidos': 0,
            'establecimientos_salud_extraidos': 0,
            'total_registros': 0,
            'apis_exitosas': 0,
            'datasets_procesados': 0,
            'errores': 0
        }
        
        # Patrones para extraer datos costarricenses
        self.patterns = {
            'cedula_fisica': re.compile(r'[1-9]-\d{4}-\d{4}'),
            'cedula_juridica': re.compile(r'3-\d{3}-\d{6}'),
            'telefono_cr': re.compile(r'\+?506[-\s]?([2-8]\d{3}[-\s]?\d{4})'),
            'email_gov': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]*\.go\.cr\b'),
            'email_general': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'salario_publico': re.compile(r'₡?\s?(\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?)'),
            'codigo_postal': re.compile(r'\b\d{5}\b'),
            'ubicacion_cr': re.compile(r'(San José|Alajuela|Cartago|Heredia|Guanacaste|Puntarenas|Limón)')
        }
    
    async def initialize(self):
        """Inicializar conexiones"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            await self.db.command('ping')
            logger.info("✅ Portal Datos Abiertos Extractor - MongoDB OK")
            return True
        except Exception as e:
            logger.error(f"❌ Error inicializando: {e}")
            return False
    
    async def extract_all_data(self):
        """Extraer todos los datos del Portal de Datos Abiertos"""
        logger.info("🌐 INICIANDO EXTRACCIÓN PORTAL DATOS ABIERTOS")
        
        timeout = httpx.Timeout(120.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as session:
            
            # 1. Extraer usando APIs REST
            await self.extract_via_apis(session)
            
            # 2. Extraer datasets CSV/JSON específicos
            await self.extract_datasets(session)
            
            # 3. Scraping de portales gubernamentales
            await self.extract_via_scraping(session)
            
            # 4. Búsquedas por instituciones específicas
            await self.extract_by_institutions(session)
        
        await self.generate_report()
        logger.info(f"✅ Extracción Portal Datos Abiertos completada - {self.stats['total_registros']} registros")
        
        return self.stats
    
    async def extract_via_apis(self, session):
        """Extraer datos usando APIs REST del Portal"""
        logger.info("🔗 Extrayendo vía APIs REST...")
        
        for api_name, endpoint in self.endpoints_api.items():
            try:
                logger.info(f"📡 Procesando API: {api_name}")
                
                # Parámetros para obtener máximos datos
                params = {
                    'limit': 1000,
                    'offset': 0,
                    'formato': 'json',
                    'activo': 'true',
                    'pais': 'CR'
                }
                
                total_extracted = 0
                offset = 0
                max_requests = 50  # Limitar requests por API
                
                while offset < max_requests * 1000:
                    try:
                        params['offset'] = offset
                        
                        # Intentar múltiples URLs base
                        urls_to_try = [
                            f"{self.api_base}{endpoint}",
                            f"{self.base_url}{endpoint}",
                            f"{self.base_url}/api{endpoint}"
                        ]
                        
                        data_extracted = None
                        
                        for url in urls_to_try:
                            try:
                                response = await session.get(url, params=params)
                                
                                if response.status_code == 200:
                                    if 'application/json' in response.headers.get('content-type', ''):
                                        json_data = response.json()
                                        data_extracted = self.process_json_response(json_data, api_name)
                                        break
                                    else:
                                        # Posiblemente HTML con datos
                                        html_data = self.process_html_response(response.text, api_name)
                                        if html_data:
                                            data_extracted = html_data
                                            break
                                
                            except Exception as e:
                                continue
                        
                        if data_extracted and len(data_extracted) > 0:
                            await self.save_api_data(data_extracted, api_name)
                            total_extracted += len(data_extracted)
                            self.stats['total_registros'] += len(data_extracted)
                            
                            logger.info(f"📊 {api_name}: +{len(data_extracted)} registros (Total: {total_extracted})")
                            
                            # Si obtuvimos menos de lo esperado, probablemente llegamos al final
                            if len(data_extracted) < params['limit']:
                                break
                        else:
                            break
                        
                        offset += params['limit']
                        await asyncio.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        logger.error(f"❌ Error en API {api_name} offset {offset}: {e}")
                        break
                
                if total_extracted > 0:
                    self.stats['apis_exitosas'] += 1
                    # Actualizar estadística específica
                    if 'funcionarios' in api_name:
                        self.stats['funcionarios_extraidos'] += total_extracted
                    elif 'contratistas' in api_name:
                        self.stats['empresas_contratistas_extraidas'] += total_extracted
                    elif 'licencias' in api_name:
                        self.stats['licencias_extraidas'] += total_extracted
                
                await asyncio.sleep(2)  # Pausa entre APIs
                
            except Exception as e:
                logger.error(f"❌ Error procesando API {api_name}: {e}")
                self.stats['errores'] += 1
                continue
    
    async def extract_datasets(self, session):
        """Extraer datasets CSV/JSON específicos"""
        logger.info("📊 Extrayendo datasets prioritarios...")
        
        for dataset in self.datasets_prioritarios:
            try:
                logger.info(f"📁 Procesando dataset: {dataset['id']}")
                
                # URLs posibles para el dataset
                dataset_urls = [
                    f"{self.base_url}/dataset/{dataset['id']}/resource.json",
                    f"{self.base_url}/dataset/{dataset['id']}.csv",
                    f"{self.base_url}/datasets/{dataset['id']}/download",
                    f"{self.api_base}/datasets/{dataset['id']}/data"
                ]
                
                for url in dataset_urls:
                    try:
                        response = await session.get(url, timeout=60)
                        
                        if response.status_code == 200:
                            content_type = response.headers.get('content-type', '').lower()
                            
                            if 'json' in content_type:
                                data = response.json()
                                processed_data = self.process_dataset_json(data, dataset)
                            elif 'csv' in content_type:
                                csv_data = response.text
                                processed_data = self.process_dataset_csv(csv_data, dataset)
                            else:
                                # Intentar parsear como JSON
                                try:
                                    data = response.json()
                                    processed_data = self.process_dataset_json(data, dataset)
                                except:
                                    # Intentar parsear como CSV
                                    processed_data = self.process_dataset_csv(response.text, dataset)
                            
                            if processed_data and len(processed_data) > 0:
                                await self.save_dataset_data(processed_data, dataset)
                                self.stats['total_registros'] += len(processed_data)
                                self.stats['datasets_procesados'] += 1
                                
                                logger.info(f"✅ Dataset {dataset['id']}: {len(processed_data)} registros")
                                break  # Exitoso, continuar al siguiente dataset
                    
                    except Exception as e:
                        continue  # Probar siguiente URL
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error procesando dataset {dataset['id']}: {e}")
                self.stats['errores'] += 1
                continue
    
    async def extract_via_scraping(self, session):
        """Extraer datos mediante scraping de portales gubernamentales"""
        logger.info("🕷️ Extrayendo via scraping de portales...")
        
        portales_gubernamentales = [
            'https://www.mep.go.cr',           # Ministerio Educación
            'https://www.minsa.go.cr',        # Ministerio Salud  
            'https://www.mtss.go.cr',         # Ministerio Trabajo
            'https://www.meic.go.cr',         # Ministerio Economía
            'https://www.mag.go.cr',          # Ministerio Agricultura
            'https://www.mopt.go.cr',         # Ministerio Transporte
            'https://www.mivah.go.cr'         # Ministerio Vivienda
        ]
        
        for portal_url in portales_gubernamentales:
            try:
                logger.info(f"🌐 Scraping portal: {portal_url}")
                
                # Buscar directorios de funcionarios
                directories = [
                    '/directorio',
                    '/funcionarios',
                    '/personal',
                    '/contactos',
                    '/transparencia/funcionarios',
                    '/who-is-who'
                ]
                
                for directory in directories:
                    try:
                        url = f"{portal_url}{directory}"
                        response = await session.get(url, timeout=30)
                        
                        if response.status_code == 200:
                            funcionarios_data = self.extract_funcionarios_from_html(response.text, portal_url)
                            
                            if funcionarios_data and len(funcionarios_data) > 0:
                                await self.save_funcionarios_data(funcionarios_data)
                                self.stats['funcionarios_extraidos'] += len(funcionarios_data)
                                self.stats['total_registros'] += len(funcionarios_data)
                                
                                logger.info(f"👥 {portal_url}{directory}: {len(funcionarios_data)} funcionarios")
                        
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        continue
                
                await asyncio.sleep(3)  # Pausa entre portales
                
            except Exception as e:
                logger.error(f"❌ Error scraping {portal_url}: {e}")
                continue
    
    async def extract_by_institutions(self, session):
        """Extraer por búsquedas específicas en instituciones"""
        logger.info("🏛️ Extrayendo por instituciones específicas...")
        
        instituciones = [
            {'nombre': 'CCSS', 'url': 'https://www.ccss.sa.cr'},
            {'nombre': 'ICE', 'url': 'https://www.grupoice.com'},
            {'nombre': 'INS', 'url': 'https://www.ins-cr.com'},
            {'nombre': 'BNCR', 'url': 'https://www.bncr.fi.cr'},
            {'nombre': 'BCR', 'url': 'https://www.bancobcr.com'},
            {'nombre': 'RECOPE', 'url': 'https://www.recope.go.cr'},
            {'nombre': 'SENASA', 'url': 'https://www.senasa.go.cr'},
            {'nombre': 'IMAS', 'url': 'https://www.imas.go.cr'}
        ]
        
        for institucion in instituciones:
            try:
                logger.info(f"🏢 Procesando institución: {institucion['nombre']}")
                
                # Buscar páginas de transparencia y personal
                search_paths = [
                    '/transparencia',
                    '/quienes-somos',
                    '/about-us', 
                    '/directorio',
                    '/personal',
                    '/funcionarios',
                    '/organigrama'
                ]
                
                for path in search_paths:
                    try:
                        url = f"{institucion['url']}{path}"
                        response = await session.get(url, timeout=45)
                        
                        if response.status_code == 200:
                            # Extraer información de empleados/funcionarios
                            empleados = self.extract_employees_from_institutional_page(
                                response.text, institucion['nombre'], url
                            )
                            
                            if empleados and len(empleados) > 0:
                                await self.save_institutional_employees(empleados, institucion['nombre'])
                                self.stats['funcionarios_extraidos'] += len(empleados)
                                self.stats['total_registros'] += len(empleados)
                                
                                logger.info(f"👤 {institucion['nombre']}: {len(empleados)} empleados")
                        
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        continue
                
                await asyncio.sleep(4)  # Pausa entre instituciones
                
            except Exception as e:
                logger.error(f"❌ Error procesando {institucion['nombre']}: {e}")
                continue
    
    def process_json_response(self, json_data: Dict, api_name: str) -> List[Dict]:
        """Procesar respuesta JSON de API"""
        try:
            results = []
            
            # Diferentes estructuras de respuesta posibles
            data_arrays = []
            
            if isinstance(json_data, list):
                data_arrays.append(json_data)
            elif isinstance(json_data, dict):
                # Buscar arrays en diferentes claves
                possible_keys = ['data', 'results', 'records', 'items', 'funcionarios', 'empresas', 'licencias']
                for key in possible_keys:
                    if key in json_data and isinstance(json_data[key], list):
                        data_arrays.append(json_data[key])
                
                # Si no hay arrays obvios, tratar el objeto como un registro
                if not data_arrays:
                    data_arrays.append([json_data])
            
            for data_array in data_arrays:
                for item in data_array:
                    if isinstance(item, dict):
                        processed_record = self.process_api_record(item, api_name)
                        if processed_record:
                            results.append(processed_record)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error procesando JSON response: {e}")
            return []
    
    def process_html_response(self, html_content: str, api_name: str) -> List[Dict]:
        """Procesar respuesta HTML con datos"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            # Buscar tablas con datos
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                headers = []
                
                # Obtener headers si existen
                if rows:
                    header_row = rows[0]
                    headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
                    data_rows = rows[1:] if len(headers) > 0 else rows
                else:
                    data_rows = []
                
                for row in data_rows:
                    cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                    
                    if len(cells) >= 2:  # Al menos 2 columnas con datos
                        record_data = {
                            'fuente_api': api_name,
                            'tipo_extraccion': 'html_table',
                            'fecha_extraccion': datetime.utcnow()
                        }
                        
                        # Mapear headers a datos si están disponibles
                        if headers and len(headers) == len(cells):
                            for i, header in enumerate(headers):
                                if i < len(cells) and cells[i]:
                                    record_data[f'campo_{header}'] = cells[i]
                        else:
                            # Sin headers, usar índices
                            for i, cell in enumerate(cells):
                                if cell:
                                    record_data[f'campo_{i}'] = cell
                        
                        # Buscar patrones específicos en el contenido
                        all_text = ' '.join(cells)
                        extracted_patterns = self.extract_patterns_from_text(all_text)
                        record_data.update(extracted_patterns)
                        
                        if self.validate_costa_rica_record(record_data):
                            record_data['id'] = str(uuid.uuid4())
                            results.append(record_data)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error procesando HTML: {e}")
            return []
    
    def process_api_record(self, record: Dict, api_name: str) -> Optional[Dict]:
        """Procesar un registro individual de API"""
        try:
            processed = {
                'id': str(uuid.uuid4()),
                'fuente_api': api_name,
                'tipo_extraccion': 'api_rest',
                'fecha_extraccion': datetime.utcnow(),
                'data_original': record
            }
            
            # Extraer campos comunes
            field_mappings = {
                'nombre': ['nombre', 'name', 'full_name', 'nombre_completo', 'apellidos_nombre'],
                'cedula': ['cedula', 'id_number', 'identification', 'documento'],
                'telefono': ['telefono', 'phone', 'tel', 'celular', 'movil'],
                'email': ['email', 'correo', 'mail', 'correo_electronico'],
                'cargo': ['cargo', 'position', 'puesto', 'titulo'],
                'institucion': ['institucion', 'institution', 'empresa', 'organizacion'],
                'salario': ['salario', 'salary', 'sueldo', 'remuneracion'],
                'direccion': ['direccion', 'address', 'ubicacion', 'domicilio']
            }
            
            for target_field, possible_keys in field_mappings.items():
                for key in possible_keys:
                    if key in record and record[key]:
                        processed[target_field] = str(record[key]).strip()
                        break
            
            # Extraer patrones adicionales del texto completo
            full_text = ' '.join([str(v) for v in record.values() if v])
            extracted_patterns = self.extract_patterns_from_text(full_text)
            processed.update(extracted_patterns)
            
            # Validar que sea de Costa Rica
            if self.validate_costa_rica_record(processed):
                return processed
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error procesando record API: {e}")
            return None
    
    def extract_patterns_from_text(self, text: str) -> Dict:
        """Extraer patrones específicos de Costa Rica del texto"""
        extracted = {}
        
        try:
            # Cédulas físicas
            cedulas_fisicas = self.patterns['cedula_fisica'].findall(text)
            if cedulas_fisicas:
                extracted['cedulas_fisicas_encontradas'] = list(set(cedulas_fisicas))
            
            # Cédulas jurídicas
            cedulas_juridicas = self.patterns['cedula_juridica'].findall(text)
            if cedulas_juridicas:
                extracted['cedulas_juridicas_encontradas'] = list(set(cedulas_juridicas))
            
            # Teléfonos CR
            telefonos = self.patterns['telefono_cr'].findall(text)
            if telefonos:
                telefonos_validados = [f"+506{tel.replace('-', '').replace(' ', '')}" for tel in telefonos]
                extracted['telefonos_cr_encontrados'] = list(set(telefonos_validados))
            
            # Emails gubernamentales
            emails_gov = self.patterns['email_gov'].findall(text)
            if emails_gov:
                extracted['emails_gubernamentales'] = list(set(emails_gov))
            
            # Emails generales
            emails = self.patterns['email_general'].findall(text)
            if emails:
                extracted['emails_encontrados'] = list(set(emails))
            
            # Salarios públicos
            salarios = self.patterns['salario_publico'].findall(text)
            if salarios:
                salarios_numericos = []
                for sal in salarios:
                    try:
                        clean_sal = sal.replace(',', '').replace('.', '')
                        if clean_sal.isdigit() and 100000 <= int(clean_sal) <= 10000000:
                            salarios_numericos.append(int(clean_sal))
                    except:
                        continue
                if salarios_numericos:
                    extracted['salarios_encontrados'] = salarios_numericos
            
            # Ubicaciones CR
            ubicaciones = self.patterns['ubicacion_cr'].findall(text)
            if ubicaciones:
                extracted['provincias_mencionadas'] = list(set(ubicaciones))
        
        except Exception as e:
            logger.error(f"❌ Error extrayendo patrones: {e}")
        
        return extracted
    
    def validate_costa_rica_record(self, record: Dict) -> bool:
        """Validar que el registro sea de Costa Rica"""
        # Palabras clave que indican Costa Rica
        cr_indicators = [
            'costa rica', 'costarricense', '.go.cr', '.cr', '+506',
            'san josé', 'alajuela', 'cartago', 'heredia', 'guanacaste',
            'gobierno', 'ministerio', 'ccss', 'ice', 'ins'
        ]
        
        # Palabras que indican otros países (rechazar)
        foreign_indicators = [
            'nicaragua', 'panama', 'colombia', 'mexico', 'guatemala',
            'honduras', 'venezuela', 'argentina', 'chile'
        ]
        
        # Concatenar todos los valores del registro en texto
        all_text = ' '.join([str(v) for v in record.values() if v]).lower()
        
        # Rechazar si contiene indicadores extranjeros
        if any(foreign in all_text for foreign in foreign_indicators):
            return False
        
        # Aceptar si tiene indicadores de Costa Rica
        has_cr_indicators = any(cr_word in all_text for cr_word in cr_indicators)
        
        # Aceptar si tiene cédulas de formato costarricense
        has_cr_cedulas = (
            bool(record.get('cedulas_fisicas_encontradas')) or
            bool(record.get('cedulas_juridicas_encontradas'))
        )
        
        # Aceptar si tiene emails .go.cr
        has_gov_emails = bool(record.get('emails_gubernamentales'))
        
        return has_cr_indicators or has_cr_cedulas or has_gov_emails
    
    def process_dataset_json(self, data: Dict, dataset_info: Dict) -> List[Dict]:
        """Procesar dataset en formato JSON"""
        try:
            results = []
            
            # Diferentes estructuras posibles
            records = []
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Buscar array principal
                for key in ['data', 'records', 'results', 'items']:
                    if key in data and isinstance(data[key], list):
                        records = data[key]
                        break
            
            for record in records:
                if isinstance(record, dict):
                    processed = {
                        'id': str(uuid.uuid4()),
                        'fuente_dataset': dataset_info['id'],
                        'tipo_dataset': dataset_info['tipo'],
                        'fecha_extraccion': datetime.utcnow(),
                        'data_original': record
                    }
                    
                    # Extraer campos relevantes
                    for key, value in record.items():
                        if value and str(value).strip():
                            processed[f'dataset_{key}'] = str(value).strip()
                    
                    # Extraer patrones
                    full_text = ' '.join([str(v) for v in record.values() if v])
                    patterns = self.extract_patterns_from_text(full_text)
                    processed.update(patterns)
                    
                    if self.validate_costa_rica_record(processed):
                        results.append(processed)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error procesando dataset JSON: {e}")
            return []
    
    def process_dataset_csv(self, csv_content: str, dataset_info: Dict) -> List[Dict]:
        """Procesar dataset en formato CSV"""
        try:
            results = []
            lines = csv_content.strip().split('\n')
            
            if len(lines) < 2:
                return results
            
            # Primera línea como headers
            headers = [h.strip().strip('"') for h in lines[0].split(',')]
            
            for line_num, line in enumerate(lines[1:], 1):
                try:
                    # Parsear CSV simple (sin librerías externas)
                    values = [v.strip().strip('"') for v in line.split(',')]
                    
                    if len(values) != len(headers):
                        continue  # Skip malformed rows
                    
                    record = {
                        'id': str(uuid.uuid4()),
                        'fuente_dataset': dataset_info['id'],
                        'tipo_dataset': dataset_info['tipo'],
                        'fecha_extraccion': datetime.utcnow(),
                        'linea_csv': line_num
                    }
                    
                    # Mapear headers a valores
                    for i, header in enumerate(headers):
                        if i < len(values) and values[i]:
                            record[f'csv_{header.lower()}'] = values[i]
                    
                    # Extraer patrones
                    full_text = ' '.join(values)
                    patterns = self.extract_patterns_from_text(full_text)
                    record.update(patterns)
                    
                    if self.validate_costa_rica_record(record):
                        results.append(record)
                
                except Exception as e:
                    continue  # Skip problematic lines
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error procesando dataset CSV: {e}")
            return []
    
    def extract_funcionarios_from_html(self, html_content: str, portal_url: str) -> List[Dict]:
        """Extraer funcionarios de páginas HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            funcionarios = []
            
            # Buscar estructuras comunes de directorios
            
            # 1. Divs o secciones de empleados
            employee_sections = soup.find_all(['div', 'section'], 
                class_=re.compile(r'(empleado|funcionario|director|staff|employee)', re.I))
            
            for section in employee_sections:
                funcionario = self.extract_employee_from_section(section, portal_url)
                if funcionario:
                    funcionarios.append(funcionario)
            
            # 2. Listas de empleados
            employee_lists = soup.find_all(['ul', 'ol'], 
                class_=re.compile(r'(staff|employees|funcionarios|directorio)', re.I))
            
            for ul in employee_lists:
                items = ul.find_all('li')
                for item in items:
                    funcionario = self.extract_employee_from_list_item(item, portal_url)
                    if funcionario:
                        funcionarios.append(funcionario)
            
            # 3. Tablas de empleados
            employee_tables = soup.find_all('table')
            for table in employee_tables:
                table_funcionarios = self.extract_employees_from_table(table, portal_url)
                funcionarios.extend(table_funcionarios)
            
            return funcionarios
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo funcionarios HTML: {e}")
            return []
    
    def extract_employee_from_section(self, section, portal_url: str) -> Optional[Dict]:
        """Extraer información de empleado de una sección"""
        try:
            funcionario = {
                'id': str(uuid.uuid4()),
                'fuente_portal': portal_url,
                'tipo_extraccion': 'scraping_section',
                'fecha_extraccion': datetime.utcnow()
            }
            
            # Buscar nombre
            name_tags = section.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b'], 
                class_=re.compile(r'(name|nombre|titulo)', re.I))
            if name_tags:
                funcionario['nombre'] = name_tags[0].get_text().strip()
            
            # Buscar cargo/posición
            position_tags = section.find_all(['p', 'span', 'div'], 
                class_=re.compile(r'(cargo|position|puesto|titulo)', re.I))
            if position_tags:
                funcionario['cargo'] = position_tags[0].get_text().strip()
            
            # Buscar email
            email_links = section.find_all('a', href=re.compile(r'mailto:'))
            if email_links:
                email = email_links[0].get('href').replace('mailto:', '')
                funcionario['email'] = email
            
            # Buscar teléfono
            text_content = section.get_text()
            phone_matches = self.patterns['telefono_cr'].findall(text_content)
            if phone_matches:
                funcionario['telefono'] = f"+506{phone_matches[0]}"
            
            # Extraer patrones adicionales
            patterns = self.extract_patterns_from_text(text_content)
            funcionario.update(patterns)
            
            if funcionario.get('nombre') and self.validate_costa_rica_record(funcionario):
                return funcionario
            
            return None
            
        except Exception as e:
            return None
    
    def extract_employee_from_list_item(self, item, portal_url: str) -> Optional[Dict]:
        """Extraer empleado de item de lista"""
        try:
            text = item.get_text().strip()
            if len(text) < 10:
                return None
            
            funcionario = {
                'id': str(uuid.uuid4()),
                'fuente_portal': portal_url,
                'tipo_extraccion': 'scraping_list',
                'fecha_extraccion': datetime.utcnow(),
                'texto_original': text
            }
            
            # Intentar parsear formato común: "Nombre - Cargo - Email"
            parts = text.split(' - ')
            if len(parts) >= 2:
                funcionario['nombre'] = parts[0].strip()
                funcionario['cargo'] = parts[1].strip()
                if len(parts) >= 3:
                    funcionario['contacto'] = parts[2].strip()
            else:
                funcionario['nombre'] = text
            
            # Extraer patrones
            patterns = self.extract_patterns_from_text(text)
            funcionario.update(patterns)
            
            if self.validate_costa_rica_record(funcionario):
                return funcionario
            
            return None
            
        except Exception as e:
            return None
    
    def extract_employees_from_table(self, table, portal_url: str) -> List[Dict]:
        """Extraer empleados de tabla"""
        try:
            funcionarios = []
            rows = table.find_all('tr')
            
            if len(rows) < 2:
                return funcionarios
            
            # Headers
            header_row = rows[0]
            headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
            
            for row in rows[1:]:
                cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                
                if len(cells) < 2:
                    continue
                
                funcionario = {
                    'id': str(uuid.uuid4()),
                    'fuente_portal': portal_url,
                    'tipo_extraccion': 'scraping_table',
                    'fecha_extraccion': datetime.utcnow()
                }
                
                # Mapear headers a datos
                for i, header in enumerate(headers):
                    if i < len(cells) and cells[i]:
                        funcionario[f'tabla_{header}'] = cells[i]
                
                # Extraer patrones
                all_text = ' '.join(cells)
                patterns = self.extract_patterns_from_text(all_text)
                funcionario.update(patterns)
                
                if self.validate_costa_rica_record(funcionario):
                    funcionarios.append(funcionario)
            
            return funcionarios
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo tabla funcionarios: {e}")
            return []
    
    def extract_employees_from_institutional_page(self, html_content: str, institucion: str, url: str) -> List[Dict]:
        """Extraer empleados de página institucional"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            empleados = []
            
            # Buscar secciones de organigrama o directorio
            org_sections = soup.find_all(['div', 'section'], 
                class_=re.compile(r'(organigrama|directorio|staff|equipo)', re.I))
            
            for section in org_sections:
                # Buscar nombres de personas (patrones comunes)
                person_elements = section.find_all(['p', 'div', 'span'], 
                    string=re.compile(r'^[A-Z][a-z]+\s+[A-Z][a-z]+.*'))
                
                for element in person_elements:
                    text = element.get_text().strip()
                    
                    empleado = {
                        'id': str(uuid.uuid4()),
                        'institucion': institucion,
                        'fuente_url': url,
                        'tipo_extraccion': 'scraping_institucional',
                        'fecha_extraccion': datetime.utcnow(),
                        'texto_encontrado': text
                    }
                    
                    # Intentar extraer cargo del contexto
                    parent = element.parent
                    if parent:
                        context_text = parent.get_text()
                        empleado['contexto'] = context_text[:200]
                    
                    # Extraer patrones
                    patterns = self.extract_patterns_from_text(text)
                    empleado.update(patterns)
                    
                    if self.validate_costa_rica_record(empleado):
                        empleados.append(empleado)
            
            return empleados
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo empleados institucionales: {e}")
            return []
    
    async def save_api_data(self, data_list: List[Dict], api_name: str):
        """Guardar datos de API"""
        try:
            if data_list:
                collection_name = f'datos_abiertos_{api_name}'
                await self.db[collection_name].insert_many(data_list, ordered=False)
                logger.info(f"💾 Guardados {len(data_list)} registros de {api_name}")
        except Exception as e:
            logger.error(f"❌ Error guardando API data: {e}")
    
    async def save_dataset_data(self, data_list: List[Dict], dataset_info: Dict):
        """Guardar datos de dataset"""
        try:
            if data_list:
                collection_name = f'dataset_{dataset_info["tipo"]}'
                await self.db[collection_name].insert_many(data_list, ordered=False)
                logger.info(f"💾 Guardados {len(data_list)} registros del dataset {dataset_info['id']}")
        except Exception as e:
            logger.error(f"❌ Error guardando dataset: {e}")
    
    async def save_funcionarios_data(self, funcionarios: List[Dict]):
        """Guardar funcionarios públicos"""
        try:
            if funcionarios:
                await self.db.funcionarios_publicos_cr.insert_many(funcionarios, ordered=False)
                logger.info(f"💾 Guardados {len(funcionarios)} funcionarios públicos")
        except Exception as e:
            logger.error(f"❌ Error guardando funcionarios: {e}")
    
    async def save_institutional_employees(self, empleados: List[Dict], institucion: str):
        """Guardar empleados institucionales"""
        try:
            if empleados:
                await self.db.empleados_institucionales_cr.insert_many(empleados, ordered=False)
                logger.info(f"💾 Guardados {len(empleados)} empleados de {institucion}")
        except Exception as e:
            logger.error(f"❌ Error guardando empleados institucionales: {e}")
    
    async def generate_report(self):
        """Generar reporte de extracción"""
        try:
            # Contar totales en BD
            total_funcionarios = await self.db.funcionarios_publicos_cr.count_documents({})
            total_apis = await self.db.command('listCollections', filter={'name': {'$regex': 'datos_abiertos_'}})
            total_datasets = await self.db.command('listCollections', filter={'name': {'$regex': 'dataset_'}})
            
            report = {
                'fecha_extraccion': datetime.utcnow(),
                'fuente': 'PORTAL_DATOS_ABIERTOS_COSTA_RICA',
                'extraccion_completada': True,
                'estadisticas_extraccion': self.stats,
                'totales_bd': {
                    'funcionarios_publicos_total': total_funcionarios,
                    'colecciones_apis': len(total_apis['cursor']['firstBatch']),
                    'colecciones_datasets': len(total_datasets['cursor']['firstBatch'])
                },
                'cobertura': {
                    'apis_rest': f'{self.stats["apis_exitosas"]} APIs exitosas',
                    'datasets_csv_json': f'{self.stats["datasets_procesados"]} datasets procesados',
                    'scraping_portales': 'Ministerios y portales gubernamentales',
                    'instituciones_autonomas': 'CCSS, ICE, INS, bancos estatales'
                }
            }
            
            await self.db.portal_datos_abiertos_reports.insert_one(report)
            
            logger.info("📊 REPORTE PORTAL DATOS ABIERTOS")
            logger.info(f"👥 Funcionarios: {self.stats['funcionarios_extraidos']}")
            logger.info(f"🏢 Empresas Contratistas: {self.stats['empresas_contratistas_extraidas']}")
            logger.info(f"📄 Licencias: {self.stats['licencias_extraidas']}")
            logger.info(f"🤝 Cooperativas: {self.stats['cooperativas_extraidas']}")
            logger.info(f"📊 Total: {self.stats['total_registros']}")
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
    
    async def close(self):
        """Cerrar conexiones"""
        if self.client:
            self.client.close()

async def run_portal_datos_abiertos_extraction():
    """Función principal"""
    extractor = PortalDatosAbiertosExtractor()
    
    try:
        if await extractor.initialize():
            result = await extractor.extract_all_data()
            return result
        else:
            return {'error': 'Falló la inicialización'}
    finally:
        await extractor.close()

if __name__ == "__main__":
    result = asyncio.run(run_portal_datos_abiertos_extraction())
    print(f"🌐 RESULTADO PORTAL DATOS ABIERTOS: {result}")