import asyncio
import logging
import os
import schedule
import time
from datetime import datetime, timedelta
import aiohttp
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from external_apis import costa_rica_integrator, DataCleaner
from faker import Faker
import uuid
import random
import threading

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker('es_ES')

class DataUpdaterService:
    """
    Servicio para actualización automática de datos desde múltiples fuentes
    """
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
        self.is_running = False
        self.update_stats = {
            'last_update': None,
            'records_updated': 0,
            'new_records': 0,
            'errors': 0
        }
    
    async def initialize_db(self):
        """Initialize database connection"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        
    async def close_db(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    async def fetch_tse_padron_updates(self):
        """
        Obtener actualizaciones del padrón electoral del TSE
        Nota: Esta es una implementación simulada - en producción usaría la API real del TSE
        """
        logger.info("🗳️ Checking TSE Padron Electoral updates...")
        
        try:
            # Simular descarga de datos del TSE
            # En producción, esto descargaría el archivo PADRON.TXT del TSE
            padron_url = "https://www.tse.go.cr/zip/padron/PADRON_COMPLETO.zip"
            
            # Por ahora, simulamos algunos registros nuevos
            nuevos_registros = await self.simulate_new_tse_records(50)
            
            updated_count = 0
            for registro in nuevos_registros:
                try:
                    # Actualizar en la base de datos
                    await self.update_persona_fisica(registro)
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating TSE record: {e}")
                    self.update_stats['errors'] += 1
            
            self.update_stats['records_updated'] += updated_count
            logger.info(f"✅ TSE Padron update completed: {updated_count} records updated")
            
        except Exception as e:
            logger.error(f"❌ Error in TSE padron update: {e}")
            self.update_stats['errors'] += 1
    
    async def simulate_new_tse_records(self, count=50):
        """Simular registros nuevos del TSE"""
        registros = []
        
        # Obtener distritos para asignar ubicaciones aleatorias
        distritos = await self.db.distritos.find().to_list(1000)
        
        for _ in range(count):
            distrito = random.choice(distritos)
            canton = await self.db.cantones.find_one({"id": distrito["canton_id"]})
            provincia = await self.db.provincias.find_one({"id": canton["provincia_id"]})
            
            cedula = f"{random.randint(1, 9)}{random.randint(100000000, 999999999)}"[:9]
            
            registro = {
                "cedula": cedula,
                "nombre": fake.first_name(),
                "primer_apellido": fake.last_name(),
                "segundo_apellido": fake.last_name() if random.choice([True, False]) else None,
                "fecha_nacimiento": fake.date_time_between(start_date='-80y', end_date='-18y'),
                "telefono": f"+506 {random.randint(2000, 9999)}-{random.randint(1000, 9999)}",
                "email": fake.email() if random.choice([True, False, False]) else None,
                "provincia_id": provincia["id"],
                "canton_id": canton["id"],
                "distrito_id": distrito["id"],
                "direccion_exacta": f"{fake.street_address()}, {distrito['nombre']}",
                "ocupacion": fake.job(),
                "fuente_datos": "TSE_PADRON",
                "fecha_actualizacion": datetime.utcnow()
            }
            registros.append(registro)
        
        return registros
    
    async def fetch_registro_nacional_updates(self):
        """
        Obtener actualizaciones del Registro Nacional de personas jurídicas
        """
        logger.info("🏛️ Checking Registro Nacional updates...")
        
        try:
            # Simular consulta al Registro Nacional
            nuevas_empresas = await self.simulate_new_companies(30)
            
            updated_count = 0
            for empresa in nuevas_empresas:
                try:
                    await self.update_persona_juridica(empresa)
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating company record: {e}")
                    self.update_stats['errors'] += 1
            
            self.update_stats['new_records'] += updated_count
            logger.info(f"✅ Registro Nacional update completed: {updated_count} new companies added")
            
        except Exception as e:
            logger.error(f"❌ Error in Registro Nacional update: {e}")
            self.update_stats['errors'] += 1
    
    async def simulate_new_companies(self, count=30):
        """Simular nuevas empresas del Registro Nacional"""
        empresas = []
        
        distritos = await self.db.distritos.find().to_list(1000)
        sectores = ["comercio", "servicios", "industria", "tecnologia", "educacion", 
                   "salud", "construccion", "turismo", "agricultura", "otros"]
        
        for _ in range(count):
            distrito = random.choice(distritos)
            canton = await self.db.cantones.find_one({"id": distrito["canton_id"]})
            provincia = await self.db.provincias.find_one({"id": canton["provincia_id"]})
            
            cedula_juridica = f"3-101-{random.randint(100000, 999999)}"
            company_name = fake.company()
            
            empresa = {
                "cedula_juridica": cedula_juridica,
                "nombre_comercial": company_name,
                "razon_social": f"{company_name} S.A.",
                "sector_negocio": random.choice(sectores),
                "telefono": f"+506 {random.randint(2000, 9999)}-{random.randint(1000, 9999)}",
                "email": f"info@{company_name.lower().replace(' ', '')}.cr",
                "website": f"www.{company_name.lower().replace(' ', '')}.cr" if random.choice([True, False]) else None,
                "provincia_id": provincia["id"],
                "canton_id": canton["id"],
                "distrito_id": distrito["id"],
                "direccion_exacta": f"{fake.street_address()}, {distrito['nombre']}",
                "numero_empleados": random.choice([1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 50, 75, 100, 150, 200]),
                "fecha_constitucion": fake.date_time_between(start_date='-20y', end_date='now'),
                "fuente_datos": "REGISTRO_NACIONAL",
                "fecha_actualizacion": datetime.utcnow()
            }
            empresas.append(empresa)
        
        return empresas
    
    async def update_persona_fisica(self, data):
        """Update or insert persona fisica"""
        await self.db.personas_fisicas.update_one(
            {"cedula": data["cedula"]},
            {"$set": data},
            upsert=True
        )
    
    async def update_persona_juridica(self, data):
        """Update or insert persona juridica"""
        await self.db.personas_juridicas.update_one(
            {"cedula_juridica": data["cedula_juridica"]},
            {"$set": data},
            upsert=True
        )
    
    async def enrich_existing_data(self, batch_size=100):
        """
        Enriquecer datos existentes con información de fuentes externas
        """
        logger.info("🔍 Enriching existing data with external sources...")
        
        try:
            # Obtener registros que no han sido enriquecidos recientemente
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            personas_to_enrich = await self.db.personas_fisicas.find({
                "$or": [
                    {"last_enriched": {"$exists": False}},
                    {"last_enriched": {"$lt": cutoff_date}}
                ]
            }).limit(batch_size).to_list(batch_size)
            
            enriched_count = 0
            for persona in personas_to_enrich:
                try:
                    cedula = persona["cedula"]
                    external_data = await costa_rica_integrator.enrich_persona_data(cedula)
                    
                    if external_data.get("data_found"):
                        # Actualizar con datos enriquecidos
                        updates = {"last_enriched": datetime.utcnow()}
                        
                        # Agregar datos externos si están disponibles
                        if "padron_electoral" in external_data["data_found"]:
                            updates["padron_electoral_data"] = external_data["data_found"]["padron_electoral"]
                        
                        await self.db.personas_fisicas.update_one(
                            {"cedula": cedula},
                            {"$set": updates}
                        )
                        enriched_count += 1
                    
                    # Pausa para no sobrecargar las APIs externas
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error enriching cedula {persona.get('cedula', 'unknown')}: {e}")
                    self.update_stats['errors'] += 1
            
            logger.info(f"✅ Data enrichment completed: {enriched_count} records enriched")
            
        except Exception as e:
            logger.error(f"❌ Error in data enrichment: {e}")
            self.update_stats['errors'] += 1
    
    async def cleanup_old_data(self):
        """
        Limpieza de datos obsoletos o duplicados
        """
        logger.info("🧹 Cleaning up old and duplicate data...")
        
        try:
            # Remover registros duplicados por cédula
            pipeline_fisica = [
                {
                    "$group": {
                        "_id": "$cedula",
                        "count": {"$sum": 1},
                        "docs": {"$push": "$$ROOT"}
                    }
                },
                {
                    "$match": {
                        "count": {"$gt": 1}
                    }
                }
            ]
            
            duplicates = await self.db.personas_fisicas.aggregate(pipeline_fisica).to_list(1000)
            
            removed_count = 0
            for duplicate_group in duplicates:
                # Mantener el registro más reciente
                docs = duplicate_group["docs"]
                docs.sort(key=lambda x: x.get("fecha_actualizacion", datetime.min), reverse=True)
                
                # Remover duplicados (mantener el primero)
                for doc in docs[1:]:
                    await self.db.personas_fisicas.delete_one({"_id": doc["_id"]})
                    removed_count += 1
            
            logger.info(f"✅ Cleanup completed: {removed_count} duplicate records removed")
            
        except Exception as e:
            logger.error(f"❌ Error in cleanup: {e}")
            self.update_stats['errors'] += 1
    
    async def run_daily_update(self):
        """Ejecutar actualización diaria completa"""
        logger.info("🚀 Starting daily data update process...")
        start_time = datetime.utcnow()
        
        # Resetear estadísticas
        self.update_stats = {
            'last_update': start_time,
            'records_updated': 0,
            'new_records': 0,
            'errors': 0
        }
        
        try:
            await self.initialize_db()
            
            # Ejecutar todas las actualizaciones
            await self.fetch_tse_padron_updates()
            await self.fetch_registro_nacional_updates()
            await self.enrich_existing_data()
            await self.cleanup_old_data()
            
            # Guardar estadísticas de actualización
            await self.save_update_stats()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Daily update completed in {duration:.2f} seconds")
            logger.info(f"📊 Stats: {self.update_stats['records_updated']} updated, "
                       f"{self.update_stats['new_records']} new, {self.update_stats['errors']} errors")
            
        except Exception as e:
            logger.error(f"❌ Fatal error in daily update: {e}")
        finally:
            await self.close_db()
    
    async def save_update_stats(self):
        """Guardar estadísticas de actualización"""
        stats_doc = {
            **self.update_stats,
            "timestamp": datetime.utcnow()
        }
        await self.db.update_statistics.insert_one(stats_doc)
    
    def schedule_updates(self):
        """Configurar actualizaciones programadas"""
        # Actualización diaria a las 2:00 AM
        schedule.every().day.at("02:00").do(lambda: asyncio.run(self.run_daily_update()))
        
        # Actualización de enriquecimiento cada 6 horas
        schedule.every(6).hours.do(lambda: asyncio.run(self.enrich_existing_data(50)))
        
        logger.info("📅 Scheduled updates configured:")
        logger.info("  - Daily full update at 2:00 AM")
        logger.info("  - Data enrichment every 6 hours")
    
    def start_scheduler(self):
        """Iniciar el programador de actualizaciones en un hilo separado"""
        def run_scheduler():
            self.is_running = True
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info("🔄 Data updater scheduler started")
    
    def stop_scheduler(self):
        """Detener el programador"""
        self.is_running = False
        logger.info("🛑 Data updater scheduler stopped")

# Instancia global del actualizador
data_updater = DataUpdaterService()

# Función para iniciar el servicio desde el servidor principal
def start_data_updater():
    """Iniciar el servicio de actualización de datos"""
    data_updater.schedule_updates()
    data_updater.start_scheduler()

# Función para ejecutar actualización manual
async def run_manual_update():
    """Ejecutar actualización manual"""
    await data_updater.run_daily_update()

if __name__ == "__main__":
    # Ejecutar actualización manual para pruebas
    asyncio.run(data_updater.run_daily_update())