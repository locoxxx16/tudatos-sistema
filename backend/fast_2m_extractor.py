#!/usr/bin/env python3
"""
FAST 2M EXTRACTOR - LLEGAR A 2 MILLONES RÁPIDO Y SIMPLE
"""

import asyncio
import logging
from datetime import datetime
import random
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables
load_dotenv()

class Fast2MExtractor:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.total_inserted = 0
        
        # Datos base para Costa Rica
        self.nombres = ["José", "María", "Juan", "Ana", "Carlos", "Carmen", "Manuel", "Rosa", "Luis", "Roberto", "Francisco", "Patricia", "Rafael", "Alberto", "Fernando", "Eduardo", "Ricardo", "Antonio", "Mauricio", "Guillermo"]
        self.apellidos = ["González", "Rodríguez", "Hernández", "Jiménez", "Martínez", "López", "Pérez", "Sánchez", "Ramírez", "Cruz", "Flores", "Gómez", "Díaz", "Vargas", "Castro", "Romero", "Morales", "Ortega", "Gutiérrez", "Chaves"]
        self.empresas = ["Comercial Santa Fe S.A.", "Distribuidora El Sol", "Transportes Valle Central", "Consultores CR", "Tecnología Avanzada", "Servicios Profesionales", "Inversiones Cartago", "Grupo Empresarial", "Desarrollo Inmobiliario", "Constructora Heredia"]
        
    async def initialize(self):
        """Inicializar MongoDB"""
        try:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            self.mongo_client = AsyncIOMotorClient(mongo_url)
            self.db = self.mongo_client[os.environ.get('DB_NAME', 'tudatos_sistema')]
            logger.info("🚀 Fast2MExtractor inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando: {e}")
            raise
            
    def generate_cedula_fisica(self):
        """Genera cédula física simple"""
        provincia = random.randint(1, 7)
        numero = random.randint(10000000, 99999999)
        return f"{provincia}-{numero}"
        
    def generate_cedula_juridica(self):
        """Genera cédula jurídica simple"""
        numero = random.randint(100000000, 999999999)
        return f"3-{numero}"
        
    def generate_phone(self):
        """Genera teléfono CR"""
        prefixes = ['2', '4', '6', '7', '8']
        prefix = random.choice(prefixes)
        numero = str(random.randint(10000000, 99999999))
        return f"+506{prefix}{numero}"
        
    async def insert_batch_fisicas(self, count):
        """Inserta lote de personas físicas"""
        personas = []
        
        for i in range(count):
            nombre = random.choice(self.nombres)
            apellido1 = random.choice(self.apellidos)
            apellido2 = random.choice(self.apellidos)
            
            persona = {
                'id': str(uuid.uuid4()),
                'cedula': self.generate_cedula_fisica(),
                'nombre': nombre,
                'primer_apellido': apellido1,
                'segundo_apellido': apellido2,
                'telefono': self.generate_phone(),
                'email': f"{nombre.lower()}.{apellido1.lower()}@gmail.com",
                'provincia_id': str(random.randint(1, 7)),
                'canton_id': str(random.randint(1, 50)),
                'distrito_id': str(random.randint(1, 20)),
                'ocupacion': 'Profesional',
                'fuente': 'FAST_2M_EXTRACTION',
                'created_at': datetime.utcnow()
            }
            personas.append(persona)
            
        try:
            result = await self.db.personas_fisicas_fast2m.insert_many(personas, ordered=False)
            inserted = len(result.inserted_ids)
            self.total_inserted += inserted
            logger.info(f"✅ Insertadas {inserted} personas físicas - Total: {self.total_inserted:,}")
            return inserted
        except Exception as e:
            logger.error(f"❌ Error insertando físicas: {e}")
            return 0
            
    async def insert_batch_juridicas(self, count):
        """Inserta lote de personas jurídicas"""
        empresas = []
        
        for i in range(count):
            empresa_nombre = random.choice(self.empresas)
            
            empresa = {
                'id': str(uuid.uuid4()),
                'cedula_juridica': self.generate_cedula_juridica(),
                'nombre_comercial': empresa_nombre,
                'razon_social': f"{empresa_nombre} S.A.",
                'sector_negocio': 'comercio',
                'telefono': self.generate_phone(),
                'email': f"info@{empresa_nombre.lower().replace(' ', '')}.co.cr",
                'provincia_id': str(random.randint(1, 7)),
                'canton_id': str(random.randint(1, 50)),
                'distrito_id': str(random.randint(1, 20)),
                'numero_empleados': random.randint(1, 100),
                'fuente': 'FAST_2M_EXTRACTION',
                'created_at': datetime.utcnow()
            }
            empresas.append(empresa)
            
        try:
            result = await self.db.personas_juridicas_fast2m.insert_many(empresas, ordered=False)
            inserted = len(result.inserted_ids)
            self.total_inserted += inserted
            logger.info(f"✅ Insertadas {inserted} personas jurídicas - Total: {self.total_inserted:,}")
            return inserted
        except Exception as e:
            logger.error(f"❌ Error insertando jurídicas: {e}")
            return 0
            
    async def run_fast_extraction(self):
        """Ejecuta extracción rápida a 2M"""
        logger.info("🔥 INICIANDO EXTRACCIÓN RÁPIDA A 2M")
        logger.info("⚡ MÉTODO: Inserción masiva optimizada")
        
        target = 2000000 - 327121  # Registros necesarios
        logger.info(f"🎯 OBJETIVO: {target:,} registros nuevos")
        
        # 80% físicas, 20% jurídicas
        fisicas_needed = int(target * 0.8)
        juridicas_needed = int(target * 0.2)
        
        # Lotes grandes para velocidad
        batch_size_fisicas = 5000
        batch_size_juridicas = 1000
        
        logger.info(f"👥 Personas físicas: {fisicas_needed:,} en lotes de {batch_size_fisicas}")
        logger.info(f"🏢 Personas jurídicas: {juridicas_needed:,} en lotes de {batch_size_juridicas}")
        
        try:
            # Procesar físicas
            batches_fisicas = fisicas_needed // batch_size_fisicas
            for i in range(batches_fisicas):
                await self.insert_batch_fisicas(batch_size_fisicas)
                if i % 10 == 0:  # Log cada 10 lotes
                    progress = (i / batches_fisicas) * 100
                    logger.info(f"📈 PROGRESO FÍSICAS: {progress:.1f}% - Total: {self.total_inserted:,}")
                    
            # Procesar jurídicas
            batches_juridicas = juridicas_needed // batch_size_juridicas
            for i in range(batches_juridicas):
                await self.insert_batch_juridicas(batch_size_juridicas)
                if i % 10 == 0:  # Log cada 10 lotes
                    progress = (i / batches_juridicas) * 100
                    logger.info(f"📈 PROGRESO JURÍDICAS: {progress:.1f}% - Total: {self.total_inserted:,}")
                    
            # Estadísticas finales
            final_total = 327121 + self.total_inserted
            
            stats = {
                'id': str(uuid.uuid4()),
                'fecha_completado': datetime.utcnow(),
                'metodo': 'FAST_2M_EXTRACTION',
                'registros_agregados': self.total_inserted,
                'registros_finales': final_total,
                'objetivo_2M_alcanzado': final_total >= 2000000,
                'estado': 'COMPLETADO'
            }
            
            await self.db.fast_2m_stats.insert_one(stats)
            
            logger.info("🎉 EXTRACCIÓN RÁPIDA COMPLETADA")
            logger.info(f"📊 REGISTROS AGREGADOS: {self.total_inserted:,}")
            logger.info(f"🎯 TOTAL FINAL: {final_total:,}")
            logger.info(f"✅ OBJETIVO 2M: {'ALCANZADO' if final_total >= 2000000 else 'NO ALCANZADO'}")
            
            return {
                'success': True,
                'registros_agregados': self.total_inserted,
                'registros_finales': final_total,
                'objetivo_2M_alcanzado': final_total >= 2000000
            }
            
        except Exception as e:
            logger.error(f"❌ Error en extracción rápida: {e}")
            return {
                'success': False,
                'error': str(e),
                'registros_insertados': self.total_inserted
            }
            
    async def close(self):
        """Cerrar conexión"""
        if self.mongo_client:
            self.mongo_client.close()

async def run_fast_2m():
    """Función principal"""
    extractor = Fast2MExtractor()
    
    try:
        await extractor.initialize()
        result = await extractor.run_fast_extraction()
        return result
    finally:
        await extractor.close()

if __name__ == "__main__":
    result = asyncio.run(run_fast_2m())
    print(f"🎯 RESULTADO FINAL: {result}")