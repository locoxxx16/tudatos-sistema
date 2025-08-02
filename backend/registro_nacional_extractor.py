"""
REGISTRO NACIONAL EXTRACTOR
Extractor para datos REALES del Registro Nacional de Costa Rica

Fuentes:
- Propiedades inmobiliarias reales
- Vehículos registrados oficiales  
- Empresas y sociedades registradas
- Hipotecas y gravámenes

URL: https://www.registronacional.go.cr/
Método: Consultas públicas + API endpoints descubiertos

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

class RegistroNacionalExtractor:
    """Extractor del Registro Nacional de Costa Rica"""
    
    def __init__(self):
        self.base_url = "https://www.registronacional.go.cr"
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
        
        # Endpoints descubiertos del Registro Nacional
        self.endpoints = {
            'consulta_publica': '/index.php/tramites-servicios/consultas-publicas',
            'busqueda_propiedades': '/index.php/bienes-inmuebles',
            'registro_vehiculos': '/index.php/vehiculos',
            'sociedades': '/index.php/personas-juridicas',
            'consulta_cedula': '/consulta/cedula',
            'consulta_placa': '/consulta/vehiculo',
            'consulta_folio': '/consulta/propiedad'
        }
        
        self.stats = {
            'propiedades_extraidas': 0,
            'vehiculos_extraidos': 0,
            'sociedades_extraidas': 0,
            'total_registros': 0,
            'errores': 0
        }
        
        # Patrones específicos Registro Nacional
        self.patterns = {
            'folio_real': re.compile(r'Folio\s+Real\s*:\s*([A-Z0-9-]+)', re.IGNORECASE),
            'placa_vehiculo': re.compile(r'Placa\s*:\s*([A-Z0-9-]+)', re.IGNORECASE),
            'cedula_propietario': re.compile(r'Propietario\s*:\s*([1-9]-\d{4}-\d{4})', re.IGNORECASE),
            'valor_fiscal': re.compile(r'Valor\s+Fiscal\s*:\s*₡?\s*([0-9,\.]+)', re.IGNORECASE),
            'ubicacion': re.compile(r'Ubicación\s*:\s*([^,\n]{10,100})', re.IGNORECASE),
            'marca_vehiculo': re.compile(r'Marca\s*:\s*(\w+)', re.IGNORECASE),
            'año_vehiculo': re.compile(r'Año\s*:\s*(\d{4})', re.IGNORECASE),
            'nombre_sociedad': re.compile(r'Razón\s+Social\s*:\s*([^,\n]{5,100})', re.IGNORECASE)
        }
    
    async def initialize(self):
        """Inicializar conexiones"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            await self.db.command('ping')
            logger.info("✅ Registro Nacional Extractor - MongoDB OK")
            return True
        except Exception as e:
            logger.error(f"❌ Error inicializando: {e}")
            return False
    
    async def extract_all_data(self):
        """Extraer todos los datos del Registro Nacional"""
        logger.info("🏛️ INICIANDO EXTRACCIÓN REGISTRO NACIONAL")
        
        # Crear sesión HTTP optimizada
        timeout = httpx.Timeout(60.0, connect=30.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as session:
            
            # 1. Extraer propiedades inmobiliarias
            await self.extract_propiedades(session)
            
            # 2. Extraer vehículos registrados
            await self.extract_vehiculos(session)
            
            # 3. Extraer sociedades/empresas
            await self.extract_sociedades(session)
            
            # 4. Búsquedas por cédulas conocidas
            await self.extract_by_cedulas_conocidas(session)
        
        await self.generate_report()
        logger.info(f"✅ Extracción Registro Nacional completada - {self.stats['total_registros']} registros")
        
        return self.stats
    
    async def extract_propiedades(self, session):
        """Extraer propiedades inmobiliarias"""
        logger.info("🏠 Extrayendo propiedades inmobiliarias...")
        
        try:
            # Estrategia 1: Consultas por rangos de folios reales
            folios_patterns = [
                'SJ-', 'AL-', 'CA-', 'HE-', 'GU-', 'PU-', 'LI-',  # Por provincia
                '001-', '002-', '003-', '004-', '005-'  # Por rangos
            ]
            
            for pattern in folios_patterns:
                for i in range(100, 1000, 50):  # Rangos de folios
                    folio_test = f"{pattern}{i:06d}"
                    
                    try:
                        # Consulta específica de propiedad
                        response = await session.get(
                            f"{self.base_url}/consulta/propiedad/{folio_test}",
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            propiedad_data = await self.parse_propiedad_response(response.text)
                            if propiedad_data:
                                await self.save_propiedad(propiedad_data)
                                self.stats['propiedades_extraidas'] += 1
                        
                        await asyncio.sleep(0.5)  # Rate limiting
                        
                    except Exception as e:
                        self.stats['errores'] += 1
                        continue
                
                if self.stats['propiedades_extraidas'] % 100 == 0:
                    logger.info(f"📊 Propiedades extraídas: {self.stats['propiedades_extraidas']}")
            
            # Estrategia 2: Búsqueda por ubicaciones conocidas
            provincias = ['San José', 'Alajuela', 'Cartago', 'Heredia', 'Guanacaste', 'Puntarenas', 'Limón']
            
            for provincia in provincias:
                try:
                    # Búsqueda por provincia
                    params = {'provincia': provincia, 'activo': '1'}
                    response = await session.get(
                        f"{self.base_url}/consulta/propiedades",
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        propiedades_list = await self.parse_propiedades_list(response.text)
                        
                        for prop in propiedades_list:
                            await self.save_propiedad(prop)
                            self.stats['propiedades_extraidas'] += 1
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error extrayendo propiedades: {e}")
    
    async def extract_vehiculos(self, session):
        """Extraer vehículos registrados"""
        logger.info("🚗 Extrayendo vehículos registrados...")
        
        try:
            # Estrategia 1: Patrones de placas comunes en CR
            placas_patterns = [
                'SJO', 'ALJ', 'CAR', 'HER', 'GUA', 'PUN', 'LIM',  # Por provincia
                'TAX', 'BUS', 'MOT', 'TRA'  # Tipos especiales
            ]
            
            for pattern in placas_patterns:
                for i in range(1000, 9999, 100):
                    placa_test = f"{pattern}{i}"
                    
                    try:
                        # Consulta específica de vehículo
                        response = await session.get(
                            f"{self.base_url}/consulta/vehiculo/{placa_test}",
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            vehiculo_data = await self.parse_vehiculo_response(response.text)
                            if vehiculo_data:
                                await self.save_vehiculo(vehiculo_data)
                                self.stats['vehiculos_extraidos'] += 1
                        
                        await asyncio.sleep(0.3)
                        
                    except Exception as e:
                        self.stats['errores'] += 1
                        continue
                
                if self.stats['vehiculos_extraidos'] % 50 == 0:
                    logger.info(f"📊 Vehículos extraídos: {self.stats['vehiculos_extraidos']}")
                    
            # Estrategia 2: Búsqueda por rangos de años
            for año in range(2010, 2025):
                try:
                    params = {'año': año, 'activo': '1'}
                    response = await session.get(
                        f"{self.base_url}/consulta/vehiculos",
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        vehiculos_list = await self.parse_vehiculos_list(response.text)
                        
                        for vehiculo in vehiculos_list:
                            await self.save_vehiculo(vehiculo)
                            self.stats['vehiculos_extraidos'] += 1
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error extrayendo vehículos: {e}")
    
    async def extract_sociedades(self, session):
        """Extraer sociedades/empresas registradas"""
        logger.info("🏢 Extrayendo sociedades registradas...")
        
        try:
            # Estrategia 1: Búsqueda por sectores comerciales
            sectores = [
                'COMERCIAL', 'SERVICIOS', 'CONSTRUCCION', 'TECNOLOGIA',
                'CONSULTORIA', 'INMOBILIARIA', 'TRANSPORTE', 'AGRICULTURA'
            ]
            
            for sector in sectores:
                try:
                    params = {'actividad': sector, 'activo': '1'}
                    response = await session.get(
                        f"{self.base_url}/consulta/sociedades",
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        sociedades_list = await self.parse_sociedades_list(response.text)
                        
                        for sociedad in sociedades_list:
                            await self.save_sociedad(sociedad)
                            self.stats['sociedades_extraidas'] += 1
                    
                    await asyncio.sleep(1.5)
                    
                except Exception as e:
                    continue
            
            # Estrategia 2: Búsqueda por tipos de sociedad
            tipos_sociedad = ['S.A.', 'LTDA', 'S.R.L.', 'CORP']
            
            for tipo in tipos_sociedad:
                try:
                    params = {'tipo': tipo, 'activo': '1'}
                    response = await session.get(
                        f"{self.base_url}/consulta/sociedades",
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        sociedades_list = await self.parse_sociedades_list(response.text)
                        
                        for sociedad in sociedades_list:
                            await self.save_sociedad(sociedad)
                            self.stats['sociedades_extraidas'] += 1
                    
                    await asyncio.sleep(1.5)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error extrayendo sociedades: {e}")
    
    async def extract_by_cedulas_conocidas(self, session):
        """Extraer datos usando cédulas ya conocidas de otras fuentes"""
        logger.info("🔍 Extrayendo por cédulas conocidas...")
        
        try:
            # Obtener cédulas únicas de nuestra BD
            cedulas_conocidas = []
            
            # Obtener muestras de cédulas físicas
            async for doc in self.db.personas_fisicas.find({}, {'cedula': 1}).limit(1000):
                if doc.get('cedula'):
                    cedulas_conocidas.append(doc['cedula'])
            
            # Obtener muestras de cédulas jurídicas
            async for doc in self.db.personas_juridicas.find({}, {'cedula_juridica': 1}).limit(500):
                if doc.get('cedula_juridica'):
                    cedulas_conocidas.append(doc['cedula_juridica'])
            
            logger.info(f"🔍 Consultando {len(cedulas_conocidas)} cédulas conocidas...")
            
            for cedula in cedulas_conocidas:
                try:
                    # Consulta por cédula en Registro Nacional
                    response = await session.get(
                        f"{self.base_url}/consulta/cedula/{cedula}",
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        # Parsear información completa de la persona
                        info_completa = await self.parse_info_completa_cedula(response.text, cedula)
                        
                        if info_completa:
                            await self.enrich_existing_person(cedula, info_completa)
                            self.stats['total_registros'] += 1
                    
                    await asyncio.sleep(0.8)  # Rate limiting más conservador
                    
                except Exception as e:
                    self.stats['errores'] += 1
                    continue
                
                if self.stats['total_registros'] % 100 == 0:
                    logger.info(f"📊 Cédulas procesadas: {self.stats['total_registros']}")
                    
        except Exception as e:
            logger.error(f"❌ Error consultando por cédulas: {e}")
    
    async def parse_propiedad_response(self, html_content: str) -> Optional[Dict]:
        """Parsear respuesta de consulta de propiedad"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            propiedad = {
                'id': str(uuid.uuid4()),
                'fuente': 'REGISTRO_NACIONAL_OFICIAL',
                'tipo': 'propiedad_inmobiliaria',
                'fecha_extraccion': datetime.utcnow()
            }
            
            # Extraer folio real
            folio_match = self.patterns['folio_real'].search(html_content)
            if folio_match:
                propiedad['folio_real'] = folio_match.group(1).strip()
            
            # Extraer propietario
            cedula_match = self.patterns['cedula_propietario'].search(html_content)
            if cedula_match:
                propiedad['cedula_propietario'] = cedula_match.group(1).strip()
            
            # Extraer valor fiscal
            valor_match = self.patterns['valor_fiscal'].search(html_content)
            if valor_match:
                valor_str = valor_match.group(1).replace(',', '').replace('.', '')
                try:
                    propiedad['valor_fiscal'] = int(valor_str)
                except:
                    pass
            
            # Extraer ubicación
            ubicacion_match = self.patterns['ubicacion'].search(html_content)
            if ubicacion_match:
                propiedad['ubicacion'] = ubicacion_match.group(1).strip()
            
            # Extraer información adicional de tablas
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    if len(cells) >= 2:
                        key = cells[0].lower().replace(' ', '_')
                        value = cells[1].strip()
                        if value and len(value) > 0:
                            propiedad[f'detalle_{key}'] = value
            
            return propiedad if propiedad.get('folio_real') else None
            
        except Exception as e:
            logger.error(f"❌ Error parseando propiedad: {e}")
            return None
    
    async def parse_vehiculo_response(self, html_content: str) -> Optional[Dict]:
        """Parsear respuesta de consulta de vehículo"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            vehiculo = {
                'id': str(uuid.uuid4()),
                'fuente': 'REGISTRO_NACIONAL_OFICIAL',
                'tipo': 'vehiculo_registrado',
                'fecha_extraccion': datetime.utcnow()
            }
            
            # Extraer placa
            placa_match = self.patterns['placa_vehiculo'].search(html_content)
            if placa_match:
                vehiculo['placa'] = placa_match.group(1).strip()
            
            # Extraer propietario
            cedula_match = self.patterns['cedula_propietario'].search(html_content)
            if cedula_match:
                vehiculo['cedula_propietario'] = cedula_match.group(1).strip()
            
            # Extraer marca
            marca_match = self.patterns['marca_vehiculo'].search(html_content)
            if marca_match:
                vehiculo['marca'] = marca_match.group(1).strip()
            
            # Extraer año
            año_match = self.patterns['año_vehiculo'].search(html_content)
            if año_match:
                try:
                    vehiculo['año'] = int(año_match.group(1))
                except:
                    pass
            
            # Información adicional de tablas
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    if len(cells) >= 2:
                        key = cells[0].lower().replace(' ', '_')
                        value = cells[1].strip()
                        if value and len(value) > 0:
                            vehiculo[f'detalle_{key}'] = value
            
            return vehiculo if vehiculo.get('placa') else None
            
        except Exception as e:
            logger.error(f"❌ Error parseando vehículo: {e}")
            return None
    
    async def parse_propiedades_list(self, html_content: str) -> List[Dict]:
        """Parsear lista de propiedades"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            propiedades = []
            
            # Buscar tablas con listados
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    
                    if len(cells) >= 3:  # Mínimo folio, propietario, ubicación
                        propiedad = {
                            'id': str(uuid.uuid4()),
                            'fuente': 'REGISTRO_NACIONAL_LISTADO',
                            'tipo': 'propiedad_inmobiliaria',
                            'fecha_extraccion': datetime.utcnow(),
                            'folio_real': cells[0] if cells[0] else f"AUTO-{uuid.uuid4().hex[:8]}",
                            'info_propietario': cells[1] if len(cells) > 1 else None,
                            'ubicacion': cells[2] if len(cells) > 2 else None,
                            'valor_referencia': cells[3] if len(cells) > 3 else None
                        }
                        
                        propiedades.append(propiedad)
            
            return propiedades
            
        except Exception as e:
            logger.error(f"❌ Error parseando lista propiedades: {e}")
            return []
    
    async def parse_vehiculos_list(self, html_content: str) -> List[Dict]:
        """Parsear lista de vehículos"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            vehiculos = []
            
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    
                    if len(cells) >= 3:
                        vehiculo = {
                            'id': str(uuid.uuid4()),
                            'fuente': 'REGISTRO_NACIONAL_LISTADO',
                            'tipo': 'vehiculo_registrado',
                            'fecha_extraccion': datetime.utcnow(),
                            'placa': cells[0] if cells[0] else f"AUTO-{uuid.uuid4().hex[:6]}",
                            'marca_modelo': cells[1] if len(cells) > 1 else None,
                            'año': cells[2] if len(cells) > 2 else None,
                            'propietario_info': cells[3] if len(cells) > 3 else None
                        }
                        
                        vehiculos.append(vehiculo)
            
            return vehiculos
            
        except Exception as e:
            logger.error(f"❌ Error parseando lista vehículos: {e}")
            return []
    
    async def parse_sociedades_list(self, html_content: str) -> List[Dict]:
        """Parsear lista de sociedades"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            sociedades = []
            
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    
                    if len(cells) >= 2:
                        sociedad = {
                            'id': str(uuid.uuid4()),
                            'fuente': 'REGISTRO_NACIONAL_SOCIEDADES',
                            'tipo': 'sociedad_registrada',
                            'fecha_extraccion': datetime.utcnow(),
                            'nombre_sociedad': cells[0] if cells[0] else None,
                            'cedula_juridica': cells[1] if len(cells) > 1 else None,
                            'actividad': cells[2] if len(cells) > 2 else None,
                            'estado': cells[3] if len(cells) > 3 else 'activa'
                        }
                        
                        sociedades.append(sociedad)
            
            return sociedades
            
        except Exception as e:
            logger.error(f"❌ Error parseando lista sociedades: {e}")
            return []
    
    async def parse_info_completa_cedula(self, html_content: str, cedula: str) -> Optional[Dict]:
        """Parsear información completa por cédula"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            info = {
                'cedula': cedula,
                'fuente_enriquecimiento': 'REGISTRO_NACIONAL',
                'fecha_enriquecimiento': datetime.utcnow(),
                'propiedades_registradas': [],
                'vehiculos_registrados': [],
                'sociedades_relacionadas': []
            }
            
            # Buscar secciones específicas
            sections = soup.find_all(['div', 'section'], class_=re.compile(r'(propiedad|vehiculo|sociedad)', re.I))
            
            for section in sections:
                section_text = section.get_text()
                
                # Detectar propiedades
                if 'propiedad' in section_text.lower() or 'folio' in section_text.lower():
                    folios = self.patterns['folio_real'].findall(section_text)
                    info['propiedades_registradas'].extend(folios)
                
                # Detectar vehículos  
                if 'vehículo' in section_text.lower() or 'placa' in section_text.lower():
                    placas = self.patterns['placa_vehiculo'].findall(section_text)
                    info['vehiculos_registrados'].extend(placas)
                
                # Detectar sociedades
                if 'sociedad' in section_text.lower() or 'empresa' in section_text.lower():
                    sociedades = self.patterns['nombre_sociedad'].findall(section_text)
                    info['sociedades_relacionadas'].extend(sociedades)
            
            return info if any([info['propiedades_registradas'], 
                              info['vehiculos_registrados'], 
                              info['sociedades_relacionadas']]) else None
            
        except Exception as e:
            logger.error(f"❌ Error parseando info completa: {e}")
            return None
    
    async def save_propiedad(self, propiedad: Dict):
        """Guardar propiedad en BD"""
        try:
            await self.db.propiedades_cr.insert_one(propiedad)
        except Exception as e:
            logger.error(f"❌ Error guardando propiedad: {e}")
    
    async def save_vehiculo(self, vehiculo: Dict):
        """Guardar vehículo en BD"""
        try:
            await self.db.vehiculos_cr.insert_one(vehiculo)
        except Exception as e:
            logger.error(f"❌ Error guardando vehículo: {e}")
    
    async def save_sociedad(self, sociedad: Dict):
        """Guardar sociedad en BD"""
        try:
            # Verificar si es nueva
            existing = await self.db.personas_juridicas.find_one({
                'cedula_juridica': sociedad.get('cedula_juridica')
            })
            
            if not existing and sociedad.get('cedula_juridica'):
                # Crear nueva persona jurídica
                nueva_juridica = {
                    'id': str(uuid.uuid4()),
                    'cedula_juridica': sociedad['cedula_juridica'],
                    'nombre_comercial': sociedad['nombre_sociedad'],
                    'razon_social': sociedad['nombre_sociedad'],
                    'sector_negocio': sociedad.get('actividad', 'otros'),
                    'estado_registro': sociedad.get('estado', 'activa'),
                    'fuente': 'REGISTRO_NACIONAL_SOCIEDADES',
                    'data_registro_nacional': sociedad,
                    'created_at': datetime.utcnow()
                }
                
                await self.db.personas_juridicas.insert_one(nueva_juridica)
            
        except Exception as e:
            logger.error(f"❌ Error guardando sociedad: {e}")
    
    async def enrich_existing_person(self, cedula: str, info_completa: Dict):
        """Enriquecer persona existente con datos del Registro Nacional"""
        try:
            # Actualizar persona física si existe
            result = await self.db.personas_fisicas.update_one(
                {'cedula': cedula},
                {
                    '$set': {
                        'registro_nacional_data': info_completa,
                        'propiedades_registradas': info_completa['propiedades_registradas'],
                        'vehiculos_registrados': info_completa['vehiculos_registrados'],
                        'enriquecido_registro_nacional': True,
                        'fecha_enriquecimiento_rn': datetime.utcnow()
                    }
                }
            )
            
            # También actualizar persona jurídica si aplica
            if cedula.startswith('3-'):
                await self.db.personas_juridicas.update_one(
                    {'cedula_juridica': cedula},
                    {
                        '$set': {
                            'registro_nacional_data': info_completa,
                            'sociedades_relacionadas': info_completa['sociedades_relacionadas'],
                            'enriquecido_registro_nacional': True,
                            'fecha_enriquecimiento_rn': datetime.utcnow()
                        }
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ Error enriqueciendo persona: {e}")
    
    async def generate_report(self):
        """Generar reporte de extracción"""
        try:
            # Calcular totales en BD
            total_propiedades = await self.db.propiedades_cr.count_documents({})
            total_vehiculos = await self.db.vehiculos_cr.count_documents({})
            total_juridicas_rn = await self.db.personas_juridicas.count_documents({'fuente': 'REGISTRO_NACIONAL_SOCIEDADES'})
            
            self.stats['total_registros'] = (self.stats['propiedades_extraidas'] + 
                                           self.stats['vehiculos_extraidos'] + 
                                           self.stats['sociedades_extraidas'])
            
            report = {
                'fecha_extraccion': datetime.utcnow(),
                'fuente': 'REGISTRO_NACIONAL_COSTA_RICA',
                'extraccion_completada': True,
                'estadisticas_extraccion': self.stats,
                'totales_bd': {
                    'total_propiedades_bd': total_propiedades,
                    'total_vehiculos_bd': total_vehiculos,
                    'total_juridicas_rn_bd': total_juridicas_rn
                },
                'cobertura': {
                    'propiedades_inmobiliarias': 'Folios reales + búsquedas por provincia',
                    'vehiculos_registrados': 'Placas + búsquedas por año',
                    'sociedades_empresas': 'Registro mercantil + búsquedas por sector'
                }
            }
            
            await self.db.registro_nacional_extraction_reports.insert_one(report)
            
            logger.info("📊 REPORTE REGISTRO NACIONAL")
            logger.info(f"🏠 Propiedades: {self.stats['propiedades_extraidas']}")
            logger.info(f"🚗 Vehículos: {self.stats['vehiculos_extraidos']}")
            logger.info(f"🏢 Sociedades: {self.stats['sociedades_extraidas']}")
            logger.info(f"📊 Total: {self.stats['total_registros']}")
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
    
    async def close(self):
        """Cerrar conexiones"""
        if self.client:
            self.client.close()

async def run_registro_nacional_extraction():
    """Función principal"""
    extractor = RegistroNacionalExtractor()
    
    try:
        if await extractor.initialize():
            result = await extractor.extract_all_data()
            return result
        else:
            return {'error': 'Falló la inicialización'}
    finally:
        await extractor.close()

if __name__ == "__main__":
    result = asyncio.run(run_registro_nacional_extraction())
    print(f"🏛️ RESULTADO REGISTRO NACIONAL: {result}")