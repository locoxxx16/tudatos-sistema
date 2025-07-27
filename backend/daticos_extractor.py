import httpx
import asyncio
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
import re
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DaticosExtractor:
    """
    Extractor para obtener datos completos de Daticos.com
    usando las credenciales proporcionadas por el usuario
    """
    
    def __init__(self):
        self.base_url = "https://www.daticos.com"
        self.session = None
        self.credentials = {
            'usuario': 'Saraya',
            'password': '12345'
        }
        self.logged_in = False
        
    async def initialize_session(self):
        """Inicializar sesión HTTP con timeout extendido"""
        if not self.session:
            timeout = httpx.Timeout(30.0, connect=10.0)
            self.session = httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
    
    async def login(self) -> bool:
        """
        Realizar login en Daticos.com usando las credenciales proporcionadas
        """
        try:
            await self.initialize_session()
            
            # Primero obtener la página de login para posibles tokens CSRF
            logger.info(f"Accediendo a la página de login de Daticos: {self.base_url}/login.php")
            login_page = await self.session.get(f"{self.base_url}/login.php")
            login_page.raise_for_status()
            
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Buscar el formulario de login y extraer campos necesarios
            form = soup.find('form')
            form_data = {
                'usuario': self.credentials['usuario'],
                'password': self.credentials['password']
            }
            
            # Buscar campos hidden adicionales (tokens CSRF, etc.)
            if form:
                hidden_inputs = form.find_all('input', type='hidden')
                for inp in hidden_inputs:
                    if inp.get('name') and inp.get('value'):
                        form_data[inp.get('name')] = inp.get('value')
            
            logger.info(f"Intentando login con usuario: {self.credentials['usuario']}")
            
            # Realizar el login
            login_response = await self.session.post(
                f"{self.base_url}/login.php",
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            # Verificar si el login fue exitoso
            if login_response.status_code == 200:
                # Buscar indicadores de login exitoso
                response_text = login_response.text.lower()
                success_indicators = ['dashboard', 'panel', 'bienvenido', 'consulta', 'logout', 'salir']
                error_indicators = ['error', 'incorrecto', 'inválido', 'login', 'usuario o contraseña']
                
                has_success = any(indicator in response_text for indicator in success_indicators)
                has_error = any(indicator in response_text for indicator in error_indicators)
                
                if has_success and not has_error:
                    self.logged_in = True
                    logger.info("✅ Login exitoso en Daticos")
                    return True
                else:
                    logger.error("❌ Login fallido - credenciales incorrectas o página de error")
                    return False
            else:
                logger.error(f"❌ Error en login - Status code: {login_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error durante el proceso de login: {e}")
            return False
    
    async def discover_system_structure(self) -> Dict:
        """
        Analizar la estructura del sistema Daticos para entender sus funcionalidades
        """
        if not self.logged_in:
            logger.error("Debe realizar login antes de explorar la estructura")
            return {}
            
        try:
            structure = {
                'menu_items': [],
                'consultation_types': [],
                'available_endpoints': [],
                'data_fields': []
            }
            
            # Obtener página principal después del login
            dashboard = await self.session.get(f"{self.base_url}/")
            soup = BeautifulSoup(dashboard.text, 'html.parser')
            
            # Buscar elementos de navegación y menús
            nav_elements = soup.find_all(['nav', 'ul', 'div'], class_=re.compile(r'menu|nav'))
            for nav in nav_elements:
                links = nav.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if href and text and len(text) > 2:
                        structure['menu_items'].append({
                            'text': text,
                            'href': href,
                            'full_url': f"{self.base_url}/{href.lstrip('/')}"
                        })
            
            # Buscar formularios de consulta
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all('input')
                selects = form.find_all('select')
                
                form_info = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET'),
                    'inputs': [{'name': inp.get('name'), 'type': inp.get('type')} for inp in inputs if inp.get('name')],
                    'selects': [{'name': sel.get('name')} for sel in selects if sel.get('name')]
                }
                
                if form_info['inputs'] or form_info['selects']:
                    structure['consultation_types'].append(form_info)
            
            logger.info(f"📋 Estructura del sistema descubierta: {len(structure['menu_items'])} elementos de menú")
            return structure
            
        except Exception as e:
            logger.error(f"Error analizando estructura del sistema: {e}")
            return {}
    
    async def extract_consultation_by_cedula(self, cedula: str) -> Dict:
        """
        Realizar consulta por cédula en el sistema original Daticos
        """
        if not self.logged_in:
            await self.login()
            
        try:
            # Buscar la página de consulta por cédula
            consultation_endpoints = [
                '/consulta.php',
                '/busqueda.php', 
                '/cedula.php',
                '/individual.php'
            ]
            
            for endpoint in consultation_endpoints:
                try:
                    page = await self.session.get(f"{self.base_url}{endpoint}")
                    if page.status_code == 200 and 'cedula' in page.text.lower():
                        # Encontrar formulario de consulta
                        soup = BeautifulSoup(page.text, 'html.parser')
                        forms = soup.find_all('form')
                        
                        for form in forms:
                            cedula_input = form.find('input', attrs={'name': re.compile(r'cedula|documento|id')})
                            if cedula_input:
                                # Realizar consulta
                                form_data = {cedula_input.get('name'): cedula}
                                
                                # Agregar otros campos requeridos
                                for inp in form.find_all('input', type='hidden'):
                                    if inp.get('name') and inp.get('value'):
                                        form_data[inp.get('name')] = inp.get('value')
                                
                                result = await self.session.post(
                                    f"{self.base_url}{form.get('action', endpoint)}",
                                    data=form_data
                                )
                                
                                if result.status_code == 200:
                                    return await self.parse_consultation_result(result.text, cedula)
                                        
                except Exception as inner_e:
                    logger.debug(f"Endpoint {endpoint} no disponible: {inner_e}")
                    continue
                    
            logger.warning(f"No se pudo encontrar endpoint de consulta por cédula")
            return {}
            
        except Exception as e:
            logger.error(f"Error en consulta por cédula {cedula}: {e}")
            return {}
    
    async def parse_consultation_result(self, html_content: str, cedula: str) -> Dict:
        """
        Parsear resultado de consulta HTML y extraer datos estructurados
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            result_data = {
                'cedula': cedula,
                'found': False,
                'data': {},
                'raw_html': html_content[:1000],  # Primeros 1000 caracteres para debug
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Buscar tablas de datos
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Mapear campos comunes
                        if any(keyword in key for keyword in ['nombre', 'name']):
                            result_data['data']['nombre'] = value
                        elif any(keyword in key for keyword in ['apellido', 'surname']):
                            if 'apellidos' not in result_data['data']:
                                result_data['data']['apellidos'] = value
                            else:
                                result_data['data']['apellidos'] += ' ' + value
                        elif any(keyword in key for keyword in ['telefono', 'phone', 'tel']):
                            result_data['data']['telefono'] = value
                        elif any(keyword in key for keyword in ['direccion', 'address']):
                            result_data['data']['direccion'] = value
                        elif any(keyword in key for keyword in ['provincia', 'province']):
                            result_data['data']['provincia'] = value
                        elif any(keyword in key for keyword in ['canton', 'county']):
                            result_data['data']['canton'] = value
                        elif any(keyword in key for keyword in ['distrito', 'district']):
                            result_data['data']['distrito'] = value
            
            # Buscar divs con información
            info_divs = soup.find_all('div', class_=re.compile(r'result|info|data|person'))
            for div in info_divs:
                text = div.get_text()
                # Usar regex para extraer información específica
                phone_match = re.search(r'(\d{4}-\d{4}|\d{8})', text)
                if phone_match and 'telefono' not in result_data['data']:
                    result_data['data']['telefono'] = phone_match.group(1)
            
            # Determinar si se encontraron datos
            result_data['found'] = bool(result_data['data'])
            
            logger.info(f"📄 Datos extraídos para cédula {cedula}: {len(result_data['data'])} campos")
            return result_data
            
        except Exception as e:
            logger.error(f"Error parseando resultado de consulta: {e}")
            return {'cedula': cedula, 'found': False, 'error': str(e)}
    
    async def bulk_extract_database(self, limit: int = 1000) -> List[Dict]:
        """
        Extraer datos masivamente de la base de datos de Daticos
        """
        if not self.logged_in:
            await self.login()
            
        extracted_data = []
        
        # Estrategias para extracción masiva
        strategies = [
            self.extract_by_cedula_range,
            self.extract_by_geographic_search,
            self.extract_by_name_patterns
        ]
        
        for strategy in strategies:
            try:
                logger.info(f"🔄 Ejecutando estrategia de extracción: {strategy.__name__}")
                batch_data = await strategy(limit // len(strategies))
                extracted_data.extend(batch_data)
                
                # Evitar sobrecargar el servidor
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error en estrategia {strategy.__name__}: {e}")
                continue
        
        logger.info(f"📊 Extracción masiva completada: {len(extracted_data)} registros")
        return extracted_data
    
    async def extract_by_cedula_range(self, limit: int) -> List[Dict]:
        """Extraer datos probando rangos de cédulas comunes"""
        results = []
        
        # Rangos comunes de cédulas costarricenses
        cedula_prefixes = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        
        for prefix in cedula_prefixes:
            for i in range(100000000 + int(prefix) * 100000000, 100000000 + int(prefix) * 100000000 + min(limit//len(cedula_prefixes), 50000), 10000):
                cedula = str(i)
                result = await self.extract_consultation_by_cedula(cedula)
                if result.get('found'):
                    results.append(result)
                    logger.info(f"✅ Encontrado: {cedula}")
                
                await asyncio.sleep(0.1)  # Rate limiting
                
        return results
    
    async def extract_by_geographic_search(self, limit: int) -> List[Dict]:
        """Extraer datos usando búsquedas geográficas"""
        results = []
        
        # Provincias de Costa Rica
        provinces = ['San José', 'Alajuela', 'Cartago', 'Heredia', 'Guanacaste', 'Puntarenas', 'Limón']
        
        for province in provinces:
            try:
                # Buscar endpoint de búsqueda geográfica
                geographic_data = await self.perform_geographic_search(province)
                results.extend(geographic_data)
                
                if len(results) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error en búsqueda geográfica para {province}: {e}")
                continue
                
        return results[:limit]
    
    async def extract_by_name_patterns(self, limit: int) -> List[Dict]:
        """Extraer datos usando patrones de nombres comunes"""
        results = []
        
        # Nombres comunes en Costa Rica
        common_names = ['María', 'José', 'Ana', 'Carlos', 'Luis', 'Rosa', 'Juan', 'Carmen']
        
        for name in common_names:
            try:
                name_results = await self.perform_name_search(name)
                results.extend(name_results)
                
                if len(results) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error en búsqueda por nombre {name}: {e}")
                continue
                
        return results[:limit]
    
    async def perform_geographic_search(self, province: str) -> List[Dict]:
        """Realizar búsqueda geográfica específica"""
        # Implementación básica - se puede extender según la estructura real
        return []
    
    async def perform_name_search(self, name: str) -> List[Dict]:
        """Realizar búsqueda por nombre específico"""
        # Implementación básica - se puede extender según la estructura real
        return []
    
    async def analyze_data_quality(self, sample_data: List[Dict]) -> Dict:
        """
        Analizar calidad de los datos extraídos
        """
        if not sample_data:
            return {'total_records': 0, 'quality_score': 0}
            
        analysis = {
            'total_records': len(sample_data),
            'complete_records': 0,
            'partial_records': 0,
            'empty_records': 0,
            'field_completeness': {},
            'quality_score': 0
        }
        
        all_fields = set()
        for record in sample_data:
            if record.get('data'):
                all_fields.update(record['data'].keys())
        
        for field in all_fields:
            analysis['field_completeness'][field] = sum(1 for record in sample_data 
                                                      if record.get('data', {}).get(field))
        
        # Calcular score de calidad
        for record in sample_data:
            data_fields = len(record.get('data', {}))
            if data_fields > 5:
                analysis['complete_records'] += 1
            elif data_fields > 0:
                analysis['partial_records'] += 1
            else:
                analysis['empty_records'] += 1
        
        if analysis['total_records'] > 0:
            analysis['quality_score'] = (analysis['complete_records'] * 1.0 + 
                                       analysis['partial_records'] * 0.5) / analysis['total_records']
        
        return analysis
    
    async def close_session(self):
        """Cerrar sesión HTTP"""
        if self.session:
            await self.session.aclose()
            self.session = None
            self.logged_in = False

# Instancia global del extractor
daticos_extractor = DaticosExtractor()