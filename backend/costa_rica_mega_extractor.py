#!/usr/bin/env python3
"""
COSTA RICA MEGA EXTRACTOR - EXTRACCIÓN MASIVA DE MÚLTIPLES FUENTES
Extrae datos de TODAS las fuentes disponibles en Costa Rica:
- Páginas Amarillas y Directorios
- Portales de Empleo y CVs
- Ministerios y Datos Abiertos
- Colegios Profesionales
- Portal TSE y CCSS
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
import json
from datetime import datetime
import re
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class CostaRicaMegaExtractor:
    def __init__(self):
        self.session = None
        self.mongo_client = None
        self.db = None
        self.extracted_data = {
            'personas_fisicas': [],
            'personas_juridicas': [],
            'profesionales': [],
            'empleos': []
        }
        
        # URLs objetivo para extracción masiva
        self.target_sources = {
            'paginas_amarillas': [
                'https://www.yellowpages.cr',
                'https://yelu.cr',
                'https://cr.eldirectorio.co',
                'https://nexdu.com/cr',
                'https://es.cybo.com/costa-rica'
            ],
            'empleo': [
                'https://www.computrabajo.co.cr',
                'https://www.empleos.net/costa-rica',
                'https://cr.linkedin.com/jobs'
            ],
            'ministerios': [
                'https://datosabiertos.gob.go.cr',
                'https://www.tse.go.cr',
                'https://www.ccss.sa.cr',
                'https://www.hacienda.go.cr',
                'https://www.mtss.go.cr'
            ],
            'colegios_profesionales': [
                'https://www.colmedcr.com',
                'https://www.colabogcr.com', 
                'https://www.cfia.or.cr',
                'https://www.colegiofarmaceutico.cr'
            ]
        }
        
    async def initialize(self):
        """Inicializar sesión HTTP y conexión MongoDB"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        # Conectar a MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.mongo_client = AsyncIOMotorClient(mongo_url)
        self.db = self.mongo_client[os.environ.get('DB_NAME', 'tudatos_sistema')]
        
        logger.info("🚀 CostaRicaMegaExtractor inicializado")
        
    async def extract_paginas_amarillas(self):
        """Extrae datos de páginas amarillas y directorios"""
        logger.info("📞 EXTRAYENDO PÁGINAS AMARILLAS Y DIRECTORIOS...")
        
        extracted_count = 0
        
        for source in self.target_sources['paginas_amarillas']:
            try:
                logger.info(f"🔍 Procesando: {source}")
                
                async with self.session.get(source) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Buscar patrones comunes de contactos
                        phones = self.extract_phones(html)
                        emails = self.extract_emails(html)
                        names = self.extract_names(soup)
                        companies = self.extract_companies(soup)
                        
                        # Procesar datos encontrados
                        for i, phone in enumerate(phones[:50]):  # Limitar para evitar spam
                            if self.validate_cr_phone(phone):
                                person_data = {
                                    'id': str(uuid.uuid4()),
                                    'telefono': phone,
                                    'email': emails[i] if i < len(emails) else None,
                                    'nombre': names[i] if i < len(names) else f"Contacto {i+1}",
                                    'fuente': f'PAGINAS_AMARILLAS_{source.split("//")[1].split(".")[1].upper()}',
                                    'tipo_persona': 'fisica',
                                    'created_at': datetime.utcnow()
                                }
                                
                                self.extracted_data['personas_fisicas'].append(person_data)
                                extracted_count += 1
                        
                        # Procesar empresas
                        for i, company in enumerate(companies[:30]):
                            if len(company) > 3:
                                company_data = {
                                    'id': str(uuid.uuid4()),
                                    'nombre_comercial': company,
                                    'telefono': phones[i] if i < len(phones) else None,
                                    'email': emails[i] if i < len(emails) else None,
                                    'fuente': f'DIRECTORIO_{source.split("//")[1].split(".")[1].upper()}',
                                    'tipo_persona': 'juridica',
                                    'created_at': datetime.utcnow()
                                }
                                
                                self.extracted_data['personas_juridicas'].append(company_data)
                                extracted_count += 1
                                
                        logger.info(f"✅ {source}: {extracted_count} registros extraídos")
                        
            except Exception as e:
                logger.error(f"❌ Error en {source}: {e}")
                
        return extracted_count
        
    async def extract_employment_sites(self):
        """Extrae datos de portales de empleo y CVs"""
        logger.info("💼 EXTRAYENDO PORTALES DE EMPLEO Y CVS...")
        
        extracted_count = 0
        
        for source in self.target_sources['empleo']:
            try:
                logger.info(f"🔍 Procesando portal empleo: {source}")
                
                # Buscar páginas con perfiles y CVs
                search_paths = [
                    '/perfiles',
                    '/candidatos',
                    '/cv',
                    '/profesionales',
                    '/trabajos'
                ]
                
                for path in search_paths:
                    try:
                        url = f"{source}{path}"
                        async with self.session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extraer datos profesionales
                                phones = self.extract_phones(html)
                                emails = self.extract_emails(html)
                                names = self.extract_professional_names(soup)
                                skills = self.extract_skills(soup)
                                
                                for i, name in enumerate(names[:20]):
                                    if len(name) > 5:
                                        professional_data = {
                                            'id': str(uuid.uuid4()),
                                            'nombre': name,
                                            'telefono': phones[i] if i < len(phones) else None,
                                            'email': emails[i] if i < len(emails) else None,
                                            'habilidades': skills[i] if i < len(skills) else None,
                                            'fuente': f'EMPLEO_{source.split("//")[1].split(".")[1].upper()}',
                                            'tipo_persona': 'profesional',
                                            'created_at': datetime.utcnow()
                                        }
                                        
                                        self.extracted_data['profesionales'].append(professional_data)
                                        extracted_count += 1
                                        
                                logger.info(f"✅ {url}: datos profesionales extraídos")
                                
                    except Exception as e:
                        logger.debug(f"Path {path} no disponible en {source}")
                        
            except Exception as e:
                logger.error(f"❌ Error en portal empleo {source}: {e}")
                
        return extracted_count
        
    async def extract_government_data(self):
        """Extrae datos de ministerios y entidades gubernamentales"""
        logger.info("🏛️ EXTRAYENDO DATOS GUBERNAMENTALES...")
        
        extracted_count = 0
        
        for source in self.target_sources['ministerios']:
            try:
                logger.info(f"🔍 Procesando ministerio: {source}")
                
                # Buscar APIs y datos abiertos
                api_paths = [
                    '/api',
                    '/datos',
                    '/funcionarios',
                    '/directorio',
                    '/contactos',
                    '/transparencia'
                ]
                
                for path in api_paths:
                    try:
                        url = f"{source}{path}"
                        async with self.session.get(url) as response:
                            if response.status == 200:
                                content_type = response.headers.get('content-type', '')
                                
                                if 'json' in content_type:
                                    # Datos JSON estructurados
                                    data = await response.json()
                                    gov_count = await self.process_government_json(data, source)
                                    extracted_count += gov_count
                                    
                                else:
                                    # HTML con información de contacto
                                    html = await response.text()
                                    soup = BeautifulSoup(html, 'html.parser')
                                    
                                    phones = self.extract_phones(html)
                                    emails = self.extract_emails(html)
                                    names = self.extract_official_names(soup)
                                    
                                    for i, name in enumerate(names[:15]):
                                        if len(name) > 5:
                                            official_data = {
                                                'id': str(uuid.uuid4()),
                                                'nombre': name,
                                                'telefono': phones[i] if i < len(phones) else None,
                                                'email': emails[i] if i < len(emails) else None,
                                                'institucion': source.split("//")[1].split(".")[1].upper(),
                                                'fuente': f'MINISTERIO_{source.split("//")[1].split(".")[1].upper()}',
                                                'tipo_persona': 'funcionario',
                                                'created_at': datetime.utcnow()
                                            }
                                            
                                            self.extracted_data['personas_fisicas'].append(official_data)
                                            extracted_count += 1
                                            
                                logger.info(f"✅ {url}: datos gubernamentales procesados")
                                
                    except Exception as e:
                        logger.debug(f"Path {path} no disponible en {source}")
                        
            except Exception as e:
                logger.error(f"❌ Error en ministerio {source}: {e}")
                
        return extracted_count
        
    async def extract_professional_colleges(self):
        """Extrae datos de colegios profesionales"""
        logger.info("🎓 EXTRAYENDO COLEGIOS PROFESIONALES...")
        
        extracted_count = 0
        
        for source in self.target_sources['colegios_profesionales']:
            try:
                logger.info(f"🔍 Procesando colegio: {source}")
                
                college_paths = [
                    '/directorio',
                    '/colegiados',
                    '/miembros',
                    '/profesionales',
                    '/buscar'
                ]
                
                for path in college_paths:
                    try:
                        url = f"{source}{path}"
                        async with self.session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                phones = self.extract_phones(html)
                                emails = self.extract_emails(html)
                                names = self.extract_professional_names(soup)
                                specialties = self.extract_specialties(soup)
                                
                                for i, name in enumerate(names[:25]):
                                    if len(name) > 5:
                                        professional_data = {
                                            'id': str(uuid.uuid4()),
                                            'nombre': name,
                                            'telefono': phones[i] if i < len(phones) else None,
                                            'email': emails[i] if i < len(emails) else None,
                                            'especialidad': specialties[i] if i < len(specialties) else None,
                                            'colegio': source.split("//")[1].split(".")[0],
                                            'fuente': f'COLEGIO_{source.split("//")[1].split(".")[0].upper()}',
                                            'tipo_persona': 'profesional_colegiado',
                                            'created_at': datetime.utcnow()
                                        }
                                        
                                        self.extracted_data['profesionales'].append(professional_data)
                                        extracted_count += 1
                                        
                                logger.info(f"✅ {url}: profesionales colegiados extraídos")
                                
                    except Exception as e:
                        logger.debug(f"Path {path} no disponible en {source}")
                        
            except Exception as e:
                logger.error(f"❌ Error en colegio {source}: {e}")
                
        return extracted_count
        
    # Funciones utilitarias de extracción
    def extract_phones(self, html):
        """Extrae números telefónicos de Costa Rica"""
        phone_patterns = [
            r'\+506[\s-]?\d{4}[\s-]?\d{4}',
            r'506[\s-]?\d{4}[\s-]?\d{4}',
            r'\d{4}[\s-]?\d{4}',
            r'\(\+506\)[\s-]?\d{4}[\s-]?\d{4}'
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, html)
            phones.extend(matches)
            
        # Limpiar y validar teléfonos
        clean_phones = []
        for phone in phones:
            clean = re.sub(r'[^\d]', '', phone)
            if clean.startswith('506'):
                clean = clean[3:]
            if len(clean) == 8:
                clean_phones.append(f"+506{clean}")
                
        return list(set(clean_phones))  # Eliminar duplicados
        
    def extract_emails(self, html):
        """Extrae emails válidos"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, html)
        
        # Filtrar emails de Costa Rica o genéricos válidos
        cr_emails = []
        for email in emails:
            if any(domain in email.lower() for domain in ['.cr', '.com', '.net', '.org', 'gmail', 'hotmail', 'yahoo']):
                cr_emails.append(email)
                
        return list(set(cr_emails))
        
    def extract_names(self, soup):
        """Extrae nombres de personas"""
        name_selectors = [
            'h1', 'h2', 'h3', '.name', '.nombre', '.contact-name',
            '.person-name', '.full-name', '.employee-name'
        ]
        
        names = []
        for selector in name_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if self.is_likely_name(text):
                    names.append(text)
                    
        return list(set(names))
        
    def extract_companies(self, soup):
        """Extrae nombres de empresas"""
        company_selectors = [
            '.company', '.empresa', '.business-name', '.company-name',
            '.organization', '.corp', '.ltd', '.sa', '.srl'
        ]
        
        companies = []
        for selector in company_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 3 and len(text) < 100:
                    companies.append(text)
                    
        return list(set(companies))
        
    def extract_professional_names(self, soup):
        """Extrae nombres profesionales específicos"""
        prof_selectors = [
            '.professional', '.doctor', '.engineer', '.lawyer',
            '.profile-name', '.cv-name', '.candidate-name'
        ]
        
        names = []
        for selector in prof_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if self.is_likely_name(text):
                    names.append(text)
                    
        return list(set(names))
        
    def extract_skills(self, soup):
        """Extrae habilidades profesionales"""
        skill_selectors = [
            '.skills', '.habilidades', '.competencias', '.expertise'
        ]
        
        skills = []
        for selector in skill_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 3 and len(text) < 200:
                    skills.append(text)
                    
        return skills
        
    def extract_official_names(self, soup):
        """Extrae nombres de funcionarios oficiales"""
        official_selectors = [
            '.funcionario', '.official', '.director', '.jefe',
            '.coordinador', '.ministro', '.viceministro'
        ]
        
        names = []
        for selector in official_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if self.is_likely_name(text):
                    names.append(text)
                    
        return list(set(names))
        
    def extract_specialties(self, soup):
        """Extrae especialidades profesionales"""
        specialty_selectors = [
            '.specialty', '.especialidad', '.area', '.campo'
        ]
        
        specialties = []
        for selector in specialty_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 3 and len(text) < 100:
                    specialties.append(text)
                    
        return specialties
        
    def is_likely_name(self, text):
        """Verifica si un texto parece ser un nombre"""
        if len(text) < 5 or len(text) > 80:
            return False
            
        # Patrones de nombres comunes en Costa Rica
        name_patterns = [
            r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+',
            r'^Dr\.\s+[A-ZÁÉÍÓÚÑ]',
            r'^Dra\.\s+[A-ZÁÉÍÓÚÑ]',
            r'^Ing\.\s+[A-ZÁÉÍÓÚÑ]',
            r'^Lic\.\s+[A-ZÁÉÍÓÚÑ]'
        ]
        
        return any(re.match(pattern, text) for pattern in name_patterns)
        
    def validate_cr_phone(self, phone):
        """Valida que sea un teléfono de Costa Rica"""
        clean = re.sub(r'[^\d]', '', phone)
        if clean.startswith('506'):
            clean = clean[3:]
        return len(clean) == 8 and clean[0] in ['2', '4', '6', '7', '8']
        
    async def process_government_json(self, data, source):
        """Procesa datos JSON de APIs gubernamentales"""
        count = 0
        
        try:
            if isinstance(data, dict):
                # Buscar campos con información de personas
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value[:20]:  # Limitar cantidad
                            if isinstance(item, dict):
                                person_data = self.extract_person_from_json(item, source)
                                if person_data:
                                    self.extracted_data['personas_fisicas'].append(person_data)
                                    count += 1
                                    
        except Exception as e:
            logger.error(f"Error procesando JSON de {source}: {e}")
            
        return count
        
    def extract_person_from_json(self, json_item, source):
        """Extrae datos de persona de un JSON"""
        try:
            person_data = {
                'id': str(uuid.uuid4()),
                'fuente': f'API_{source.split("//")[1].split(".")[1].upper()}',
                'created_at': datetime.utcnow()
            }
            
            # Mapear campos comunes
            field_mapping = {
                'nombre': ['name', 'nombre', 'full_name', 'fullName'],
                'email': ['email', 'correo', 'mail'],
                'telefono': ['phone', 'telefono', 'tel', 'telephone'],
                'cedula': ['id', 'cedula', 'identification', 'dni']
            }
            
            for target_field, possible_fields in field_mapping.items():
                for field in possible_fields:
                    if field in json_item and json_item[field]:
                        person_data[target_field] = json_item[field]
                        break
                        
            # Solo retornar si tiene al menos nombre o teléfono
            if person_data.get('nombre') or person_data.get('telefono'):
                return person_data
                
        except Exception as e:
            logger.debug(f"Error extrayendo persona de JSON: {e}")
            
        return None
        
    async def save_to_database(self):
        """Guarda todos los datos extraídos a MongoDB"""
        logger.info("💾 GUARDANDO DATOS EN BASE DE DATOS...")
        
        saved_count = 0
        
        try:
            # Guardar personas físicas
            if self.extracted_data['personas_fisicas']:
                await self.db.personas_fisicas_mega.insert_many(self.extracted_data['personas_fisicas'])
                saved_count += len(self.extracted_data['personas_fisicas'])
                logger.info(f"✅ {len(self.extracted_data['personas_fisicas'])} personas físicas guardadas")
                
            # Guardar personas jurídicas
            if self.extracted_data['personas_juridicas']:
                await self.db.personas_juridicas_mega.insert_many(self.extracted_data['personas_juridicas'])
                saved_count += len(self.extracted_data['personas_juridicas'])
                logger.info(f"✅ {len(self.extracted_data['personas_juridicas'])} personas jurídicas guardadas")
                
            # Guardar profesionales
            if self.extracted_data['profesionales']:
                await self.db.profesionales_cr.insert_many(self.extracted_data['profesionales'])
                saved_count += len(self.extracted_data['profesionales'])
                logger.info(f"✅ {len(self.extracted_data['profesionales'])} profesionales guardados")
                
            # Crear estadísticas finales
            stats = {
                'id': str(uuid.uuid4()),
                'fecha_extraccion': datetime.utcnow(),
                'total_extraido': saved_count,
                'fuentes_procesadas': len(self.target_sources),
                'personas_fisicas': len(self.extracted_data['personas_fisicas']),
                'personas_juridicas': len(self.extracted_data['personas_juridicas']),
                'profesionales': len(self.extracted_data['profesionales']),
                'estado': 'COMPLETADO'
            }
            
            await self.db.mega_extraction_stats.insert_one(stats)
            
        except Exception as e:
            logger.error(f"❌ Error guardando en base de datos: {e}")
            
        return saved_count
        
    async def close(self):
        """Cerrar conexiones"""
        if self.session:
            await self.session.close()
        if self.mongo_client:
            self.mongo_client.close()
            
async def run_mega_extraction():
    """Función principal para ejecutar extracción masiva"""
    extractor = CostaRicaMegaExtractor()
    
    try:
        await extractor.initialize()
        
        logger.info("🚀 INICIANDO EXTRACCIÓN MASIVA DE COSTA RICA")
        logger.info("📋 FUENTES: Páginas Amarillas, Empleo, Ministerios, Colegios")
        
        total_extracted = 0
        
        # Ejecutar todas las extracciones
        total_extracted += await extractor.extract_paginas_amarillas()
        total_extracted += await extractor.extract_employment_sites()
        total_extracted += await extractor.extract_government_data()
        total_extracted += await extractor.extract_professional_colleges()
        
        # Guardar en base de datos
        saved_count = await extractor.save_to_database()
        
        logger.info(f"🎯 EXTRACCIÓN COMPLETADA")
        logger.info(f"📊 TOTAL EXTRAÍDO: {total_extracted} registros")
        logger.info(f"💾 TOTAL GUARDADO: {saved_count} registros")
        
        return {
            'success': True,
            'total_extracted': total_extracted,
            'total_saved': saved_count,
            'sources_processed': len(extractor.target_sources),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error en extracción masiva: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    finally:
        await extractor.close()

if __name__ == "__main__":
    result = asyncio.run(run_mega_extraction())
    print(f"RESULTADO: {result}")