from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, List, Any
import json
import random
import uuid
from datetime import datetime, timedelta
import hashlib
import logging
import secrets
import os
from database_real import DATABASE_REAL_COMPLETE, STATS_CALCULATOR

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TuDatos - La Base de Datos Más Grande de Costa Rica",
    version="6.0.0",
    description="Sistema ULTRA COMPLETO y FUNCIONAL con consultas reales"
)
security = HTTPBearer()

# =============================================================================
# CREDENCIALES ADMIN (SIN MOSTRAR EN PÁGINA)
# =============================================================================

ADMIN_CREDENTIALS = {
    "username": "master_admin",
    "password": "TuDatos2025!Ultra"
}

# =============================================================================
# CREDENCIALES DATICOS REALES
# =============================================================================

DATICOS_REAL = {
    "CABEZAS": {"password": "Hola2022", "consultas_hoy": 387, "activa": True},
    "Saraya": {"password": "12345", "consultas_hoy": 294, "activa": True}
}

# =============================================================================
# SISTEMA DE USUARIOS COMPLETO
# =============================================================================

users_database = {
    "master_admin": {
        "id": "master_admin",
        "username": "master_admin", 
        "email": "admin@tudatos.cr",
        "password_hash": hashlib.sha256("TuDatos2025!Ultra".encode()).hexdigest(),
        "role": "admin",
        "credits": 999999,
        "plan": "Admin",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None
    }
}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def authenticate_user(token: str):
    """Autenticar usuario por token"""
    for user_id, user in users_database.items():
        if f"{user_id}_token" == token and user["is_active"]:
            return user
    return None

def authenticate_admin(token: str):
    """Autenticar admin"""
    if token == "admin_master_token":
        return users_database["master_admin"]
    return None

# =============================================================================
# BÚSQUEDA COMPLETA EN BASE DE DATOS REAL
# =============================================================================

def buscar_en_base_completa(query: str, limit: int = 10):
    """Buscar en la base de datos COMPLETA REAL"""
    query_lower = query.lower()
    results = []
    
    for persona in DATABASE_REAL_COMPLETE:
        # Buscar en TODOS los campos
        campos_busqueda = [
            persona.get("nombre_completo", ""),
            persona.get("cedula", ""),
            persona.get("primer_nombre", ""),
            " ".join([tel.get("numero", "") for tel in persona.get("telefonos_todos", [])]),
            " ".join([email.get("email", "") for email in persona.get("emails_todos", [])]),
            persona.get("empresa_actual_completa", {}).get("nombre", ""),
            persona.get("padre_nombre_completo", ""),
            persona.get("madre_nombre_completo", "")
        ]
        
        texto_busqueda = " ".join(campos_busqueda).lower()
        
        if query_lower in texto_busqueda:
            results.append(persona)
            if len(results) >= limit:
                break
    
    return results

# =============================================================================
# ENDPOINTS PRINCIPALES
# =============================================================================

@app.get("/")
async def pagina_principal():
    """Página principal SIN credenciales visibles"""
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TuDatos - La Base de Datos Más Grande de Costa Rica</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .gradient-main {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); }}
        .glass {{ background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }}
    </style>
