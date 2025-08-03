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

# Login endpoints y resto del código continúa igual...
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