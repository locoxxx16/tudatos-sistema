#!/usr/bin/env python3
"""
SCRIPT DE INICIO RÁPIDO - ULTRA MASSIVE EXTRACTION
Para usar inmediatamente después de la implementación

Ejecutar:
python3 /app/backend/start_ultra_extraction.py

O para sistema autónomo:
python3 /app/backend/start_ultra_extraction.py --autonomous
"""

import asyncio
import sys
import logging
import argparse
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - START_SCRIPT - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(description="Ultra Massive Data Extraction for Costa Rica")
    parser.add_argument('--autonomous', action='store_true', 
                       help='Start autonomous daily scheduler (5am)')
    parser.add_argument('--status', action='store_true',
                       help='Check current database status')
    
    args = parser.parse_args()
    
    if args.status:
        asyncio.run(check_status())
    elif args.autonomous:
        start_autonomous_system()
    else:
        asyncio.run(run_single_extraction())

async def check_status():
    """Verificar estado actual de la base de datos"""
    try:
        import os
        from dotenv import load_dotenv
        from motor.motor_asyncio import AsyncIOMotorClient
        
        load_dotenv()
        
        client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
        db = client[os.environ.get('DB_NAME', 'test_database')]
        
        collections = await db.list_collection_names()
        
        print("🔍 ESTADO ACTUAL DE LA BASE DE DATOS")
        print("=" * 50)
        
        total_records = 0
        
        for collection in ['personas_fisicas', 'personas_juridicas', 'vehiculos_cr', 'propiedades_cr']:
            if collection in collections:
                count = await db[collection].count_documents({})
                total_records += count
                print(f"📊 {collection}: {count:,} registros")
            else:
                print(f"📊 {collection}: 0 registros (no existe)")
        
        print("-" * 50)
        print(f"🎯 TOTAL REGISTROS: {total_records:,}")
        print(f"🎯 OBJETIVO 3M: {'✅ ALCANZADO' if total_records >= 3000000 else f'📈 {((total_records/3000000)*100):.1f}% completado'}")
        print(f"📍 RESTANTES: {max(0, 3000000 - total_records):,} registros")
        
        # Verificar sistema autónomo
        try:
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'autonomous_scheduler.py'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"🤖 SISTEMA AUTÓNOMO: ✅ ACTIVO (PID: {result.stdout.strip()})")
            else:
                print(f"🤖 SISTEMA AUTÓNOMO: ❌ INACTIVO")
        except:
            print(f"🤖 SISTEMA AUTÓNOMO: ❓ NO DETECTADO")
        
        client.close()
        
    except Exception as e:
        logger.error(f"❌ Error verificando status: {e}")

async def run_single_extraction():
    """Ejecutar una extracción única inmediatamente"""
    try:
        print("🚀 INICIANDO ULTRA MASSIVE EXTRACTION")
        print("🎯 Objetivo: 3+ millones de registros")
        print("🇨🇷 Filtrado: Solo Costa Rica")
        print("📱 Validación: Teléfonos y emails CR")
        print("")
        
        from ultra_massive_extractor import run_ultra_extraction
        
        start_time = datetime.now()
        print(f"⏰ Inicio: {start_time}")
        
        # Ejecutar extracción
        result = await run_ultra_extraction()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        print("")
        print("🎉 EXTRACCIÓN COMPLETADA!")
        print("=" * 50)
        
        if result.get('success'):
            print(f"✅ Estado: EXITOSA")
            print(f"📊 Total registros: {result.get('total_registros', 0):,}")
            print(f"🎯 Objetivo 3M: {'ALCANZADO' if result.get('objetivo_3M_alcanzado') else 'EN PROGRESO'}")
            print(f"⏱️ Duración: {duration:.1f} minutos")
        else:
            print(f"❌ Estado: ERROR")
            print(f"🐛 Error: {result.get('error', 'Unknown error')}")
        
        print(f"🕐 Finalizado: {end_time}")
        
    except Exception as e:
        logger.error(f"❌ Error en extracción única: {e}")
        import traceback
        traceback.print_exc()

def start_autonomous_system():
    """Iniciar sistema autónomo"""
    try:
        print("🤖 INICIANDO SISTEMA AUTÓNOMO")
        print("⏰ Programado para: 5:00 AM diariamente")
        print("🎯 Objetivo: 3+ millones de registros por día")
        print("")
        
        from autonomous_scheduler import main as autonomous_main
        
        # Ejecutar sistema autónomo
        autonomous_main()
        
    except KeyboardInterrupt:
        print("\n⌨️ Interrupción por teclado - Sistema detenido")
    except Exception as e:
        logger.error(f"❌ Error en sistema autónomo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🇨🇷 ULTRA MASSIVE DATA EXTRACTOR - COSTA RICA")
    print("🎯 Sistema de extracción de 3+ millones de registros")
    print("⚡ Credenciales: CABEZAS/Hola2022 + Saraya/12345")
    print("🚗 Fuentes: Daticos + COSEVI + TSE")
    print("=" * 60)
    print("")
    
    main()