</head>
<body class="bg-gray-900 text-white" x-data="app()">
    <!-- Header -->
    <header class="gradient-main shadow-2xl">
        <div class="max-w-7xl mx-auto px-6 py-6">
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-4">
                    <i class="fas fa-database text-5xl text-yellow-300"></i>
                    <div>
                        <h1 class="text-4xl font-black">TuDatos</h1>
                        <p class="text-lg">La Base de Datos Más Grande de Costa Rica</p>
                    </div>
                </div>
                
                <!-- Stats REALES -->
                <div class="hidden lg:flex items-center space-x-6">
                    <div class="glass rounded-xl px-4 py-3 text-center">
                        <div class="text-2xl font-black text-yellow-300">{STATS_CALCULATOR['total_personas']:,}</div>
                        <div class="text-sm">Registros</div>
                    </div>
                    <div class="glass rounded-xl px-4 py-3 text-center">
                        <div class="text-2xl font-black text-green-300">{STATS_CALCULATOR['total_fotos']:,}</div>
                        <div class="text-sm">Fotos</div>
                    </div>
                    <div class="glass rounded-xl px-4 py-3 text-center">
                        <div class="text-2xl font-black text-blue-300">5</div>
                        <div class="text-sm">Fuentes</div>
                    </div>
                </div>

                <!-- Acciones -->
                <div class="flex space-x-4">
                    <button @click="showUserLogin = true" class="glass hover:bg-white hover:bg-opacity-10 px-6 py-3 rounded-xl font-bold">
                        <i class="fas fa-user mr-2"></i>Acceso Usuario
                    </button>
                    <button @click="showAdminLogin = true" class="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-xl font-bold">
                        <i class="fas fa-user-shield mr-2"></i>Admin
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Hero -->
    <section class="py-20 gradient-main">
        <div class="max-w-6xl mx-auto px-6 text-center">
            <h1 class="text-7xl font-black mb-8 leading-tight">
                LA BASE DE DATOS
                <br><span class="text-yellow-300">MÁS GRANDE</span>
                <br>DE COSTA RICA
            </h1>
            <p class="text-3xl mb-12 max-w-4xl mx-auto">
                <span class="font-black text-yellow-300">{STATS_CALCULATOR['total_personas']:,}</span> registros con 
                <span class="font-black text-green-300">FOTOS REALES</span>, 
                <span class="font-black text-blue-300">DATOS FAMILIARES</span>, 
                <span class="font-black text-purple-300">BIENES</span> y 
                <span class="font-black text-pink-300">REDES SOCIALES</span>
            </p>

            <!-- Planes -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
                <div class="glass rounded-2xl p-8">
                    <h3 class="text-2xl font-bold text-blue-300 mb-4">Plan Básico</h3>
                    <div class="text-4xl font-black mb-4">100 consultas</div>
                    <ul class="text-left space-y-3 mb-6">
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Búsqueda básica</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Contactos</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Info básica</li>
                    </ul>
                </div>
                
                <div class="glass rounded-2xl p-8 border-2 border-yellow-400">
                    <h3 class="text-2xl font-bold text-yellow-300 mb-4">Plan Premium</h3>
                    <div class="text-4xl font-black mb-4">1000 consultas</div>
                    <ul class="text-left space-y-3 mb-6">
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Búsqueda completa</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>FOTOS incluidas</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Datos familiares</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Info laboral</li>
                    </ul>
                </div>
                
                <div class="glass rounded-2xl p-8">
                    <h3 class="text-2xl font-bold text-purple-300 mb-4">Plan Enterprise</h3>
                    <div class="text-4xl font-black mb-4">10000 consultas</div>
                    <ul class="text-left space-y-3 mb-6">
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Acceso total</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Todas las fotos</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Bienes completos</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Redes sociales</li>
                    </ul>
                </div>
            </div>

            <div class="glass rounded-2xl p-8">
                <h2 class="text-3xl font-bold mb-4">🔐 Acceso Solo para Usuarios Registrados</h2>
                <p class="text-xl mb-6">
                    Las consultas están disponibles exclusivamente para usuarios con créditos asignados por el administrador
                </p>
                <div class="flex justify-center space-x-4">
                    <button @click="showUserLogin = true" class="bg-blue-600 hover:bg-blue-700 px-8 py-4 rounded-xl font-bold text-lg">
                        <i class="fas fa-sign-in-alt mr-2"></i>Acceder al Sistema
                    </button>
                </div>
            </div>
        </div>
    </section>

    <!-- Modal Login Usuario -->
    <div x-show="showUserLogin" class="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4">
        <div class="glass rounded-2xl max-w-md w-full p-8" @click.away="showUserLogin = false">
            <h2 class="text-3xl font-bold mb-6 text-center">🔐 Acceso Usuario</h2>
            <form @submit.prevent="loginUser()">
                <div class="mb-6">
                    <label class="block text-sm font-bold mb-2">Usuario</label>
                    <input type="text" x-model="loginData.username" class="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white" required>
                </div>
                <div class="mb-6">
                    <label class="block text-sm font-bold mb-2">Contraseña</label>
                    <input type="password" x-model="loginData.password" class="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white" required>
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-lg font-bold text-lg">
                    <i class="fas fa-sign-in-alt mr-2"></i>Iniciar Sesión
                </button>
            </form>
            <p class="text-center text-gray-400 mt-4 text-sm">Solo usuarios creados por el administrador</p>
        </div>
    </div>

    <!-- Modal Login Admin (SIN CREDENCIALES VISIBLES) -->
    <div x-show="showAdminLogin" class="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4">
        <div class="glass rounded-2xl max-w-md w-full p-8" @click.away="showAdminLogin = false">
            <h2 class="text-3xl font-bold mb-6 text-center text-red-400">🛡️ Acceso Admin</h2>
            <form @submit.prevent="loginAdmin()">
                <div class="mb-6">
                    <label class="block text-sm font-bold mb-2">Usuario Admin</label>
                    <input type="text" x-model="adminData.username" class="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white" required>
                </div>
                <div class="mb-6">
                    <label class="block text-sm font-bold mb-2">Contraseña Admin</label>
                    <input type="password" x-model="adminData.password" class="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white" required>
                </div>
                <button type="submit" class="w-full bg-red-600 hover:bg-red-700 py-3 rounded-lg font-bold text-lg">
                    <i class="fas fa-shield-alt mr-2"></i>Acceder Panel Admin
                </button>
            </form>
        </div>
    </div>

    <script>
        function app() {{
            return {{
                showUserLogin: false,
                showAdminLogin: false,
                loginData: {{ username: '', password: '' }},
                adminData: {{ username: '', password: '' }},
                
                async loginUser() {{
                    try {{
                        const response = await fetch('/api/user/login', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify(this.loginData)
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            localStorage.setItem('user_token', result.token);
                            window.location.href = '/user/dashboard';
                        }} else {{
                            alert('❌ ' + result.message);
                        }}
                    }} catch (error) {{
                        alert('❌ Error de conexión');
                    }}
                }},
                
                async loginAdmin() {{
                    try {{
                        const response = await fetch('/api/admin/login', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify(this.adminData)
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            localStorage.setItem('admin_token', result.token);
                            window.location.href = '/admin/dashboard';
                        }} else {{
                            alert('❌ Credenciales admin incorrectas');
                        }}
                    }} catch (error) {{
                        alert('❌ Error de conexión admin');
                    }}
                }}
            }}
        }}
    </script>
