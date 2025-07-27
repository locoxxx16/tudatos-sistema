#!/usr/bin/env python3
"""
Extractor avanzado para Daticos con todas las funcionalidades identificadas
Incluye extracción de datos mercantiles, laborales, matrimonio, etc.
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import logging
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedDaticosExtractor:
    """
    Extractor avanzado para obtener TODA la información disponible en Daticos
    incluyendo datos mercantiles, laborales, matrimonio, etc.
    """
    
    def __init__(self):
        self.base_url = "https://www.daticos.com"
        self.session = None
        self.credentials = {
            'usuario': 'Saraya',
            'password': '12345'
        }
        self.logged_in = False
        self.extracted_data = []
        
        # Endpoints identificados para diferentes tipos de consulta
        self.endpoints = {
            'consultas_individuales': {
                'foto': '/foto.php',
                'global': '/buscedglobal.php', 
                'telefono': '/bustel.php',
                'nombres': '/busnom.php'
            },
            'consultas_masivas': {
                'patronos': '/buspat.php',
                'geografica': '/masgeo/index.php',
                'colegiados': '/mascol/index.php', 
                'pensionados': '/maspen/index.php',
                'independientes': '/masind/index.php'
            },
            'consultas_especiales': {
                'bloque_personales': '/bloque/bloquecedulas.php'
            },
            'otros': {
                'bitacora_csv': '/consultasusr.php',
                'telegram': '/telegram.php'
            }
        }
        
    async def initialize_session(self):
        """Inicializar sesión HTTP con configuración optimizada"""
        if not self.session:
            timeout = httpx.Timeout(60.0, connect=15.0)
            self.session = httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'no-cache'
                }
            )
    
    async def login(self) -> bool:
        """Login con las credenciales correctas identificadas"""
        try:
            await self.initialize_session()
            
            logger.info(f"🔐 Realizando login con usuario: {self.credentials['usuario']}")
            
            # Obtener página de login
            login_page = await self.session.get(f"{self.base_url}/login.php")
            login_page.raise_for_status()
            
            # Datos del formulario según análisis previo
            form_data = {
                'login': self.credentials['usuario'],
                'password': self.credentials['password'],
                'submit': 'Ingresar'
            }
            
            # Realizar login
            login_response = await self.session.post(
                f"{self.base_url}/login.php",
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            # Verificar login exitoso
            if login_response.status_code == 200:
                response_text = login_response.text.lower()
                success_indicators = ['consultas individuales', 'consultas masivas', 'salir', 'logout.php', 'saraya']
                successful_url = 'index.php' in str(login_response.url)
                
                has_success = any(indicator in response_text for indicator in success_indicators)
                
                if has_success and successful_url:
                    self.logged_in = True
                    logger.info("✅ Login exitoso en Daticos")
                    return True
                else:
                    logger.error("❌ Login fallido")
                    return False
            else:
                logger.error(f"❌ Error en login - Status: {login_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error durante login: {e}")
            return False
    
    async def explore_endpoint(self, endpoint: str, endpoint_name: str) -> Dict:
        """Explorar un endpoint específico y extraer su funcionalidad"""
        if not self.logged_in:
            await self.login()
            
        try:
            logger.info(f"🔍 Explorando endpoint: {endpoint_name} ({endpoint})")
            
            response = await self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code != 200:
                logger.warning(f"⚠️  Endpoint {endpoint} no accesible: {response.status_code}")
                return {'endpoint': endpoint, 'accessible': False, 'data': []}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Analizar formularios disponibles
            forms = soup.find_all('form')
            form_analysis = []
            
            for i, form in enumerate(forms):
                form_info = {
                    'action': form.get('action', endpoint),
                    'method': form.get('method', 'GET').upper(),
                    'inputs': [],
                    'selects': []
                }
                
                # Analizar inputs
                for inp in form.find_all('input'):
                    if inp.get('name'):
                        form_info['inputs'].append({
                            'name': inp.get('name'),
                            'type': inp.get('type', 'text'),
                            'value': inp.get('value', ''),
                            'placeholder': inp.get('placeholder', '')
                        })
                
                # Analizar selects
                for sel in form.find_all('select'):
                    if sel.get('name'):
                        options = [{'value': opt.get('value', ''), 'text': opt.get_text(strip=True)} 
                                 for opt in sel.find_all('option')]
                        form_info['selects'].append({
                            'name': sel.get('name'),
                            'options': options
                        })
                
                form_analysis.append(form_info)
            
            # Buscar tablas de datos existentes
            tables = soup.find_all('table')
            table_data = []
            
            for table in tables:
                rows = []
                for tr in table.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    if cells:  # Solo agregar filas no vacías
                        rows.append(cells)
                
                if rows:
                    table_data.append(rows)
            
            result = {
                'endpoint': endpoint,
                'endpoint_name': endpoint_name,
                'accessible': True,
                'forms': form_analysis,
                'existing_data': table_data,
                'html_content': response.text[:2000]  # Primeros 2000 caracteres para debug
            }
            
            logger.info(f"✅ Endpoint {endpoint_name}: {len(form_analysis)} formularios, {len(table_data)} tablas")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error explorando {endpoint}: {e}")
            return {'endpoint': endpoint, 'accessible': False, 'error': str(e)}
    
    async def extract_global_search_data(self, limit: int = 100) -> List[Dict]:
        """Extraer datos usando búsqueda global (/buscedglobal.php)"""
        logger.info("🌍 Iniciando extracción masiva via búsqueda global...")
        
        endpoint_info = await self.explore_endpoint('/buscedglobal.php', 'Búsqueda Global')
        if not endpoint_info.get('accessible'):
            return []
        
        extracted_records = []
        
        # Estrategias de búsqueda masiva
        search_strategies = [
            # Búsqueda por cédulas
            {'type': 'cedula', 'patterns': self.generate_cedula_patterns()},
            # Búsqueda por nombres comunes
            {'type': 'nombre', 'patterns': self.generate_name_patterns()},
            # Búsqueda por teléfonos
            {'type': 'telefono', 'patterns': self.generate_phone_patterns()}
        ]
        
        for strategy in search_strategies:
            logger.info(f"🔄 Ejecutando estrategia: {strategy['type']}")
            
            for pattern in strategy['patterns'][:limit//len(search_strategies)]:
                try:
                    result = await self.perform_global_search(pattern, strategy['type'])
                    if result.get('found'):
                        extracted_records.extend(result.get('data', []))
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error en búsqueda {pattern}: {e}")
                    continue
            
            if len(extracted_records) >= limit:
                break
        
        logger.info(f"📊 Extracción global completada: {len(extracted_records)} registros")
        return extracted_records
    
    async def perform_global_search(self, search_term: str, search_type: str) -> Dict:
        """Realizar búsqueda global específica"""
        try:
            # Datos del formulario para búsqueda global
            search_data = {
                'buscar': search_term,
                'submit': 'Buscar'
            }
            
            response = await self.session.post(
                f"{self.base_url}/buscedglobal.php",
                data=search_data
            )
            
            if response.status_code == 200:
                return await self.parse_search_results(response.text, search_term, search_type)
            else:
                return {'found': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'found': False, 'error': str(e)}
    
    async def parse_search_results(self, html_content: str, search_term: str, search_type: str) -> Dict:
        """Parsear resultados de búsqueda y extraer datos estructurados"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Buscar tablas de resultados
            tables = soup.find_all('table')
            extracted_data = []
            
            for table in tables:
                rows = table.find_all('tr')
                
                if len(rows) > 1:  # Tabla con headers y datos
                    # Extraer headers
                    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                    
                    # Extraer datos de cada fila
                    for row in rows[1:]:
                        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                        if len(cells) == len(headers):
                            record = dict(zip(headers, cells))
                            record['search_term'] = search_term
                            record['search_type'] = search_type
                            record['extracted_at'] = datetime.utcnow().isoformat()
                            extracted_data.append(record)
            
            # Buscar divs con información adicional
            info_divs = soup.find_all('div', class_=re.compile(r'result|info|data|person'))
            for div in info_divs:
                text = div.get_text()
                if len(text.strip()) > 20:  # Filtrar divs con contenido significativo
                    record = {
                        'content': text.strip(),
                        'search_term': search_term,
                        'search_type': search_type,
                        'extracted_at': datetime.utcnow().isoformat()
                    }
                    extracted_data.append(record)
            
            result = {
                'found': len(extracted_data) > 0,
                'data': extracted_data,
                'search_term': search_term,
                'search_type': search_type,
                'raw_html': html_content[:1000]  # Para debugging
            }
            
            if result['found']:
                logger.info(f"✅ Encontrados {len(extracted_data)} registros para '{search_term}'")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parseando resultados para '{search_term}': {e}")
            return {'found': False, 'error': str(e)}
    
    def generate_cedula_patterns(self) -> List[str]:
        """Generar patrones de cédulas para búsqueda masiva"""
        patterns = []
        
        # Cédulas físicas (formato: X-XXXX-XXXX)
        for province in range(1, 8):  # 7 provincias de Costa Rica
            for i in range(0, 9999, 100):  # Muestreo cada 100
                cedula = f"{province}-{i:04d}-{(i*7)%10000:04d}"
                patterns.append(cedula)
        
        # Cédulas jurídicas (formato: 3-XXX-XXXXXX)
        for i in range(101, 999, 10):
            for j in range(100000, 999999, 10000):
                cedula = f"3-{i:03d}-{j:06d}"
                patterns.append(cedula)
        
        return patterns[:500]  # Limitar a 500 patrones
    
    def generate_name_patterns(self) -> List[str]:
        """Generar patrones de nombres comunes en Costa Rica"""
        nombres_comunes = [
            'María', 'José', 'Ana', 'Carlos', 'Luis', 'Carmen', 'Juan', 'Rosa',
            'Antonio', 'Francisca', 'Manuel', 'Isabel', 'Pedro', 'Juana',
            'Francisco', 'Teresa', 'Ramón', 'Mercedes', 'Miguel', 'Concepción',
            'Rafael', 'Dolores', 'Jesús', 'Pilar', 'Ángel', 'Josefa',
            'Alejandro', 'Antonia', 'Fernando', 'Esperanza'
        ]
        
        apellidos_comunes = [
            'González', 'Rodríguez', 'García', 'Fernández', 'López', 'Martínez',
            'Sánchez', 'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz',
            'Hernández', 'Díaz', 'Moreno', 'Muñoz', 'Álvarez', 'Romero',
            'Alonso', 'Gutiérrez', 'Navarro', 'Torres', 'Domínguez', 'Vázquez',
            'Ramos', 'Gil', 'Ramírez', 'Serrano', 'Blanco', 'Suárez'
        ]
        
        patterns = []
        
        # Combinaciones de nombres y apellidos
        for nombre in nombres_comunes[:15]:
            patterns.append(nombre)
            for apellido in apellidos_comunes[:10]:
                patterns.append(f"{nombre} {apellido}")
        
        return patterns
    
    def generate_phone_patterns(self) -> List[str]:
        """Generar patrones de teléfonos costarricenses"""
        patterns = []
        
        # Teléfonos móviles (8XXX-XXXX)
        for prefix in ['8', '7', '6']:
            for i in range(1000, 9999, 100):
                phone = f"{prefix}{i:03d}-{(i*3)%10000:04d}"
                patterns.append(phone)
        
        # Teléfonos fijos por provincia
        # San José: 2XXX-XXXX
        for i in range(2000, 2999, 50):
            phone = f"{i}-{(i*5)%10000:04d}"
            patterns.append(phone)
        
        return patterns[:200]  # Limitar a 200 patrones
    
    async def extract_massive_geographic_data(self) -> List[Dict]:
        """Extraer datos usando consultas geográficas masivas"""
        logger.info("🗺️ Iniciando extracción masiva geográfica...")
        
        endpoint_info = await self.explore_endpoint('/masgeo/index.php', 'Consulta Geográfica')
        if not endpoint_info.get('accessible'):
            return []
        
        extracted_data = []
        
        # Provincias de Costa Rica
        provincias = [
            'San José', 'Alajuela', 'Cartago', 'Heredia', 
            'Guanacaste', 'Puntarenas', 'Limón'
        ]
        
        for provincia in provincias:
            try:
                logger.info(f"📍 Extrayendo datos de {provincia}...")
                provincia_data = await self.extract_geographic_by_province(provincia)
                extracted_data.extend(provincia_data)
                
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error extrayendo datos de {provincia}: {e}")
                continue
        
        logger.info(f"🗺️ Extracción geográfica completada: {len(extracted_data)} registros")
        return extracted_data
    
    async def extract_geographic_by_province(self, provincia: str) -> List[Dict]:
        """Extraer datos de una provincia específica"""
        try:
            # Formulario para consulta geográfica
            geo_data = {
                'provincia': provincia,
                'submit': 'Consultar'
            }
            
            response = await self.session.post(
                f"{self.base_url}/masgeo/index.php",
                data=geo_data
            )
            
            if response.status_code == 200:
                return await self.parse_geographic_results(response.text, provincia)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error en consulta geográfica {provincia}: {e}")
            return []
    
    async def parse_geographic_results(self, html_content: str, provincia: str) -> List[Dict]:
        """Parsear resultados de consulta geográfica"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            data = []
            
            # Buscar tablas de resultados
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                
                if len(rows) > 1:
                    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                    
                    for row in rows[1:]:
                        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                        if len(cells) >= len(headers):
                            record = dict(zip(headers, cells))
                            record['provincia_consulta'] = provincia
                            record['tipo_consulta'] = 'geografica'
                            record['extracted_at'] = datetime.utcnow().isoformat()
                            data.append(record)
            
            return data
            
        except Exception as e:
            logger.error(f"Error parseando resultados geográficos: {e}")
            return []
    
    async def extract_all_endpoint_data(self) -> Dict:
        """Extraer datos de TODOS los endpoints disponibles"""
        logger.info("🚀 Iniciando extracción COMPLETA de todos los endpoints...")
        
        if not self.logged_in:
            await self.login()
        
        all_data = {
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'credentials_used': self.credentials['usuario'],
            'endpoints_explored': {},
            'total_records': 0
        }
        
        # Explorar todos los endpoints identificados
        for category, endpoints in self.endpoints.items():
            logger.info(f"📂 Procesando categoría: {category}")
            all_data['endpoints_explored'][category] = {}
            
            for name, endpoint in endpoints.items():
                try:
                    logger.info(f"🔍 Procesando {name} ({endpoint})...")
                    
                    # Explorar endpoint y obtener estructura
                    endpoint_data = await self.explore_endpoint(endpoint, name)
                    
                    # Intentar extraer datos específicos según el tipo
                    if 'global' in name.lower():
                        extracted_data = await self.extract_global_search_data(200)
                    elif 'geografica' in name.lower():
                        extracted_data = await self.extract_massive_geographic_data()
                    else:
                        extracted_data = await self.extract_from_endpoint(endpoint, name)
                    
                    endpoint_data['extracted_records'] = extracted_data
                    endpoint_data['record_count'] = len(extracted_data)
                    
                    all_data['endpoints_explored'][category][name] = endpoint_data
                    all_data['total_records'] += len(extracted_data)
                    
                    logger.info(f"✅ {name}: {len(extracted_data)} registros extraídos")
                    
                    # Rate limiting entre endpoints
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando {name}: {e}")
                    all_data['endpoints_explored'][category][name] = {
                        'error': str(e),
                        'extracted_records': [],
                        'record_count': 0
                    }
                    continue
        
        logger.info(f"🎉 Extracción COMPLETA finalizada: {all_data['total_records']} registros totales")
        
        # Guardar resultado completo
        with open('/app/backend/daticos_complete_extraction.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        return all_data
    
    async def extract_from_endpoint(self, endpoint: str, name: str) -> List[Dict]:
        """Extracción genérica de cualquier endpoint"""
        try:
            response = await self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code == 200:
                return await self.parse_generic_endpoint(response.text, endpoint, name)
            else:
                return []
        except Exception as e:
            logger.error(f"Error extrayendo de {endpoint}: {e}")
            return []
    
    async def parse_generic_endpoint(self, html_content: str, endpoint: str, name: str) -> List[Dict]:
        """Parser genérico para cualquier endpoint"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            data = []
            
            # Buscar todas las tablas con datos
            tables = soup.find_all('table')
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                
                if len(rows) > 1:  # Tabla con headers y datos
                    headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                    
                    for row in rows[1:]:
                        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                        if cells:  # Solo procesar filas no vacías
                            record = {}
                            for j, cell in enumerate(cells):
                                header = headers[j] if j < len(headers) else f'column_{j}'
                                record[header] = cell
                            
                            record['source_endpoint'] = endpoint
                            record['source_name'] = name
                            record['table_index'] = i
                            record['extracted_at'] = datetime.utcnow().isoformat()
                            data.append(record)
            
            return data
            
        except Exception as e:
            logger.error(f"Error parseando endpoint genérico: {e}")
            return []
    
    async def close_session(self):
        """Cerrar sesión"""
        if self.session:
            await self.session.aclose()
            self.session = None
            self.logged_in = False

# Función principal para ejecutar la extracción completa
async def run_complete_extraction():
    """Ejecutar extracción completa de Daticos"""
    extractor = AdvancedDaticosExtractor()
    
    try:
        logger.info("🚀 Iniciando extracción MASIVA de Daticos...")
        
        # Login
        if not await extractor.login():
            logger.error("❌ No se pudo realizar login")
            return None
        
        # Extracción completa
        complete_data = await extractor.extract_all_endpoint_data()
        
        logger.info(f"🎉 ¡Extracción completada exitosamente!")
        logger.info(f"📊 Total de registros extraídos: {complete_data['total_records']}")
        
        return complete_data
        
    except Exception as e:
        logger.error(f"❌ Error durante extracción completa: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        await extractor.close_session()

if __name__ == "__main__":
    # Ejecutar extracción completa
    result = asyncio.run(run_complete_extraction())
    if result:
        print(f"\n🎯 EXTRACCIÓN COMPLETADA:")
        print(f"   📊 Total registros: {result['total_records']}")
        print(f"   📂 Categorías procesadas: {len(result['endpoints_explored'])}")
        print(f"   💾 Resultado guardado en: daticos_complete_extraction.json")
    else:
        print("\n❌ Extracción falló")