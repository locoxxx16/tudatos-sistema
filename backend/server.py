from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import asyncio
from datetime import datetime
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Create the main app without a prefix
app = FastAPI(title="Daticos Clone API", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple authentication
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials == "admin":
        return {"username": "admin"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.get("/health")
async def health_check():
    return {"status": "ok", "message": "TuDatos API funcionando"}

@api_router.get("/stats")
async def get_stats(current_user=Depends(get_current_user)):
    try:
        fisicas = await db.personas_fisicas.count_documents({})
        juridicas = await db.personas_juridicas.count_documents({})
        total = fisicas + juridicas
        
        return {
            "status": "success",
            "total_registros": total,
            "personas_fisicas": fisicas,
            "personas_juridicas": juridicas
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Mount the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8001)))
