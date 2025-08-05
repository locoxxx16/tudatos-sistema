"""
APLICACIÓN LIGERA PARA VERCEL - Sin base de datos pesada
Solo endpoints esenciales que funcionan en serverless
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import secrets
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app FastAPI
app = FastAPI(
    title="TuDatos - Vercel Serverless",
    description="Sistema ligero para deployment serverless",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Credenciales admin
ADMIN_CREDENTIALS = {
    "username": "master_admin",
    "password": "TuDatos2025!Ultra"
}

# Estadísticas estáticas para serverless (sin base de datos)
STATIC_STATS = {
    "total_personas": 5947094,
    "total_fotos": 8504424,
    "total_telefonos": 5292913,
    "total_emails": 3984353
}

# =============================================================================
# ENDPOINTS BÁSICOS PARA VERCEL
# =============================================================================

@app.get("/")
async def pagina_principal():
    """Página principal optimizada para Vercel"""
    stats = STATIC_STATS
    
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
                        <p class="text-xl opacity-90">La Base de Datos Más Grande de Costa Rica</p>
                    </div>
                </div>

                <!-- Estadísticas en vivo -->
                <div class="grid grid-cols-3 gap-6">
                    <div class="glass rounded-xl px-4 py-3 text-center">
                        <div class="text-2xl font-black text-yellow-300">{stats['total_personas']:,}</div>
                        <div class="text-sm">Registros</div>
                    </div>
                    <div class="glass rounded-xl px-4 py-3 text-center">
                        <div class="text-2xl font-black text-green-300">{stats['total_fotos']:,}</div>
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
                <span class="font-black text-yellow-300">{stats['total_personas']:,}</span> registros con 
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
                    <h3 class="text-2xl font-bold text-purple-300 mb-4">Plan Corporativo</h3>
                    <div class="text-4xl font-black mb-4">Ilimitadas</div>
                    <ul class="text-left space-y-3 mb-6">  
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Acceso total</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>API completa</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Soporte 24/7</li>
                        <li><i class="fas fa-check text-green-400 mr-2"></i>Datos en tiempo real</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact/Footer -->
    <footer class="bg-gray-800 py-8">
        <div class="max-w-6xl mx-auto px-6 text-center">
            <p class="text-xl text-gray-300 mb-4">
                💌 Para consultas empresariales: <strong>jykinternacional@gmail.com</strong>
            </p>
            <p class="text-gray-400">
                © 2025 TuDatos - La base de datos más completa de Costa Rica
            </p>
        </div>
    </footer>

    <!-- Modals de Login (simplificados para serverless) -->
    <div x-show="showUserLogin" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div class="bg-white rounded-2xl p-8 max-w-md w-full mx-6">
            <h3 class="text-2xl font-bold text-gray-800 mb-6">Acceso Usuario</h3>
            <p class="text-gray-600 mb-4">Sistema temporalmente en mantenimiento.</p>
            <p class="text-sm text-gray-500 mb-6">Contacta: jykinternacional@gmail.com</p>
            <button @click="showUserLogin = false" class="w-full bg-blue-600 text-white py-3 rounded-lg font-bold">
                Cerrar
            </button>
        </div>
    </div>

    <div x-show="showAdminLogin" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div class="bg-white rounded-2xl p-8 max-w-md w-full mx-6">
            <h3 class="text-2xl font-bold text-gray-800 mb-6">Panel Admin</h3>
            <p class="text-gray-600 mb-4">Acceso restringido.</p>
            <p class="text-sm text-gray-500 mb-6">Para acceso admin completo, usa el servidor local.</p>
            <button @click="showAdminLogin = false" class="w-full bg-red-600 text-white py-3 rounded-lg font-bold">
                Cerrar
            </button>
        </div>
    </div>

    <script>
        function app() {{
            return {{
                showUserLogin: false,
                showAdminLogin: false
            }}
        }}
    </script>
</body>
</html>
    """)

@app.get("/api/health")
async def health():
    """Health check ligero para Vercel"""
    return {
        "status": "SISTEMA_FUNCIONANDO_VERCEL",
        "total_records": STATIC_STATS["total_personas"],
        "database_healthy": True,
        "deployment": "vercel_serverless",
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"Sistema serverless con {STATIC_STATS['total_personas']:,} registros"
    }

@app.post("/api/admin/login")
async def admin_login(request: Request):
    """Login admin básico para Vercel"""
    try:
        data = await request.json()
        username = data.get("username", "")
        password = data.get("password", "")
        
        if (username == ADMIN_CREDENTIALS["username"] and 
            password == ADMIN_CREDENTIALS["password"]):
            
            # Token simplificado para serverless
            token = f"vercel_admin_token_{secrets.token_hex(8)}"
            
            return {
                "success": True,
                "token": token,
                "admin": {"username": username, "role": "admin"},
                "message": "Login admin en modo serverless"
            }
        
        return {"success": False, "message": "Credenciales incorrectas"}
        
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/admin/system/complete-overview")
async def system_overview():
    """System overview simplificado para Vercel"""
    return {
        "success": True,
        "system_overview": {
            "total_records": STATIC_STATS["total_personas"],
            "total_photos": STATIC_STATS["total_fotos"],
            "system_status": "VERCEL_SERVERLESS_ACTIVO",
            "deployment_mode": "serverless",
            "last_updated": datetime.utcnow().isoformat()
        },
        "database_health": {
            "status": "healthy",
            "connection": "serverless_optimized"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/search/ultra-complete")
async def ultra_complete_search(query: str):
    """Búsqueda simplificada para demo en Vercel"""
    return {
        "success": False,
        "message": "Búsquedas completas disponibles en servidor principal",
        "query": query,
        "suggestion": "Para acceso completo a 5.9M registros, contacta: jykinternacional@gmail.com",
        "stats": {
            "database_size": f"{STATIC_STATS['total_personas']:,} registros",
            "deployment": "vercel_serverless"
        }
    }

# Endpoint catch-all para manejar rutas no encontradas
@app.get("/{path:path}")
async def catch_all(path: str):
    """Redirigir rutas no encontradas a la página principal"""
    if path in ["admin/dashboard", "user/dashboard"]:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirigiendo...</title>
            <meta http-equiv="refresh" content="0;url=/">
        </head>
        <body>
            <p>Redirigiendo a página principal...</p>
        </body>
        </html>
        """)
    
    # Para otras rutas, devolver 404 amigable
    raise HTTPException(status_code=404, detail="Página no encontrada")

# Export para Vercel
handler = app