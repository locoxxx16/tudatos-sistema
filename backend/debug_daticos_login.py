#!/usr/bin/env python3
"""
Script de debugging avanzado para entender el proceso de login de Daticos
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import logging
import json

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DaticosDebugger:
    def __init__(self):
        self.base_url = "https://www.daticos.com"
        self.session = None
        
    async def debug_login_process(self):
        """Debugging completo del proceso de login"""
        print("🔍 Iniciando debugging del proceso de login de Daticos...")
        
        # Configurar sesión con logging detallado
        timeout = httpx.Timeout(30.0, connect=10.0)
        self.session = httpx.AsyncClient(
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
            # 1. Verificar que el sitio esté accesible
            print("\n🌐 Verificando accesibilidad del sitio...")
            response = await self.session.get(self.base_url)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"URL final: {response.url}")
            
            if response.status_code != 200:
                print(f"❌ Sitio no accesible. Status: {response.status_code}")
                return
                
            # 2. Buscar página de login
            print("\n🔐 Buscando página de login...")
            login_urls_to_try = [
                '/login.php',
                '/login',
                '/admin.php',
                '/index.php',
                '/',
                '/signin.php',
                '/auth.php'
            ]
            
            login_page_content = None
            login_url = None
            
            for url in login_urls_to_try:
                try:
                    full_url = f"{self.base_url}{url}"
                    print(f"   Probando: {full_url}")
                    
                    login_response = await self.session.get(full_url)
                    content = login_response.text.lower()
                    
                    # Buscar indicadores de página de login
                    login_indicators = ['password', 'usuario', 'login', 'iniciar', 'entrar', 'contraseña']
                    if any(indicator in content for indicator in login_indicators):
                        print(f"   ✅ Página de login encontrada: {full_url}")
                        login_page_content = login_response.text
                        login_url = full_url
                        break
                    else:
                        print(f"   ❌ No parece ser página de login")
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            if not login_page_content:
                print("❌ No se pudo encontrar página de login")
                return
                
            # 3. Analizar estructura del formulario de login
            print(f"\n📋 Analizando formulario de login en: {login_url}")
            soup = BeautifulSoup(login_page_content, 'html.parser')
            
            # Guardar HTML para análisis manual
            with open('/app/backend/daticos_login_page.html', 'w', encoding='utf-8') as f:
                f.write(login_page_content)
                
            print("💾 Página de login guardada en daticos_login_page.html")
            
            # Buscar todos los formularios
            forms = soup.find_all('form')
            print(f"📝 Formularios encontrados: {len(forms)}")
            
            for i, form in enumerate(forms):
                print(f"\n🔍 Formulario {i+1}:")
                print(f"   Action: {form.get('action', 'N/A')}")
                print(f"   Method: {form.get('method', 'GET')}")
                
                # Buscar todos los inputs
                inputs = form.find_all('input')
                print(f"   Inputs encontrados: {len(inputs)}")
                
                for inp in inputs:
                    print(f"     - Name: {inp.get('name', 'N/A')}, Type: {inp.get('type', 'text')}, Value: {inp.get('value', 'N/A')}")
                
                # Buscar selects
                selects = form.find_all('select')
                if selects:
                    print(f"   Selects: {len(selects)}")
                    for sel in selects:
                        print(f"     - Name: {sel.get('name', 'N/A')}")
            
            # 4. Intentar diferentes combinaciones de campos de login
            print(f"\n🔐 Probando diferentes combinaciones de login...")
            
            credentials_to_try = [
                {'usuario': 'Saraya', 'password': '12345'},
                {'user': 'Saraya', 'pass': '12345'},
                {'username': 'Saraya', 'password': '12345'},
                {'login': 'Saraya', 'contraseña': '12345'},
                {'email': 'Saraya', 'password': '12345'}
            ]
            
            for form_index, form in enumerate(forms):
                if not form.find('input', attrs={'type': 'password'}):
                    continue  # Skip forms without password field
                    
                print(f"\n🧪 Probando con formulario {form_index + 1}...")
                
                for cred_index, credentials in enumerate(credentials_to_try):
                    print(f"   Intento {cred_index + 1}: {list(credentials.keys())}")
                    
                    # Construir datos del formulario
                    form_data = credentials.copy()
                    
                    # Agregar campos hidden
                    hidden_inputs = form.find_all('input', type='hidden')
                    for inp in hidden_inputs:
                        if inp.get('name') and inp.get('value'):
                            form_data[inp.get('name')] = inp.get('value')
                            print(f"     + Campo hidden: {inp.get('name')} = {inp.get('value')}")
                    
                    try:
                        # Determinar URL de envío
                        action = form.get('action', login_url)
                        if not action.startswith('http'):
                            if action.startswith('/'):
                                submit_url = f"{self.base_url}{action}"
                            else:
                                submit_url = f"{self.base_url}/{action}" if action else login_url
                        else:
                            submit_url = action
                        
                        print(f"     🎯 Enviando a: {submit_url}")
                        print(f"     📦 Datos: {form_data}")
                        
                        # Realizar login
                        login_result = await self.session.post(
                            submit_url,
                            data=form_data,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'}
                        )
                        
                        print(f"     📊 Status: {login_result.status_code}")
                        print(f"     🔗 URL final: {login_result.url}")
                        
                        # Analizar respuesta
                        response_text = login_result.text.lower()
                        
                        # Indicadores de éxito
                        success_indicators = [
                            'bienvenido', 'welcome', 'dashboard', 'panel', 'consulta', 
                            'menu', 'logout', 'salir', 'cerrar sesion', 'perfil'
                        ]
                        
                        # Indicadores de error
                        error_indicators = [
                            'error', 'incorrecto', 'inválido', 'invalid', 'wrong',
                            'usuario no encontrado', 'contraseña incorrecta', 'login failed'
                        ]
                        
                        success_found = [ind for ind in success_indicators if ind in response_text]
                        errors_found = [ind for ind in error_indicators if ind in response_text]
                        
                        print(f"     ✅ Indicadores de éxito: {success_found}")
                        print(f"     ❌ Indicadores de error: {errors_found}")
                        
                        if success_found and not errors_found:
                            print(f"     🎉 ¡LOGIN EXITOSO!")
                            
                            # Guardar página de éxito para análisis
                            with open('/app/backend/daticos_success_page.html', 'w', encoding='utf-8') as f:
                                f.write(login_result.text)
                            
                            return {
                                'success': True,
                                'credentials': credentials,
                                'form_data': form_data,
                                'url': submit_url
                            }
                        else:
                            print(f"     ❌ Login fallido")
                            
                    except Exception as e:
                        print(f"     ❌ Error en intento: {e}")
            
            print("\n❌ Todos los intentos de login fallaron")
            
            # 5. Verificar si hay captcha o medidas anti-bot
            print("\n🤖 Verificando medidas anti-bot...")
            captcha_indicators = ['captcha', 'recaptcha', 'verify', 'robot']
            if any(indicator in login_page_content.lower() for indicator in captcha_indicators):
                print("⚠️  Posible CAPTCHA detectado")
            else:
                print("✅ No se detectó CAPTCHA obvio")
            
        except Exception as e:
            print(f"❌ Error durante debugging: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.session.aclose()

async def main():
    debugger = DaticosDebugger()
    await debugger.debug_login_process()

if __name__ == "__main__":
    asyncio.run(main())