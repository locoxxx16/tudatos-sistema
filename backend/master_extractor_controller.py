#!/usr/bin/env python3
"""
🎛️ MASTER EXTRACTOR CONTROLLER - EL CEREBRO DE EXTRACCIÓN
Controla y ejecuta TODOS los extractores al máximo rendimiento
¡Crecimiento exponencial de la base de datos!
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterExtractorController:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.extractores_activos = {}
        self.stats_globales = {
            'total_extraido_hoy': 0,
            'fuentes_activas': 0,
            'extractores_ejecutados': 0,
            'tiempo_total_extraccion': 0,
            'empresas_nuevas': 0,
            'personas_nuevas': 0
        }
        
    async def initialize(self):
        """Inicializar controlador maestro"""
        try:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            self.mongo_client = AsyncIOMotorClient(mongo_url)
            self.db = self.mongo_client[os.environ.get('DB_NAME', 'test_database')]
            
            logger.info("🎛️ MASTER EXTRACTOR CONTROLLER INICIALIZADO")
            logger.info("⚡ PREPARANDO PARA DOMINACIÓN TOTAL DE DATOS")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando controlador: {e}")
            return False
    
    async def activar_extractor_ultra_empresarial(self):
        """🔥 Activar Ultra Empresarial Extractor"""
        logger.info("🔥 ACTIVANDO ULTRA EMPRESARIAL EXTRACTOR")
        
        try:
            from ultra_empresarial_extractor import ejecutar_extraccion_empresarial
            
            inicio = time.time()
            stats = await ejecutar_extraccion_empresarial()
            duracion = time.time() - inicio
            
            if stats:
                self.stats_globales['empresas_nuevas'] += stats['empresas_extraidas']
                self.stats_globales['extractores_ejecutados'] += 1
                self.stats_globales['tiempo_total_extraccion'] += duracion
                self.stats_globales['fuentes_activas'] += stats['fuentes_consultadas']
                
                logger.info(f"✅ ULTRA EMPRESARIAL: {stats['empresas_extraidas']:,} empresas extraídas")
                return True
            
        except Exception as e:
            logger.error(f"❌ Error en Ultra Empresarial: {e}")
            
        return False
    
    async def activar_fast_2m_extractor(self):
        """⚡ Activar Fast 2M Extractor"""
        logger.info("⚡ ACTIVANDO FAST 2M EXTRACTOR")
        
        try:
            from fast_2m_extractor import Fast2MExtractor
            
            extractor = Fast2MExtractor()
            await extractor.initialize()
            
            # Ejecutar extracción rápida adicional
            inicio = time.time()
            resultado = await extractor.run_fast_extraction()
            duracion = time.time() - inicio
            
            if resultado and resultado.get('exito'):
                nuevos_registros = resultado.get('registros_finales', 0)
                self.stats_globales['personas_nuevas'] += nuevos_registros
                self.stats_globales['extractores_ejecutados'] += 1
                self.stats_globales['tiempo_total_extraccion'] += duracion
                
                logger.info(f"✅ FAST 2M: {nuevos_registros:,} registros agregados")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error en Fast 2M: {e}")
            
        return False
    
    async def activar_ultra_deep_extractor(self):
        """🕳️ Activar Ultra Deep Extractor"""
        logger.info("🕳️ ACTIVANDO ULTRA DEEP EXTRACTOR")
        
        try:
            from ultra_deep_extractor import UltraDeepExtractor
            
            extractor = UltraDeepExtractor()
            await extractor.initialize()
            
            inicio = time.time()
            await extractor.execute_ultra_deep_extraction_immediate()
            duracion = time.time() - inicio
            
            self.stats_globales['extractores_ejecutados'] += 1
            self.stats_globales['tiempo_total_extraccion'] += duracion
            
            logger.info("✅ ULTRA DEEP: Extracción profunda ejecutada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Ultra Deep: {e}")
            
        return False
    
    async def activar_mega_aggressive_extractor(self):
        """💥 Activar Mega Aggressive Extractor"""
        logger.info("💥 ACTIVANDO MEGA AGGRESSIVE EXTRACTOR")
        
        try:
            from mega_aggressive_extractor import MegaAggressiveExtractor
            
            extractor = MegaAggressiveExtractor()
            await extractor.initialize()
            
            inicio = time.time()
            # Ejecutar extracción agresiva
            result = await extractor.run_mega_aggressive_extraction()
            duracion = time.time() - inicio
            
            if result:
                self.stats_globales['extractores_ejecutados'] += 1
                self.stats_globales['tiempo_total_extraccion'] += duracion
                
                logger.info("✅ MEGA AGGRESSIVE: Extracción agresiva completada")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error en Mega Aggressive: {e}")
            
        return False
    
    async def activar_daticos_extractor(self):
        """📊 Activar Daticos Extractor Avanzado"""
        logger.info("📊 ACTIVANDO DATICOS EXTRACTOR AVANZADO")
        
        try:
            from advanced_daticos_extractor import AdvancedDaticosExtractor
            
            extractor = AdvancedDaticosExtractor()
            await extractor.initialize()
            
            inicio = time.time()
            # Usar credenciales reales
            await extractor.login_and_extract_massive("CABEZAS", "Hola2022")
            await extractor.login_and_extract_massive("Saraya", "12345")
            duracion = time.time() - inicio
            
            self.stats_globales['extractores_ejecutados'] += 1
            self.stats_globales['tiempo_total_extraccion'] += duracion
            
            logger.info("✅ DATICOS: Extracción avanzada completada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Daticos: {e}")
            
        return False
    
    async def activar_registro_nacional_extractor(self):
        """📋 Activar Registro Nacional Extractor"""
        logger.info("📋 ACTIVANDO REGISTRO NACIONAL EXTRACTOR")
        
        try:
            from registro_nacional_extractor import RegistroNacionalExtractor
            
            extractor = RegistroNacionalExtractor()
            await extractor.initialize()
            
            inicio = time.time()
            await extractor.extract_massive_registry_data()
            duracion = time.time() - inicio
            
            self.stats_globales['extractores_ejecutados'] += 1
            self.stats_globales['tiempo_total_extraccion'] += duracion
            
            logger.info("✅ REGISTRO NACIONAL: Extracción masiva completada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Registro Nacional: {e}")
            
        return False
    
    async def activar_portal_datos_abiertos(self):
        """🌐 Activar Portal Datos Abiertos Extractor"""
        logger.info("🌐 ACTIVANDO PORTAL DATOS ABIERTOS EXTRACTOR")
        
        try:
            from portal_datos_abiertos_extractor import PortalDatosAbiertosExtractor
            
            extractor = PortalDatosAbiertosExtractor()
            await extractor.initialize()
            
            inicio = time.time()
            await extractor.extract_all_government_data()
            duracion = time.time() - inicio
            
            self.stats_globales['extractores_ejecutados'] += 1
            self.stats_globales['tiempo_total_extraccion'] += duracion
            
            logger.info("✅ PORTAL DATOS ABIERTOS: Extracción gubernamental completada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en Portal Datos Abiertos: {e}")
            
        return False
    
    async def contar_registros_actuales(self):
        """📊 Contar registros totales actuales"""
        try:
            collections_principales = [
                'personas_fisicas_fast2m',
                'personas_juridicas_fast2m',
                'empresas_sicop_ultra',
                'empresas_hacienda_ultra',
                'empresas_registro_nacional_ultra',
                'empresas_meic_ultra',
                'empresas_ccss_ultra',
                'tse_datos_hibridos',
                'ultra_deep_extraction'
            ]
            
            total = 0
            desglose = {}
            
            for collection_name in collections_principales:
                try:
                    count = await self.db[collection_name].count_documents({})
                    if count > 0:
                        desglose[collection_name] = count
                        total += count
                except:
                    pass
            
            return total, desglose
            
        except Exception as e:
            logger.error(f"Error contando registros: {e}")
            return 0, {}
    
    async def ejecutar_extraccion_masiva_paralela(self):
        """🚀 EJECUTAR TODOS LOS EXTRACTORES EN PARALELO - MÁXIMO RENDIMIENTO"""
        logger.info("🔥 INICIANDO EXTRACCIÓN MASIVA PARALELA")
        logger.info("⚡ TODOS LOS EXTRACTORES A MÁXIMO RENDIMIENTO")
        
        # Contar registros antes
        registros_antes, _ = await self.contar_registros_actuales()
        logger.info(f"📊 REGISTROS ANTES: {registros_antes:,}")
        
        inicio_total = time.time()
        
        # EJECUTAR TODOS LOS EXTRACTORES EN PARALELO
        tareas_extraction = [
            self.activar_extractor_ultra_empresarial(),  # NUEVO - Empresarial masivo
            self.activar_fast_2m_extractor(),           # Personas rápidas
            self.activar_ultra_deep_extractor(),        # Extracción profunda
            self.activar_mega_aggressive_extractor(),   # Agresivo
            self.activar_daticos_extractor(),           # Daticos avanzado
            self.activar_registro_nacional_extractor(), # Registro Nacional
            self.activar_portal_datos_abiertos()        # Datos gubernamentales
        ]
        
        logger.info(f"⚡ Ejecutando {len(tareas_extraction)} extractores en paralelo...")
        
        # Ejecutar todas las tareas
        resultados = await asyncio.gather(*tareas_extraction, return_exceptions=True)
        
        # Procesar resultados
        extractores_exitosos = sum(1 for r in resultados if r is True)
        extractores_fallidos = len(resultados) - extractores_exitosos
        
        # Contar registros después
        registros_despues, desglose = await self.contar_registros_actuales()
        registros_agregados = registros_despues - registros_antes
        
        # Estadísticas finales
        duracion_total = time.time() - inicio_total
        
        logger.info("🎉 EXTRACCIÓN MASIVA PARALELA COMPLETADA")
        logger.info("=" * 80)
        logger.info(f"⏱️  TIEMPO TOTAL: {duracion_total/60:.2f} minutos")
        logger.info(f"✅ EXTRACTORES EXITOSOS: {extractores_exitosos}")
        logger.info(f"❌ EXTRACTORES FALLIDOS: {extractores_fallidos}")
        logger.info(f"📊 REGISTROS ANTES: {registros_antes:,}")
        logger.info(f"📊 REGISTROS DESPUÉS: {registros_despues:,}")
        logger.info(f"🚀 REGISTROS AGREGADOS: {registros_agregados:,}")
        logger.info(f"📈 CRECIMIENTO: {((registros_agregados/max(registros_antes,1))*100):.2f}%")
        logger.info("=" * 80)
        
        logger.info("📋 DESGLOSE POR COLECCIÓN:")
        for collection, count in desglose.items():
            logger.info(f"   • {collection}: {count:,}")
        
        # Actualizar estadísticas globales
        self.stats_globales.update({
            'total_extraido_hoy': registros_agregados,
            'registros_antes': registros_antes,
            'registros_despues': registros_despues,
            'extractores_exitosos': extractores_exitosos,
            'extractores_fallidos': extractores_fallidos,
            'duracion_total_minutos': duracion_total/60,
            'desglose_colecciones': desglose
        })
        
        # Guardar estadísticas en MongoDB
        await self.guardar_estadisticas_extraccion()
        
        return self.stats_globales
    
    async def guardar_estadisticas_extraccion(self):
        """💾 Guardar estadísticas de extracción"""
        try:
            stats_record = {
                **self.stats_globales,
                'fecha_extraccion': datetime.now().isoformat(),
                'timestamp': datetime.now()
            }
            
            collection = self.db['estadisticas_extraccion_masiva']
            await collection.insert_one(stats_record)
            
            logger.info("💾 Estadísticas de extracción guardadas")
            
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")
    
    async def cerrar_conexiones(self):
        """Cerrar conexiones"""
        if self.mongo_client:
            self.mongo_client.close()

# Función principal
async def ejecutar_master_extractor():
    """🎛️ Ejecutar Master Extractor Controller"""
    controller = MasterExtractorController()
    
    try:
        await controller.initialize()
        stats = await controller.ejecutar_extraccion_masiva_paralela()
        return stats
    finally:
        await controller.cerrar_conexiones()

if __name__ == "__main__":
    logger.info("🎛️ INICIANDO MASTER EXTRACTOR CONTROLLER")
    logger.info("🔥 PREPARANDO PARA EXTRACCIÓN MASIVA")
    
    stats = asyncio.run(ejecutar_master_extractor())
    
    logger.info("🎉 MASTER EXTRACTOR CONTROLLER COMPLETADO")
    logger.info(f"📊 ESTADÍSTICAS FINALES: {json.dumps(stats, indent=2, default=str)}")