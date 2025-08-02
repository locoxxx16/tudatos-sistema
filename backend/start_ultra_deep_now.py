#!/usr/bin/env python3
"""
INICIADOR INMEDIATO - ULTRA DEEP EXTRACTION
Ejecutar AHORA la extracción ultra profunda de TODA la base de datos de Daticos

Uso:
python3 start_ultra_deep_now.py
"""

import asyncio
import sys
import os
sys.path.append('/app')

from backend.ultra_deep_extractor import run_ultra_deep_extraction
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Función principal"""
    print("🚀🚀🚀 INICIANDO ULTRA DEEP EXTRACTION INMEDIATO 🚀🚀🚀")
    print("🎯 OBJETIVO: EXTRAER TODA LA BASE DE DATOS DE DATICOS.COM")
    print("🔥 MODO: ULTRA AGRESIVO CON TODAS LAS CREDENCIALES")
    print("📊 META: 3,000,000+ REGISTROS LIMPIOS DE COSTA RICA")
    print("")
    print("Credenciales a utilizar:")
    print("✅ CABEZAS/Hola2022 (Principal)")
    print("✅ Saraya/12345 (Secundaria)")
    print("")
    print("Métodos de extracción:")
    print("🔍 TODOS los endpoints disponibles")
    print("📝 TODOS los términos de búsqueda posibles")
    print("🇨🇷 Filtrado exclusivo Costa Rica")
    print("📱 Validación teléfonos +506")
    print("📧 Validación emails CR")
    print("🚗 Simulación datos COSEVI")
    print("🏠 Simulación propiedades")
    print("")
    
    confirmation = input("¿Proceder con la extracción ULTRA PROFUNDA? (s/N): ")
    
    if confirmation.lower() in ['s', 'si', 'y', 'yes']:
        print("\n🚀 INICIANDO EXTRACCIÓN ULTRA PROFUNDA...")
        print("⚠️  ADVERTENCIA: Este proceso puede tomar varias horas")
        print("📊 Se generarán informes de progreso cada 10,000 registros")
        print("")
        
        try:
            result = await run_ultra_deep_extraction()
            
            if result.get('success'):
                print("\n🎉🎉🎉 EXTRACCIÓN ULTRA COMPLETADA EXITOSAMENTE! 🎉🎉🎉")
                print(f"📊 REGISTROS EXTRAÍDOS: {result.get('total_extracted', 0):,}")
                print(f"⏱️ TIEMPO TOTAL: {result.get('time_minutes', 0):.2f} minutos")
                print(f"🎯 OBJETIVO 3M ALCANZADO: {'✅ SÍ' if result.get('objetivo_alcanzado') else '❌ NO'}")
            else:
                print("\n❌ ERROR EN LA EXTRACCIÓN ULTRA")
                print(f"Error: {result.get('error', 'Desconocido')}")
                
        except KeyboardInterrupt:
            print("\n⚠️ EXTRACCIÓN CANCELADA POR USUARIO")
            print("💾 Los datos extraídos hasta ahora se han guardado")
            
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("❌ Extracción cancelada por usuario")

if __name__ == "__main__":
    asyncio.run(main())