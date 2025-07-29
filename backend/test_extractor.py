#!/usr/bin/env python3
"""
Script de prueba para el extractor masivo
Ejecuta extracción con cantidades pequeñas para testing
"""
import asyncio
from massive_data_extractor import MassiveDataExtractor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_extraction():
    """Probar extracción con cantidades pequeñas"""
    extractor = MassiveDataExtractor()
    
    try:
        await extractor.initialize()
        logger.info("🚀 Iniciando prueba de extracción...")
        
        # Fase 1: TSE con 1000 cédulas
        logger.info("1️⃣ Probando extracción TSE (1K cédulas)")
        tse_count = await extractor.extract_tse_hybrid_data(
            cedula_batch_size=500,
            max_cedulas=1000
        )
        logger.info(f"✅ TSE completado: {tse_count} registros")
        
        # Fase 2: Daticos
        logger.info("2️⃣ Probando extracción Daticos")
        daticos_count = await extractor.extract_daticos_massive_data(target_records=50000)
        logger.info(f"✅ Daticos completado: {daticos_count} registros")
        
        # Fase 3: Mercantiles
        logger.info("3️⃣ Probando extracción mercantiles")
        mercantile_count = await extractor.extract_mercantile_data_enhanced()
        logger.info(f"✅ Mercantiles completado: {mercantile_count} registros")
        
        # Estadísticas
        logger.info(f"📊 RESULTADOS DE PRUEBA:")
        logger.info(f"   🗳️  TSE: {tse_count:,}")
        logger.info(f"   🏛️  Daticos: {daticos_count:,}")
        logger.info(f"   🏢 Mercantiles: {mercantile_count:,}")
        logger.info(f"   📱 Teléfonos: {extractor.extraction_stats['phone_numbers_found']:,}")
        logger.info(f"   💼 Total estimado para 2M: {(tse_count + daticos_count + mercantile_count) * 1000:,}")
        
        return {
            'tse': tse_count,
            'daticos': daticos_count,
            'mercantile': mercantile_count,
            'phones': extractor.extraction_stats['phone_numbers_found']
        }
        
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await extractor.close()

if __name__ == "__main__":
    result = asyncio.run(test_extraction())
    print(f"\n🎯 Resultado final: {result}")