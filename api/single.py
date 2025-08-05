import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import motor.motor_asyncio
from typing import List, Dict, Any, Optional
import re
from urllib.parse import quote_plus
import asyncio

# Configuración de MongoDB ObjectRocket
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = "datatico_cr"

# Cliente MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

app = FastAPI(title="DataTico CR - Ultra Complete Search", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página principal con búsqueda integrada"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DataTico CR - Búsqueda de Datos</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .search-box { width: 100%; padding: 15px; font-size: 16px; border: 2px solid #007bff; border-radius: 5px; }
            .search-btn { background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-left: 10px; }
            .result { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .loading { text-align: center; color: #666; }
            .stats { background: #e7f3ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🇨🇷 DataTico CR - Búsqueda Ultra Completa</h1>
        <p>Base de datos con <strong>5.9+ millones de registros</strong> de Costa Rica</p>
        
        <div style="display: flex; margin: 20px 0;">
            <input type="text" id="searchInput" class="search-box" placeholder="Busca por cédula, nombre, empresa, teléfono..." />
            <button onclick="search()" class="search-btn">🔍 Buscar</button>
        </div>
        
        <div id="stats" class="stats" style="display: none;"></div>
        <div id="results"></div>

        <script>
            async function search() {
                const query = document.getElementById('searchInput').value.trim();
                if (!query) return;
                
                document.getElementById('results').innerHTML = '<div class="loading">🔍 Buscando en 5.9M+ registros...</div>';
                document.getElementById('stats').style.display = 'none';
                
                try {
                    const response = await fetch(`/api/ultra-search?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    if (data.results && data.results.length > 0) {
                        document.getElementById('stats').innerHTML = 
                            `📊 <strong>${data.total_found}</strong> resultados encontrados en <strong>${data.search_time_ms}ms</strong>`;
                        document.getElementById('stats').style.display = 'block';
                        
                        document.getElementById('results').innerHTML = data.results.map(result => 
                            `<div class="result">
                                <strong>${result.tipo || 'Registro'}</strong><br>
                                ${Object.entries(result.data || {}).map(([k,v]) => 
                                    k !== '_id' ? `<strong>${k}:</strong> ${v}<br>` : ''
                                ).join('')}
                            </div>`
                        ).join('');
                    } else {
                        document.getElementById('results').innerHTML = 
                            '<div class="result">❌ No se encontraron resultados</div>';
                    }
                } catch (error) {
                    document.getElementById('results').innerHTML = 
                        '<div class="result">⚠️ Error en la búsqueda</div>';
                }
            }
            
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') search();
            });
        </script>
    </body>
    </html>
    """

@app.get("/api/ultra-search")
async def ultra_search(q: str):
    """Búsqueda ultra completa en todas las colecciones"""
    start_time = asyncio.get_event_loop().time()
    
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query muy corto")
    
    query = q.strip()
    results = []
    
    # Colecciones principales
    collections = [
        'personas_fisicas_fast2m',
        'personas_juridicas_fast2m', 
        'tse_datos_hibridos',
        'personas_fisicas',
        'ultra_deep_extraction',
        'personas_juridicas',
        'daticos_datos_masivos'
    ]
    
    # Búsqueda por tipo de dato
    search_patterns = []
    
    # Si es cédula (solo números)
    if query.replace('-', '').isdigit():
        cedula_clean = query.replace('-', '')
        search_patterns.extend([
            {"cedula": {"$regex": cedula_clean, "$options": "i"}},
            {"cedula_juridica": {"$regex": cedula_clean, "$options": "i"}},
            {"numero_cedula": {"$regex": cedula_clean, "$options": "i"}},
        ])
    
    # Búsqueda de texto general
    search_patterns.extend([
        {"nombre": {"$regex": query, "$options": "i"}},
        {"nombre_completo": {"$regex": query, "$options": "i"}}, 
        {"primer_apellido": {"$regex": query, "$options": "i"}},
        {"segundo_apellido": {"$regex": query, "$options": "i"}},
        {"razon_social": {"$regex": query, "$options": "i"}},
        {"telefono": {"$regex": query.replace('-', ''), "$options": "i"}},
        {"email": {"$regex": query, "$options": "i"}},
    ])
    
    # Búsqueda en cada colección
    for collection_name in collections:
        try:
            collection = db[collection_name]
            
            # Buscar con OR de todos los patrones
            cursor = collection.find(
                {"$or": search_patterns}
            ).limit(50)  # Limitar resultados por colección
            
            async for doc in cursor:
                # Limpiar _id para JSON
                if '_id' in doc:
                    del doc['_id']
                
                results.append({
                    "tipo": collection_name.replace('_', ' ').title(),
                    "coleccion": collection_name,
                    "data": doc
                })
                
                if len(results) >= 100:  # Límite total
                    break
                    
        except Exception as e:
            continue  # Ignorar errores de colecciones
    
    end_time = asyncio.get_event_loop().time()
    search_time_ms = int((end_time - start_time) * 1000)
    
    return {
        "results": results,
        "total_found": len(results),
        "search_time_ms": search_time_ms,
        "query": query
    }

@app.get("/api/health")
async def health_check():
    """Check de salud de la aplicación"""
    try:
        # Test de conexión a MongoDB
        await client.admin.command('ping')
        
        # Contar registros en colección principal
        main_collection = db['personas_fisicas_fast2m']
        total_records = await main_collection.count_documents({})
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_records": total_records,
            "database_name": DATABASE_NAME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
