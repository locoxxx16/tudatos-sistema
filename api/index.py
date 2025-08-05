"""
HANDLER ULTRA-SIMPLE PARA VERCEL
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

# App ultra ligera
app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>TuDatos - La Base de Datos Más Grande de Costa Rica</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-main { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); }
        .glass { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }
    </style>
</head>
<body class="bg-gray-900 text-white">
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
                <div class="grid grid-cols-3 gap-6">
                    <div class="glass rounded-xl px-4 py-3 text-center">
                        <div class="text-2xl font-black text-yellow-300">5,947,094</div>
                        <div class="text-sm">Registros</div>
                    </div>
                    <div class="glass rounded-xl px-4 py-3 text-center">
                        <div class="text-2xl font-black text-green-300">8,504,424</div>
                        <div class="text-sm">Fotos</div>
                    </div>
                    <div class="glass rounded-xl px-4 py-3 text-center">
                        <div class="text-2xl font-black text-blue-300">5</div>
                        <div class="text-sm">Fuentes</div>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <section class="py-20 gradient-main">
        <div class="max-w-6xl mx-auto px-6 text-center">
            <h1 class="text-7xl font-black mb-8 leading-tight">
                LA BASE DE DATOS
                <br><span class="text-yellow-300">MÁS GRANDE</span>
                <br>DE COSTA RICA
            </h1>
            <p class="text-3xl mb-12 max-w-4xl mx-auto">
                <span class="font-black text-yellow-300">5,947,094</span> registros con 
                <span class="font-black text-green-300">FOTOS REALES</span>, 
                <span class="font-black text-blue-300">DATOS FAMILIARES</span>, 
                <span class="font-black text-purple-300">BIENES</span> y 
                <span class="font-black text-pink-300">REDES SOCIALES</span>
            </p>
            
            <div class="bg-yellow-500 text-black p-6 rounded-2xl mb-8 max-w-2xl mx-auto">
                <h3 class="text-2xl font-bold mb-4">🚀 Sistema en Desarrollo</h3>
                <p class="text-lg">Para acceso completo a consultas y funcionalidades:</p>
                <p class="font-bold text-xl mt-2">📧 jykinternacional@gmail.com</p>
            </div>
        </div>
    </section>

    <footer class="bg-gray-800 py-8">
        <div class="max-w-6xl mx-auto px-6 text-center">
            <p class="text-xl text-gray-300 mb-4">
                💌 Contacto: <strong>jykinternacional@gmail.com</strong>
            </p>
            <p class="text-gray-400">© 2025 TuDatos - La base de datos más completa de Costa Rica</p>
        </div>
    </footer>
</body>
</html>
    """)

@app.get("/api/health")
async def health():
    return {
        "status": "OK",
        "records": 5947094,
        "timestamp": datetime.utcnow().isoformat()
    }

# Handler para Vercel
handler = app