"""
COLEGIOS PROFESIONALES EXTRACTOR
Extractor para datos de los Colegios Profesionales de Costa Rica

Fuentes principales:
- Colegio de Médicos y Cirujanos (CMCR)
- Colegio de Ingenieros y Arquitectos (CFIA)
- Colegio de Abogados (CACR)
- Colegio de Farmacéuticos (CFCR)
- Colegio de Enfermeras (CECR)
- Colegio de Contadores Públicos (CCPCR)
- Y todos los colegios profesionales reconocidos

URLs objetivo:
- https://www.medicos.cr/
- https://www.cfia.or.cr/
- https://www.abogados.or.cr/
- https://www.colfar.com/
- Y portales de verificación de profesionales

Datos objetivo:
- Profesionales colegiados activos
- Números de colegiado
- Especialidades y certificaciones
- Estado de incorporación
- Direcciones de consultorio/oficina
- Teléfonos de contacto profesional

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

class ColegiosProfesionalesExtractor:
    """Extractor de Colegios Profesionales de Costa Rica"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
        
        # Colegios profesionales principales de Costa Rica
        self.colegios = {
            'medicos': {
                'nombre': 'Colegio de Médicos y Cirujanos',
                'url': 'https://www.medicos.cr',
                'codigo': 'CMCR',
                'verificacion_url': '/verificacion-profesionales',
                'directorio_url': '/directorio-medicos'
            },
            'ingenieros': {
                'nombre': 'Colegio Federado de Ingenieros y Arquitectos',
                'url': 'https://www.cfia.or.cr',
                'codigo': 'CFIA',
                'verificacion_url': '/verificacion',
                'directorio_url': '/profesionales'
            },
            'abogados': {
                'nombre': 'Colegio de Abogados',
                'url': 'https://www.abogados.or.cr',
                'codigo': 'CACR',
                'verificacion_url': '/verificacion-abogados',
                'directorio_url': '/directorio'
            },
            'farmaceuticos': {
                'nombre': 'Colegio de Farmacéuticos',
                'url': 'https://www.colfar.com',
                'codigo': 'CFCR',
                'verificacion_url': '/verificar-colegiado',
                'directorio_url': '/farmaceuticos'
            },
            'enfermeras': {
                'nombre': 'Colegio de Enfermeras',
                'url': 'https://www.cecr.or.cr',
                'codigo': 'CECR',
                'verificacion_url': '/verificacion',
                'directorio_url': '/enfermeras-colegiadas'
            },
            'contadores': {
                'nombre': 'Colegio de Contadores Públicos',
                'url': 'https://www.ccpcr.com',
                'codigo': 'CCPCR',
                'verificacion_url': '/verificacion-cpa',
                'directorio_url': '/contadores-publicos'
            },
            'psicologos': {
                'nombre': 'Colegio Profesional de Psicólogos',
                'url': 'https://www.colpsicr.com',
                'codigo': 'CPPCR',
                'verificacion_url': '/verificacion-psicologos',
                'directorio_url': '/psicologos-colegiados'
            },
            'trabajadores_sociales': {
                'nombre': 'Colegio de Trabajadores Sociales',
                'url': 'https://www.coltsocr.com',
                'codigo': 'CTSCR',
                'verificacion_url': '/verificacion',
                'directorio_url': '/trabajadores-sociales'
            },
            'veterinarios': {
                'nombre': 'Colegio de Médicos Veterinarios',
                'url': 'https://www.colvet.or.cr',
                'codigo': 'CMVCR',
                'verificacion_url': '/verificacion-veterinarios',
                'directorio_url': '/veterinarios'
            },
            'odontologos': {
                'nombre': 'Colegio de Cirujanos Dentistas',
                'url': 'https://www.ccdcr.com',
                'codigo': 'CCDCR',
                'verificacion_url': '/verificacion-odontologos',
                'directorio_url': '/dentistas'
            },
            'optometristas': {
                'nombre': 'Colegio de Optometristas',
                'url': 'https://www.coo.cr',
                'codigo': 'COOCR',
                'verificacion_url': '/verificacion',
                'directorio_url': '/optometristas'
            },
            'nutricionistas': {
                'nombre': 'Colegio de Profesionales en Nutrición',
                'url': 'https://www.cpn.cr',
                'codigo': 'CPNCR',
                'verificacion_url': '/verificacion-nutricionistas',
                'directorio_url': '/nutricionistas-colegiados'
            }
        }
        
        self.stats = {
            'medicos_extraidos': 0,
            'ingenieros_extraidos': 0,
            'abogados_extraidos': 0,
            'farmaceuticos_extraidos': 0,
            'enfermeras_extraidas': 0,
            'contadores_extraidos': 0,
            'otros_profesionales_extraidos': 0,
            'total_profesionales': 0,
            'colegios_procesados': 0,
            'numeros_colegiado_encontrados': 0,
            'consultoros_direcciones_encontradas': 0,
            'especialidades_encontradas': 0,
            'errores': 0
        }
        
        # Patrones específicos para profesionales
        self.patterns = {
            'numero_colegiado': re.compile(r'(?:No\.?\s*|Número\s*|#\s*)([A-Z]*\d{3,6})', re.IGNORECASE),
            'cedula_profesional': re.compile(r'[1-9]-\d{4}-\d{4}'),
            'especialidad': re.compile(r'Especialidad[:\s]*([A-Za-záéíóúñ\s]{5,50})', re.IGNORECASE),
            'consultorio': re.compile(r'Consultorio[:\s]*([^,\n]{10,100})', re.IGNORECASE),
            'telefono_consultorio': re.compile(r'(?:Tel|Teléfono)[:\s]*\+?506[-\s]?([2-8]\d{3}[-\s]?\d{4})', re.IGNORECASE),
            'email_profesional': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'horario_atencion': re.compile(r'Horario[:\s]*([^,\n]{5,50})', re.IGNORECASE),
            'ubicacion_consultorio': re.compile(r'(?:Dirección|Ubicación)[:\s]*([^,\n]{10,100})', re.IGNORECASE)
        }
        
        # Métodos de búsqueda por rangos
        self.search_methods = {
            'por_numero_colegiado': list(range(1, 20000, 100)),  # Rangos de números
            'por_cedula': [],  # Se llena con cédulas conocidas
            'por_apellido': ['RODRIGUEZ', 'GONZALEZ', 'FERNANDEZ', 'LOPEZ', 'MARTINEZ', 'SANCHEZ', 'PEREZ', 'RAMIREZ'],
            'por_especialidad': ['MEDICINA_INTERNA', 'PEDIATRIA', 'GINECOLOGIA', 'CARDIOLOGIA', 'NEUROLOGIA']
        }
    
    async def initialize(self):
        """Inicializar conexiones y datos"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            await self.db.command('ping')
            logger.info("✅ Colegios Profesionales Extractor - MongoDB OK")
            
            # Cargar cédulas conocidas para búsquedas
            await self.load_known_cedulas()
            
            return True
        except Exception as e:
            logger.error(f"❌ Error inicializando: {e}")
            return False
    
    async def load_known_cedulas(self):
        """Cargar cédulas conocidas de otras fuentes para búsquedas dirigidas"""
        try:
            # Obtener muestra de cédulas físicas existentes
            cedulas_conocidas = []
            
            async for doc in self.db.personas_fisicas.find({}, {'cedula': 1}).limit(2000):
                if doc.get('cedula') and re.match(r'[1-9]-\d{4}-\d{4}', doc['cedula']):
                    cedulas_conocidas.append(doc['cedula'])
            
            self.search_methods['por_cedula'] = cedulas_conocidas
            logger.info(f"📋 Cargadas {len(cedulas_conocidas)} cédulas para búsquedas dirigidas")
            
        except Exception as e:
            logger.error(f"❌ Error cargando cédulas conocidas: {e}")
    
    async def extract_all_data(self):
        """Extraer datos de todos los colegios profesionales"""
        logger.info("🎓 INICIANDO EXTRACCIÓN COLEGIOS PROFESIONALES")
        
        timeout = httpx.Timeout(120.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as session:
            
            # Procesar cada colegio profesional
            for colegio_key, colegio_info in self.colegios.items():
                try:
                    logger.info(f"🏛️ Procesando: {colegio_info['nombre']}")
                    
                    # Extraer por diferentes métodos
                    extracted_total = 0
                    
                    # 1. Directorio público (si existe)
                    directorio_count = await self.extract_from_directorio(session, colegio_key, colegio_info)
                    extracted_total += directorio_count
                    
                    # 2. Sistema de verificación
                    verificacion_count = await self.extract_from_verificacion(session, colegio_key, colegio_info)
                    extracted_total += verificacion_count
                    
                    # 3. Búsquedas por rangos de números de colegiado
                    numeros_count = await self.extract_by_numero_colegiado(session, colegio_key, colegio_info)
                    extracted_total += numeros_count
                    
                    # 4. Búsquedas por cédulas conocidas
                    cedulas_count = await self.extract_by_cedulas_conocidas(session, colegio_key, colegio_info)
                    extracted_total += cedulas_count
                    
                    # Actualizar estadísticas específicas del colegio
                    stat_key = f'{colegio_key}_extraidos'
                    if stat_key in self.stats:
                        self.stats[stat_key] += extracted_total
                    else:
                        self.stats['otros_profesionales_extraidos'] += extracted_total
                    
                    self.stats['total_profesionales'] += extracted_total
                    self.stats['colegios_procesados'] += 1
                    
                    logger.info(f"✅ {colegio_info['nombre']}: {extracted_total} profesionales extraídos")
                    
                    # Pausa entre colegios
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando {colegio_info['nombre']}: {e}")
                    self.stats['errores'] += 1
                    continue
        
        await self.generate_report()
        logger.info(f"✅ Extracción Colegios Profesionales completada - {self.stats['total_profesionales']} profesionales")
        
        return self.stats
    
    async def extract_from_directorio(self, session, colegio_key: str, colegio_info: Dict) -> int:
        """Extraer desde directorio público del colegio"""
        logger.info(f"📖 Extrayendo directorio: {colegio_info['nombre']}")
        
        try:
            directorio_url = f"{colegio_info['url']}{colegio_info['directorio_url']}"
            extracted_count = 0
            
            # URLs alternativas para el directorio
            directorio_urls = [
                directorio_url,
                f"{colegio_info['url']}/directorio",
                f"{colegio_info['url']}/profesionales",
                f"{colegio_info['url']}/miembros",
                f"{colegio_info['url']}/colegiados",
                f"{colegio_info['url']}/listado-profesionales"
            ]
            
            for url in directorio_urls:
                try:
                    response = await session.get(url, timeout=45)
                    
                    if response.status_code == 200:
                        profesionales = self.extract_professionals_from_directory_page(
                            response.text, colegio_key, colegio_info, url
                        )
                        
                        if profesionales and len(profesionales) > 0:
                            await self.save_professionals(profesionales, colegio_key)
                            extracted_count += len(profesionales)
                            logger.info(f"📋 Directorio {colegio_key}: {len(profesionales)} profesionales")
                            
                            # Si encontramos profesionales, intentar paginar
                            paginated_count = await self.extract_paginated_directory(
                                session, url, colegio_key, colegio_info
                            )
                            extracted_count += paginated_count
                            break
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    continue
            
            return extracted_count
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo directorio {colegio_key}: {e}")
            return 0
    
    async def extract_paginated_directory(self, session, base_url: str, colegio_key: str, colegio_info: Dict) -> int:
        """Extraer páginas adicionales del directorio"""
        try:
            total_extracted = 0
            
            # Intentar paginación común
            pagination_patterns = [
                '?page={}',
                '?p={}',
                '?pagina={}',
                '/page/{}',
                '/pagina/{}'
            ]
            
            for pattern in pagination_patterns:
                for page_num in range(2, 21):  # Páginas 2-20
                    try:
                        paginated_url = base_url + pattern.format(page_num)
                        response = await session.get(paginated_url, timeout=30)
                        
                        if response.status_code == 200:
                            profesionales = self.extract_professionals_from_directory_page(
                                response.text, colegio_key, colegio_info, paginated_url
                            )
                            
                            if profesionales and len(profesionales) > 0:
                                await self.save_professionals(profesionales, colegio_key)
                                total_extracted += len(profesionales)
                                logger.info(f"📄 Página {page_num}: {len(profesionales)} profesionales")
                            else:
                                break  # No más datos, salir del loop
                        else:
                            break  # Error, probar siguiente patrón
                        
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        break
                
                if total_extracted > 0:
                    break  # Patrón exitoso, no probar otros
            
            return total_extracted
            
        except Exception as e:
            logger.error(f"❌ Error en paginación: {e}")
            return 0
    
    async def extract_from_verificacion(self, session, colegio_key: str, colegio_info: Dict) -> int:
        """Extraer usando sistema de verificación"""
        logger.info(f"🔍 Extrayendo por verificación: {colegio_info['nombre']}")
        
        try:
            verificacion_url = f"{colegio_info['url']}{colegio_info['verificacion_url']}"
            extracted_count = 0
            
            # URLs alternativas para verificación
            verificacion_urls = [
                verificacion_url,
                f"{colegio_info['url']}/verificacion",
                f"{colegio_info['url']}/consulta",
                f"{colegio_info['url']}/buscar",
                f"{colegio_info['url']}/search"
            ]
            
            for url in verificacion_urls:
                try:
                    # Obtener página de verificación
                    response = await session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        # Intentar búsquedas sistemáticas
                        search_count = await self.perform_systematic_searches(
                            session, url, colegio_key, colegio_info
                        )
                        extracted_count += search_count
                        
                        if search_count > 0:
                            break  # URL exitosa, no probar otras
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    continue
            
            return extracted_count
            
        except Exception as e:
            logger.error(f"❌ Error verificación {colegio_key}: {e}")
            return 0
    
    async def perform_systematic_searches(self, session, search_url: str, colegio_key: str, colegio_info: Dict) -> int:
        """Realizar búsquedas sistemáticas en el sistema de verificación"""
        try:
            total_found = 0
            
            # Obtener formulario de búsqueda
            form_response = await session.get(search_url, timeout=30)
            if form_response.status_code != 200:
                return 0
            
            soup = BeautifulSoup(form_response.text, 'html.parser')
            form = soup.find('form')
            
            if not form:
                return 0
            
            # Identificar campos del formulario
            form_action = form.get('action', search_url)
            if not form_action.startswith('http'):
                form_action = colegio_info['url'] + form_action
            
            form_method = form.get('method', 'GET').upper()
            
            # Buscar por apellidos comunes
            for apellido in self.search_methods['por_apellido']:
                try:
                    # Preparar datos del formulario
                    form_data = self.prepare_search_form_data(soup, 'apellido', apellido)
                    
                    if form_method == 'POST':
                        search_response = await session.post(form_action, data=form_data, timeout=30)
                    else:
                        search_response = await session.get(form_action, params=form_data, timeout=30)
                    
                    if search_response.status_code == 200:
                        profesionales = self.extract_professionals_from_search_results(
                            search_response.text, colegio_key, colegio_info, apellido
                        )
                        
                        if profesionales and len(profesionales) > 0:
                            await self.save_professionals(profesionales, colegio_key)
                            total_found += len(profesionales)
                            logger.info(f"🔎 Búsqueda '{apellido}': {len(profesionales)} profesionales")
                    
                    await asyncio.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    continue
            
            return total_found
            
        except Exception as e:
            logger.error(f"❌ Error búsquedas sistemáticas: {e}")
            return 0
    
    async def extract_by_numero_colegiado(self, session, colegio_key: str, colegio_info: Dict) -> int:
        """Extraer por rangos de números de colegiado"""
        logger.info(f"🔢 Extrayendo por números de colegiado: {colegio_info['nombre']}")
        
        try:
            extracted_count = 0
            verificacion_url = f"{colegio_info['url']}{colegio_info['verificacion_url']}"
            
            # Probar rangos de números
            for numero_base in self.search_methods['por_numero_colegiado'][:50]:  # Limitar a 50 rangos
                try:
                    # Generar números en el rango
                    numeros_a_probar = [
                        f"{numero_base}",
                        f"{colegio_info['codigo']}{numero_base}",
                        f"{numero_base:04d}",  # Con ceros a la izquierda
                        f"{colegio_info['codigo']}{numero_base:04d}"
                    ]
                    
                    for numero in numeros_a_probar:
                        try:
                            # Construir URL de consulta directa
                            consulta_urls = [
                                f"{verificacion_url}?numero={numero}",
                                f"{verificacion_url}?colegiado={numero}",
                                f"{colegio_info['url']}/consulta/{numero}",
                                f"{colegio_info['url']}/profesional/{numero}"
                            ]
                            
                            for consulta_url in consulta_urls:
                                try:
                                    response = await session.get(consulta_url, timeout=20)
                                    
                                    if response.status_code == 200 and len(response.text) > 500:
                                        profesional = self.extract_professional_from_profile(
                                            response.text, colegio_key, colegio_info, numero
                                        )
                                        
                                        if profesional:
                                            await self.save_professionals([profesional], colegio_key)
                                            extracted_count += 1
                                            self.stats['numeros_colegiado_encontrados'] += 1
                                            logger.info(f"👨‍⚕️ Encontrado profesional #{numero}")
                                            break  # URL exitosa
                                
                                except Exception as e:
                                    continue
                            
                            await asyncio.sleep(0.5)
                            
                        except Exception as e:
                            continue
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    continue
            
            return extracted_count
            
        except Exception as e:
            logger.error(f"❌ Error números colegiado {colegio_key}: {e}")
            return 0
    
    async def extract_by_cedulas_conocidas(self, session, colegio_key: str, colegio_info: Dict) -> int:
        """Extraer usando cédulas conocidas"""
        logger.info(f"🆔 Extrayendo por cédulas conocidas: {colegio_info['nombre']}")
        
        try:
            extracted_count = 0
            cedulas_a_consultar = self.search_methods['por_cedula'][:500]  # Máximo 500
            
            for cedula in cedulas_a_consultar:
                try:
                    # URLs de consulta por cédula
                    consulta_urls = [
                        f"{colegio_info['url']}/verificacion?cedula={cedula}",
                        f"{colegio_info['url']}/consulta/{cedula}",
                        f"{colegio_info['url']}/buscar?id={cedula}",
                        f"{colegio_info['url']}/profesional/cedula/{cedula}"
                    ]
                    
                    for consulta_url in consulta_urls:
                        try:
                            response = await session.get(consulta_url, timeout=25)
                            
                            if response.status_code == 200:
                                # Verificar si es profesional colegiado
                                if self.is_professional_found_in_response(response.text, cedula):
                                    profesional = self.extract_professional_from_profile(
                                        response.text, colegio_key, colegio_info, cedula
                                    )
                                    
                                    if profesional:
                                        await self.save_professionals([profesional], colegio_key)
                                        extracted_count += 1
                                        logger.info(f"👤 Profesional encontrado: {cedula}")
                                        break
                        
                        except Exception as e:
                            continue
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    continue
            
            return extracted_count
            
        except Exception as e:
            logger.error(f"❌ Error cédulas conocidas {colegio_key}: {e}")
            return 0
    
    def extract_professionals_from_directory_page(self, html_content: str, colegio_key: str, colegio_info: Dict, url: str) -> List[Dict]:
        """Extraer profesionales de página de directorio"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            profesionales = []
            
            # Patrones comunes de directorios
            
            # 1. Tablas de profesionales
            tables = soup.find_all('table')
            for table in tables:
                table_professionals = self.extract_from_professional_table(table, colegio_key, colegio_info)
                profesionales.extend(table_professionals)
            
            # 2. Listas de profesionales
            lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'(professional|doctor|lawyer|engineer)', re.I))
            for ul in lists:
                list_professionals = self.extract_from_professional_list(ul, colegio_key, colegio_info)
                profesionales.extend(list_professionals)
            
            # 3. Divs/secciones de profesionales
            prof_sections = soup.find_all(['div', 'section'], class_=re.compile(r'(professional|member|colegiado)', re.I))
            for section in prof_sections:
                section_professionals = self.extract_from_professional_section(section, colegio_key, colegio_info)
                profesionales.extend(section_professionals)
            
            # 4. Cards de profesionales
            prof_cards = soup.find_all(['div', 'article'], class_=re.compile(r'(card|profile|bio)', re.I))
            for card in prof_cards:
                card_professional = self.extract_from_professional_card(card, colegio_key, colegio_info)
                if card_professional:
                    profesionales.append(card_professional)
            
            return profesionales
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo directorio: {e}")
            return []
    
    def extract_from_professional_table(self, table, colegio_key: str, colegio_info: Dict) -> List[Dict]:
        """Extraer profesionales de tabla"""
        try:
            profesionales = []
            rows = table.find_all('tr')
            
            if len(rows) < 2:
                return profesionales
            
            # Headers
            header_row = rows[0]
            headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
            
            for row in rows[1:]:
                cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                
                if len(cells) < 2:
                    continue
                
                profesional = {
                    'id': str(uuid.uuid4()),
                    'colegio_profesional': colegio_info['nombre'],
                    'codigo_colegio': colegio_info['codigo'],
                    'categoria': colegio_key,
                    'fuente_extraccion': 'tabla_directorio',
                    'fecha_extraccion': datetime.utcnow()
                }
                
                # Mapear headers a campos
                for i, header in enumerate(headers):
                    if i < len(cells) and cells[i]:
                        if 'nombre' in header or 'name' in header:
                            profesional['nombre_completo'] = cells[i]
                        elif 'numero' in header or 'colegiado' in header:
                            profesional['numero_colegiado'] = cells[i]
                        elif 'especialidad' in header or 'specialty' in header:
                            profesional['especialidad'] = cells[i]
                        elif 'cedula' in header or 'id' in header:
                            profesional['cedula'] = cells[i]
                        elif 'telefono' in header or 'phone' in header:
                            profesional['telefono'] = cells[i]
                        elif 'email' in header or 'correo' in header:
                            profesional['email'] = cells[i]
                        else:
                            profesional[f'campo_{header}'] = cells[i]
                
                # Extraer patrones adicionales
                all_text = ' '.join(cells)
                patterns = self.extract_professional_patterns(all_text)
                profesional.update(patterns)
                
                if profesional.get('nombre_completo') or profesional.get('numero_colegiado'):
                    profesionales.append(profesional)
            
            return profesionales
            
        except Exception as e:
            logger.error(f"❌ Error tabla profesionales: {e}")
            return []
    
    def extract_from_professional_list(self, ul, colegio_key: str, colegio_info: Dict) -> List[Dict]:
        """Extraer profesionales de lista"""
        try:
            profesionales = []
            items = ul.find_all('li')
            
            for item in items:
                text = item.get_text().strip()
                
                if len(text) < 10:  # Muy corto para ser profesional
                    continue
                
                profesional = {
                    'id': str(uuid.uuid4()),
                    'colegio_profesional': colegio_info['nombre'],
                    'codigo_colegio': colegio_info['codigo'],
                    'categoria': colegio_key,
                    'fuente_extraccion': 'lista_directorio',
                    'fecha_extraccion': datetime.utcnow(),
                    'texto_original': text
                }
                
                # Parsear formato común: "Dr. Juan Pérez - Cardiólogo - #1234"
                parts = text.split(' - ')
                if len(parts) >= 2:
                    profesional['nombre_completo'] = parts[0].strip()
                    if len(parts) >= 3:
                        profesional['especialidad'] = parts[1].strip()
                        if parts[2].strip().startswith('#'):
                            profesional['numero_colegiado'] = parts[2].strip()[1:]
                
                # Extraer patrones
                patterns = self.extract_professional_patterns(text)
                profesional.update(patterns)
                
                profesionales.append(profesional)
            
            return profesionales
            
        except Exception as e:
            logger.error(f"❌ Error lista profesionales: {e}")
            return []
    
    def extract_from_professional_section(self, section, colegio_key: str, colegio_info: Dict) -> List[Dict]:
        """Extraer profesionales de sección"""
        try:
            profesionales = []
            
            # Buscar nombres en headers
            headers = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for header in headers:
                text = header.get_text().strip()
                
                # Verificar si parece nombre de profesional
                if self.is_likely_professional_name(text):
                    profesional = {
                        'id': str(uuid.uuid4()),
                        'colegio_profesional': colegio_info['nombre'],
                        'codigo_colegio': colegio_info['codigo'],
                        'categoria': colegio_key,
                        'fuente_extraccion': 'seccion_directorio',
                        'fecha_extraccion': datetime.utcnow(),
                        'nombre_completo': text
                    }
                    
                    # Buscar información adicional en el contexto
                    context_text = section.get_text()
                    patterns = self.extract_professional_patterns(context_text)
                    profesional.update(patterns)
                    
                    profesionales.append(profesional)
            
            return profesionales
            
        except Exception as e:
            logger.error(f"❌ Error sección profesionales: {e}")
            return []
    
    def extract_from_professional_card(self, card, colegio_key: str, colegio_info: Dict) -> Optional[Dict]:
        """Extraer profesional de card/perfil"""
        try:
            text = card.get_text().strip()
            
            if len(text) < 20:
                return None
            
            profesional = {
                'id': str(uuid.uuid4()),
                'colegio_profesional': colegio_info['nombre'],
                'codigo_colegio': colegio_info['codigo'],
                'categoria': colegio_key,
                'fuente_extraccion': 'card_directorio',
                'fecha_extraccion': datetime.utcnow()
            }
            
            # Buscar nombre en elementos prominentes
            name_elements = card.find_all(['h1', 'h2', 'h3', 'strong', 'b'])
            for elem in name_elements:
                name_text = elem.get_text().strip()
                if self.is_likely_professional_name(name_text):
                    profesional['nombre_completo'] = name_text
                    break
            
            # Extraer patrones del texto completo
            patterns = self.extract_professional_patterns(text)
            profesional.update(patterns)
            
            if profesional.get('nombre_completo'):
                return profesional
            
            return None
            
        except Exception as e:
            return None
    
    def extract_professionals_from_search_results(self, html_content: str, colegio_key: str, colegio_info: Dict, search_term: str) -> List[Dict]:
        """Extraer profesionales de resultados de búsqueda"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            profesionales = []
            
            # Buscar tablas de resultados
            result_tables = soup.find_all('table')
            for table in result_tables:
                table_professionals = self.extract_from_professional_table(table, colegio_key, colegio_info)
                for prof in table_professionals:
                    prof['termino_busqueda'] = search_term
                profesionales.extend(table_professionals)
            
            # Buscar divs de resultados
            result_divs = soup.find_all(['div', 'section'], class_=re.compile(r'(result|professional|match)', re.I))
            for div in result_divs:
                div_professional = self.extract_from_professional_card(div, colegio_key, colegio_info)
                if div_professional:
                    div_professional['termino_busqueda'] = search_term
                    profesionales.append(div_professional)
            
            return profesionales
            
        except Exception as e:
            logger.error(f"❌ Error resultados búsqueda: {e}")
            return []
    
    def extract_professional_from_profile(self, html_content: str, colegio_key: str, colegio_info: Dict, identifier: str) -> Optional[Dict]:
        """Extraer profesional de página de perfil individual"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            profesional = {
                'id': str(uuid.uuid4()),
                'colegio_profesional': colegio_info['nombre'],
                'codigo_colegio': colegio_info['codigo'],
                'categoria': colegio_key,
                'fuente_extraccion': 'perfil_individual',
                'fecha_extraccion': datetime.utcnow(),
                'identificador_busqueda': identifier
            }
            
            # Extraer información específica de perfil
            
            # Nombre
            name_selectors = ['h1', 'h2', '.name', '.nombre', '.professional-name']
            for selector in name_selectors:
                elem = soup.select_one(selector)
                if elem:
                    nombre = elem.get_text().strip()
                    if self.is_likely_professional_name(nombre):
                        profesional['nombre_completo'] = nombre
                        break
            
            # Información estructurada
            info_sections = soup.find_all(['div', 'section', 'p'], class_=re.compile(r'(info|data|detail)', re.I))
            for section in info_sections:
                text = section.get_text()
                patterns = self.extract_professional_patterns(text)
                profesional.update(patterns)
            
            # Información de tablas de datos
            data_tables = soup.find_all('table')
            for table in data_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                    if len(cells) >= 2:
                        key = cells[0].lower()
                        value = cells[1]
                        
                        if 'numero' in key or 'colegiado' in key:
                            profesional['numero_colegiado'] = value
                        elif 'especialidad' in key:
                            profesional['especialidad'] = value
                        elif 'telefono' in key or 'tel' in key:
                            profesional['telefono'] = value
                        elif 'email' in key or 'correo' in key:
                            profesional['email'] = value
                        elif 'direccion' in key or 'consultorio' in key:
                            profesional['direccion_consultorio'] = value
                            self.stats['consultoros_direcciones_encontradas'] += 1
            
            # Verificar si encontramos información suficiente
            if profesional.get('nombre_completo') or profesional.get('numero_colegiado'):
                if profesional.get('especialidad'):
                    self.stats['especialidades_encontradas'] += 1
                return profesional
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error perfil profesional: {e}")
            return None
    
    def extract_professional_patterns(self, text: str) -> Dict:
        """Extraer patrones específicos de profesionales"""
        patterns_found = {}
        
        try:
            # Número de colegiado
            numero_match = self.patterns['numero_colegiado'].search(text)
            if numero_match:
                patterns_found['numero_colegiado'] = numero_match.group(1)
            
            # Cédula profesional
            cedula_matches = self.patterns['cedula_profesional'].findall(text)
            if cedula_matches:
                patterns_found['cedula'] = cedula_matches[0]
            
            # Especialidad
            especialidad_match = self.patterns['especialidad'].search(text)
            if especialidad_match:
                patterns_found['especialidad'] = especialidad_match.group(1).strip()
            
            # Consultorio
            consultorio_match = self.patterns['consultorio'].search(text)
            if consultorio_match:
                patterns_found['direccion_consultorio'] = consultorio_match.group(1).strip()
            
            # Teléfono consultorio
            telefono_match = self.patterns['telefono_consultorio'].search(text)
            if telefono_match:
                patterns_found['telefono'] = f"+506{telefono_match.group(1)}"
            
            # Email profesional
            email_matches = self.patterns['email_profesional'].findall(text)
            if email_matches:
                patterns_found['email'] = email_matches[0]
            
            # Horario de atención
            horario_match = self.patterns['horario_atencion'].search(text)
            if horario_match:
                patterns_found['horario_atencion'] = horario_match.group(1).strip()
        
        except Exception as e:
            logger.error(f"❌ Error extrayendo patrones: {e}")
        
        return patterns_found
    
    def is_likely_professional_name(self, text: str) -> bool:
        """Verificar si el texto parece nombre de profesional"""
        if not text or len(text) < 5:
            return False
        
        # Patrones que indican nombres de profesionales
        professional_patterns = [
            re.compile(r'^Dr\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+', re.IGNORECASE),
            re.compile(r'^Dra\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+', re.IGNORECASE),
            re.compile(r'^Ing\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+', re.IGNORECASE),
            re.compile(r'^Lic\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+', re.IGNORECASE),
            re.compile(r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+'),  # Tres nombres
            re.compile(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$')  # Dos nombres
        ]
        
        return any(pattern.match(text.strip()) for pattern in professional_patterns)
    
    def is_professional_found_in_response(self, html_content: str, cedula: str) -> bool:
        """Verificar si se encontró un profesional en la respuesta"""
        content_lower = html_content.lower()
        
        positive_indicators = [
            'colegiado activo', 'profesional encontrado', 'incorporado',
            'habilitado', 'vigente', 'activo', 'verificado'
        ]
        
        negative_indicators = [
            'no encontrado', 'no existe', 'no registrado', 'inactivo',
            'suspendido', 'no incorporado', 'error'
        ]
        
        # Si hay indicadores negativos, no es válido
        if any(neg in content_lower for neg in negative_indicators):
            return False
        
        # Si hay indicadores positivos o la cédula aparece en contexto profesional, es válido
        has_positive = any(pos in content_lower for pos in positive_indicators)
        has_cedula_context = cedula in html_content and len(html_content) > 500
        
        return has_positive or has_cedula_context
    
    def prepare_search_form_data(self, soup, field_type: str, search_value: str) -> Dict:
        """Preparar datos del formulario de búsqueda"""
        try:
            form_data = {}
            
            # Buscar form
            form = soup.find('form')
            if not form:
                return {'q': search_value}  # Fallback genérico
            
            # Obtener todos los inputs
            inputs = form.find_all('input')
            
            for input_elem in inputs:
                input_name = input_elem.get('name', '')
                input_type = input_elem.get('type', 'text')
                input_value = input_elem.get('value', '')
                
                if input_type == 'hidden':
                    form_data[input_name] = input_value
                elif field_type == 'apellido' and any(word in input_name.lower() for word in ['apellido', 'surname', 'lastname']):
                    form_data[input_name] = search_value
                elif field_type == 'nombre' and any(word in input_name.lower() for word in ['nombre', 'name', 'firstname']):
                    form_data[input_name] = search_value
                elif field_type == 'numero' and any(word in input_name.lower() for word in ['numero', 'number', 'colegiado']):
                    form_data[input_name] = search_value
                elif field_type == 'cedula' and any(word in input_name.lower() for word in ['cedula', 'id', 'identification']):
                    form_data[input_name] = search_value
            
            # Si no encontramos campos específicos, usar genéricos
            if not any(search_value in str(v) for v in form_data.values()):
                generic_fields = ['q', 'search', 'query', 'buscar', 'texto']
                for field in generic_fields:
                    form_data[field] = search_value
                    break
            
            return form_data
            
        except Exception as e:
            logger.error(f"❌ Error preparando formulario: {e}")
            return {'q': search_value}
    
    async def save_professionals(self, profesionales: List[Dict], colegio_key: str):
        """Guardar profesionales en BD"""
        try:
            if profesionales:
                collection_name = f'profesionales_{colegio_key}'
                await self.db[collection_name].insert_many(profesionales, ordered=False)
                
                # También guardar en colección general
                await self.db.profesionales_colegiados_cr.insert_many(profesionales, ordered=False)
                
                logger.info(f"💾 Guardados {len(profesionales)} profesionales de {colegio_key}")
        except Exception as e:
            logger.error(f"❌ Error guardando profesionales: {e}")
    
    async def generate_report(self):
        """Generar reporte de extracción"""
        try:
            # Contar totales en BD
            total_profesionales_bd = await self.db.profesionales_colegiados_cr.count_documents({})
            
            report = {
                'fecha_extraccion': datetime.utcnow(),
                'fuente': 'COLEGIOS_PROFESIONALES_COSTA_RICA',
                'extraccion_completada': True,
                'estadisticas_extraccion': self.stats,
                'totales_bd': {
                    'total_profesionales_bd': total_profesionales_bd
                },
                'cobertura_colegios': {
                    'total_colegios': len(self.colegios),
                    'colegios_procesados': self.stats['colegios_procesados'],
                    'metodos_extraccion': [
                        'Directorios públicos',
                        'Sistemas de verificación',
                        'Búsquedas por número de colegiado',
                        'Búsquedas por cédula conocida'
                    ]
                }
            }
            
            await self.db.colegios_profesionales_reports.insert_one(report)
            
            logger.info("📊 REPORTE COLEGIOS PROFESIONALES")
            logger.info(f"👨‍⚕️ Médicos: {self.stats['medicos_extraidos']}")
            logger.info(f"👨‍💼 Ingenieros: {self.stats['ingenieros_extraidos']}")
            logger.info(f"⚖️ Abogados: {self.stats['abogados_extraidos']}")
            logger.info(f"💊 Farmacéuticos: {self.stats['farmaceuticos_extraidos']}")
            logger.info(f"👩‍⚕️ Enfermeras: {self.stats['enfermeras_extraidas']}")
            logger.info(f"📊 Total: {self.stats['total_profesionales']}")
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
    
    async def close(self):
        """Cerrar conexiones"""
        if self.client:
            self.client.close()

async def run_colegios_profesionales_extraction():
    """Función principal"""
    extractor = ColegiosProfesionalesExtractor()
    
    try:
        if await extractor.initialize():
            result = await extractor.extract_all_data()
            return result
        else:
            return {'error': 'Falló la inicialización'}
    finally:
        await extractor.close()

if __name__ == "__main__":
    result = asyncio.run(run_colegios_profesionales_extraction())
    print(f"🎓 RESULTADO COLEGIOS PROFESIONALES: {result}")