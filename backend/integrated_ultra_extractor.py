"""
INTEGRATED ULTRA EXTRACTOR
Sistema integrado que ejecuta TODOS los extractores en secuencia optimizada

Extractores incluidos:
1. Ultra Deep Extractor (base principal)
2. Registro Nacional Extractor
3. Portal Datos Abiertos Extractor  
4. Colegios Profesionales Extractor

Meta: 5+ millones de registros con máxima cobertura
Ejecuta todos los extractores de manera optimizada y coordinada

Creado: Diciembre 2024
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Imports de todos los extractores
from ultra_deep_extractor import run_ultra_deep_extraction
from registro_nacional_extractor import run_registro_nacional_extraction
from portal_datos_abiertos_extractor import run_portal_datos_abiertos_extraction
from colegios_profesionales_extractor import run_colegios_profesionales_extraction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class IntegratedUltraExtractor:
    """Extractor integrado que ejecuta todos los sistemas de extracción"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
        
        # Lista de extractores en orden de prioridad
        self.extractors = [
            {
                'name': 'Ultra Deep Extractor',
                'code': 'ultra_deep',
                'function': run_ultra_deep_extraction,
                'priority': 1,
                'expected_records': 3000000,
                'description': 'Extractor principal de Daticos con 18 endpoints y 118 términos'
            },
            {
                'name': 'Registro Nacional',
                'code': 'registro_nacional', 
                'function': run_registro_nacional_extraction,
                'priority': 2,
                'expected_records': 500000,
                'description': 'Propiedades, vehículos y sociedades del Registro Nacional'
            },
            {
                'name': 'Portal Datos Abiertos',
                'code': 'portal_datos_abiertos',
                'function': run_portal_datos_abiertos_extraction,
                'priority': 3,
                'expected_records': 800000,
                'description': 'Funcionarios públicos, contratistas y datasets gubernamentales'
            },
            {
                'name': 'Colegios Profesionales',
                'code': 'colegios_profesionales',
                'function': run_colegios_profesionales_extraction,
                'priority': 4,
                'expected_records': 200000,
                'description': 'Médicos, abogados, ingenieros y otros profesionales colegiados'
            }
        ]
        
        self.global_stats = {
            'total_registros_antes': 0,
            'total_registros_despues': 0,
            'nuevos_registros': 0,
            'extractores_exitosos': 0,
            'extractores_fallidos': 0,
            'tiempo_total_minutos': 0,
            'objetivo_5M_alcanzado': False,
            'extraccion_detallada': {},
            'errores_encontrados': []
        }
    
    async def initialize(self):
        """Inicializar sistema integrado"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            await self.db.command('ping')
            logger.info("✅ Integrated Ultra Extractor - MongoDB OK")
            return True
        except Exception as e:
            logger.error(f"❌ Error inicializando: {e}")
            return False
    
    async def run_integrated_extraction(self):
        """Ejecutar extracción integrada con todos los extractores"""
        start_time = datetime.utcnow()
        logger.info("🚀🚀🚀 INICIANDO EXTRACCIÓN INTEGRADA ULTRA COMPLETA 🚀🚀🚀")
        logger.info(f"🎯 META: 5+ MILLONES DE REGISTROS")
        logger.info(f"📊 EXTRACTORES A EJECUTAR: {len(self.extractors)}")
        
        try:
            # Obtener conteo inicial
            self.global_stats['total_registros_antes'] = await self.get_total_records()
            logger.info(f"📊 REGISTROS ACTUALES: {self.global_stats['total_registros_antes']:,}")
            
            # Ejecutar cada extractor en secuencia optimizada
            for extractor_info in self.extractors:
                await self.execute_single_extractor(extractor_info)
            
            # Obtener conteo final
            self.global_stats['total_registros_despues'] = await self.get_total_records()
            self.global_stats['nuevos_registros'] = (
                self.global_stats['total_registros_despues'] - 
                self.global_stats['total_registros_antes']
            )
            
            # Calcular tiempo total
            end_time = datetime.utcnow()
            self.global_stats['tiempo_total_minutos'] = (end_time - start_time).total_seconds() / 60
            
            # Verificar objetivo 5M
            self.global_stats['objetivo_5M_alcanzado'] = self.global_stats['total_registros_despues'] >= 5000000
            
            # Generar reporte final
            await self.generate_integrated_report()
            
            logger.info("🎉🎉🎉 EXTRACCIÓN INTEGRADA COMPLETADA 🎉🎉🎉")
            logger.info(f"📊 REGISTROS FINALES: {self.global_stats['total_registros_despues']:,}")
            logger.info(f"🆕 NUEVOS REGISTROS: {self.global_stats['nuevos_registros']:,}")
            logger.info(f"⏱️ TIEMPO TOTAL: {self.global_stats['tiempo_total_minutos']:.2f} minutos")
            logger.info(f"🎯 OBJETIVO 5M: {'✅ ALCANZADO' if self.global_stats['objetivo_5M_alcanzado'] else '❌ NO ALCANZADO'}")
            
            return {
                'success': True,
                'total_extracted': self.global_stats['nuevos_registros'],
                'total_final': self.global_stats['total_registros_despues'],
                'objetivo_5M_alcanzado': self.global_stats['objetivo_5M_alcanzado'],
                'time_minutes': self.global_stats['tiempo_total_minutos'],
                'extractores_exitosos': self.global_stats['extractores_exitosos'],
                'extraccion_detallada': self.global_stats['extraccion_detallada']
            }
            
        except Exception as e:
            logger.error(f"❌ Error en extracción integrada: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'total_extracted': self.global_stats['nuevos_registros'],
                'time_minutes': self.global_stats['tiempo_total_minutos']
            }
        
        finally:
            await self.close()
    
    async def execute_single_extractor(self, extractor_info: Dict):
        """Ejecutar un extractor individual"""
        extractor_name = extractor_info['name']
        extractor_code = extractor_info['code']
        extractor_function = extractor_info['function']
        
        logger.info(f"🔄 EJECUTANDO: {extractor_name}")
        logger.info(f"📝 {extractor_info['description']}")
        logger.info(f"🎯 REGISTROS ESPERADOS: {extractor_info['expected_records']:,}")
        
        extractor_start = datetime.utcnow()
        records_before = await self.get_total_records()
        
        try:
            # Ejecutar extractor
            result = await extractor_function()
            
            records_after = await self.get_total_records()
            new_records = records_after - records_before
            extractor_end = datetime.utcnow()
            duration_minutes = (extractor_end - extractor_start).total_seconds() / 60
            
            if result and not result.get('error'):
                # Extractor exitoso
                self.global_stats['extractores_exitosos'] += 1
                
                extraction_detail = {
                    'status': 'success',
                    'nuevos_registros': new_records,
                    'tiempo_minutos': round(duration_minutes, 2),
                    'resultado_completo': result,
                    'timestamp': extractor_end.isoformat()
                }
                
                logger.info(f"✅ {extractor_name}: {new_records:,} nuevos registros en {duration_minutes:.2f} min")
                
            else:
                # Extractor falló
                self.global_stats['extractores_fallidos'] += 1
                error_msg = result.get('error', 'Error desconocido') if result else 'No result returned'
                
                extraction_detail = {
                    'status': 'error',
                    'error': error_msg,
                    'nuevos_registros': new_records,
                    'tiempo_minutos': round(duration_minutes, 2),
                    'timestamp': extractor_end.isoformat()
                }
                
                logger.error(f"❌ {extractor_name}: Error - {error_msg}")
                self.global_stats['errores_encontrados'].append({
                    'extractor': extractor_name,
                    'error': error_msg,
                    'timestamp': extractor_end.isoformat()
                })
            
            self.global_stats['extraccion_detallada'][extractor_code] = extraction_detail
            
            # Pausa entre extractores para evitar sobrecarga
            await asyncio.sleep(10)
            
        except Exception as e:
            # Error crítico en extractor
            extractor_end = datetime.utcnow()
            duration_minutes = (extractor_end - extractor_start).total_seconds() / 60
            
            self.global_stats['extractores_fallidos'] += 1
            error_msg = f"Error crítico: {str(e)}"
            
            extraction_detail = {
                'status': 'critical_error',
                'error': error_msg,
                'nuevos_registros': 0,
                'tiempo_minutos': round(duration_minutes, 2),
                'timestamp': extractor_end.isoformat()
            }
            
            self.global_stats['extraccion_detallada'][extractor_code] = extraction_detail
            self.global_stats['errores_encontrados'].append({
                'extractor': extractor_name,
                'error': error_msg,
                'timestamp': extractor_end.isoformat()
            })
            
            logger.error(f"💥 {extractor_name}: Error crítico - {error_msg}")
            # Nota: El bucle continuará automáticamente con el siguiente extractor
    
    async def get_total_records(self):
        """Obtener total de registros en todas las colecciones"""
        try:
            collections_to_count = [
                'personas_fisicas',
                'personas_juridicas', 
                'vehiculos_cr',
                'propiedades_cr',
                'funcionarios_publicos_cr',
                'profesionales_colegiados_cr',
                'empleados_institucionales_cr'
            ]
            
            total = 0
            collection_names = await self.db.list_collection_names()
            
            for collection in collections_to_count:
                if collection in collection_names:
                    count = await self.db[collection].count_documents({})
                    total += count
            
            # También contar colecciones dinámicas de extractores
            dynamic_collections = [name for name in collection_names if any(prefix in name for prefix in [
                'datos_abiertos_', 'dataset_', 'profesionales_'
            ])]
            
            for collection in dynamic_collections:
                count = await self.db[collection].count_documents({})
                total += count
            
            return total
            
        except Exception as e:
            logger.error(f"❌ Error contando registros: {e}")
            return 0
    
    async def generate_integrated_report(self):
        """Generar reporte detallado de la extracción integrada"""
        try:
            # Contar registros por colección
            collection_counts = {}
            collection_names = await self.db.list_collection_names()
            
            main_collections = ['personas_fisicas', 'personas_juridicas', 'vehiculos_cr', 'propiedades_cr']
            for collection in main_collections:
                if collection in collection_names:
                    collection_counts[collection] = await self.db[collection].count_documents({})
                else:
                    collection_counts[collection] = 0
            
            # Contar colecciones especializadas
            specialized_counts = {}
            specialized_collections = [
                'funcionarios_publicos_cr',
                'profesionales_colegiados_cr', 
                'empleados_institucionales_cr'
            ]
            
            for collection in specialized_collections:
                if collection in collection_names:
                    specialized_counts[collection] = await self.db[collection].count_documents({})
                else:
                    specialized_counts[collection] = 0
            
            report = {
                'id': str(uuid.uuid4()),
                'fecha_extraccion': datetime.utcnow(),
                'tipo_extraccion': 'INTEGRATED_ULTRA_EXTRACTION',
                'extraccion_completada': True,
                
                # Stats globales
                'estadisticas_globales': self.global_stats,
                
                # Conteos detallados
                'conteos_colecciones_principales': collection_counts,
                'conteos_colecciones_especializadas': specialized_counts,
                
                # Análisis de cobertura
                'analisis_cobertura': {
                    'personas_fisicas': collection_counts.get('personas_fisicas', 0),
                    'personas_juridicas': collection_counts.get('personas_juridicas', 0),
                    'vehiculos_propiedades': collection_counts.get('vehiculos_cr', 0) + collection_counts.get('propiedades_cr', 0),
                    'funcionarios_publicos': specialized_counts.get('funcionarios_publicos_cr', 0),
                    'profesionales_colegiados': specialized_counts.get('profesionales_colegiados_cr', 0),
                    'empleados_institucionales': specialized_counts.get('empleados_institucionales_cr', 0)
                },
                
                # Rendimiento por extractor
                'rendimiento_extractores': {
                    extractor_code: {
                        'nuevos_registros': details.get('nuevos_registros', 0),
                        'tiempo_minutos': details.get('tiempo_minutos', 0),
                        'registros_por_minuto': round(details.get('nuevos_registros', 0) / max(details.get('tiempo_minutos', 1), 1), 2),
                        'status': details.get('status', 'unknown')
                    }
                    for extractor_code, details in self.global_stats['extraccion_detallada'].items()
                },
                
                # Recomendaciones
                'recomendaciones': self.generate_recommendations()
            }
            
            # Guardar reporte
            await self.db.integrated_extraction_reports.insert_one(report)
            
            logger.info("📊 REPORTE INTEGRADO GENERADO")
            logger.info(f"📋 ID Reporte: {report['id']}")
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
    
    def generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en los resultados"""
        recommendations = []
        
        # Verificar objetivo 5M
        if self.global_stats['objetivo_5M_alcanzado']:
            recommendations.append("✅ Objetivo de 5M registros alcanzado. Sistema optimizado.")
        else:
            recommendations.append("⚠️ Objetivo de 5M no alcanzado. Considerar optimizar extractores con mayor rendimiento.")
        
        # Analizar extractores fallidos
        if self.global_stats['extractores_fallidos'] > 0:
            recommendations.append(f"🔧 {self.global_stats['extractores_fallidos']} extractores fallaron. Revisar configuración y conexiones.")
        
        # Analizar rendimiento
        if self.global_stats['tiempo_total_minutos'] > 240:  # Más de 4 horas
            recommendations.append("⏱️ Tiempo de extracción alto. Considerar paralelización de extractores.")
        
        # Verificar nuevos registros
        if self.global_stats['nuevos_registros'] < 100000:
            recommendations.append("📊 Pocos registros nuevos extraídos. Verificar fuentes de datos y filtros de duplicados.")
        
        return recommendations
    
    async def close(self):
        """Cerrar conexiones"""
        if self.client:
            self.client.close()

async def run_integrated_ultra_extraction():
    """Función principal para ejecutar la extracción integrada"""
    extractor = IntegratedUltraExtractor()
    
    if await extractor.initialize():
        result = await extractor.run_integrated_extraction()
        return result
    else:
        return {'success': False, 'error': 'Falló la inicialización del sistema integrado'}

if __name__ == "__main__":
    result = asyncio.run(run_integrated_ultra_extraction())
    print(f"🚀 RESULTADO EXTRACCIÓN INTEGRADA: {result}")