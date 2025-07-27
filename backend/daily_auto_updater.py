#!/usr/bin/env python3
"""
Sistema de actualización automática diaria para enriquecimiento continuo de datos
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
import threading
import json
import os

# Importar nuestros extractores e integradores
from advanced_daticos_extractor import AdvancedDaticosExtractor
from daticos_data_integrator import DaticosDataIntegrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyAutoUpdater:
    """
    Sistema que ejecuta actualizaciones automáticas diarias para:
    1. Extraer nuevos datos de Daticos
    2. Enriquecer datos existentes
    3. Actualizar información de registros existentes
    4. Generar reportes de actualización
    """
    
    def __init__(self):
        self.extractor = AdvancedDaticosExtractor()
        self.integrator = DaticosDataIntegrator()
        self.update_running = False
        self.last_update_time = None
        self.update_stats = {}
        
        # Configuración de horarios
        self.config = {
            'daily_update_hour': '02:00',  # 2 AM cada día
            'backup_update_hour': '14:00',  # 2 PM backup
            'max_daily_extractions': 1000,  # Límite de extracciones por día
            'quality_threshold': 0.6,  # Umbral mínimo de calidad de datos
            'enable_automatic_updates': True
        }
        
        self.load_config()
    
    def load_config(self):
        """Cargar configuración desde archivo si existe"""
        try:
            config_file = '/app/backend/auto_updater_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
                    logger.info("📁 Configuración personalizada cargada")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
    
    def save_config(self):
        """Guardar configuración actual"""
        try:
            config_file = '/app/backend/auto_updater_config.json'
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("💾 Configuración guardada")
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    async def run_daily_update(self):
        """Ejecutar actualización diaria completa"""
        if self.update_running:
            logger.warning("⚠️  Actualización ya en progreso, omitiendo...")
            return
        
        try:
            self.update_running = True
            self.last_update_time = datetime.utcnow()
            
            logger.info("🚀 Iniciando actualización diaria automática...")
            
            # Fase 1: Extracción de nuevos datos
            extraction_stats = await self.perform_daily_extraction()
            
            # Fase 2: Integración de datos extraídos
            integration_stats = await self.perform_daily_integration()
            
            # Fase 3: Enriquecimiento de datos existentes
            enrichment_stats = await self.perform_data_enrichment()
            
            # Fase 4: Limpieza y optimización
            cleanup_stats = await self.perform_daily_cleanup()
            
            # Compilar estadísticas finales
            self.update_stats = {
                'timestamp': datetime.utcnow().isoformat(),
                'extraction': extraction_stats,
                'integration': integration_stats,
                'enrichment': enrichment_stats,
                'cleanup': cleanup_stats,
                'total_duration_minutes': (datetime.utcnow() - self.last_update_time).total_seconds() / 60
            }
            
            # Guardar reporte de actualización
            await self.save_update_report()
            
            logger.info(f"🎉 Actualización diaria completada en {self.update_stats['total_duration_minutes']:.2f} minutos")
            
        except Exception as e:
            logger.error(f"❌ Error durante actualización diaria: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.update_running = False
    
    async def perform_daily_extraction(self) -> Dict:
        """Realizar extracción diaria de datos"""
        logger.info("🔍 Fase 1: Extracción diaria de datos...")
        
        try:
            # Configurar extractor para búsqueda incremental
            extraction_data = await self.extractor.extract_all_endpoint_data()
            
            if extraction_data:
                # Guardar datos con timestamp diario
                daily_file = f'/app/backend/daily_extractions/daticos_daily_{datetime.now().strftime("%Y%m%d")}.json'
                os.makedirs('/app/backend/daily_extractions', exist_ok=True)
                
                with open(daily_file, 'w', encoding='utf-8') as f:
                    json.dump(extraction_data, f, indent=2, ensure_ascii=False)
                
                stats = {
                    'success': True,
                    'total_records': extraction_data.get('total_records', 0),
                    'endpoints_processed': len(extraction_data.get('endpoints_explored', {})),
                    'file_saved': daily_file
                }
                
                logger.info(f"✅ Extracción completada: {stats['total_records']} registros")
                return stats
            else:
                return {'success': False, 'error': 'No data extracted'}
                
        except Exception as e:
            logger.error(f"Error en extracción diaria: {e}")
            return {'success': False, 'error': str(e)}
    
    async def perform_daily_integration(self) -> Dict:
        """Integrar datos extraídos diariamente"""
        logger.info("🔄 Fase 2: Integración diaria de datos...")
        
        try:
            # Buscar archivo de extracción del día
            daily_file = f'/app/backend/daily_extractions/daticos_daily_{datetime.now().strftime("%Y%m%d")}.json'
            
            if os.path.exists(daily_file):
                # Usar integrador con el archivo específico del día
                integration_result = await self.integrator.process_and_integrate_data()
                
                if integration_result.get('success'):
                    stats = integration_result.get('stats', {})
                    stats['source_file'] = daily_file
                    
                    logger.info(f"✅ Integración completada: {stats.get('total_processed', 0)} registros procesados")
                    return stats
                else:
                    return {'success': False, 'error': integration_result.get('error', 'Unknown error')}
            else:
                return {'success': False, 'error': 'No daily extraction file found'}
                
        except Exception as e:
            logger.error(f"Error en integración diaria: {e}")
            return {'success': False, 'error': str(e)}
    
    async def perform_data_enrichment(self) -> Dict:
        """Enriquecer datos existentes con información adicional"""
        logger.info("💎 Fase 3: Enriquecimiento de datos existentes...")
        
        try:
            await self.integrator.initialize_db()
            
            # Obtener registros que necesitan enriquecimiento
            personas_col = self.integrator.db[self.integrator.collections['personas']]
            
            # Buscar registros con calidad baja o sin actualizar recientemente
            cutoff_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
            
            records_to_enrich = await personas_col.find({
                '$or': [
                    {'enrichment.data_quality_score': {'$lt': self.config['quality_threshold']}},
                    {'updated_at': {'$lt': cutoff_date}},
                    {'enrichment.last_enriched': {'$exists': False}}
                ]
            }).limit(100).to_list(100)
            
            enriched_count = 0
            errors = 0
            
            for record in records_to_enrich:
                try:
                    # Re-enriquecer registro
                    if record.get('cedula'):
                        # Intentar obtener más información de este registro
                        additional_data = await self.extractor.extract_consultation_by_cedula(record['cedula'])
                        
                        if additional_data.get('found'):
                            # Actualizar registro con nueva información
                            update_data = {
                                'enrichment.last_enriched': datetime.utcnow().isoformat(),
                                'enrichment.enrichment_attempts': record.get('enrichment', {}).get('enrichment_attempts', 0) + 1
                            }
                            
                            # Agregar nueva información encontrada
                            for key, value in additional_data.get('data', {}).items():
                                if value and not record.get(key):
                                    update_data[key] = value
                            
                            await personas_col.update_one(
                                {'id': record['id']},
                                {'$set': update_data}
                            )
                            
                            enriched_count += 1
                    
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error enriqueciendo registro {record.get('id', 'N/A')}: {e}")
                    errors += 1
                    continue
            
            stats = {
                'success': True,
                'records_processed': len(records_to_enrich),
                'successfully_enriched': enriched_count,
                'errors': errors
            }
            
            logger.info(f"✅ Enriquecimiento completado: {enriched_count} registros mejorados")
            return stats
            
        except Exception as e:
            logger.error(f"Error en enriquecimiento: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            await self.integrator.close_connection()
    
    async def perform_daily_cleanup(self) -> Dict:
        """Realizar limpieza y optimización diaria"""
        logger.info("🧹 Fase 4: Limpieza y optimización...")
        
        try:
            await self.integrator.initialize_db()
            
            cleanup_stats = {
                'duplicates_removed': 0,
                'empty_records_removed': 0,
                'indexes_optimized': True
            }
            
            # Remover registros duplicados basados en cédula
            personas_col = self.integrator.db[self.integrator.collections['personas']]
            
            # Encontrar duplicados por cédula
            duplicates_pipeline = [
                {'$group': {
                    '_id': '$cedula',
                    'ids': {'$push': '$id'},
                    'count': {'$sum': 1}
                }},
                {'$match': {'count': {'$gt': 1}}}
            ]
            
            duplicate_groups = await personas_col.aggregate(duplicates_pipeline).to_list(1000)
            
            for group in duplicate_groups:
                # Mantener solo el primer registro de cada cédula duplicada
                ids_to_remove = group['ids'][1:]  # Remover todos excepto el primero
                
                for id_to_remove in ids_to_remove:
                    await personas_col.delete_one({'id': id_to_remove})
                    cleanup_stats['duplicates_removed'] += 1
            
            # Remover registros con información insuficiente
            empty_records = await personas_col.delete_many({
                '$and': [
                    {'cedula': {'$in': ['', None]}},
                    {'nombre': {'$in': ['', None]}},
                    {'telefono': {'$in': ['', None]}}
                ]
            })
            
            cleanup_stats['empty_records_removed'] = empty_records.deleted_count
            
            # Re-crear índices para optimización
            await self.integrator.create_indexes()
            
            logger.info(f"✅ Limpieza completada: {cleanup_stats['duplicates_removed']} duplicados removidos")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Error en limpieza: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            await self.integrator.close_connection()
    
    async def save_update_report(self):
        """Guardar reporte detallado de actualización"""
        try:
            report_dir = '/app/backend/update_reports'
            os.makedirs(report_dir, exist_ok=True)
            
            report_file = f"{report_dir}/daily_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.update_stats, f, indent=2, ensure_ascii=False)
            
            # Mantener solo los últimos 30 reportes
            await self.cleanup_old_reports(report_dir)
            
            logger.info(f"📊 Reporte guardado: {report_file}")
            
        except Exception as e:
            logger.error(f"Error guardando reporte: {e}")
    
    async def cleanup_old_reports(self, report_dir: str):
        """Limpiar reportes antiguos"""
        try:
            import glob
            
            report_files = glob.glob(f"{report_dir}/daily_update_*.json")
            report_files.sort(reverse=True)  # Más recientes primero
            
            # Mantener solo los últimos 30
            for old_file in report_files[30:]:
                os.remove(old_file)
                
        except Exception as e:
            logger.error(f"Error limpiando reportes antiguos: {e}")
    
    def setup_scheduler(self):
        """Configurar programador de tareas diarias"""
        try:
            if self.config['enable_automatic_updates']:
                # Actualización principal diaria
                schedule.every().day.at(self.config['daily_update_hour']).do(
                    lambda: asyncio.run(self.run_daily_update())
                )
                
                # Actualización de respaldo
                schedule.every().day.at(self.config['backup_update_hour']).do(
                    lambda: asyncio.run(self.run_daily_update())
                )
                
                logger.info(f"⏰ Actualizaciones programadas para: {self.config['daily_update_hour']} y {self.config['backup_update_hour']}")
            else:
                logger.info("⏸️  Actualizaciones automáticas deshabilitadas")
                
        except Exception as e:
            logger.error(f"Error configurando programador: {e}")
    
    def run_scheduler(self):
        """Ejecutar el programador en un hilo separado"""
        def scheduler_thread():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        
        thread = threading.Thread(target=scheduler_thread, daemon=True)
        thread.start()
        logger.info("🔄 Programador de actualizaciones iniciado")
    
    def get_update_status(self) -> Dict:
        """Obtener estado actual del sistema de actualizaciones"""
        return {
            'update_running': self.update_running,
            'last_update_time': self.last_update_time.isoformat() if self.last_update_time else None,
            'config': self.config,
            'last_stats': self.update_stats,
            'next_scheduled_update': schedule.jobs[0].next_run.isoformat() if schedule.jobs else None
        }
    
    async def force_update_now(self):
        """Forzar actualización inmediata (para testing/admin)"""
        logger.info("🔥 Forzando actualización inmediata...")
        await self.run_daily_update()
        return self.update_stats

# Instancia global del actualizador
daily_updater = DailyAutoUpdater()

# Funciones para integración con FastAPI
def start_auto_updater():
    """Iniciar el sistema de actualizaciones automáticas"""
    daily_updater.setup_scheduler()
    daily_updater.run_scheduler()
    logger.info("🚀 Sistema de actualizaciones automáticas iniciado")

def get_updater_status():
    """Obtener estado del actualizador para API"""
    return daily_updater.get_update_status()

async def force_update():
    """Forzar actualización inmediata desde API"""
    return await daily_updater.force_update_now()

def update_config(new_config: Dict):
    """Actualizar configuración del actualizador"""
    daily_updater.config.update(new_config)
    daily_updater.save_config()
    daily_updater.setup_scheduler()  # Re-configurar programador
    return daily_updater.config

if __name__ == "__main__":
    # Para ejecutar standalone
    async def test_update():
        await daily_updater.run_daily_update()
    
    logger.info("🧪 Ejecutando actualización de prueba...")
    asyncio.run(test_update())