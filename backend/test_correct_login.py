#!/usr/bin/env python3
"""
Script para probar login con los campos correctos identificados
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def test_login_saraya():
    """Probar login con credenciales Saraya usando campos correctos"""
    
    print("🔐 Probando login con Saraya y campos correctos...")
    
    timeout = httpx.Timeout(30.0, connect=10.0)
    session = httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    )
    
    try:
        # Datos del formulario según el HTML analizado
        form_data = {
            'login': 'Saraya',        # Campo correcto encontrado en el HTML
            'password': '12345',      # Campo correcto encontrado en el HTML  
            'submit': 'Ingresar'      # Botón submit
        }
        
        print(f"📦 Enviando datos: {form_data}")
        
        # Realizar login
        login_response = await session.post(
            "https://www.daticos.com/login.php",
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"📊 Status Code: {login_response.status_code}")
        print(f"🔗 URL final: {login_response.url}")
        
        # Analizar respuesta
        response_text = login_response.text.lower()
        
        # Indicadores de éxito más específicos
        success_indicators = [
            'bienvenido', 'welcome', 'dashboard', 'panel', 'consulta',
            'menu principal', 'logout', 'salir', 'cerrar sesion',
            'opciones', 'busqueda', 'reportes'
        ]
        
        # Indicadores de error
        error_indicators = [
            'usuario o contraseña incorrecto', 'credenciales inválidas',
            'login incorrecto', 'acceso denegado', 'error de autenticacion'
        ]
        
        success_found = [ind for ind in success_indicators if ind in response_text]
        errors_found = [ind for ind in error_indicators if ind in response_text]
        
        print(f"✅ Indicadores de éxito encontrados: {success_found}")
        print(f"❌ Indicadores de error encontrados: {errors_found}")
        
        # Verificar si hay elementos que indican login exitoso
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # Buscar enlaces o elementos que aparecen solo después del login
        dashboard_elements = soup.find_all(['a', 'div', 'span'], string=lambda text: 
            text and any(keyword in text.lower() for keyword in ['consulta', 'busqueda', 'reporte', 'logout', 'salir']))
        
        print(f"🔍 Elementos de dashboard encontrados: {len(dashboard_elements)}")
        for elem in dashboard_elements[:5]:  # Mostrar primeros 5
            print(f"   - {elem.name}: {elem.get_text(strip=True)}")
        
        # Verificar cookies de sesión
        cookies = dict(login_response.cookies)
        print(f"🍪 Cookies recibidas: {list(cookies.keys())}")
        
        # Guardar página de respuesta para análisis
        with open('/app/backend/daticos_login_response.html', 'w', encoding='utf-8') as f:
            f.write(login_response.text)
        print("💾 Respuesta guardada en daticos_login_response.html")
        
        # Determinar resultado
        if success_found or dashboard_elements or 'PHPSESSID' in cookies:
            print("🎉 ¡LOGIN PROBABLEMENTE EXITOSO!")
            
            # Probar acceso a una página interna
            try:
                internal_page = await session.get("https://www.daticos.com/consulta.php")
                print(f"🔍 Acceso a página interna - Status: {internal_page.status_code}")
                
                if internal_page.status_code == 200 and 'login.php' not in str(internal_page.url):
                    print("✅ Confirmado: Acceso a páginas internas exitoso")
                    return True
                else:
                    print("❌ Redirección a login - sesión no establecida")
                    
            except Exception as e:
                print(f"❌ Error probando páginas internas: {e}")
                
        else:
            print("❌ Login fallido - no se encontraron indicadores de éxito")
            
        return False
        
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await session.aclose()

if __name__ == "__main__":
    result = asyncio.run(test_login_saraya())
    print(f"\n🎯 Resultado final: {'✅ EXITOSO' if result else '❌ FALLIDO'}")