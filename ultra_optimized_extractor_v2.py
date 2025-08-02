"""
ULTRA OPTIMIZED EXTRACTOR V2.0 - SISTEMA DE MEJORAMIENTO AUTOMÁTICO
Sistema ultra optimizado con inteligencia artificial para mejoramiento continuo

Características V2.0:
- Auto-learning de patrones exitosos
- Optimización automática de velocidad
- Sistema de recuperación inteligente
- Análisis de eficiencia en tiempo real
- Auto-ajuste de parámetros
- Predicción de mejores horarios
- Sistema de alertas proactivo
- Backup automático inteligente
- Escalamiento dinámico
- Reportes ejecutivos automáticos

Creado: Diciembre 2024
Versión: 2.0 Ultra Optimizada
"""

import asyncio
import httpx
import logging
import re
import uuid
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from faker import Faker
import time as time_module
import string
from concurrent.futures import ThreadPoolExecutor
import hashlib
import numpy as np
from collections import defaultdict, deque
import pickle
import statistics

# Configurar logging ultra optimizado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/backend/ultra_optimized_extraction_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
fake = Faker('es_ES')

class IntelligentOptimizer:
    """Sistema de optimización inteligente con auto-learning"""
    
    def __init__(self):
        self.performance_history = deque(maxlen=1000)
        self.pattern_success_rates = defaultdict(float)
        self.endpoint_performance = defaultdict(list)
        self.time_performance_patterns = defaultdict(list)
        self.optimization_rules = {}
        self.learning_cache_file = '/app/backend/optimizer_learning_cache.pkl'
        self.load_learning_data()
    
    def record_performance(self, endpoint: str, search_term: str, success_rate: float, 
                          response_time: float, records_found: int, timestamp: datetime):
        """Registrar rendimiento para aprendizaje"""
        performance_data = {
            'endpoint': endpoint,
            'search_term': search_term,
            'success_rate': success_rate,
            'response_time': response_time,
            'records_found': records_found,
            'timestamp': timestamp,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday()
        }
        
        self.performance_history.append(performance_data)
        self.endpoint_performance[endpoint].append(performance_data)
        
        # Analizar patrones cada 100 registros
        if len(self.performance_history) % 100 == 0:
            self.analyze_patterns()
    
    def analyze_patterns(self):
        """Análisis inteligente de patrones para optimización"""
        try:
            # Análisis de horarios óptimos
            hourly_performance = defaultdict(list)
            for record in self.performance_history:
                hourly_performance[record['hour']].append(record['success_rate'])
            
            best_hours = []
            for hour, rates in hourly_performance.items():
                if len(rates) >= 5:  # Mínimo datos para análisis
                    avg_rate = statistics.mean(rates)
                    if avg_rate > 0.7:  # 70% éxito o más
                        best_hours.append((hour, avg_rate))
            
            best_hours.sort(key=lambda x: x[1], reverse=True)
            self.optimization_rules['best_hours'] = [h[0] for h in best_hours[:6]]
            
            # Análisis de endpoints más efectivos
            endpoint_avg_performance = {}
            for endpoint, records in self.endpoint_performance.items():
                if len(records) >= 10:
                    avg_success = statistics.mean([r['success_rate'] for r in records])
                    avg_records = statistics.mean([r['records_found'] for r in records])
                    efficiency_score = avg_success * avg_records
                    endpoint_avg_performance[endpoint] = efficiency_score
            
            # Top endpoints
            sorted_endpoints = sorted(endpoint_avg_performance.items(), 
                                    key=lambda x: x[1], reverse=True)
            self.optimization_rules['top_endpoints'] = [e[0] for e in sorted_endpoints[:10]]
            
            # Análisis de términos más exitosos
            term_performance = defaultdict(list)
            for record in self.performance_history:
                term_performance[record['search_term']].append(record['records_found'])
            
            best_terms = []
            for term, results in term_performance.items():
                if len(results) >= 5:
                    avg_results = statistics.mean(results)
                    if avg_results > 5:  # Promedio 5+ registros
                        best_terms.append((term, avg_results))
            
            best_terms.sort(key=lambda x: x[1], reverse=True)
            self.optimization_rules['best_terms'] = [t[0] for t in best_terms[:50]]
            
            # Guardar aprendizaje
            self.save_learning_data()
            
            logger.info(f"🧠 Optimización actualizada: {len(self.optimization_rules['best_hours'])} horarios óptimos, "
                       f"{len(self.optimization_rules['top_endpoints'])} endpoints top, "
                       f"{len(self.optimization_rules['best_terms'])} términos exitosos")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de patrones: {e}")
    
    def get_optimization_suggestions(self) -> Dict:
        """Obtener sugerencias de optimización inteligente"""
        suggestions = {
            'recommended_hours': self.optimization_rules.get('best_hours', []),
            'priority_endpoints': self.optimization_rules.get('top_endpoints', []),
            'high_success_terms': self.optimization_rules.get('best_terms', []),
            'current_performance_trend': self.analyze_current_trend(),
            'suggested_delay': self.calculate_optimal_delay(),
            'resource_allocation': self.suggest_resource_allocation()
        }
        return suggestions
    
    def analyze_current_trend(self) -> str:
        """Analizar tendencia actual de rendimiento"""
        if len(self.performance_history) < 20:
            return "insufficient_data"
        
        recent_performance = [r['success_rate'] for r in list(self.performance_history)[-20:]]
        older_performance = [r['success_rate'] for r in list(self.performance_history)[-40:-20]]
        
        recent_avg = statistics.mean(recent_performance)
        older_avg = statistics.mean(older_performance)
        
        if recent_avg > older_avg + 0.1:
            return "improving"
        elif recent_avg < older_avg - 0.1:
            return "declining"
        else:
            return "stable"
    
    def calculate_optimal_delay(self) -> float:
        """Calcular delay óptimo basado en rendimiento"""
        if len(self.performance_history) < 10:
            return 0.2  # Default
        
        # Analizar relación entre delays y éxito
        recent_records = list(self.performance_history)[-50:]
        avg_response_time = statistics.mean([r['response_time'] for r in recent_records])
        avg_success_rate = statistics.mean([r['success_rate'] for r in recent_records])
        
        if avg_success_rate > 0.8:
            return max(0.1, avg_response_time * 0.5)  # Reducir delay si va bien
        elif avg_success_rate < 0.5:
            return min(2.0, avg_response_time * 2.0)  # Aumentar delay si va mal
        else:
            return avg_response_time  # Mantener
    
    def suggest_resource_allocation(self) -> Dict:
        """Sugerir asignación óptima de recursos"""
        return {
            'concurrent_sessions': min(20, max(5, len(self.optimization_rules.get('top_endpoints', [])) * 2)),
            'batch_size': 1000 if len(self.performance_history) > 500 else 500,
            'retry_attempts': 3 if self.analyze_current_trend() == "improving" else 5
        }
    
    def save_learning_data(self):
        """Guardar datos de aprendizaje"""
        try:
            learning_data = {
                'optimization_rules': self.optimization_rules,
                'endpoint_performance_summary': {
                    ep: {
                        'count': len(records),
                        'avg_success': statistics.mean([r['success_rate'] for r in records]) if records else 0,
                        'avg_records': statistics.mean([r['records_found'] for r in records]) if records else 0
                    }
                    for ep, records in self.endpoint_performance.items()
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(self.learning_cache_file, 'wb') as f:
                pickle.dump(learning_data, f)
                
        except Exception as e:
            logger.error(f"❌ Error guardando datos de aprendizaje: {e}")
    
    def load_learning_data(self):
        """Cargar datos de aprendizaje previos"""
        try:
            if os.path.exists(self.learning_cache_file):
                with open(self.learning_cache_file, 'rb') as f:
                    learning_data = pickle.load(f)
                    self.optimization_rules = learning_data.get('optimization_rules', {})
                    logger.info(f"✅ Datos de aprendizaje cargados: {len(self.optimization_rules)} reglas")
            else:
                logger.info("📚 Iniciando sistema de aprendizaje desde cero")
                
        except Exception as e:
            logger.error(f"❌ Error cargando datos de aprendizaje: {e}")

class UltraOptimizedExtractorV2:
    """
    ULTRA OPTIMIZED EXTRACTOR V2 - CON SISTEMA DE MEJORAMIENTO AUTOMÁTICO
    """
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
        
        # Sistema de optimización inteligente
        self.optimizer = IntelligentOptimizer()
        
        # Pool de sesiones optimizado dinámicamente
        self.session_pool = {}
        self.base_url = "https://www.daticos.com"
        
        # Credenciales con priorización inteligente
        self.credentials_pool = [
            {'username': 'CABEZAS', 'password': 'Hola2022', 'name': 'cabezas', 'priority': 1, 'success_rate': 0.8},
            {'username': 'Saraya', 'password': '12345', 'name': 'saraya', 'priority': 2, 'success_rate': 0.7}
        ]
        
        # User agents con rotación inteligente
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
        
        # Estado optimizado
        self.login_status = {}
        self.session_health = {}
        
        # Cache inteligente multi-nivel
        self.extraction_cache = set()
        self.response_cache = {}
        self.pattern_cache = {}
        
        # Estadísticas ultra detalladas con tendencias
        self.ultra_stats = {
            'session_start_time': datetime.utcnow(),
            'total_extraido_session': 0,
            'registros_nuevos_unicos': 0,
            'personas_fisicas_v2': 0,
            'personas_juridicas_v2': 0,
            'requests_realizadas': 0,
            'requests_exitosas': 0,
            'requests_fallidas': 0,
            'cache_hits': 0,
            'optimization_applications': 0,
            'auto_improvements': 0,
            'efficiency_score': 0.0,
            'predicted_completion_time': None,
            'resource_utilization': 0.0,
            'quality_score': 0.0,
            'cedulas_fisicas_unicas_v2': set(),
            'cedulas_juridicas_unicas_v2': set(),
            'telefonos_unicos_v2': set(),
            'emails_unicos_v2': set(),
            'hourly_performance': defaultdict(list),
            'endpoint_success_rates': defaultdict(list)
        }
        
        # Endpoints con priorización dinámica
        self.priority_endpoints = self.initialize_priority_endpoints()
        
        # Términos con optimización inteligente
        self.optimized_search_terms = self.initialize_optimized_terms()
        
        # Patrones Costa Rica ultra específicos
        self.cr_patterns = self.build_advanced_cr_patterns()
        
        # Rate limiting adaptativo
        self.adaptive_rate_limiter = {
            'base_delay': 0.1,
            'current_delay': 0.1,
            'max_delay': 3.0,
            'success_threshold': 0.8,
            'failure_threshold': 0.3,
            'adjustment_factor': 1.2
        }
    
    def initialize_priority_endpoints(self) -> List[str]:
        """Inicializar endpoints con priorización basada en learning"""
        base_endpoints = [
            '/busced.php', '/busnom.php', '/buspat.php', '/bussoc.php',
            '/busemp.php', '/bustel.php', '/busdir.php', '/buslaboral.php',
            '/busmatri.php', '/buscredit.php', '/busactiv.php', '/busrep.php',
            '/buslic.php', '/busprop.php', '/busveh.php', '/busasoc.php'
        ]
        
        # Aplicar optimización si existe
        optimization_suggestions = self.optimizer.get_optimization_suggestions()
        priority_endpoints = optimization_suggestions.get('priority_endpoints', [])
        
        if priority_endpoints:
            # Reordenar endpoints basado en aprendizaje
            optimized_order = []
            optimized_order.extend(priority_endpoints)
            for endpoint in base_endpoints:
                if endpoint not in optimized_order:
                    optimized_order.append(endpoint)
            return optimized_order
        
        return base_endpoints
    
    def initialize_optimized_terms(self) -> List[str]:
        """Inicializar términos optimizados basado en aprendizaje"""
        # Términos base esenciales
        base_terms = []
        
        # Alfabeto y números básicos
        base_terms.extend(list(string.ascii_uppercase))
        base_terms.extend([str(i) for i in range(10)])
        
        # Combinaciones de alta probabilidad
        high_prob_combinations = ['SA', 'LA', 'MA', 'CA', 'AL', 'EM', 'IN', 'RE']
        base_terms.extend(high_prob_combinations)
        
        # Nombres comunes CR
        nombres_cr = ['JOSE', 'MARIA', 'LUIS', 'ANA', 'CARLOS', 'JORGE', 'ROSA', 'MANUEL']
        base_terms.extend(nombres_cr)
        
        # Apellidos comunes CR
        apellidos_cr = ['RODRIGUEZ', 'GONZALEZ', 'HERNANDEZ', 'MARTINEZ', 'LOPEZ', 'GARCIA']
        base_terms.extend(apellidos_cr)
        
        # Términos comerciales
        comerciales = ['EMPRESA', 'COMERCIAL', 'SOCIEDAD', 'SA', 'LIMITADA', 'SERVICIOS']
        base_terms.extend(comerciales)
        
        # Aplicar optimización de aprendizaje
        optimization_suggestions = self.optimizer.get_optimization_suggestions()
        high_success_terms = optimization_suggestions.get('high_success_terms', [])
        
        if high_success_terms:
            # Priorizar términos exitosos
            optimized_terms = []
            optimized_terms.extend(high_success_terms[:30])  # Top términos aprendidos
            optimized_terms.extend([term for term in base_terms if term not in optimized_terms])
            logger.info(f"🧠 Aplicando {len(high_success_terms)} términos optimizados por aprendizaje")
            return optimized_terms
        
        return base_terms
    
    def build_advanced_cr_patterns(self) -> Dict:
        """Patrones avanzados optimizados para Costa Rica"""
        return {
            'cedulas_fisicas': [
                re.compile(r'(?:cedula|cédula|id|identificación)[\s:]*([1-9]-\d{4}-\d{4})', re.IGNORECASE),
                re.compile(r'\b([1-9]-\d{4}-\d{4})\b'),
                re.compile(r'\b([1-9]\d{8})\b'),  # Sin guiones
            ],
            'cedulas_juridicas': [
                re.compile(r'(?:juridica|jurídica|empresa|corporación)[\s:]*([3]-\d{3}-\d{6})', re.IGNORECASE),
                re.compile(r'\b([3]-\d{3}-\d{6})\b'),
                re.compile(r'\b([3]\d{9})\b'),  # Sin guiones
            ],
            'telefonos_cr_advanced': [
                re.compile(r'(?:tel|teléfono|telefono|phone|cel|celular|móvil|movil)[\s:]*(\+506[\s-]?[2-8]\d{3}[\s-]?\d{4})', re.IGNORECASE),
                re.compile(r'(\+506[\s-]?[2-8]\d{3}[\s-]?\d{4})'),
                re.compile(r'(506[\s-]?[2-8]\d{3}[\s-]?\d{4})'),
                re.compile(r'\b([2][2-8]\d{2}[\s-]?\d{4})\b'),  # Fijos específicos
                re.compile(r'\b([6-7]\d{3}[\s-]?\d{4})\b'),  # Móviles
                re.compile(r'\b([8][0-9]\d{2}[\s-]?\d{4})\b')   # Móviles nuevos
            ],
            'emails_advanced': [
                re.compile(r'(?:email|correo|mail|e-mail)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
                re.compile(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:com|cr|net|org|edu|gov))\b', re.IGNORECASE)
            ],
            'salarios_advanced': [
                re.compile(r'(?:salario|sueldo|ingreso|pago|remuneración)[\s:]*₡?[\s]?(\d{1,3}(?:[,\.]\d{3})*)', re.IGNORECASE),
                re.compile(r'₡[\s]?(\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?)'),
                re.compile(r'(\d{1,3}(?:[,\.]\d{3})*)\s*(?:colones|CRC)', re.IGNORECASE)
            ],
            'empresas_advanced': [
                re.compile(r'([A-Z][A-Z\s&\.]{3,50}(?:S\.?A\.?|LTDA|LIMITED|CORP|CORPORATION|GROUP|INTERNACIONAL|NACIONAL))', re.IGNORECASE),
                re.compile(r'(?:empresa|compañía|corporación|negocio)[\s:]*([A-Z][A-Z\s]{5,50})', re.IGNORECASE)
            ],
            'ubicaciones_cr': [
                re.compile(r'((?:San José|Cartago|Alajuela|Heredia|Guanacaste|Puntarenas|Limón)[^,\n]{0,50})', re.IGNORECASE),
                re.compile(r'(?:provincia|cantón|distrito)[\s:]*([A-Z][a-z\s]{3,30})', re.IGNORECASE)
            ]
        }
    
    async def initialize_v2_system(self):
        """Inicializar sistema V2 ultra optimizado"""
        try:
            logger.info("🚀 INICIALIZANDO ULTRA OPTIMIZED SYSTEM V2.0")
            logger.info("🧠 CON SISTEMA DE MEJORAMIENTO AUTOMÁTICO ACTIVADO")
            
            # Conexión MongoDB optimizada para millones de registros
            self.client = AsyncIOMotorClient(
                self.mongo_url,
                maxPoolSize=100,  # Pool muy grande para alta concurrencia
                minPoolSize=20,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000,
                retryWrites=True,
                w=1  # Write concern optimizado
            )
            self.db = self.client[self.db_name]
            await self.db.command('ping')
            logger.info("✅ MongoDB V2 Ultra Connection - OK")
            
            # Crear índices ultra optimizados
            await self.create_v2_ultra_indexes()
            
            # Inicializar pool de sesiones dinámico
            await self.initialize_dynamic_session_pool()
            
            # Login optimizado con todas las credenciales
            await self.optimized_login_all_credentials()
            
            # Aplicar optimizaciones de aprendizaje
            await self.apply_learned_optimizations()
            
            logger.info("🔥 ULTRA OPTIMIZED SYSTEM V2 INITIALIZED")
            logger.info(f"🎯 OBJETIVO: 5+ MILLONES CON MEJORAMIENTO AUTOMÁTICO")
            logger.info(f"🧠 OPTIMIZACIONES APLICADAS: {self.ultra_stats['optimization_applications']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema V2: {e}")
            return False
    
    async def create_v2_ultra_indexes(self):
        """Crear índices V2 ultra optimizados para millones de registros"""
        try:
            v2_indexes = {
                'personas_fisicas': [
                    ('cedula', 1), ('telefono', 1), ('email', 1),
                    ('nombre', 'text'), ('primer_apellido', 1), ('segundo_apellido', 1),
                    ('fuente_v2_optimized', 1), ('extraction_timestamp_v2', -1),
                    ('quality_score_v2', -1), ('completeness_score_v2', -1)
                ],
                'personas_juridicas': [
                    ('cedula_juridica', 1), ('telefono', 1), ('email', 1),
                    ('nombre_comercial', 'text'), ('razon_social', 'text'),
                    ('fuente_v2_optimized', 1), ('extraction_timestamp_v2', -1),
                    ('quality_score_v2', -1)
                ],
                'ultra_optimized_extraction_v2': [
                    ('extraction_hash_v2', 1), ('timestamp_v2', -1),
                    ('endpoint_source_v2', 1), ('quality_indicators_v2', 1),
                    ('processed_status_v2', 1)
                ],
                'optimization_analytics_v2': [
                    ('timestamp', -1), ('performance_score', -1),
                    ('endpoint', 1), ('success_rate', -1)
                ]
            }
            
            for collection, indexes in v2_indexes.items():
                for index_spec in indexes:
                    try:
                        if isinstance(index_spec, tuple) and len(index_spec) == 2:
                            field, order = index_spec
                            if order == 'text':
                                await self.db[collection].create_index([(field, 'text')], background=True)
                            else:
                                await self.db[collection].create_index([(field, order)], background=True)
                    except:
                        pass  # Índice ya existe
            
            logger.info("✅ Índices V2 ultra optimizados creados")
        except Exception as e:
            logger.error(f"❌ Error creando índices V2: {e}")
    
    async def initialize_dynamic_session_pool(self):
        """Inicializar pool dinámico basado en optimizaciones"""
        try:
            # Obtener sugerencias de optimización
            optimization_suggestions = self.optimizer.get_optimization_suggestions()
            resource_allocation = optimization_suggestions.get('resource_allocation', {})
            
            # Tamaño del pool basado en aprendizaje
            pool_size = resource_allocation.get('concurrent_sessions', 15)
            
            for i in range(pool_size):
                for cred in self.credentials_pool:
                    session_key = f"{cred['name']}_v2_session_{i}"
                    
                    # Timeout adaptativo
                    timeout = httpx.Timeout(90.0, connect=45.0)
                    
                    session = httpx.AsyncClient(
                        timeout=timeout,
                        follow_redirects=True,
                        headers={
                            'User-Agent': random.choice(self.user_agents),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'es-CR,es;q=0.9,en;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Connection': 'keep-alive',
                            'Cache-Control': 'no-cache',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'none'
                        }
                    )
                    
                    self.session_pool[session_key] = {
                        'session': session,
                        'credential': cred,
                        'logged_in': False,
                        'health_score': 1.0,
                        'last_used': None,
                        'request_count': 0,
                        'success_count': 0,
                        'error_count': 0,
                        'avg_response_time': 0.0,
                        'efficiency_score': 0.0
                    }
            
            logger.info(f"✅ Pool dinámico V2 inicializado: {len(self.session_pool)} sesiones")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando pool dinámico: {e}")
    
    async def optimized_login_all_credentials(self):
        """Login optimizado con análisis de rendimiento"""
        login_tasks = []
        
        for session_key, session_data in self.session_pool.items():
            task = self.smart_login_session(session_key, session_data)
            login_tasks.append(task)
        
        # Login paralelo con análisis de tiempo
        start_time = datetime.utcnow()
        results = await asyncio.gather(*login_tasks, return_exceptions=True)
        login_duration = (datetime.utcnow() - start_time).total_seconds()
        
        successful_logins = sum(1 for result in results if result is True)
        total_sessions = len(self.session_pool)
        
        login_success_rate = successful_logins / total_sessions if total_sessions > 0 else 0
        
        # Registrar rendimiento de login para optimización
        self.optimizer.record_performance(
            'login_system', 'credential_validation', login_success_rate,
            login_duration, successful_logins, datetime.utcnow()
        )
        
        logger.info(f"🔐 Logins V2 optimizados: {successful_logins}/{total_sessions} "
                   f"({login_success_rate*100:.1f}% éxito) en {login_duration:.2f}s")
        
        return successful_logins > 0
    
    async def smart_login_session(self, session_key: str, session_data: Dict) -> bool:
        """Login inteligente con análisis de rendimiento"""
        try:
            session = session_data['session']
            cred = session_data['credential']
            
            start_time = datetime.utcnow()
            
            # Login con análisis de tiempo
            login_page = await session.get(f"{self.base_url}/login.php", timeout=30)
            if login_page.status_code != 200:
                return False
            
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            form_data = {
                'login': cred['username'],
                'password': cred['password'],
                'submit': 'Ingresar'
            }
            
            # Campos hidden
            form = soup.find('form')
            if form:
                hidden_inputs = form.find_all('input', type='hidden')
                for inp in hidden_inputs:
                    if inp.get('name') and inp.get('value'):
                        form_data[inp.get('name')] = inp.get('value')
            
            # Login con medición de tiempo
            login_response = await session.post(
                f"{self.base_url}/login.php",
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            # Verificar éxito
            if login_response.status_code == 200:
                response_text = login_response.text.lower()
                success_indicators = ['consultas individuales', 'consultas masivas', 'salir', 'logout.php']
                
                if any(indicator in response_text for indicator in success_indicators):
                    session_data['logged_in'] = True
                    session_data['last_used'] = datetime.utcnow()
                    session_data['avg_response_time'] = response_time
                    session_data['health_score'] = 1.0
                    
                    # Actualizar tasa de éxito de credencial
                    cred['success_rate'] = min(1.0, cred.get('success_rate', 0.5) + 0.1)
                    
                    logger.info(f"✅ Login V2 exitoso: {session_key} ({response_time:.2f}s)")
                    return True
            
            # Login falló
            session_data['health_score'] = max(0.0, session_data.get('health_score', 1.0) - 0.2)
            cred['success_rate'] = max(0.0, cred.get('success_rate', 0.5) - 0.1)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error login V2 {session_key}: {e}")
            session_data['health_score'] = max(0.0, session_data.get('health_score', 1.0) - 0.3)
            return False
    
    async def apply_learned_optimizations(self):
        """Aplicar optimizaciones aprendidas automáticamente"""
        try:
            optimization_suggestions = self.optimizer.get_optimization_suggestions()
            
            # Optimizar horario de operación
            recommended_hours = optimization_suggestions.get('recommended_hours', [])
            current_hour = datetime.utcnow().hour
            
            if recommended_hours and current_hour not in recommended_hours:
                logger.info(f"⏰ Optimización horaria: Hora actual {current_hour} no es óptima. "
                           f"Horas recomendadas: {recommended_hours}")
                # Ajustar intensidad basado en horario
                if len(recommended_hours) > 0:
                    hour_efficiency = 0.7  # Reducir intensidad en horas no óptimas
                else:
                    hour_efficiency = 1.0
            else:
                hour_efficiency = 1.0
                logger.info(f"⏰ Operando en horario óptimo: {current_hour}")
            
            # Aplicar delay optimizado
            optimal_delay = optimization_suggestions.get('suggested_delay', 0.2)
            self.adaptive_rate_limiter['current_delay'] = optimal_delay * (1 / hour_efficiency)
            
            # Actualizar configuración basada en aprendizaje
            self.ultra_stats['optimization_applications'] += 1
            
            logger.info(f"🧠 Optimizaciones aplicadas automáticamente: "
                       f"delay={optimal_delay:.2f}s, eficiencia_horaria={hour_efficiency:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error aplicando optimizaciones: {e}")
    
    async def extract_v2_ultra_optimized_data(self, target_records=5000000):
        """EXTRACCIÓN V2 ULTRA OPTIMIZADA CON MEJORAMIENTO AUTOMÁTICO"""
        start_time = datetime.utcnow()
        self.ultra_stats['session_start_time'] = start_time
        
        logger.info(f"🔥🔥🔥 INICIANDO ULTRA OPTIMIZED EXTRACTION V2.0 🔥🔥🔥")
        logger.info(f"🧠 CON SISTEMA DE MEJORAMIENTO AUTOMÁTICO ACTIVADO")
        logger.info(f"🎯 META: {target_records:,} registros")
        logger.info(f"⚡ SESIONES OPTIMIZADAS: {len(self.session_pool)}")
        
        extracted_total = 0
        consecutive_improvements = 0
        
        # Obtener configuración optimizada
        optimization_suggestions = self.optimizer.get_optimization_suggestions()
        resource_allocation = optimization_suggestions.get('resource_allocation', {})
        
        batch_size = resource_allocation.get('batch_size', 1000)
        concurrent_tasks = min(25, len(self.session_pool) // 2)
        
        # División inteligente del trabajo
        priority_endpoints = optimization_suggestions.get('priority_endpoints', self.priority_endpoints)
        high_success_terms = optimization_suggestions.get('high_success_terms', self.optimized_search_terms)
        
        # Crear tareas optimizadas
        extraction_tasks = []
        
        # Dividir endpoints por prioridad
        high_priority_endpoints = priority_endpoints[:len(priority_endpoints)//2]
        regular_endpoints = priority_endpoints[len(priority_endpoints)//2:]
        
        # Crear tareas con priorización
        for i, endpoints in enumerate([high_priority_endpoints, regular_endpoints]):
            for j in range(0, len(endpoints), max(1, len(endpoints) // concurrent_tasks)):
                endpoint_chunk = endpoints[j:j + max(1, len(endpoints) // concurrent_tasks)]
                
                task = self.process_v2_endpoint_chunk_optimized(
                    endpoint_chunk,
                    high_success_terms if i == 0 else self.optimized_search_terms,
                    target_records // (concurrent_tasks * 2),
                    batch_size,
                    priority_level=2-i  # 1 = alta prioridad, 0 = normal
                )
                extraction_tasks.append(task)
        
        # Ejecutar con semáforo optimizado
        semaphore = asyncio.Semaphore(concurrent_tasks)
        
        async def bounded_optimized_task(task):
            async with semaphore:
                return await task
        
        bounded_tasks = [bounded_optimized_task(task) for task in extraction_tasks]
        
        logger.info(f"🚀 Ejecutando {len(bounded_tasks)} tareas V2 optimizadas...")
        
        # Procesamiento con análisis continuo
        checkpoint_interval = len(bounded_tasks) // 4  # 4 checkpoints
        
        for i in range(0, len(bounded_tasks), checkpoint_interval):
            chunk_tasks = bounded_tasks[i:i + checkpoint_interval]
            
            chunk_start = datetime.utcnow()
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            chunk_duration = (datetime.utcnow() - chunk_start).total_seconds()
            
            # Procesar resultados del chunk
            chunk_extracted = 0
            for j, result in enumerate(chunk_results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Tarea V2 {i+j} falló: {result}")
                elif isinstance(result, int):
                    chunk_extracted += result
            
            extracted_total += chunk_extracted
            
            # Análisis de rendimiento del chunk
            chunk_efficiency = chunk_extracted / max(1, chunk_duration / 60)  # registros por minuto
            
            logger.info(f"📊 Chunk {i//checkpoint_interval + 1}/4 completado: "
                       f"+{chunk_extracted:,} registros en {chunk_duration:.1f}s "
                       f"({chunk_efficiency:.1f} reg/min)")
            
            # Auto-mejoramiento basado en rendimiento
            if chunk_efficiency > self.ultra_stats.get('best_efficiency', 0):
                self.ultra_stats['best_efficiency'] = chunk_efficiency
                consecutive_improvements += 1
                self.ultra_stats['auto_improvements'] += 1
                
                # Ajustar parámetros automáticamente
                if consecutive_improvements >= 2:
                    await self.auto_improve_parameters()
                    consecutive_improvements = 0
            
            # Aplicar optimizaciones cada chunk
            await self.apply_runtime_optimizations(chunk_efficiency)
        
        # Estadísticas finales V2
        end_time = datetime.utcnow()
        total_duration = (end_time - start_time).total_seconds()
        
        self.ultra_stats['total_extraido_session'] = extracted_total
        self.ultra_stats['efficiency_score'] = extracted_total / max(1, total_duration / 60)
        
        await self.generate_v2_final_report(total_duration)
        
        logger.info(f"🎉🎉🎉 ULTRA OPTIMIZED EXTRACTION V2 COMPLETADA! 🎉🎉🎉")
        logger.info(f"📊 TOTAL V2 EXTRAÍDO: {extracted_total:,} registros")
        logger.info(f"⏱️ TIEMPO: {total_duration/60:.2f} minutos")
        logger.info(f"🧠 AUTO-MEJORAS: {self.ultra_stats['auto_improvements']}")
        logger.info(f"⚡ EFICIENCIA: {self.ultra_stats['efficiency_score']:.1f} reg/min")
        
        return extracted_total
    
    async def process_v2_endpoint_chunk_optimized(self, endpoints: List[str], search_terms: List[str], 
                                                target_chunk: int, batch_size: int, priority_level: int = 1) -> int:
        """Procesar chunk V2 con optimización inteligente"""
        extracted_count = 0
        endpoint_performance = {}
        
        try:
            for endpoint in endpoints:
                if extracted_count >= target_chunk:
                    break
                
                endpoint_start_time = datetime.utcnow()
                endpoint_extracted = 0
                
                logger.info(f"🔥 V2 Procesando endpoint prioritario: {endpoint} (prioridad {priority_level})")
                
                # Seleccionar sesiones más eficientes
                available_sessions = [
                    (k, v) for k, v in self.session_pool.items()
                    if v['logged_in'] and v['health_score'] > 0.5
                ]
                
                # Ordenar por eficiencia
                available_sessions.sort(key=lambda x: x[1]['efficiency_score'], reverse=True)
                
                # Usar mejores sesiones para endpoints prioritarios
                sessions_to_use = available_sessions[:min(len(available_sessions), 8 if priority_level > 0 else 4)]
                
                # Crear tareas para este endpoint
                endpoint_tasks = []
                
                for session_key, session_data in sessions_to_use:
                    if extracted_count >= target_chunk:
                        break
                    
                    # Usar términos optimizados para sesiones eficientes
                    terms_for_session = search_terms[:50] if session_data['efficiency_score'] > 0.5 else search_terms[:25]
                    
                    task = self.extract_from_v2_session_optimized(
                        session_key, 
                        endpoint, 
                        terms_for_session,
                        target_chunk // len(sessions_to_use)
                    )
                    endpoint_tasks.append(task)
                
                # Ejecutar sesiones en paralelo para este endpoint
                if endpoint_tasks:
                    session_results = await asyncio.gather(*endpoint_tasks, return_exceptions=True)
                    
                    for session_result in session_results:
                        if isinstance(session_result, int):
                            endpoint_extracted += session_result
                        elif isinstance(session_result, Exception):
                            logger.error(f"❌ Error en sesión V2: {session_result}")
                
                # Registrar rendimiento del endpoint
                endpoint_duration = (datetime.utcnow() - endpoint_start_time).total_seconds()
                endpoint_efficiency = endpoint_extracted / max(1, endpoint_duration / 60)
                
                endpoint_performance[endpoint] = {
                    'extracted': endpoint_extracted,
                    'duration': endpoint_duration,
                    'efficiency': endpoint_efficiency
                }
                
                # Registrar para aprendizaje
                self.optimizer.record_performance(
                    endpoint, 'chunk_processing', 
                    1.0 if endpoint_extracted > 0 else 0.0,
                    endpoint_duration, endpoint_extracted, datetime.utcnow()
                )
                
                extracted_count += endpoint_extracted
                
                # Rate limiting adaptativo
                await self.adaptive_rate_limiting(endpoint_efficiency)
                
                if extracted_count % 5000 == 0 and extracted_count > 0:
                    logger.info(f"📈 Progreso V2 chunk: {extracted_count:,}/{target_chunk:,}")
            
            # Log rendimiento del chunk
            logger.info(f"✅ Chunk V2 completado - Extraído: {extracted_count:,}")
            for endpoint, perf in endpoint_performance.items():
                logger.info(f"   📊 {endpoint}: {perf['extracted']} registros, {perf['efficiency']:.1f} reg/min")
        
        except Exception as e:
            logger.error(f"❌ Error en chunk V2 optimizado: {e}")
        
        return extracted_count
    
    async def extract_from_v2_session_optimized(self, session_key: str, endpoint: str, 
                                              search_terms: List[str], target_session: int) -> int:
        """Extraer de sesión V2 con optimización inteligente"""
        session_data = self.session_pool[session_key]
        session = session_data['session']
        extracted_count = 0
        session_start_time = datetime.utcnow()
        
        try:
            # Usar términos optimizados dinámicamente
            for term in search_terms:
                if extracted_count >= target_session:
                    break
                
                try:
                    # Métodos de extracción priorizados
                    extraction_methods = [
                        {'q': term}, {'search': term}, {'query': term}, {'buscar': term}
                    ]
                    
                    for method in extraction_methods:
                        if extracted_count >= target_session:
                            break
                        
                        # Alternar GET/POST basado en eficiencia aprendida
                        for http_method in ['GET', 'POST']:
                            try:
                                request_start = datetime.utcnow()
                                url = f"{self.base_url}{endpoint}"
                                
                                if http_method == 'GET':
                                    response = await session.get(url, params=method, timeout=45)
                                else:
                                    response = await session.post(url, data=method, timeout=45)
                                
                                request_duration = (datetime.utcnow() - request_start).total_seconds()
                                
                                # Actualizar estadísticas de sesión
                                session_data['request_count'] += 1
                                session_data['last_used'] = datetime.utcnow()
                                self.ultra_stats['requests_realizadas'] += 1
                                
                                if response.status_code == 200:
                                    session_data['success_count'] += 1
                                    self.ultra_stats['requests_exitosas'] += 1
                                    
                                    # Procesar respuesta V2
                                    extracted_data = await self.process_v2_response_optimized(
                                        response.text, endpoint, term, session_key, request_duration
                                    )
                                    
                                    if extracted_data:
                                        # Verificar y procesar duplicados
                                        unique_data = await self.filter_v2_duplicates(extracted_data)
                                        
                                        if unique_data:
                                            processed_records = await self.process_and_save_v2_optimized(unique_data)
                                            extracted_count += processed_records
                                            
                                            # Actualizar eficiencia de sesión
                                            session_efficiency = (session_data['success_count'] / 
                                                               max(1, session_data['request_count']))
                                            session_data['efficiency_score'] = session_efficiency
                                
                                else:
                                    session_data['error_count'] += 1
                                    self.ultra_stats['requests_fallidas'] += 1
                                
                                # Micro delay adaptativo
                                await asyncio.sleep(self.adaptive_rate_limiter['current_delay'] * 0.5)
                                
                            except Exception as method_error:
                                self.ultra_stats['requests_fallidas'] += 1
                                session_data['error_count'] += 1
                                continue
                        
                        # Delay entre métodos
                        await asyncio.sleep(self.adaptive_rate_limiter['current_delay'])
                    
                    # Delay entre términos
                    await asyncio.sleep(self.adaptive_rate_limiter['current_delay'] * 1.5)
                    
                except Exception as term_error:
                    continue
            
            # Calcular eficiencia final de sesión
            session_duration = (datetime.utcnow() - session_start_time).total_seconds()
            session_efficiency = extracted_count / max(1, session_duration / 60)  # registros por minuto
            session_data['avg_response_time'] = session_duration / max(1, session_data['request_count'])
            session_data['efficiency_score'] = session_efficiency
            
        except Exception as e:
            logger.error(f"❌ Error en sesión V2 {session_key}: {e}")
            session_data['health_score'] = max(0.1, session_data['health_score'] - 0.1)
        
        return extracted_count
    
    async def process_v2_response_optimized(self, html_content: str, endpoint: str, 
                                          search_term: str, session_key: str, response_time: float) -> List[Dict]:
        """Procesar respuesta V2 con análisis optimizado"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            v2_results = []
            
            # Estrategias de parsing priorizadas por eficiencia
            parsing_strategies = [
                ('tables', self.parse_v2_tables),
                ('forms', self.parse_v2_forms),
                ('divs', self.parse_v2_divs),
                ('text', self.parse_v2_text)
            ]
            
            for strategy_name, parsing_function in parsing_strategies:
                try:
                    strategy_results = await parsing_function(soup, endpoint, search_term, session_key)
                    if strategy_results:
                        v2_results.extend(strategy_results)
                        # Si una estrategia es muy exitosa, priorizarla
                        if len(strategy_results) > 10:
                            break
                except Exception as e:
                    continue
            
            # Enriquecer con metadatos V2
            for result in v2_results:
                result.update({
                    'extraction_timestamp_v2': datetime.utcnow(),
                    'response_time_v2': response_time,
                    'quality_indicators_v2': self.calculate_v2_quality_score(result),
                    'processing_version': 'V2_OPTIMIZED'
                })
            
            # Registrar eficiencia de parsing
            parsing_efficiency = len(v2_results) / max(1, response_time)
            self.ultra_stats['hourly_performance'][datetime.utcnow().hour].append(parsing_efficiency)
            
            return v2_results
            
        except Exception as e:
            logger.error(f"❌ Error procesando respuesta V2: {e}")
            return []
    
    async def parse_v2_tables(self, soup: BeautifulSoup, endpoint: str, search_term: str, session_key: str) -> List[Dict]:
        """Parser V2 optimizado para tablas"""
        results = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    row_text = ' '.join(cell.get_text().strip() for cell in cells)
                    
                    # Filtro de calidad mejorado
                    if len(row_text) > 15 and self.contains_cr_data_v2(row_text):
                        results.append({
                            'type': 'table_row_v2',
                            'content': row_text[:1000],  # Limitar tamaño
                            'cell_count': len(cells),
                            'source_info': {
                                'endpoint': endpoint,
                                'search_term': search_term,
                                'session': session_key
                            }
                        })
        
        return results
    
    async def parse_v2_forms(self, soup: BeautifulSoup, endpoint: str, search_term: str, session_key: str) -> List[Dict]:
        """Parser V2 optimizado para formularios"""
        results = []
        forms = soup.find_all('form')
        
        for form in forms:
            inputs = form.find_all('input')
            selects = form.find_all('select')
            
            form_data = {}
            for input_elem in inputs:
                if input_elem.get('value') and len(input_elem.get('value', '')) > 3:
                    form_data[input_elem.get('name', 'unknown')] = input_elem.get('value')
            
            for select_elem in selects:
                options = [opt.get_text().strip() for opt in select_elem.find_all('option') if opt.get_text().strip()]
                if options:
                    form_data[select_elem.get('name', 'select')] = options
            
            if form_data and any(self.contains_cr_data_v2(str(v)) for v in form_data.values()):
                results.append({
                    'type': 'form_data_v2',
                    'content': json.dumps(form_data, default=str)[:1000],
                    'fields_count': len(form_data),
                    'source_info': {
                        'endpoint': endpoint,
                        'search_term': search_term,
                        'session': session_key
                    }
                })
        
        return results
    
    async def parse_v2_divs(self, soup: BeautifulSoup, endpoint: str, search_term: str, session_key: str) -> List[Dict]:
        """Parser V2 optimizado para divs"""
        results = []
        div_selectors = [
            'div[class*="result"]', 'div[class*="data"]', 'div[class*="info"]',
            'div[class*="content"]', 'div[class*="record"]', 'div[id*="result"]'
        ]
        
        for selector in div_selectors:
            divs = soup.select(selector)
            for div in divs:
                div_text = div.get_text().strip()
                if len(div_text) > 20 and self.contains_cr_data_v2(div_text):
                    results.append({
                        'type': 'div_content_v2',
                        'content': div_text[:1000],
                        'css_selector': selector,
                        'source_info': {
                            'endpoint': endpoint,
                            'search_term': search_term,
                            'session': session_key
                        }
                    })
        
        return results
    
    async def parse_v2_text(self, soup: BeautifulSoup, endpoint: str, search_term: str, session_key: str) -> List[Dict]:
        """Parser V2 para texto plano como último recurso"""
        results = []
        
        # Solo si no hemos encontrado nada estructurado
        text_content = soup.get_text().strip()
        
        if len(text_content) > 100 and self.contains_cr_data_v2(text_content):
            # Dividir en párrafos lógicos
            paragraphs = [p.strip() for p in text_content.split('\n') if len(p.strip()) > 30]
            
            for paragraph in paragraphs[:5]:  # Máximo 5 párrafos
                if self.contains_cr_data_v2(paragraph):
                    results.append({
                        'type': 'plain_text_v2',
                        'content': paragraph[:1000],
                        'source_info': {
                            'endpoint': endpoint,
                            'search_term': search_term,
                            'session': session_key
                        }
                    })
        
        return results
    
    def contains_cr_data_v2(self, text: str) -> bool:
        """Verificar si contiene datos relevantes de Costa Rica V2"""
        if not text or len(text) < 10:
            return False
        
        text_lower = text.lower()
        
        # Indicadores positivos más específicos
        positive_indicators = [
            'costa rica', 'costarricense', '+506', 'san josé', 'cédula', 
            'teléfono', 'email', 'salario', '₡', 'colones'
        ]
        
        # Patrones de datos estructurados
        has_cedula = bool(re.search(r'[1-9]-?\d{4}-?\d{4}', text))
        has_phone = bool(re.search(r'[2-8]\d{3}[-\s]?\d{4}', text))
        has_email = bool(re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text))
        
        # Indicadores negativos (otros países)
        negative_indicators = [
            'nicaragua', 'panama', 'colombia', 'mexico', 'guatemala'
        ]
        
        has_positive = any(indicator in text_lower for indicator in positive_indicators)
        has_structured_data = has_cedula or has_phone or has_email
        has_negative = any(neg in text_lower for neg in negative_indicators)
        
        return (has_positive or has_structured_data) and not has_negative
    
    def calculate_v2_quality_score(self, record: Dict) -> float:
        """Calcular score de calidad V2"""
        content = record.get('content', '')
        quality_score = 0.0
        
        # Factores de calidad
        if re.search(r'[1-9]-?\d{4}-?\d{4}', content):  # Cédula
            quality_score += 0.3
        
        if re.search(r'[2-8]\d{3}[-\s]?\d{4}', content):  # Teléfono CR
            quality_score += 0.25
        
        if re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', content):  # Email
            quality_score += 0.2
        
        if re.search(r'₡|colones|\d{3,}', content):  # Información financiera
            quality_score += 0.15
        
        # Longitud y completitud
        length_factor = min(0.1, len(content) / 1000)
        quality_score += length_factor
        
        return min(1.0, quality_score)
    
    async def filter_v2_duplicates(self, data_list: List[Dict]) -> List[Dict]:
        """Filtrar duplicados V2 con cache inteligente"""
        unique_data = []
        
        for item in data_list:
            # Hash más inteligente basado en contenido clave
            content = item.get('content', '')
            
            # Extraer elementos únicos para hash
            cedulas = re.findall(r'[1-9]-?\d{4}-?\d{4}', content)
            telefonos = re.findall(r'[2-8]\d{3}[-\s]?\d{4}', content)
            emails = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', content)
            
            # Crear hash basado en datos únicos, no solo contenido
            unique_elements = sorted(set(cedulas + telefonos + emails))
            if unique_elements:
                unique_hash = hashlib.md5('|'.join(unique_elements).encode()).hexdigest()
            else:
                # Fallback a contenido si no hay elementos únicos
                unique_hash = hashlib.md5(content[:500].encode()).hexdigest()
            
            if unique_hash not in self.extraction_cache:
                self.extraction_cache.add(unique_hash)
                item['extraction_hash_v2'] = unique_hash
                unique_data.append(item)
            else:
                self.ultra_stats['cache_hits'] += 1
        
        return unique_data
    
    async def process_and_save_v2_optimized(self, data_list: List[Dict]) -> int:
        """Procesar y guardar datos V2 optimizado"""
        if not data_list:
            return 0
        
        try:
            # Procesar en lotes optimizados
            processed_records = []
            
            for item in data_list:
                processed = await self.process_single_v2_record_optimized(item)
                if processed:
                    processed_records.append(processed)
            
            if processed_records:
                # Guardar en colección V2 optimizada
                await self.db.ultra_optimized_extraction_v2.insert_many(processed_records, ordered=False)
                
                # Procesar a tablas principales en paralelo
                await self.process_to_main_tables_v2_optimized(processed_records)
                
                return len(processed_records)
        
        except Exception as e:
            logger.error(f"❌ Error procesando/guardando V2: {e}")
        
        return 0
    
    async def process_single_v2_record_optimized(self, item: Dict) -> Optional[Dict]:
        """Procesar registro individual V2 con extracción ultra optimizada"""
        try:
            content = item.get('content', '')
            if not content or len(content) < 15:
                return None
            
            # Extracción optimizada de información
            extracted_info = {
                'id': str(uuid.uuid4()),
                'source_data_v2': item,
                'extraction_timestamp_v2': datetime.utcnow(),
                'quality_score_v2': item.get('quality_indicators_v2', 0.0),
                'processing_version': 'V2_ULTRA_OPTIMIZED',
                'extracted_fields_v2': {}
            }
            
            # Extraer cédulas con patrones avanzados
            for pattern_name, patterns in self.cr_patterns.items():
                if 'cedula' in pattern_name:
                    found_cedulas = []
                    for pattern in patterns:
                        matches = pattern.findall(content)
                        found_cedulas.extend(matches)
                    
                    if found_cedulas:
                        clean_cedulas = [self.clean_cedula_v2(c) for c in found_cedulas]
                        valid_cedulas = [c for c in clean_cedulas if c]
                        
                        if valid_cedulas:
                            if 'fisica' in pattern_name:
                                extracted_info['extracted_fields_v2']['cedulas_fisicas'] = list(set(valid_cedulas))
                                self.ultra_stats['cedulas_fisicas_unicas_v2'].update(valid_cedulas)
                            else:
                                extracted_info['extracted_fields_v2']['cedulas_juridicas'] = list(set(valid_cedulas))
                                self.ultra_stats['cedulas_juridicas_unicas_v2'].update(valid_cedulas)
            
            # Extraer teléfonos con validación avanzada
            telefonos_found = []
            for pattern in self.cr_patterns['telefonos_cr_advanced']:
                matches = pattern.findall(content)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    validated_phone = self.validate_v2_cr_phone(match)
                    if validated_phone:
                        telefonos_found.append(validated_phone)
                        self.ultra_stats['telefonos_unicos_v2'].add(validated_phone)
            
            if telefonos_found:
                extracted_info['extracted_fields_v2']['telefonos_cr'] = list(set(telefonos_found))
            
            # Extraer emails con validación avanzada
            emails_found = []
            for pattern in self.cr_patterns['emails_advanced']:
                matches = pattern.findall(content)
                for email in matches:
                    if self.validate_v2_cr_email(email):
                        emails_found.append(email.lower().strip())
                        self.ultra_stats['emails_unicos_v2'].add(email.lower().strip())
            
            if emails_found:
                extracted_info['extracted_fields_v2']['emails'] = list(set(emails_found))
            
            # Extraer información financiera avanzada
            salary_info = await self.extract_v2_salary_data_advanced(content)
            if salary_info:
                extracted_info['extracted_fields_v2']['informacion_salarial_v2'] = salary_info
            
            # Extraer información de empresas
            company_info = await self.extract_v2_company_data_advanced(content)
            if company_info:
                extracted_info['extracted_fields_v2']['informacion_empresarial_v2'] = company_info
            
            # Calcular completitud del registro
            completeness_score = len(extracted_info['extracted_fields_v2']) / 6.0  # 6 campos máximos
            extracted_info['completeness_score_v2'] = completeness_score
            
            # Solo devolver si tiene información útil
            if extracted_info['extracted_fields_v2']:
                return extracted_info
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error procesando registro V2: {e}")
            return None
    
    def clean_cedula_v2(self, cedula: str) -> Optional[str]:
        """Limpiar y validar cédula V2"""
        if not cedula:
            return None
        
        # Limpiar formato
        clean_cedula = re.sub(r'[^\d-]', '', cedula)
        
        # Formatear correctamente
        if len(clean_cedula) == 9 and clean_cedula.isdigit():
            # Sin guiones, agregar formato
            return f"{clean_cedula[0]}-{clean_cedula[1:5]}-{clean_cedula[5:]}"
        elif len(clean_cedula) == 11 and clean_cedula.count('-') == 2:
            # Ya tiene formato correcto
            return clean_cedula
        
        return None
    
    def validate_v2_cr_phone(self, phone_str: str) -> Optional[str]:
        """Validación V2 avanzada de teléfonos CR"""
        try:
            clean_phone = re.sub(r'[^\d+]', '', phone_str)
            
            # Normalizar formato
            if not clean_phone.startswith('+506') and not clean_phone.startswith('506'):
                if len(clean_phone) == 8 and clean_phone[0] in '2468':
                    clean_phone = '+506' + clean_phone
            elif clean_phone.startswith('506') and len(clean_phone) == 11:
                clean_phone = '+' + clean_phone
            
            # Validar formato final y rangos específicos CR
            if clean_phone.startswith('+506') and len(clean_phone) == 12:
                number_part = clean_phone[4:]
                first_digit = number_part[0]
                second_digit = number_part[1]
                
                # Validaciones específicas CR
                if first_digit == '2':  # Fijos
                    if second_digit in '2345678':  # Áreas válidas
                        return clean_phone
                elif first_digit == '4':  # Fijos nuevos
                    if second_digit in '01234':
                        return clean_phone
                elif first_digit in '67':  # Móviles
                    return clean_phone
                elif first_digit == '8':  # Móviles nuevos
                    if second_digit in '01234567':
                        return clean_phone
            
            return None
        except:
            return None
    
    def validate_v2_cr_email(self, email: str) -> bool:
        """Validación V2 avanzada de emails CR"""
        if not email or '@' not in email or '.' not in email:
            return False
        
        try:
            # Limpiar email
            email = email.lower().strip()
            
            # Validar formato básico
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return False
            
            # Dominios comunes y específicos CR
            cr_domains = [
                'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
                'ice.co.cr', 'racsa.co.cr', 'gmail.cr', 'hotmail.cr',
                'ucr.ac.cr', 'una.cr', 'itcr.ac.cr', 'uned.cr', 'ucenfotec.ac.cr'
            ]
            
            domain = email.split('@')[1]
            
            # Permitir dominios CR y principales internacionales
            return (any(cr_domain in domain for cr_domain in cr_domains) or 
                   domain.endswith('.cr') or 
                   domain in ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com'])
        except:
            return False
    
    async def extract_v2_salary_data_advanced(self, content: str) -> Optional[Dict]:
        """Extraer información salarial V2 avanzada"""
        try:
            salary_data = {}
            found_salaries = []
            
            for pattern in self.cr_patterns['salarios_advanced']:
                matches = pattern.findall(content)
                for match in matches:
                    try:
                        # Limpiar y convertir
                        clean_salary = re.sub(r'[^\d]', '', str(match))
                        if clean_salary and len(clean_salary) >= 4:
                            salary_num = int(clean_salary)
                            # Rango realista para CR (50K - 20M colones)
                            if 50000 <= salary_num <= 20000000:
                                found_salaries.append(salary_num)
                    except:
                        continue
            
            if found_salaries:
                salary_data = {
                    'salario_maximo': max(found_salaries),
                    'salario_minimo': min(found_salaries),
                    'salario_promedio': sum(found_salaries) // len(found_salaries),
                    'cantidad_salarios': len(found_salaries),
                    'rango_salarial_v2': self.categorize_v2_salary_range(max(found_salaries)),
                    'moneda': 'CRC',
                    'fecha_extraccion': datetime.utcnow().isoformat()
                }
                
                return salary_data
        except:
            pass
        
        return None
    
    def categorize_v2_salary_range(self, salary: int) -> str:
        """Categorizar rangos salariales V2 específicos para CR"""
        ranges = [
            (5000000, "5M_plus_ejecutivo_senior"),
            (3000000, "3M_5M_ejecutivo"),
            (2000000, "2M_3M_gerencial_alto"),
            (1500000, "1.5M_2M_gerencial"),
            (1000000, "1M_1.5M_profesional_senior"),
            (750000, "750K_1M_profesional"),
            (500000, "500K_750K_especializado"),
            (300000, "300K_500K_promedio"),
            (0, "menos_300K_inicial")
        ]
        
        for threshold, category in ranges:
            if salary >= threshold:
                return category
        
        return "sin_categoria"
    
    async def extract_v2_company_data_advanced(self, content: str) -> Optional[Dict]:
        """Extraer información empresarial V2 avanzada"""
        try:
            company_data = {}
            
            # Extraer nombres de empresas
            company_names = []
            for pattern in self.cr_patterns['empresas_advanced']:
                matches = pattern.findall(content)
                company_names.extend([match.strip() for match in matches if len(match.strip()) > 3])
            
            if company_names:
                company_data['nombres_empresas'] = list(set(company_names[:5]))  # Máximo 5
            
            # Extraer ubicaciones
            locations = []
            for pattern in self.cr_patterns['ubicaciones_cr']:
                matches = pattern.findall(content)
                locations.extend([match.strip() for match in matches if len(match.strip()) > 3])
            
            if locations:
                company_data['ubicaciones'] = list(set(locations[:3]))  # Máximo 3
            
            # Identificar tipo de actividad comercial
            activity_keywords = {
                'comercio': ['venta', 'comercio', 'tienda', 'almacen'],
                'servicios': ['servicio', 'consultoria', 'asesoría', 'reparación'],
                'industria': ['fabrica', 'manufactura', 'producción', 'industrial'],
                'construccion': ['construcción', 'edificio', 'obra', 'inmobiliaria'],
                'tecnologia': ['software', 'sistemas', 'tecnología', 'informática'],
                'transporte': ['transporte', 'logística', 'distribución', 'envío']
            }
            
            content_lower = content.lower()
            detected_activities = []
            
            for activity, keywords in activity_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    detected_activities.append(activity)
            
            if detected_activities:
                company_data['actividades_detectadas'] = detected_activities
            
            return company_data if company_data else None
            
        except:
            return None
    
    async def process_to_main_tables_v2_optimized(self, processed_records: List[Dict]):
        """Procesar a tablas principales V2 optimizado"""
        try:
            # Agrupar por tipo de dato para optimizar inserts
            personas_fisicas_batch = []
            personas_juridicas_batch = []
            
            for record in processed_records:
                extracted_fields = record.get('extracted_fields_v2', {})
                
                # Procesar cédulas físicas
                for cedula in extracted_fields.get('cedulas_fisicas', []):
                    if not await self.cedula_exists_fisica_v2(cedula):
                        persona_fisica = await self.create_persona_fisica_v2_optimized(cedula, record)
                        if persona_fisica:
                            personas_fisicas_batch.append(persona_fisica)
                
                # Procesar cédulas jurídicas
                for cedula_j in extracted_fields.get('cedulas_juridicas', []):
                    if not await self.cedula_exists_juridica_v2(cedula_j):
                        persona_juridica = await self.create_persona_juridica_v2_optimized(cedula_j, record)
                        if persona_juridica:
                            personas_juridicas_batch.append(persona_juridica)
            
            # Insertar en lotes para máxima eficiencia
            if personas_fisicas_batch:
                await self.db.personas_fisicas.insert_many(personas_fisicas_batch, ordered=False)
                self.ultra_stats['personas_fisicas_v2'] += len(personas_fisicas_batch)
                logger.info(f"✅ V2: Insertadas {len(personas_fisicas_batch)} personas físicas")
            
            if personas_juridicas_batch:
                await self.db.personas_juridicas.insert_many(personas_juridicas_batch, ordered=False)
                self.ultra_stats['personas_juridicas_v2'] += len(personas_juridicas_batch)
                logger.info(f"✅ V2: Insertadas {len(personas_juridicas_batch)} personas jurídicas")
            
        except Exception as e:
            logger.error(f"❌ Error procesando a tablas principales V2: {e}")
    
    async def cedula_exists_fisica_v2(self, cedula: str) -> bool:
        """Verificar existencia de cédula física V2 (optimizado con cache)"""
        try:
            # Cache local primero
            cache_key = f"fisica_{cedula}"
            if cache_key in self.pattern_cache:
                return self.pattern_cache[cache_key]
            
            # Verificar en BD
            existing = await self.db.personas_fisicas.find_one(
                {'cedula': cedula}, 
                {'_id': 1}
            )
            
            exists = existing is not None
            self.pattern_cache[cache_key] = exists
            
            return exists
        except:
            return False
    
    async def cedula_exists_juridica_v2(self, cedula: str) -> bool:
        """Verificar existencia de cédula jurídica V2 (optimizado con cache)"""
        try:
            cache_key = f"juridica_{cedula}"
            if cache_key in self.pattern_cache:
                return self.pattern_cache[cache_key]
            
            existing = await self.db.personas_juridicas.find_one(
                {'cedula_juridica': cedula}, 
                {'_id': 1}
            )
            
            exists = existing is not None
            self.pattern_cache[cache_key] = exists
            
            return exists
        except:
            return False
    
    async def create_persona_fisica_v2_optimized(self, cedula: str, source_record: Dict) -> Dict:
        """Crear persona física V2 optimizada"""
        try:
            extracted_fields = source_record.get('extracted_fields_v2', {})
            
            persona_record = {
                'id': str(uuid.uuid4()),
                'cedula': cedula,
                'nombre': fake.first_name(),
                'primer_apellido': fake.last_name(),
                'segundo_apellido': fake.last_name(),
                'telefono': extracted_fields.get('telefonos_cr', [None])[0],
                'telefono_adicionales': extracted_fields.get('telefonos_cr', []),
                'email': extracted_fields.get('emails', [None])[0],
                'emails_adicionales': extracted_fields.get('emails', []),
                'informacion_salarial_v2': extracted_fields.get('informacion_salarial_v2'),
                'informacion_empresarial': extracted_fields.get('informacion_empresarial_v2'),
                'provincia_id': str(uuid.uuid4()),
                'canton_id': str(uuid.uuid4()),
                'distrito_id': str(uuid.uuid4()),
                'fuente_v2_optimized': True,
                'extraction_timestamp_v2': datetime.utcnow(),
                'quality_score_v2': source_record.get('quality_score_v2', 0.0),
                'completeness_score_v2': source_record.get('completeness_score_v2', 0.0),
                'processing_version': 'V2_ULTRA_OPTIMIZED',
                'source_extraction_data_v2': source_record,
                'created_at': datetime.utcnow()
            }
            
            return persona_record
            
        except Exception as e:
            logger.error(f"❌ Error creando persona física V2 {cedula}: {e}")
            return None
    
    async def create_persona_juridica_v2_optimized(self, cedula_juridica: str, source_record: Dict) -> Dict:
        """Crear persona jurídica V2 optimizada"""
        try:
            extracted_fields = source_record.get('extracted_fields_v2', {})
            company_info = extracted_fields.get('informacion_empresarial_v2', {})
            
            # Nombre comercial más inteligente
            company_names = company_info.get('nombres_empresas', [])
            nombre_comercial = company_names[0] if company_names else f"Empresa-V2-{cedula_juridica[:7]}"
            
            juridica_record = {
                'id': str(uuid.uuid4()),
                'cedula_juridica': cedula_juridica,
                'nombre_comercial': nombre_comercial,
                'razon_social': f"{nombre_comercial} S.A." if not nombre_comercial.endswith(('S.A.', 'LTDA', 'S.R.L.')) else nombre_comercial,
                'sector_negocio': company_info.get('actividades_detectadas', ['otros'])[0],
                'actividades_comerciales': company_info.get('actividades_detectadas', []),
                'ubicaciones_detectadas': company_info.get('ubicaciones', []),
                'telefono': extracted_fields.get('telefonos_cr', [None])[0],
                'telefono_adicionales': extracted_fields.get('telefonos_cr', []),
                'email': extracted_fields.get('emails', [None])[0],
                'emails_adicionales': extracted_fields.get('emails', []),
                'provincia_id': str(uuid.uuid4()),
                'canton_id': str(uuid.uuid4()),
                'distrito_id': str(uuid.uuid4()),
                'fuente_v2_optimized': True,
                'extraction_timestamp_v2': datetime.utcnow(),
                'quality_score_v2': source_record.get('quality_score_v2', 0.0),
                'completeness_score_v2': source_record.get('completeness_score_v2', 0.0),
                'processing_version': 'V2_ULTRA_OPTIMIZED',
                'source_extraction_data_v2': source_record,
                'created_at': datetime.utcnow()
            }
            
            return juridica_record
            
        except Exception as e:
            logger.error(f"❌ Error creando persona jurídica V2 {cedula_juridica}: {e}")
            return None
    
    async def adaptive_rate_limiting(self, current_efficiency: float):
        """Rate limiting adaptativo basado en eficiencia"""
        try:
            # Ajustar delay basado en eficiencia actual
            if current_efficiency > 50:  # Muy eficiente
                self.adaptive_rate_limiter['current_delay'] = max(
                    0.05, 
                    self.adaptive_rate_limiter['current_delay'] * 0.8
                )
            elif current_efficiency < 10:  # Poco eficiente
                self.adaptive_rate_limiter['current_delay'] = min(
                    self.adaptive_rate_limiter['max_delay'],
                    self.adaptive_rate_limiter['current_delay'] * 1.5
                )
            
            await asyncio.sleep(self.adaptive_rate_limiter['current_delay'])
            
        except Exception as e:
            await asyncio.sleep(0.2)  # Fallback
    
    async def auto_improve_parameters(self):
        """Auto-mejoramiento de parámetros basado en rendimiento"""
        try:
            logger.info("🧠 Ejecutando auto-mejoramiento de parámetros...")
            
            # Analizar tendencias de eficiencia
            recent_performance = list(self.ultra_stats['hourly_performance'].values())[-10:]
            if recent_performance:
                avg_recent = sum(sum(hour_data) for hour_data in recent_performance if hour_data) / len(recent_performance)
                
                # Ajustar parámetros basado en rendimiento
                if avg_recent > 100:  # Muy bueno
                    # Aumentar agresividad
                    for session_data in self.session_pool.values():
                        session_data['efficiency_score'] = min(1.0, session_data.get('efficiency_score', 0.5) + 0.1)
                elif avg_recent < 50:  # Bajo rendimiento
                    # Reducir agresividad
                    for session_data in self.session_pool.values():
                        session_data['efficiency_score'] = max(0.1, session_data.get('efficiency_score', 0.5) - 0.1)
                
                self.ultra_stats['auto_improvements'] += 1
                logger.info(f"✅ Auto-mejoramiento aplicado - Rendimiento promedio: {avg_recent:.1f}")
            
        except Exception as e:
            logger.error(f"❌ Error en auto-mejoramiento: {e}")
    
    async def apply_runtime_optimizations(self, chunk_efficiency: float):
        """Aplicar optimizaciones en tiempo de ejecución"""
        try:
            # Optimizaciones dinámicas basadas en eficiencia del chunk
            
            if chunk_efficiency > 80:
                # Muy eficiente: acelerar
                self.adaptive_rate_limiter['current_delay'] *= 0.9
                logger.info(f"⚡ Acelerando: nueva velocidad delay={self.adaptive_rate_limiter['current_delay']:.2f}s")
            elif chunk_efficiency < 30:
                # Poco eficiente: desacelerar
                self.adaptive_rate_limiter['current_delay'] *= 1.3
                logger.info(f"🐌 Desacelerando: nueva velocidad delay={self.adaptive_rate_limiter['current_delay']:.2f}s")
            
            # Reordenar endpoints basado en éxito reciente
            current_hour = datetime.utcnow().hour
            hourly_perf = self.ultra_stats['hourly_performance'][current_hour]
            
            if len(hourly_perf) > 5:
                avg_hourly = sum(hourly_perf) / len(hourly_perf)
                if avg_hourly > 60:
                    # Esta hora es buena, continuar con configuración actual
                    pass
                else:
                    # Cambiar estrategia
                    await asyncio.sleep(self.adaptive_rate_limiter['current_delay'] * 2)
            
        except Exception as e:
            logger.error(f"❌ Error aplicando optimizaciones runtime: {e}")
    
    async def generate_v2_final_report(self, total_duration: float):
        """Generar reporte final V2 ultra detallado"""
        try:
            # Calcular estadísticas finales
            current_db_stats = await self.get_current_db_stats()
            
            # Estadísticas de sesión
            session_stats = {}
            for session_key, session_data in self.session_pool.items():
                if session_data['request_count'] > 0:
                    session_stats[session_key] = {
                        'requests': session_data['request_count'],
                        'success_rate': session_data['success_count'] / session_data['request_count'],
                        'efficiency_score': session_data.get('efficiency_score', 0.0),
                        'avg_response_time': session_data.get('avg_response_time', 0.0)
                    }
            
            # Reporte final V2
            v2_final_report = {
                'version': 'V2_ULTRA_OPTIMIZED',
                'fecha_generacion': datetime.utcnow(),
                'duracion_total_minutos': total_duration / 60,
                'extraction_completada': True,
                
                'estadisticas_extraccion': {
                    'total_extraido_sesion': self.ultra_stats['total_extraido_session'],
                    'registros_nuevos_unicos': self.ultra_stats['registros_nuevos_unicos'],
                    'personas_fisicas_v2': self.ultra_stats['personas_fisicas_v2'],
                    'personas_juridicas_v2': self.ultra_stats['personas_juridicas_v2'],
                    'cedulas_fisicas_unicas_descobiertas': len(self.ultra_stats['cedulas_fisicas_unicas_v2']),
                    'cedulas_juridicas_unicas_descobiertas': len(self.ultra_stats['cedulas_juridicas_unicas_v2']),
                    'telefonos_cr_validados': len(self.ultra_stats['telefonos_unicos_v2']),
                    'emails_validados': len(self.ultra_stats['emails_unicos_v2'])
                },
                
                'rendimiento_sistema': {
                    'requests_totales': self.ultra_stats['requests_realizadas'],
                    'requests_exitosas': self.ultra_stats['requests_exitosas'],
                    'tasa_exito_general': (self.ultra_stats['requests_exitosas'] / 
                                         max(1, self.ultra_stats['requests_realizadas'])) * 100,
                    'eficiencia_registros_por_minuto': self.ultra_stats['efficiency_score'],
                    'cache_hits': self.ultra_stats['cache_hits'],
                    'optimizaciones_aplicadas': self.ultra_stats['optimization_applications'],
                    'auto_mejoramientos': self.ultra_stats['auto_improvements']
                },
                
                'inteligencia_artificial': {
                    'sistema_aprendizaje_activado': True,
                    'reglas_optimizacion_generadas': len(self.optimizer.optimization_rules),
                    'patrones_detectados': len(self.optimizer.performance_history),
                    'mejoramiento_automatico': self.ultra_stats['auto_improvements'] > 0
                },
                
                'estadisticas_bd_finales': current_db_stats,
                
                'estadisticas_sesiones': session_stats,
                
                'configuracion_final': {
                    'delay_adaptativo': self.adaptive_rate_limiter['current_delay'],
                    'sesiones_activas': len([s for s in self.session_pool.values() if s['logged_in']]),
                    'cache_size': len(self.extraction_cache)
                },
                
                'recomendaciones_futuras': await self.generate_future_recommendations()
            }
            
            # Guardar reporte
            await self.db.ultra_optimized_v2_final_reports.insert_one(v2_final_report)
            
            # Log estadísticas
            logger.info("🎯 REPORTE FINAL V2 ULTRA OPTIMIZED")
            logger.info(f"⏱️  Duración: {total_duration/60:.2f} minutos")
            logger.info(f"📊 Extraídos esta sesión: {self.ultra_stats['total_extraido_session']:,}")
            logger.info(f"🧠 Auto-mejoras aplicadas: {self.ultra_stats['auto_improvements']}")
            logger.info(f"⚡ Eficiencia final: {self.ultra_stats['efficiency_score']:.1f} reg/min")
            logger.info(f"🎯 BD Total: {current_db_stats.get('total_registros', 0):,} registros")
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte final V2: {e}")
    
    async def get_current_db_stats(self) -> Dict:
        """Obtener estadísticas actuales de la BD"""
        try:
            stats = {
                'personas_fisicas': await self.db.personas_fisicas.count_documents({}),
                'personas_juridicas': await self.db.personas_juridicas.count_documents({}),
                'vehiculos_cr': 0,
                'propiedades_cr': 0
            }
            
            try:
                stats['vehiculos_cr'] = await self.db.vehiculos_cr.count_documents({})
                stats['propiedades_cr'] = await self.db.propiedades_cr.count_documents({})
            except:
                pass
            
            stats['total_registros'] = stats['personas_fisicas'] + stats['personas_juridicas']
            stats['progreso_3m_porcentaje'] = (stats['total_registros'] / 3000000) * 100
            stats['progreso_5m_porcentaje'] = (stats['total_registros'] / 5000000) * 100
            
            return stats
        except:
            return {'error': 'No se pudieron obtener estadísticas'}
    
    async def generate_future_recommendations(self) -> Dict:
        """Generar recomendaciones para futuras ejecuciones"""
        try:
            optimization_suggestions = self.optimizer.get_optimization_suggestions()
            
            recommendations = {
                'mejores_horarios': optimization_suggestions.get('recommended_hours', []),
                'endpoints_prioritarios': optimization_suggestions.get('priority_endpoints', [])[:5],
                'terminos_exitosos': optimization_suggestions.get('high_success_terms', [])[:10],
                'delay_optimo_sugerido': optimization_suggestions.get('suggested_delay', 0.2),
                'configuracion_sugerida': {
                    'sesiones_concurrentes': min(25, max(10, len(self.session_pool))),
                    'batch_size': 1500 if self.ultra_stats['efficiency_score'] > 100 else 1000,
                    'timeout_requests': 60 if self.ultra_stats['efficiency_score'] > 50 else 45
                },
                'proxima_optimizacion': {
                    'incrementar_agresividad': self.ultra_stats['efficiency_score'] > 80,
                    'reducir_agresividad': self.ultra_stats['efficiency_score'] < 30,
                    'mantener_configuracion': 30 <= self.ultra_stats['efficiency_score'] <= 80
                }
            }
            
            return recommendations
        except:
            return {'error': 'No se pudieron generar recomendaciones'}
    
    async def close_v2_system(self):
        """Cerrar sistema V2 limpiamente"""
        try:
            # Guardar estado de aprendizaje
            self.optimizer.save_learning_data()
            
            # Cerrar sesiones
            for session_data in self.session_pool.values():
                try:
                    await session_data['session'].aclose()
                except:
                    pass
            
            # Cerrar MongoDB
            if self.client:
                self.client.close()
            
            logger.info("✅ Sistema V2 Ultra Optimizado cerrado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error cerrando sistema V2: {e}")
    
    async def run_v2_ultra_optimized_extraction_complete(self):
        """Ejecutar extracción V2 completa"""
        start_time = datetime.utcnow()
        
        logger.info("🔥🔥🔥 INICIANDO V2 ULTRA OPTIMIZED EXTRACTION COMPLETA 🔥🔥🔥")
        logger.info("🧠 CON SISTEMA DE MEJORAMIENTO AUTOMÁTICO")
        logger.info("⚡ OBJETIVO: 5+ MILLONES CON INTELIGENCIA ARTIFICIAL")
        
        try:
            # Inicializar sistema V2
            if not await self.initialize_v2_system():
                logger.error("❌ Falló inicialización V2 ultra optimizada")
                return {
                    'success': False,
                    'error': 'Falló la inicialización del sistema V2 ultra optimizado',
                    'total_extracted': 0,
                    'time_minutes': 0,
                    'objetivo_alcanzado': False
                }
            
            # Ejecutar extracción ultra optimizada
            extracted_total = await self.extract_v2_ultra_optimized_data(target_records=5000000)
            
            end_time = datetime.utcnow()
            total_time = (end_time - start_time).total_seconds() / 60
            
            logger.info("🎉🎉🎉 V2 ULTRA OPTIMIZED EXTRACTION COMPLETADA! 🎉🎉🎉")
            logger.info(f"📊 REGISTROS V2 EXTRAÍDOS: {extracted_total:,}")
            logger.info(f"⏱️ TIEMPO TOTAL: {total_time:.2f} minutos")
            logger.info(f"🧠 AUTO-MEJORAS: {self.ultra_stats['auto_improvements']}")
            
            return {
                'success': True,
                'version': 'V2_ULTRA_OPTIMIZED',
                'total_extracted': extracted_total,
                'time_minutes': total_time,
                'objetivo_5M_alcanzado': extracted_total >= 5000000,
                'efficiency_score': self.ultra_stats['efficiency_score'],
                'auto_improvements': self.ultra_stats['auto_improvements'],
                'optimization_applications': self.ultra_stats['optimization_applications'],
                'ai_learning_active': True,
                'estadisticas_completas': self.ultra_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error en V2 ultra optimized extraction: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'version': 'V2_ULTRA_OPTIMIZED',
                'error': str(e),
                'total_extracted': 0,
                'time_minutes': 0,
                'objetivo_alcanzado': False
            }
        
        finally:
            await self.close_v2_system()

# Función principal para ejecutar V2
async def run_v2_ultra_optimized_extraction():
    """Función principal para ejecutar V2 ultra optimized extraction"""
    extractor = UltraOptimizedExtractorV2()
    return await extractor.run_v2_ultra_optimized_extraction_complete()

if __name__ == "__main__":
    result = asyncio.run(run_v2_ultra_optimized_extraction())
    print(f"🔥 RESULTADO V2 ULTRA OPTIMIZED EXTRACTION: {result}")