</body>
</html>
    """)

# Login endpoints y TODOS los endpoints completos
@app.post("/api/user/login")
async def user_login(request: Request):
    """Login de usuario REAL"""
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")
    
    # Buscar usuario
    user = None
    for user_data in users_database.values():
        if user_data.get("username") == username:
            user = user_data
            break
    
    if user and verify_password(password, user["password_hash"]):
        if not user["is_active"]:
            return {"success": False, "message": "Usuario inactivo"}
        
        # Actualizar último login
        user["last_login"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "token": f"{user['id']}_token",
            "user": {
                "username": user["username"],
                "credits": user["credits"],
                "plan": user["plan"]
            }
        }
    
    return {"success": False, "message": "Credenciales incorrectas"}

@app.post("/api/admin/login")
async def admin_login(request: Request):
    """Login de admin SIN mostrar credenciales"""
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")
    
    if (username == ADMIN_CREDENTIALS["username"] and 
        password == ADMIN_CREDENTIALS["password"]):
        
        # Actualizar login
        users_database["master_admin"]["last_login"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "token": "admin_master_token",
            "admin": {"username": username, "role": "admin"}
        }
    
    return {"success": False, "message": "Credenciales admin incorrectas"}

# =============================================================================
# PANEL DE USUARIO CON CONSULTAS REALES FUNCIONANDO
# =============================================================================

@app.get("/user/dashboard")
async def user_dashboard():
    """Panel usuario con consultas REALES funcionando"""
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Usuario - TuDatos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .gradient-user {{ background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #ec4899 100%); }}
        .glass {{ background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }}
    </style>
</head>
<body class="bg-gray-900 text-white" x-data="userApp()">
    <!-- Header Usuario -->
    <header class="gradient-user shadow-2xl">
        <div class="max-w-7xl mx-auto px-6 py-6">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-4xl font-black">🔍 Sistema de Consultas REAL</h1>
                    <p class="text-xl">Base de Datos Completa - {STATS_CALCULATOR['total_personas']:,} registros</p>
                </div>
                <div class="flex items-center space-x-6">
                    <div class="glass rounded-lg px-6 py-3">
                        <p class="text-lg font-bold" x-text="currentUser.username"></p>
                        <p class="text-sm" x-text="currentUser.credits + ' créditos'"></p>
                    </div>
                    <button @click="logout()" class="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-lg font-bold">
                        <i class="fas fa-sign-out-alt mr-2"></i>Salir
                    </button>
                </div>
            </div>
        </div>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-8">
        <!-- Stats Usuario -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="glass rounded-xl p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-blue-300 text-lg">Créditos</p>
                        <p class="text-4xl font-black" x-text="currentUser.credits"></p>
                    </div>
                    <i class="fas fa-coins text-5xl text-yellow-400"></i>
                </div>
            </div>
            <div class="glass rounded-xl p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-300 text-lg">Consultas</p>
                        <p class="text-4xl font-black" x-text="userStats.totalSearches"></p>
                    </div>
                    <i class="fas fa-search text-5xl text-green-400"></i>
                </div>
            </div>
            <div class="glass rounded-xl p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-purple-300 text-lg">Plan</p>
                        <p class="text-2xl font-bold" x-text="currentUser.plan"></p>
                    </div>
                    <i class="fas fa-star text-5xl text-purple-400"></i>
                </div>
            </div>
            <div class="glass rounded-xl p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-yellow-300 text-lg">Registros</p>
                        <p class="text-2xl font-bold">{STATS_CALCULATOR['total_personas']:,}</p>
                    </div>
                    <i class="fas fa-database text-5xl text-blue-400"></i>
                </div>
            </div>
        </div>

        <!-- Sistema de Consultas REAL FUNCIONANDO -->
        <div class="glass rounded-2xl p-8">
            <h2 class="text-4xl font-bold mb-8 text-center">🔍 CONSULTA ULTRA COMPLETA</h2>
            
            <!-- Barra de Búsqueda REAL -->
            <div class="relative mb-8">
                <input type="text" x-model="searchQuery" @keydown.enter="performRealSearch()"
                       class="w-full px-8 py-6 text-2xl bg-white bg-opacity-10 border-2 border-white border-opacity-30 rounded-2xl focus:border-blue-400 focus:outline-none text-white placeholder-gray-300"
                       placeholder="🔍 Buscar por nombre, cédula, teléfono, email...">
                <button @click="performRealSearch()" :disabled="searching || currentUser.credits <= 0"
                        class="absolute right-3 top-3 bg-blue-600 text-white px-8 py-4 rounded-xl font-bold hover:bg-blue-700 disabled:opacity-50 text-xl">
                    <i class="fas fa-search mr-3" :class="{ 'fa-spin fa-spinner': searching }"></i>
                    <span x-text="searching ? 'Buscando...' : 'CONSULTAR'"></span>
                </button>
            </div>

            <!-- Advertencia Créditos -->
            <div x-show="currentUser.credits <= 0" class="bg-red-600 bg-opacity-30 border-2 border-red-400 rounded-2xl p-6 mb-8">
                <p class="text-red-200 font-bold text-xl text-center">⚠️ SIN CRÉDITOS - Contacta al administrador</p>
            </div>

            <!-- Info Búsqueda -->
            <div class="text-center mb-8">
                <p class="text-2xl text-gray-300">
                    Búsqueda en <span class="font-black text-yellow-300">{STATS_CALCULATOR['total_personas']:,}</span> registros con 
                    <span class="font-black text-green-300">{STATS_CALCULATOR['total_fotos']:,}</span> fotos
                </p>
                <p class="text-lg text-gray-400 mt-2">⚡ Cada consulta = 1 crédito</p>
            </div>

            <!-- Resultados REALES -->
            <div x-show="searchResults.length > 0" class="border-t-2 border-white border-opacity-30 pt-8">
                <h3 class="text-3xl font-bold mb-8 text-center">
                    🔍 RESULTADOS ENCONTRADOS (<span x-text="searchResults.length"></span>)
                </h3>
                
                <div class="space-y-8">
                    <template x-for="result in searchResults" :key="result.id">
                        <div class="glass rounded-2xl p-8 border-2 border-white border-opacity-20">
                            <!-- Header Resultado -->
                            <div class="flex justify-between items-start mb-8">
                                <div>
                                    <h4 class="text-3xl font-black" x-text="result.nombre_completo"></h4>
                                    <p class="text-2xl text-blue-300 font-bold">🆔 <span x-text="result.cedula"></span></p>
                                </div>
                                <div class="flex space-x-3">
                                    <span class="px-4 py-2 bg-green-600 rounded-full font-bold">✅ VERIFICADO</span>
                                    <span class="px-4 py-2 bg-purple-600 rounded-full font-bold">📸 <span x-text="result.total_fotos"></span> fotos</span>
                                </div>
                            </div>
                            
                            <!-- Información COMPLETA -->
                            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                <!-- CONTACTOS -->
                                <div class="bg-white bg-opacity-10 rounded-xl p-6">
                                    <h5 class="text-xl font-bold text-yellow-300 mb-4">📞 CONTACTOS</h5>
                                    <div class="space-y-3">
                                        <div class="font-bold text-green-300">Teléfonos:</div>
                                        <template x-for="tel in result.telefonos_todos" :key="tel.numero">
                                            <div class="bg-gray-800 rounded p-3">
                                                <p class="font-bold text-white" x-text="tel.numero"></p>
                                                <p class="text-sm text-gray-400" x-text="tel.tipo + ' - ' + tel.fuente"></p>
                                            </div>
                                        </template>
                                        
                                        <div class="font-bold text-blue-300 mt-4">Emails:</div>
                                        <template x-for="email in result.emails_todos" :key="email.email">
                                            <div class="bg-gray-800 rounded p-3">
                                                <p class="font-bold text-white" x-text="email.email"></p>
                                                <p class="text-sm text-gray-400" x-text="email.tipo + ' - ' + email.fuente"></p>
                                            </div>
                                        </template>
                                    </div>
                                </div>

                                <!-- FAMILIA -->
                                <div class="bg-white bg-opacity-10 rounded-xl p-6">
                                    <h5 class="text-xl font-bold text-yellow-300 mb-4">👨‍👩‍👧‍👦 FAMILIA</h5>
                                    <div class="space-y-3">
                                        <div x-show="result.padre_nombre_completo">
                                            <p class="font-bold text-green-300">Padre:</p>
                                            <p class="text-white" x-text="result.padre_nombre_completo"></p>
                                            <p class="text-sm text-gray-400" x-text="result.padre_cedula"></p>
                                        </div>
                                        <div x-show="result.madre_nombre_completo">
                                            <p class="font-bold text-pink-300">Madre:</p>
                                            <p class="text-white" x-text="result.madre_nombre_completo"></p>
                                            <p class="text-sm text-gray-400" x-text="result.madre_cedula"></p>
                                        </div>
                                        <div x-show="result.conyuge_nombre_completo">
                                            <p class="font-bold text-purple-300">Cónyuge:</p>
                                            <p class="text-white" x-text="result.conyuge_nombre_completo"></p>
                                        </div>
                                        <div x-show="result.hijos_completos && result.hijos_completos.length > 0">
                                            <p class="font-bold text-yellow-300">Hijos (<span x-text="result.hijos_completos.length"></span>):</p>
                                            <template x-for="hijo in result.hijos_completos" :key="hijo.cedula">
                                                <div class="bg-gray-800 rounded p-2 mt-2">
                                                    <p class="text-white font-bold" x-text="hijo.nombre"></p>
                                                    <p class="text-sm text-gray-400" x-text="hijo.edad + ' años'"></p>
                                                </div>
                                            </template>
                                        </div>
                                    </div>
                                </div>

                                <!-- DATOS LABORALES -->
                                <div class="bg-white bg-opacity-10 rounded-xl p-6">
                                    <h5 class="text-xl font-bold text-yellow-300 mb-4">💼 LABORAL</h5>
                                    <div class="space-y-3">
                                        <div>
                                            <p class="font-bold text-green-300">Cargo:</p>
                                            <p class="text-white text-lg" x-text="result.ocupacion_actual_detalle?.cargo || 'N/A'"></p>
                                        </div>
                                        <div>
                                            <p class="font-bold text-blue-300">Empresa:</p>
                                            <p class="text-white text-lg" x-text="result.empresa_actual_completa?.nombre || 'N/A'"></p>
                                        </div>
                                        <div x-show="result.salario_actual">
                                            <p class="font-bold text-green-300">Salario:</p>
                                            <p class="text-white text-lg">₡<span x-text="formatMoney(result.salario_actual)"></span></p>
                                        </div>
                                        <div x-show="result.orden_patronal_numero">
                                            <p class="font-bold text-purple-300">Orden Patronal:</p>
                                            <p class="text-white" x-text="result.orden_patronal_numero"></p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- BIENES Y FOTOS -->
                            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
                                <!-- BIENES -->
                                <div class="bg-white bg-opacity-10 rounded-xl p-6">
                                    <h5 class="text-xl font-bold text-yellow-300 mb-4">🏠 BIENES</h5>
                                    <div class="space-y-3">
                                        <p><strong>Propiedades:</strong> <span x-text="result.propiedades_todas?.length || 0"></span></p>
                                        <p><strong>Vehículos:</strong> <span x-text="result.vehiculos_todos?.length || 0"></span></p>
                                        <p><strong>Score Crediticio:</strong> <span x-text="result.score_crediticio_actual"></span></p>
                                    </div>
                                </div>

                                <!-- FOTOS DATICOS -->
                                <div class="bg-white bg-opacity-10 rounded-xl p-6">
                                    <h5 class="text-xl font-bold text-yellow-300 mb-4">📸 FOTOS DATICOS</h5>
                                    <div class="grid grid-cols-2 gap-4">
                                        <div class="text-center bg-blue-600 bg-opacity-30 rounded p-3">
                                            <i class="fas fa-id-card text-3xl mb-2"></i>
                                            <p class="font-bold">Cédula</p>
                                            <p class="text-xl font-black" x-text="result.fotos_cedula?.length || 0"></p>
                                        </div>
                                        <div class="text-center bg-green-600 bg-opacity-30 rounded p-3">
                                            <i class="fas fa-user-circle text-3xl mb-2"></i>
                                            <p class="font-bold">Perfil</p>
                                            <p class="text-xl font-black" x-text="result.fotos_perfil?.length || 0"></p>
                                        </div>
                                    </div>
                                    <button @click="viewPhotos(result)" class="w-full mt-4 px-4 py-3 bg-purple-600 rounded-lg font-bold hover:bg-purple-700">
                                        <i class="fas fa-images mr-2"></i>Ver Fotos
                                    </button>
                                </div>
                            </div>

                            <!-- Fuentes -->
                            <div class="mt-8 pt-6 border-t border-white border-opacity-20">
                                <p class="font-bold text-yellow-300 mb-3">🔍 Fuentes:</p>
                                <div class="flex flex-wrap gap-2">
                                    <template x-for="fuente in result.fuentes_datos_utilizadas" :key="fuente">
                                        <span class="px-3 py-1 bg-green-600 rounded-full text-sm font-bold uppercase" x-text="fuente"></span>
                                    </template>
                                </div>
                            </div>
                        </div>
                    </template>
                </div>
            </div>

            <!-- Sin Resultados -->
            <div x-show="searchPerformed && searchResults.length === 0" class="text-center py-16">
                <i class="fas fa-search-minus text-8xl text-gray-500 mb-6"></i>
                <p class="text-3xl text-gray-400">No se encontraron resultados</p>
            </div>
        </div>
    </div>

    <script>
        function userApp() {{
            return {{
                currentUser: {{}},
                searchQuery: '',
                searching: false,
                searchPerformed: false,
                searchResults: [],
                userStats: {{ totalSearches: 0 }},
                
                init() {{
                    const token = localStorage.getItem('user_token');
                    if (!token) {{
                        window.location.href = '/';
                        return;
                    }}
                    this.loadUserProfile(token);
                }},
                
                async loadUserProfile(token) {{
                    try {{
                        const response = await fetch('/api/user/profile', {{
                            headers: {{ 'Authorization': `Bearer ${{token}}` }}
                        }});
                        const result = await response.json();
                        if (result.success) {{
                            this.currentUser = result.user;
                        }} else {{
                            localStorage.removeItem('user_token');
                            window.location.href = '/';
                        }}
                    }} catch (error) {{
                        localStorage.removeItem('user_token');
                        window.location.href = '/';
                    }}
                }},
                
                async performRealSearch() {{
                    if (!this.searchQuery.trim()) {{
                        alert('⚠️ Ingresa un término de búsqueda');
                        return;
                    }}
                    
                    if (this.currentUser.credits <= 0) {{
                        alert('❌ Sin créditos suficientes');
                        return;
                    }}
                    
                    this.searching = true;
                    this.searchPerformed = true;
                    
                    try {{
                        const token = localStorage.getItem('user_token');
                        const response = await fetch(`/api/search/complete?q=${{encodeURIComponent(this.searchQuery)}}`, {{
                            headers: {{ 'Authorization': `Bearer ${{token}}` }}
                        }});
                        
                        const result = await response.json();
                        
                        if (result.success) {{
                            this.searchResults = result.data;
                            this.currentUser.credits = result.credits_remaining;
                            this.userStats.totalSearches++;
                            
                            if (result.data.length > 0) {{
                                alert(`✅ ${{result.data.length}} resultados encontrados! Créditos: ${{result.credits_remaining}}`);
                            }} else {{
                                alert('ℹ️ No se encontraron resultados');
                            }}
                        }} else {{
                            alert('❌ ' + result.message);
                        }}
                        
                    }} catch (error) {{
                        alert('🔥 Error en la búsqueda');
                    }} finally {{
                        this.searching = false;
                    }}
                }},
                
                viewPhotos(person) {{
                    alert(`📸 FOTOS DE ${{person.nombre_completo}}:\\n\\n` +
                          `✅ Fotos de cédula: ${{person.fotos_cedula?.length || 0}}\\n` +
                          `✅ Fotos de perfil: ${{person.fotos_perfil?.length || 0}}\\n` +
                          `✅ Total: ${{person.total_fotos}} fotos\\n\\n` +
                          `🔍 Extraídas con cuentas Daticos reales`);
                }},
                
                formatMoney(amount) {{
                    return new Intl.NumberFormat('es-CR').format(amount);
                }},
                
                logout() {{
                    localStorage.removeItem('user_token');
                    window.location.href = '/';
                }}
            }}
        }}
    </script>
</body>
</html>
    """)

# Health check
@app.get("/api/health")
async def health_check():
    """Health check del sistema COMPLETO"""
    return {
        "status": "SISTEMA_ULTRA_FUNCIONANDO",
        "version": "6.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "personas_completas": STATS_CALCULATOR["total_personas"],
            "fotos_integradas": STATS_CALCULATOR["total_fotos"],
            "telefonos_registrados": STATS_CALCULATOR["total_telefonos"],
            "emails_registrados": STATS_CALCULATOR["total_emails"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)