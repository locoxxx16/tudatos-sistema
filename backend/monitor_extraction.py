#!/usr/bin/env python3
"""
MONITOR DE EXTRACCIÓN ULTRA PROFUNDA
Script para monitorear el progreso de la extracción masiva en tiempo real
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

async def monitor_extraction_progress():
    """Monitorear progreso de extracción en tiempo real"""
    
    try:
        # Conectar a MongoDB
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print("🔍 MONITOR DE EXTRACCIÓN ULTRA PROFUNDA")
        print("=" * 50)
        print(f"📅 Inicio del monitoreo: {datetime.now()}")
        print(f"🌐 Base de datos: {db_name}")
        print("=" * 50)
        
        # Estado inicial
        start_time = datetime.now()
        initial_fisicas = await db.personas_fisicas.count_documents({})
        initial_juridicas = await db.personas_juridicas.count_documents({})
        initial_total = initial_fisicas + initial_juridicas
        
        print(f"📊 ESTADO INICIAL:")
        print(f"   👥 Personas físicas: {initial_fisicas:,}")
        print(f"   🏢 Personas jurídicas: {initial_juridicas:,}")
        print(f"   📈 Total inicial: {initial_total:,}")
        print(f"   🎯 Meta 3M: {(initial_total/3000000)*100:.2f}%")
        print("=" * 50)
        
        # Monitoreo continuo
        iteration = 0
        max_unchanged_minutes = 30  # Si no hay cambios en 30 min, posiblemente terminó
        last_total = initial_total
        unchanged_minutes = 0
        
        while True:
            iteration += 1
            current_time = datetime.now()
            elapsed = (current_time - start_time).total_seconds() / 60
            
            # Obtener estadísticas actuales
            current_fisicas = await db.personas_fisicas.count_documents({})
            current_juridicas = await db.personas_juridicas.count_documents({})
            current_total = current_fisicas + current_juridicas
            
            # Ultra Deep específicos
            ultra_deep_fisicas = 0
            ultra_deep_juridicas = 0
            ultra_deep_raw = 0
            
            try:
                ultra_deep_fisicas = await db.personas_fisicas.count_documents({'fuente_ultra_deep': True})
                ultra_deep_juridicas = await db.personas_juridicas.count_documents({'fuente_ultra_deep': True})
                ultra_deep_raw = await db.ultra_deep_extraction.count_documents({})
            except:
                pass
            
            # COSEVI data
            vehiculos = 0
            propiedades = 0
            try:
                vehiculos = await db.vehiculos_cr.count_documents({})
                propiedades = await db.propiedades_cr.count_documents({})
            except:
                pass
            
            # Calcular incrementos
            total_increment = current_total - initial_total
            recent_increment = current_total - last_total
            
            # Calcular velocidad (registros por minuto)
            velocity = total_increment / elapsed if elapsed > 0 else 0
            
            # Progreso hacia 3M
            progress_3m = (current_total / 3000000) * 100
            remaining_3m = max(0, 3000000 - current_total)
            
            # ETA estimado
            eta_minutes = remaining_3m / velocity if velocity > 0 else float('inf')
            eta_hours = eta_minutes / 60
            
            # Progress bar simple
            progress_bar_length = 30
            filled_length = int(progress_bar_length * progress_3m / 100)
            bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
            
            # Display
            print(f"\n🔄 ITERACIÓN #{iteration} - {current_time.strftime('%H:%M:%S')}")
            print(f"⏱️  Tiempo transcurrido: {elapsed:.1f} min")
            print(f"📊 REGISTROS ACTUALES:")
            print(f"   👥 Personas físicas: {current_fisicas:,} (+{current_fisicas-initial_fisicas:,})")
            print(f"   🏢 Personas jurídicas: {current_juridicas:,} (+{current_juridicas-initial_juridicas:,})")
            print(f"   📈 TOTAL: {current_total:,} (+{total_increment:,})")
            print(f"   ⚡ Incremento reciente: +{recent_increment:,}")
            
            print(f"🔥 ULTRA DEEP ESPECÍFICOS:")
            print(f"   👥 Ultra Deep físicas: {ultra_deep_fisicas:,}")
            print(f"   🏢 Ultra Deep jurídicas: {ultra_deep_juridicas:,}")
            print(f"   📄 Registros raw: {ultra_deep_raw:,}")
            
            print(f"🚗 COSEVI DATA:")
            print(f"   🚙 Vehículos: {vehiculos:,}")
            print(f"   🏠 Propiedades: {propiedades:,}")
            
            print(f"📈 PROGRESO META 3M:")
            print(f"   {bar} {progress_3m:.2f}%")
            print(f"   🎯 Faltan: {remaining_3m:,} registros")
            print(f"   ⚡ Velocidad: {velocity:.1f} registros/min")
            
            if eta_hours < float('inf'):
                if eta_hours < 24:
                    print(f"   ⏰ ETA: {eta_hours:.1f} horas")
                else:
                    print(f"   ⏰ ETA: {eta_hours/24:.1f} días")
            
            # Verificar si la extracción se detuvo
            if recent_increment == 0:
                unchanged_minutes += 2  # Cada iteración son ~2 minutos
                if unchanged_minutes >= max_unchanged_minutes:
                    print(f"\n⚠️  POSIBLE FINALIZACIÓN: Sin cambios por {unchanged_minutes} minutos")
                    
                    # Verificar si alcanzó la meta
                    if current_total >= 3000000:
                        print("🎉 ¡META 3M ALCANZADA!")
                        print("✅ Extracción ultra profunda posiblemente completada")
                    else:
                        print("🔄 Extracción puede estar en proceso o finalizada prematuramente")
                    
                    break
            else:
                unchanged_minutes = 0
            
            last_total = current_total
            
            # Verificar meta alcanzada
            if current_total >= 3000000:
                print("\n🎉🎉🎉 ¡META DE 3 MILLONES ALCANZADA! 🎉🎉🎉")
                print("✅ Extracción ultra profunda EXITOSA")
                break
            
            print("=" * 50)
            
            # Esperar 2 minutos antes de la siguiente verificación
            await asyncio.sleep(120)
        
        # Estadísticas finales
        final_time = datetime.now()
        total_elapsed = (final_time - start_time).total_seconds() / 60
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN FINAL")
        print("=" * 50)
        print(f"⏱️  Tiempo total: {total_elapsed:.1f} minutos ({total_elapsed/60:.1f} horas)")
        print(f"📈 Registros extraídos: {current_total - initial_total:,}")
        print(f"📊 Total final: {current_total:,}")
        print(f"🎯 Meta 3M: {'✅ ALCANZADA' if current_total >= 3000000 else '❌ NO ALCANZADA'}")
        print(f"⚡ Velocidad promedio: {(current_total - initial_total) / total_elapsed:.1f} registros/min")
        
        client.close()
        
    except KeyboardInterrupt:
        print("\n⚠️ Monitoreo cancelado por usuario")
        if 'client' in locals():
            client.close()
    
    except Exception as e:
        print(f"\n❌ Error en monitoreo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando monitor de extracción...")
    print("🔄 El monitoreo se actualizará cada 2 minutos")
    print("⚠️  Presiona Ctrl+C para cancelar")
    print()
    
    asyncio.run(monitor_extraction_progress())