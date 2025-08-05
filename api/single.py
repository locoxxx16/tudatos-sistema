"""
TUDATOS SISTEMA COMPLETO PARA VERCEL
"""
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from typing import Optional

app = FastAPI()

# Configuración de MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = "tudatos_system"

# Cliente MongoDB global
mongo_client = None
database = None

async def get_database():
    global mongo_client, database
    if mongo_client is None:
        try:
            mongo_client = AsyncIOMotorClient(MONGO_URL)
            database = mongo_client[DATABASE_NAME]
            await mongo_client.admin.command('ping')
        except Exception as e:
            print(f"Error conectando a MongoDB: {e}")
            database = None
    return database

@app.get("/")
async def home():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>TuDatos - Sistema Completo</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>.gradient-main{background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%)}.glass{background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.1)}</style>
</head><body class="bg-gray-900 text-white">
<header class="gradient-main shadow-2xl"><div class="max-w-7xl mx-auto px-6 py-6">
<h1 class="text-6xl font-black text-center">TuDatos</h1>
<p class="text-2xl text-center mt-4">La Base de Datos Más Grande de Costa Rica</p>
<div class="text-center mt-8"><div class="inline-block glass rounded-xl px-8 py-4">
<div class="text-4xl font-black text-yellow-300" id="recordCount">5,947,094</div>
<div>Registros Disponibles</div></div></div></div></header>

<section class="py-20 px-6">
<div class="max-w-4xl mx-auto">
<h2 class="text-5xl font-black mb-8 text-center">BÚSQUEDA COMPLETA</h2>

<div class="bg-gray-800 p-8 rounded-2xl mb-8">
<form id="searchForm" class="space-y-4">
<input type="text" id="searchQuery" placeholder="Buscar por cédula, nombre, teléfono, email..." 
class="w-full p-4 rounded-lg bg-gray-700 text-white text-xl" required>
<button type="submit" class="w-full bg-yellow-500 text-black p-4 rounded-lg text-xl font-bold hover:bg-yellow-400">
🔍 BUSCAR AHORA
</button>
</form>
</div>

<div id="results" class="hidden bg-gray-800 p-8 rounded-2xl">
<h3 class="text-2xl font-bold mb-4">Resultados:</h3>
<div id="resultContent"></div>
</div>

<div class="bg-yellow-500 text-black p-6 rounded-2xl text-center">
<h3 class="text-2xl font-bold mb-4">🚀 Para Acceso Completo</h3>
<p class="text-xl font-bold">📧 jykinternacional@gmail.com</p>
</div>
</div></section>

<script>
document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const query = document.getElementById('searchQuery').value;
    const results = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');
    
    resultContent.innerHTML = '<div class="text-center">🔍 Buscando...</div>';
    results.classList.remove('hidden');
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success && data.results.length > 0) {
            resultContent.innerHTML = data.results.map(result => `
                <div class="bg-gray-700 p-4 rounded-lg mb-4">
                    <h4 class="text-xl font-bold text-yellow-300">${result.nombre || 'N/A'}</h4>
                    <p><strong>Cédula:</strong> ${result.cedula || 'N/A'}</p>
                    <p><strong>Teléfono:</strong> ${result.telefono || 'N/A'}</p>
                    <p><strong>Email:</strong> ${result.email || 'N/A'}</p>
                </div>
            `).join('');
        } else {
            resultContent.innerHTML = '<div class="text-center text-gray-400">No se encontraron resultados</div>';
        }
    } catch (error) {
        resultContent.innerHTML = '<div class="text-center text-red-400">Error en la búsqueda</div>';
    }
});

// Actualizar contador de registros
fetch('/api/count').then(r => r.json()).then(data => {
    if (data.count) document.getElementById('recordCount').textContent = data.count.toLocaleString();
});
</script>
</body></html>""")

@app.get("/api/search")
async def search_records(q: str):
    db = await get_database()
    if not db:
        return JSONResponse({"success": False, "error": "Base de datos no disponible"})
    
    try:
        # Búsqueda en múltiples colecciones
        collections = ["personas", "empresas", "juridicas", "sicop_data"]
        all_results = []
        
        for collection_name in collections:
            collection = db[collection_name]
            
            # Búsqueda por cédula, nombre, teléfono, email
            query = {
                "$or": [
                    {"cedula": {"$regex": q, "$options": "i"}},
                    {"nombre": {"$regex": q, "$options": "i"}},
                    {"telefono": {"$regex": q, "$options": "i"}},
                    {"email": {"$regex": q, "$options": "i"}},
                    {"nombre_comercial": {"$regex": q, "$options": "i"}},
                    {"razon_social": {"$regex": q, "$options": "i"}}
                ]
            }
            
            cursor = collection.find(query).limit(10)
            results = await cursor.to_list(length=10)
            
            for result in results:
                result["_id"] = str(result["_id"])  # Convertir ObjectId a string
                result["fuente"] = collection_name
                all_results.append(result)
        
        return JSONResponse({
            "success": True,
            "results": all_results[:20],  # Máximo 20 resultados
            "total": len(all_results)
        })
        
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@app.get("/api/count")
async def get_record_count():
    db = await get_database()
    if not db:
        return JSONResponse({"count": 5947094})  # Fallback estático
    
    try:
        collections = ["personas", "empresas", "juridicas", "sicop_data"]
        total_count = 0
        
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            total_count += count
        
        return JSONResponse({"count": total_count})
        
    except Exception as e:
        return JSONResponse({"count": 5947094})  # Fallback en caso de error

@app.get("/api/status")
async def status():
    db = await get_database()
    return JSONResponse({
        "status": "ok",
        "message": "TuDatos Sistema funcionando correctamente",
        "database": "connected" if db else "disconnected"
    })

@app.get("/{path:path}")
async def catch_all(path: str = ""):
    return await home()

handler = app