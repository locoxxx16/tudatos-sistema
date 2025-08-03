from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Crear app
app = FastAPI(title="TuDatos API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "TuDatos Sistema funcionando correctamente"}

@app.get("/api/health")
async def health():
    return {"status": "success", "message": "API funcionando"}

@app.get("/api/stats")
async def stats():
    return {
        "status": "success",
        "total_registros": 310840,
        "mensaje": "Sistema TuDatos activo"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
