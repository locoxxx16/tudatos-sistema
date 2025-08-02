"""
SISTEMA AUTÓNOMO DE EXTRACCIÓN DIARIA
Scheduler independiente que funciona 24/7 sin intervención

Ejecuta extracción masiva automáticamente cada día a las 5:00 AM
Sistema robusto con reintentos y logging completo
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.asyncio import AsyncIOExecutor
import signal
from backend.ultra_massive_extractor import UltraMassiveExtractor
import json

# Configurar logging para sistema autónomo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - AUTONOMOUS - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/backend/autonomous_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutonomousExtractionScheduler:
    """
    Scheduler autónomo que funciona independientemente
    Sin necesidad de conexión de agente
    """
    
    def __init__(self):
        self.scheduler = None
        self.is_running = False
        self.extraction_count = 0
        
        # Configurar scheduler robusto
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutos de gracia
        }
        
        self.scheduler = AsyncIOScheduler(
            executors=executors,
            job_defaults=job_defaults,
            timezone='America/Costa_Rica'  # Zona horaria Costa Rica
        )
    
    async def autonomous_extraction_job(self):
        """
        Trabajo de extracción que se ejecuta automáticamente
        Completamente independiente
        """
        execution_id = f"AUTO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"🤖 INICIANDO EXTRACCIÓN AUTÓNOMA #{self.extraction_count + 1}")
            logger.info(f"🆔 ID Ejecución: {execution_id}")
            logger.info(f"⏰ Hora: {datetime.now()}")
            
            # Crear extractor ultra masivo
            extractor = UltraMassiveExtractor()
            
            # Ejecutar extracción completa
            start_time = datetime.now()
            result = await extractor.run_ultra_massive_extraction()
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds() / 60
            
            # Log resultado
            if result.get('success'):
                logger.info(f"✅ EXTRACCIÓN AUTÓNOMA EXITOSA #{self.extraction_count + 1}")
                logger.info(f"📊 Registros totales: {result.get('total_registros', 0):,}")
                logger.info(f"⏱️ Duración: {duration:.1f} minutos")
                logger.info(f"🎯 Objetivo 3M: {'ALCANZADO' if result.get('objetivo_3M_alcanzado') else 'EN PROGRESO'}")
                
                self.extraction_count += 1
                
                # Guardar log de éxito
                await self.log_autonomous_success(execution_id, result, duration)
                
            else:
                logger.error(f"❌ EXTRACCIÓN AUTÓNOMA FALLÓ #{self.extraction_count + 1}")
                logger.error(f"🐛 Error: {result.get('error', 'Unknown error')}")
                
                # Guardar log de fallo
                await self.log_autonomous_failure(execution_id, result, duration)
                
                # Programar reintento en 2 horas si es un fallo
                await self.schedule_retry(execution_id)
        
        except Exception as e:
            logger.error(f"❌ ERROR CRÍTICO EN EXTRACCIÓN AUTÓNOMA: {e}")
            import traceback
            traceback.print_exc()
            
            # Guardar error crítico
            await self.log_critical_error(execution_id, str(e))
            
            # Programar reintento de emergencia
            await self.schedule_emergency_retry(execution_id)
    
    async def log_autonomous_success(self, execution_id: str, result: dict, duration: float):
        """Registrar ejecución exitosa"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
            db = client[os.environ.get('DB_NAME', 'test_database')]
            
            success_log = {
                'execution_id': execution_id,
                'tipo': 'AUTONOMOUS_SUCCESS',
                'fecha_ejecucion': datetime.now(),
                'duracion_minutos': duration,
                'resultado_completo': result,
                'extractor_version': 'ULTRA_MASSIVE_V1.0',
                'modo': 'AUTOMATICO_5AM',
                'execution_number': self.extraction_count + 1
            }
            
            await db.autonomous_extraction_logs.insert_one(success_log)
            client.close()
            
        except Exception as e:
            logger.error(f"❌ Error logging success: {e}")
    
    async def log_autonomous_failure(self, execution_id: str, result: dict, duration: float):
        """Registrar ejecución fallida"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
            db = client[os.environ.get('DB_NAME', 'test_database')]
            
            failure_log = {
                'execution_id': execution_id,
                'tipo': 'AUTONOMOUS_FAILURE',
                'fecha_ejecucion': datetime.now(),
                'duracion_minutos': duration,
                'error_detallado': result,
                'extractor_version': 'ULTRA_MASSIVE_V1.0',
                'modo': 'AUTOMATICO_5AM',
                'requiere_reintento': True
            }
            
            await db.autonomous_extraction_logs.insert_one(failure_log)
            client.close()
            
        except Exception as e:
            logger.error(f"❌ Error logging failure: {e}")
    
    async def log_critical_error(self, execution_id: str, error: str):
        """Registrar error crítico"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
            db = client[os.environ.get('DB_NAME', 'test_database')]
            
            critical_log = {
                'execution_id': execution_id,
                'tipo': 'CRITICAL_ERROR',
                'fecha_error': datetime.now(),
                'error_critico': error,
                'requiere_intervencion': True,
                'reintentos_programados': 3
            }
            
            await db.autonomous_extraction_logs.insert_one(critical_log)
            client.close()
            
        except Exception as e:
            logger.error(f"❌ Error logging critical: {e}")
    
    async def schedule_retry(self, execution_id: str):
        """Programar reintento en caso de fallo"""
        try:
            retry_time = datetime.now().replace(hour=datetime.now().hour + 2, minute=0, second=0)
            
            self.scheduler.add_job(
                self.autonomous_extraction_job,
                trigger='date',
                run_date=retry_time,
                id=f'retry_{execution_id}',
                replace_existing=True
            )
            
            logger.info(f"🔄 Reintento programado para: {retry_time}")
            
        except Exception as e:
            logger.error(f"❌ Error programando reintento: {e}")
    
    async def schedule_emergency_retry(self, execution_id: str):
        """Programar reintento de emergencia"""
        try:
            # Reintentos cada 30 minutos por 3 veces
            for i in range(1, 4):
                retry_time = datetime.now().replace(
                    minute=datetime.now().minute + (30 * i), 
                    second=0
                )
                
                self.scheduler.add_job(
                    self.autonomous_extraction_job,
                    trigger='date',
                    run_date=retry_time,
                    id=f'emergency_retry_{execution_id}_{i}',
                    replace_existing=True
                )
            
            logger.info(f"🚨 Reintentos de emergencia programados: 3 intentos cada 30min")
            
        except Exception as e:
            logger.error(f"❌ Error programando reintentos emergencia: {e}")
    
    def start_autonomous_system(self):
        """Iniciar sistema autónomo completo"""
        try:
            logger.info("🤖 INICIANDO SISTEMA AUTÓNOMO DE EXTRACCIÓN")
            logger.info("🕐 Programado para ejecutarse diariamente a las 5:00 AM")
            logger.info("🇨🇷 Zona horaria: Costa Rica (America/Costa_Rica)")
            logger.info("🎯 Objetivo: 3+ millones de registros diarios")
            
            # Programar trabajo diario a las 5:00 AM
            self.scheduler.add_job(
                self.autonomous_extraction_job,
                trigger=CronTrigger(hour=5, minute=0, timezone='America/Costa_Rica'),
                id='daily_extraction_5am',
                replace_existing=True,
                name='Extracción Masiva Diaria 5AM'
            )
            
            # Programar verificación de salud cada hora
            self.scheduler.add_job(
                self.health_check,
                trigger=CronTrigger(minute=0),  # Cada hora
                id='hourly_health_check',
                replace_existing=True,
                name='Verificación de Salud Sistema'
            )
            
            # Programar limpieza de logs semanalmente
            self.scheduler.add_job(
                self.weekly_log_cleanup,
                trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
                id='weekly_log_cleanup',
                replace_existing=True,
                name='Limpieza Semanal de Logs'
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info("✅ SISTEMA AUTÓNOMO INICIADO EXITOSAMENTE")
            logger.info("📅 Próxima ejecución programada: 5:00 AM")
            
            # Configurar manejadores de señal para apagado graceful
            signal.signal(signal.SIGINT, self.graceful_shutdown)
            signal.signal(signal.SIGTERM, self.graceful_shutdown)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando sistema autónomo: {e}")
            return False
    
    async def health_check(self):
        """Verificación de salud del sistema cada hora"""
        try:
            logger.info("🩺 Verificación de salud del sistema autónomo")
            
            # Verificar MongoDB
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
            db = client[os.environ.get('DB_NAME', 'test_database')]
            
            await db.admin.command('ping')
            
            # Contar registros actuales
            total_fisicas = await db.personas_fisicas.count_documents({})
            total_juridicas = await db.personas_juridicas.count_documents({})
            total_vehiculos = await db.vehiculos_cr.count_documents({})
            total_propiedades = await db.propiedades_cr.count_documents({})
            
            grand_total = total_fisicas + total_juridicas + total_vehiculos + total_propiedades
            
            health_status = {
                'timestamp': datetime.now(),
                'sistema_activo': True,
                'mongodb_conectado': True,
                'total_registros_actuales': grand_total,
                'objetivo_3M_status': grand_total >= 3000000,
                'extracciones_completadas': self.extraction_count,
                'scheduler_jobs': len(self.scheduler.get_jobs())
            }
            
            await db.autonomous_health_checks.insert_one(health_status)
            client.close()
            
            logger.info(f"✅ Sistema saludable - Registros: {grand_total:,}")
            
        except Exception as e:
            logger.error(f"❌ Error en verificación de salud: {e}")
    
    async def weekly_log_cleanup(self):
        """Limpieza semanal de logs para optimizar espacio"""
        try:
            logger.info("🧹 Iniciando limpieza semanal de logs")
            
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
            db = client[os.environ.get('DB_NAME', 'test_database')]
            
            # Eliminar logs de más de 30 días
            cutoff_date = datetime.now().replace(day=datetime.now().day - 30)
            
            deleted_health = await db.autonomous_health_checks.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            deleted_extraction = await db.autonomous_extraction_logs.delete_many({
                'fecha_ejecucion': {'$lt': cutoff_date}
            })
            
            logger.info(f"🗑️ Logs eliminados - Health: {deleted_health.deleted_count}, Extraction: {deleted_extraction.deleted_count}")
            
            client.close()
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza de logs: {e}")
    
    def graceful_shutdown(self, signum, frame):
        """Apagado graceful del sistema"""
        logger.info("🛑 Recibida señal de apagado - Cerrando sistema autónomo gracefully")
        
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
        
        self.is_running = False
        logger.info("✅ Sistema autónomo cerrado correctamente")
        sys.exit(0)
    
    def run_forever(self):
        """Ejecutar sistema autónomo indefinidamente"""
        if not self.start_autonomous_system():
            logger.error("❌ No se pudo iniciar el sistema autónomo")
            return
        
        try:
            logger.info("♾️ Sistema autónomo ejecutándose indefinidamente...")
            logger.info("🔄 Presiona Ctrl+C para detener el sistema")
            
            # Mantener el sistema ejecutándose
            while self.is_running:
                asyncio.run(asyncio.sleep(60))  # Verificar cada minuto
                
        except KeyboardInterrupt:
            logger.info("⌨️ Interrupción por teclado detectada")
            self.graceful_shutdown(None, None)
        except Exception as e:
            logger.error(f"❌ Error en ejecución perpetua: {e}")
            self.graceful_shutdown(None, None)

# Función principal para ejecución directa
def main():
    """Punto de entrada principal"""
    print("🤖 SISTEMA AUTÓNOMO DE EXTRACCIÓN MASIVA")
    print("🇨🇷 Costa Rica - 3+ Millones de Registros Diarios")
    print("⏰ Programado para 5:00 AM diariamente")
    print("")
    
    scheduler_system = AutonomousExtractionScheduler()
    scheduler_system.run_forever()

if __name__ == "__main__":
    main()