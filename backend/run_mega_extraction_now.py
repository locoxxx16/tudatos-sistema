#!/usr/bin/env python3
"""
EJECUTAR EXTRACCIÓN MASIVA INMEDIATA
"""

import asyncio
import logging
from costa_rica_mega_extractor import run_mega_extraction

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Ejecutar extracción masiva inmediatamente"""
    logger.info("🚀 INICIANDO EXTRACCIÓN MASIVA COSTA RICA")
    logger.info("📋 OBJETIVO: EXTRAER MÁXIMO DE DATOS DE TODAS LAS FUENTES")
    
    try:
        result = await run_mega_extraction()
        
        if result['success']:
            logger.info("✅ EXTRACCIÓN MASIVA COMPLETADA EXITOSAMENTE")
            logger.info(f"📊 TOTAL EXTRAÍDO: {result['total_extracted']}")
            logger.info(f"💾 TOTAL GUARDADO: {result['total_saved']}")
            logger.info(f"🔢 FUENTES PROCESADAS: {result['sources_processed']}")
        else:
            logger.error(f"❌ ERROR EN EXTRACCIÓN: {result['error']}")
            
    except Exception as e:
        logger.error(f"❌ EXCEPCIÓN CRÍTICA: {e}")

if __name__ == "__main__":
    print("🔥 MEGA EXTRACTOR COSTA RICA - EJECUCIÓN INMEDIATA")
    asyncio.run(main())