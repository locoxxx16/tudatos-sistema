#!/usr/bin/env python3
"""
Script para probar las nuevas credenciales de Daticos y analizar 
los tipos de consultas disponibles.
"""

import asyncio
import logging
import sys
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Agregar el directorio backend al path
sys.path.append('/app/backend')

from daticos_extractor import daticos_extractor

async def main():
    """Función principal para probar Daticos con nuevas credenciales"""
    print("🚀 Iniciando prueba de credenciales Daticos...")
    print(f"👤 Usuario: {daticos_extractor.credentials['usuario']}")
    print(f"🔐 Password: {'*' * len(daticos_extractor.credentials['password'])}")
    
    try:
        # 1. Probar login
        print("\n🔐 Probando login...")
        login_success = await daticos_extractor.login()
        
        if not login_success:
            print("❌ Login fallido. Verificando detalles...")
            return
        
        print("✅ Login exitoso!")
        
        # 2. Analizar estructura del sistema
        print("\n📋 Analizando estructura del sistema...")
        structure = await daticos_extractor.discover_system_structure()
        
        if structure:
            print(f"📂 Elementos de menú encontrados: {len(structure.get('menu_items', []))}")
            for item in structure.get('menu_items', [])[:10]:  # Mostrar primeros 10
                print(f"  - {item.get('text', 'N/A')}: {item.get('href', 'N/A')}")
            
            print(f"📝 Tipos de consulta encontrados: {len(structure.get('consultation_types', []))}")
            for consult in structure.get('consultation_types', [])[:5]:  # Mostrar primeros 5
                print(f"  - Método: {consult.get('method', 'N/A')}, Action: {consult.get('action', 'N/A')}")
                print(f"    Inputs: {[inp.get('name') for inp in consult.get('inputs', [])]}")
        
        # 3. Probar consulta por cédula de muestra
        print("\n🔍 Probando consulta por cédula...")
        test_cedulas = ['1-0001-0001', '110010001', '692785539']  # Algunas cédulas de prueba
        
        for cedula in test_cedulas:
            print(f"\n   Consultando cédula: {cedula}")
            result = await daticos_extractor.extract_consultation_by_cedula(cedula)
            
            if result.get('found'):
                print(f"   ✅ Datos encontrados: {len(result.get('data', {}))} campos")
                for key, value in result.get('data', {}).items():
                    print(f"     {key}: {value}")
            else:
                print(f"   ❌ No se encontraron datos para {cedula}")
        
        # 4. Analizar página principal para encontrar más funcionalidades
        print("\n🔍 Explorando funcionalidades adicionales...")
        
        # Intentar acceder a diferentes secciones
        sections_to_test = [
            '/consulta.php',
            '/busqueda.php',
            '/mercantil.php',
            '/laboral.php',
            '/matrimonio.php',
            '/sociedades.php',
            '/vehiculos.php',
            '/propiedades.php'
        ]
        
        available_sections = []
        for section in sections_to_test:
            try:
                response = await daticos_extractor.session.get(f"{daticos_extractor.base_url}{section}")
                if response.status_code == 200 and 'error' not in response.text.lower():
                    available_sections.append(section)
                    print(f"   ✅ Sección disponible: {section}")
                else:
                    print(f"   ❌ Sección no disponible: {section}")
            except Exception as e:
                print(f"   ❌ Error accediendo a {section}: {e}")
        
        print(f"\n📊 Resumen:")
        print(f"   - Login: {'✅ Exitoso' if login_success else '❌ Fallido'}")
        print(f"   - Elementos de menú: {len(structure.get('menu_items', []))}")
        print(f"   - Secciones disponibles: {len(available_sections)}")
        print(f"   - Secciones: {', '.join(available_sections)}")
        
        # Guardar estructura para análisis posterior
        import json
        with open('/app/backend/daticos_structure.json', 'w') as f:
            json.dump({
                'structure': structure,
                'available_sections': available_sections,
                'test_results': 'successful_login'
            }, f, indent=2, ensure_ascii=False)
        
        print("\n💾 Estructura guardada en daticos_structure.json")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cerrar sesión
        await daticos_extractor.close_session()
        print("🔚 Sesión cerrada")

if __name__ == "__main__":
    asyncio.run(main())