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
from datetime import datetime
from enum import Enum
from external_apis import costa_rica_integrator, DataCleaner
from data_updater import data_updater, start_data_updater, run_manual_update
from admin_panel import AdminPanelManager, AdminPanelModels, get_admin_manager
from daticos_extractor import daticos_extractor


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Daticos Clone API", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

security = HTTPBearer()

# Enums
class PersonType(str, Enum):
    FISICA = "fisica"
    JURIDICA = "juridica"

class BusinessSector(str, Enum):
    COMERCIO = "comercio"
    SERVICIOS = "servicios"
    INDUSTRIA = "industria"
    TECNOLOGIA = "tecnologia"
    EDUCACION = "educacion"
    SALUD = "salud"
    CONSTRUCCION = "construccion"
    TURISMO = "turismo"
    AGRICULTURA = "agricultura"
    OTROS = "otros"

# Location Models
class Provincia(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    codigo: str

class Canton(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    codigo: str
    provincia_id: str

class Distrito(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    codigo: str
    canton_id: str

# Person/Entity Models
class PersonaFisica(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cedula: str
    nombre: str
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    provincia_id: str
    canton_id: str
    distrito_id: str
    direccion_exacta: Optional[str] = None
    ocupacion: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PersonaJuridica(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cedula_juridica: str
    nombre_comercial: str
    razon_social: str
    sector_negocio: BusinessSector
    telefono: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    provincia_id: str
    canton_id: str
    distrito_id: str
    direccion_exacta: Optional[str] = None
    numero_empleados: Optional[int] = None
    fecha_constitucion: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# User and Auth Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserLogin(BaseModel):
    login: str
    password: str

# Search and Query Models
class DemographicQuery(BaseModel):
    provincia_id: Optional[str] = None
    canton_id: Optional[str] = None
    distrito_id: Optional[str] = None
    person_type: Optional[PersonType] = None
    business_sector: Optional[BusinessSector] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None

class ProspectingQuery(BaseModel):
    sector_negocio: Optional[BusinessSector] = None
    provincia_id: Optional[str] = None
    canton_id: Optional[str] = None
    distrito_id: Optional[str] = None
    min_employees: Optional[int] = None
    max_employees: Optional[int] = None

# SMS Models
class SMSCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    message: str
    target_query: Dict[str, Any]
    scheduled_date: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, sent, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_count: int = 0
    failed_count: int = 0

# Response Models
class DemographicStats(BaseModel):
    total_personas_fisicas: int
    total_personas_juridicas: int
    by_provincia: Dict[str, int]
    by_sector: Dict[str, int]
    by_age_group: Dict[str, int]

class ProspectResult(BaseModel):
    total_prospects: int
    prospects: List[PersonaJuridica]
    by_sector: Dict[str, int]
    by_location: Dict[str, int]

# Auth function (simplified for demo)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In real implementation, validate JWT token
    return {"username": "admin", "is_active": True}

# Routes
@api_router.get("/")
async def root():
    return {"message": "Daticos Clone API - Todo en Base de Datos", "version": "2.0.0"}

# Authentication
@api_router.post("/auth/login")
async def login(user_login: UserLogin):
    # Simplified auth - in real app, hash passwords and use JWT
    if user_login.login == "admin" and user_login.password == "admin123":
        return {
            "access_token": "demo-token",
            "token_type": "bearer",
            "user": {
                "username": "admin",
                "full_name": "Administrador Daticos",
                "is_active": True
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Location endpoints
@api_router.get("/locations/provincias", response_model=List[Provincia])
async def get_provincias():
    provincias = await db.provincias.find().to_list(100)
    return [Provincia(**p) for p in provincias]

@api_router.get("/locations/cantones/{provincia_id}", response_model=List[Canton])
async def get_cantones(provincia_id: str):
    cantones = await db.cantones.find({"provincia_id": provincia_id}).to_list(100)
    return [Canton(**c) for c in cantones]

@api_router.get("/locations/distritos/{canton_id}", response_model=List[Distrito])
async def get_distritos(canton_id: str):
    distritos = await db.distritos.find({"canton_id": canton_id}).to_list(100)
    return [Distrito(**d) for d in distritos]

# Demographics endpoints
@api_router.post("/demographics/query", response_model=DemographicStats)
async def query_demographics(query: DemographicQuery, current_user=Depends(get_current_user)):
    # Build MongoDB query
    filters_fisica = {}
    filters_juridica = {}
    
    if query.provincia_id:
        filters_fisica["provincia_id"] = query.provincia_id
        filters_juridica["provincia_id"] = query.provincia_id
    if query.canton_id:
        filters_fisica["canton_id"] = query.canton_id
        filters_juridica["canton_id"] = query.canton_id
    if query.distrito_id:
        filters_fisica["distrito_id"] = query.distrito_id
        filters_juridica["distrito_id"] = query.distrito_id
    
    if query.business_sector:
        filters_juridica["sector_negocio"] = query.business_sector
    
    # Count totals
    total_fisica = await db.personas_fisicas.count_documents(filters_fisica)
    total_juridica = await db.personas_juridicas.count_documents(filters_juridica)
    
    # Get statistics by province
    provincia_stats = {}
    provincias = await db.provincias.find().to_list(100)
    for prov in provincias:
        count = await db.personas_fisicas.count_documents({**filters_fisica, "provincia_id": prov["id"]})
        count += await db.personas_juridicas.count_documents({**filters_juridica, "provincia_id": prov["id"]})
        provincia_stats[prov["nombre"]] = count
    
    # Get statistics by business sector
    sector_stats = {}
    for sector in BusinessSector:
        count = await db.personas_juridicas.count_documents({**filters_juridica, "sector_negocio": sector})
        sector_stats[sector.value] = count
    
    return DemographicStats(
        total_personas_fisicas=total_fisica,
        total_personas_juridicas=total_juridica,
        by_provincia=provincia_stats,
        by_sector=sector_stats,
        by_age_group={"18-30": 0, "31-50": 0, "51+": 0}  # Simplified
    )

# Prospecting endpoints
@api_router.post("/prospecting/query", response_model=ProspectResult)
async def query_prospects(query: ProspectingQuery, current_user=Depends(get_current_user)):
    filters = {}
    
    if query.sector_negocio:
        filters["sector_negocio"] = query.sector_negocio
    if query.provincia_id:
        filters["provincia_id"] = query.provincia_id
    if query.canton_id:
        filters["canton_id"] = query.canton_id
    if query.distrito_id:
        filters["distrito_id"] = query.distrito_id
    if query.min_employees:
        filters["numero_empleados"] = {"$gte": query.min_employees}
    if query.max_employees:
        if "numero_empleados" in filters:
            filters["numero_empleados"]["$lte"] = query.max_employees
        else:
            filters["numero_empleados"] = {"$lte": query.max_employees}
    
    prospects_data = await db.personas_juridicas.find(filters).limit(100).to_list(100)
    prospects = [PersonaJuridica(**p) for p in prospects_data]
    
    # Statistics
    sector_stats = {}
    location_stats = {}
    for prospect in prospects:
        sector_stats[prospect.sector_negocio] = sector_stats.get(prospect.sector_negocio, 0) + 1
        location_key = f"{prospect.provincia_id}-{prospect.canton_id}"
        location_stats[location_key] = location_stats.get(location_key, 0) + 1
    
    return ProspectResult(
        total_prospects=len(prospects),
        prospects=prospects,
        by_sector=sector_stats,
        by_location=location_stats
    )

# SMS Campaign endpoints
@api_router.post("/sms/campaigns", response_model=SMSCampaign)
async def create_sms_campaign(campaign: SMSCampaign, current_user=Depends(get_current_user)):
    campaign_dict = campaign.dict()
    await db.sms_campaigns.insert_one(campaign_dict)
    return campaign

@api_router.get("/sms/campaigns", response_model=List[SMSCampaign])
async def get_sms_campaigns(current_user=Depends(get_current_user)):
    campaigns = await db.sms_campaigns.find().to_list(100)
    return [SMSCampaign(**c) for c in campaigns]

# Helper function to convert ObjectId to string
def convert_objectid_to_string(data):
    """Convert MongoDB ObjectId to string for JSON serialization"""
    if isinstance(data, dict):
        if "_id" in data:
            data["id"] = str(data["_id"])
            del data["_id"]
        for key, value in data.items():
            data[key] = convert_objectid_to_string(value)
    elif isinstance(data, list):
        return [convert_objectid_to_string(item) for item in data]
    return data

# Enhanced Search endpoints with external data integration
@api_router.get("/search/cedula/{cedula}")
async def search_by_cedula(cedula: str, enrich: bool = True, current_user=Depends(get_current_user)):
    """Search person by cedula with optional data enrichment from external sources"""
    
    # First, search in local database
    local_result = None
    
    # Search in personas fisicas
    persona_fisica = await db.personas_fisicas.find_one({"cedula": cedula})
    if persona_fisica:
        # Convert ObjectId to string
        persona_fisica = convert_objectid_to_string(persona_fisica)
        
        # Get location info
        distrito = await db.distritos.find_one({"id": persona_fisica["distrito_id"]})
        canton = await db.cantones.find_one({"id": persona_fisica["canton_id"]})
        provincia = await db.provincias.find_one({"id": persona_fisica["provincia_id"]})
        
        local_result = {
            "type": "fisica",
            "found": True,
            "data": {
                **persona_fisica,
                "distrito_nombre": distrito["nombre"] if distrito else "N/A",
                "canton_nombre": canton["nombre"] if canton else "N/A", 
                "provincia_nombre": provincia["nombre"] if provincia else "N/A"
            }
        }
    
    # Search in personas juridicas
    if not local_result:
        persona_juridica = await db.personas_juridicas.find_one({"cedula_juridica": cedula})
        if persona_juridica:
            # Convert ObjectId to string
            persona_juridica = convert_objectid_to_string(persona_juridica)
            
            # Get location info
            distrito = await db.distritos.find_one({"id": persona_juridica["distrito_id"]})
            canton = await db.cantones.find_one({"id": persona_juridica["canton_id"]})
            provincia = await db.provincias.find_one({"id": persona_juridica["provincia_id"]})
            
            local_result = {
                "type": "juridica", 
                "found": True,
                "data": {
                    **persona_juridica,
                    "distrito_nombre": distrito["nombre"] if distrito else "N/A",
                    "canton_nombre": canton["nombre"] if canton else "N/A",
                    "provincia_nombre": provincia["nombre"] if provincia else "N/A"
                }
            }
    
    # If enrichment is requested and we have local data, try to enrich with external sources
    if enrich and local_result:
        try:
            external_data = await costa_rica_integrator.enrich_persona_data(cedula)
            local_result["external_data"] = external_data
            local_result["data_enhanced"] = True
            
            # Update local data with enriched information if available
            if external_data.get("data_found"):
                await update_local_data_with_external(cedula, external_data["data_found"])
                
        except Exception as e:
            logger.warning(f"Error enriching data for cedula {cedula}: {e}")
            local_result["enrichment_error"] = str(e)
    
    if local_result:
        return local_result
    
    # If not found locally but enrichment is enabled, try external sources only
    if enrich:
        try:
            external_data = await costa_rica_integrator.enrich_persona_data(cedula)
            if external_data.get("data_found"):
                return {
                    "found": True,
                    "type": "external",
                    "data": external_data["data_found"],
                    "sources": external_data["sources_consulted"],
                    "note": "Data found only in external sources - not in local database"
                }
        except Exception as e:
            logger.warning(f"Error in external search for cedula {cedula}: {e}")
    
    return {"found": False, "message": "No se encontró persona con esa cédula"}

async def update_local_data_with_external(cedula: str, external_data: dict):
    """Update local database with enriched external data"""
    try:
        # Extract useful information from external sources
        updates = {}
        
        # From electoral registry
        if "padron_electoral" in external_data:
            padron_data = external_data["padron_electoral"]
            if padron_data.get("provincia"):
                # Try to match province name to ID
                provincia = await db.provincias.find_one({"nombre": {"$regex": padron_data["provincia"], "$options": "i"}})
                if provincia:
                    updates["provincia_id"] = provincia["id"]
        
        # From Neodatos API
        if "neodatos" in external_data:
            neodatos_data = external_data["neodatos"]
            registro_civil = neodatos_data.get("datos_registro_civil", {})
            
            # Update phone if available and clean
            if registro_civil.get("telefono"):
                clean_phone = DataCleaner.clean_phone_number(registro_civil["telefono"])
                if clean_phone:
                    updates["telefono"] = clean_phone
            
            # Update email if valid
            if registro_civil.get("email") and DataCleaner.validate_email(registro_civil["email"]):
                updates["email"] = registro_civil["email"]
        
        # Apply updates if any
        if updates:
            updates["last_enriched"] = datetime.utcnow()
            
            # Update persona fisica or juridica accordingly
            if not cedula.startswith('3'):
                await db.personas_fisicas.update_one(
                    {"cedula": cedula},
                    {"$set": updates}
                )
            else:
                await db.personas_juridicas.update_one(
                    {"cedula_juridica": cedula},
                    {"$set": updates}
                )
                
    except Exception as e:
        logger.error(f"Error updating local data: {e}")

@api_router.get("/search/name/{nombre}")
async def search_by_name(nombre: str, limit: int = 50, current_user=Depends(get_current_user)):
    """Search person by name with improved performance"""
    results = []
    
    # Use text index for better performance
    search_regex = {"$regex": nombre, "$options": "i"}
    
    # Search in personas fisicas with aggregation for better performance
    fisica_pipeline = [
        {
            "$match": {
                "$or": [
                    {"nombre": search_regex},
                    {"primer_apellido": search_regex},
                    {"segundo_apellido": search_regex}
                ]
            }
        },
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "distritos",
                "localField": "distrito_id",
                "foreignField": "id",
                "as": "distrito_info"
            }
        },
        {
            "$lookup": {
                "from": "cantones",
                "localField": "canton_id",
                "foreignField": "id",
                "as": "canton_info"
            }
        },
        {
            "$lookup": {
                "from": "provincias",
                "localField": "provincia_id",
                "foreignField": "id",
                "as": "provincia_info"
            }
        },
        {
            "$project": {
                "_id": 0,  # Remove ObjectId
                "id": 1,
                "cedula": 1,
                "nombre": 1,
                "primer_apellido": 1,
                "segundo_apellido": 1,
                "fecha_nacimiento": 1,
                "telefono": 1,
                "email": 1,
                "provincia_id": 1,
                "canton_id": 1,
                "distrito_id": 1,
                "direccion_exacta": 1,
                "ocupacion": 1,
                "created_at": 1,
                "distrito_nombre": {"$arrayElemAt": ["$distrito_info.nombre", 0]},
                "canton_nombre": {"$arrayElemAt": ["$canton_info.nombre", 0]},
                "provincia_nombre": {"$arrayElemAt": ["$provincia_info.nombre", 0]}
            }
        },
        {"$limit": limit // 2}
    ]
    
    fisicas = await db.personas_fisicas.aggregate(fisica_pipeline).to_list(limit // 2)
    
    for persona in fisicas:
        results.append({
            "type": "fisica",
            "data": persona
        })
    
    # Search in personas juridicas with aggregation
    juridica_pipeline = [
        {
            "$match": {
                "$or": [
                    {"nombre_comercial": search_regex},
                    {"razon_social": search_regex}
                ]
            }
        },
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "distritos",
                "localField": "distrito_id",
                "foreignField": "id",
                "as": "distrito_info"
            }
        },
        {
            "$lookup": {
                "from": "cantones",
                "localField": "canton_id",
                "foreignField": "id",
                "as": "canton_info"
            }
        },
        {
            "$lookup": {
                "from": "provincias",
                "localField": "provincia_id",
                "foreignField": "id",
                "as": "provincia_info"
            }
        },
        {
            "$project": {
                "_id": 0,  # Remove ObjectId
                "id": 1,
                "cedula_juridica": 1,
                "nombre_comercial": 1,
                "razon_social": 1,
                "sector_negocio": 1,
                "telefono": 1,
                "email": 1,
                "website": 1,
                "provincia_id": 1,
                "canton_id": 1,
                "distrito_id": 1,
                "direccion_exacta": 1,
                "numero_empleados": 1,
                "fecha_constitucion": 1,
                "created_at": 1,
                "distrito_nombre": {"$arrayElemAt": ["$distrito_info.nombre", 0]},
                "canton_nombre": {"$arrayElemAt": ["$canton_info.nombre", 0]},
                "provincia_nombre": {"$arrayElemAt": ["$provincia_info.nombre", 0]}
            }
        },
        {"$limit": limit // 2}
    ]
    
    juridicas = await db.personas_juridicas.aggregate(juridica_pipeline).to_list(limit // 2)
    
    for persona in juridicas:
        results.append({
            "type": "juridica",
            "data": persona
        })
    
    return {"results": results, "total": len(results)}

@api_router.get("/search/telefono/{telefono}")
async def search_by_telefono(telefono: str, current_user=Depends(get_current_user)):
    """Search person by phone number with improved cleaning"""
    results = []
    
    # Clean the phone number for better matching
    clean_phone = DataCleaner.clean_phone_number(telefono)
    search_patterns = [telefono, clean_phone]
    
    # Add partial matches
    if len(telefono) >= 4:
        partial = telefono[-4:]  # Last 4 digits
        search_patterns.append(partial)
    
    # Escape regex special characters to prevent regex errors
    import re
    escaped_patterns = [re.escape(pattern) for pattern in search_patterns if pattern]
    search_conditions = [{"telefono": {"$regex": pattern, "$options": "i"}} for pattern in escaped_patterns]
    
    if not search_conditions:
        return {"results": [], "total": 0}
    
    # Search in personas fisicas with aggregation
    fisica_pipeline = [
        {"$match": {"$or": search_conditions}},
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "distritos",
                "localField": "distrito_id",
                "foreignField": "id",
                "as": "distrito_info"
            }
        },
        {
            "$lookup": {
                "from": "cantones",
                "localField": "canton_id",
                "foreignField": "id",
                "as": "canton_info"
            }
        },
        {
            "$lookup": {
                "from": "provincias",
                "localField": "provincia_id",
                "foreignField": "id",
                "as": "provincia_info"
            }
        },
        {
            "$project": {
                "_id": 0,  # Remove ObjectId
                "id": 1,
                "cedula": 1,
                "nombre": 1,
                "primer_apellido": 1,
                "segundo_apellido": 1,
                "fecha_nacimiento": 1,
                "telefono": 1,
                "email": 1,
                "provincia_id": 1,
                "canton_id": 1,
                "distrito_id": 1,
                "direccion_exacta": 1,
                "ocupacion": 1,
                "created_at": 1,
                "distrito_nombre": {"$arrayElemAt": ["$distrito_info.nombre", 0]},
                "canton_nombre": {"$arrayElemAt": ["$canton_info.nombre", 0]},
                "provincia_nombre": {"$arrayElemAt": ["$provincia_info.nombre", 0]}
            }
        },
        {"$limit": 25}
    ]
    
    fisicas = await db.personas_fisicas.aggregate(fisica_pipeline).to_list(25)
    
    for persona in fisicas:
        results.append({
            "type": "fisica",
            "data": persona
        })
    
    # Search in personas juridicas with aggregation
    juridica_pipeline = [
        {"$match": {"$or": search_conditions}},
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
        },
        {
            "$lookup": {
                "from": "distritos",
                "localField": "distrito_id",
                "foreignField": "id",
                "as": "distrito_info"
            }
        },
        {
            "$lookup": {
                "from": "cantones",
                "localField": "canton_id",
                "foreignField": "id",
                "as": "canton_info"
            }
        },
        {
            "$lookup": {
                "from": "provincias",
                "localField": "provincia_id",
                "foreignField": "id",
                "as": "provincia_info"
            }
        },
        {
            "$project": {
                "_id": 0,  # Remove ObjectId
                "id": 1,
                "cedula_juridica": 1,
                "nombre_comercial": 1,
                "razon_social": 1,
                "sector_negocio": 1,
                "telefono": 1,
                "email": 1,
                "website": 1,
                "provincia_id": 1,
                "canton_id": 1,
                "distrito_id": 1,
                "direccion_exacta": 1,
                "numero_empleados": 1,
                "fecha_constitucion": 1,
                "created_at": 1,
                "distrito_nombre": {"$arrayElemAt": ["$distrito_info.nombre", 0]},
                "canton_nombre": {"$arrayElemAt": ["$canton_info.nombre", 0]},
                "provincia_nombre": {"$arrayElemAt": ["$provincia_info.nombre", 0]}
            }
        },
        {"$limit": 25}
    ]
    
    juridicas = await db.personas_juridicas.aggregate(juridica_pipeline).to_list(25)
    
    for persona in juridicas:
        results.append({
            "type": "juridica", 
            "data": persona
        })
    
    return {"results": results, "total": len(results)}

@api_router.post("/search/geografica")
async def search_geografica(query: DemographicQuery, current_user=Depends(get_current_user)):
    """Geographic search with improved performance using aggregation"""
    
    # Build match conditions
    match_conditions = {}
    if query.provincia_id:
        match_conditions["provincia_id"] = query.provincia_id
    if query.canton_id:
        match_conditions["canton_id"] = query.canton_id  
    if query.distrito_id:
        match_conditions["distrito_id"] = query.distrito_id
    
    results = []
    
    # Search personas fisicas if requested
    if not query.person_type or query.person_type == PersonType.FISICA:
        fisica_pipeline = [
            {"$match": match_conditions},
            {
                "$addFields": {
                    "id": {"$toString": "$_id"}
                }
            },
            {
                "$lookup": {
                    "from": "distritos",
                    "localField": "distrito_id",
                    "foreignField": "id",
                    "as": "distrito_info"
                }
            },
            {
                "$lookup": {
                    "from": "cantones",
                    "localField": "canton_id",
                    "foreignField": "id",
                    "as": "canton_info"
                }
            },
            {
                "$lookup": {
                    "from": "provincias",
                    "localField": "provincia_id",
                    "foreignField": "id",
                    "as": "provincia_info"
                }
            },
            {
                "$project": {
                    "_id": 0,  # Remove ObjectId
                    "id": 1,
                    "cedula": 1,
                    "nombre": 1,
                    "primer_apellido": 1,
                    "segundo_apellido": 1,
                    "fecha_nacimiento": 1,
                    "telefono": 1,
                    "email": 1,
                    "provincia_id": 1,
                    "canton_id": 1,
                    "distrito_id": 1,
                    "direccion_exacta": 1,
                    "ocupacion": 1,
                    "created_at": 1,
                    "distrito_nombre": {"$arrayElemAt": ["$distrito_info.nombre", 0]},
                    "canton_nombre": {"$arrayElemAt": ["$canton_info.nombre", 0]},
                    "provincia_nombre": {"$arrayElemAt": ["$provincia_info.nombre", 0]}
                }
            },
            {"$limit": 50}
        ]
        
        fisicas = await db.personas_fisicas.aggregate(fisica_pipeline).to_list(50)
        
        for persona in fisicas:
            results.append({
                "type": "fisica",
                "data": persona
            })
    
    # Search personas juridicas if requested
    if not query.person_type or query.person_type == PersonType.JURIDICA:
        juridica_match = match_conditions.copy()
        if query.business_sector:
            juridica_match["sector_negocio"] = query.business_sector
            
        juridica_pipeline = [
            {"$match": juridica_match},
            {
                "$addFields": {
                    "id": {"$toString": "$_id"}
                }
            },
            {
                "$lookup": {
                    "from": "distritos",
                    "localField": "distrito_id",
                    "foreignField": "id",
                    "as": "distrito_info"
                }
            },
            {
                "$lookup": {
                    "from": "cantones",
                    "localField": "canton_id",
                    "foreignField": "id",
                    "as": "canton_info"
                }
            },
            {
                "$lookup": {
                    "from": "provincias",
                    "localField": "provincia_id",
                    "foreignField": "id",
                    "as": "provincia_info"
                }
            },
            {
                "$project": {
                    "_id": 0,  # Remove ObjectId
                    "id": 1,
                    "cedula_juridica": 1,
                    "nombre_comercial": 1,
                    "razon_social": 1,
                    "sector_negocio": 1,
                    "telefono": 1,
                    "email": 1,
                    "website": 1,
                    "provincia_id": 1,
                    "canton_id": 1,
                    "distrito_id": 1,
                    "direccion_exacta": 1,
                    "numero_empleados": 1,
                    "fecha_constitucion": 1,
                    "created_at": 1,
                    "distrito_nombre": {"$arrayElemAt": ["$distrito_info.nombre", 0]},
                    "canton_nombre": {"$arrayElemAt": ["$canton_info.nombre", 0]},
                    "provincia_nombre": {"$arrayElemAt": ["$provincia_info.nombre", 0]}
                }
            },
            {"$limit": 50}
        ]
        
        juridicas = await db.personas_juridicas.aggregate(juridica_pipeline).to_list(50)
        
        for persona in juridicas:
            results.append({
                "type": "juridica",
                "data": persona
            })
    
    return {"results": results, "total": len(results)}

# Data Update Management endpoints
@api_router.post("/admin/trigger-update")
async def trigger_manual_update(current_user=Depends(get_current_user)):
    """Trigger manual data update (Admin only)"""
    try:
        # Run update in background
        import asyncio
        asyncio.create_task(run_manual_update())
        
        return {
            "message": "Data update initiated",
            "status": "started",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting update: {str(e)}")

@api_router.get("/admin/update-stats")
async def get_update_statistics(current_user=Depends(get_current_user)):
    """Get data update statistics"""
    try:
        # Get latest update statistics
        latest_stats = await db.update_statistics.find().sort("timestamp", -1).limit(10).to_list(10)
        
        # Get system statistics
        system_stats = {
            "total_personas_fisicas": await db.personas_fisicas.count_documents({}),
            "total_personas_juridicas": await db.personas_juridicas.count_documents({}),
            "total_provincias": await db.provincias.count_documents({}),
            "last_enrichment": await db.personas_fisicas.count_documents({"last_enriched": {"$exists": True}}),
            "data_sources": [
                {"name": "TSE_PADRON", "count": await db.personas_fisicas.count_documents({"fuente_datos": "TSE_PADRON"})},
                {"name": "REGISTRO_NACIONAL", "count": await db.personas_juridicas.count_documents({"fuente_datos": "REGISTRO_NACIONAL"})},
                {"name": "LOCAL_DATABASE", "count": await db.personas_fisicas.count_documents({"fuente_datos": {"$exists": False}})}
            ]
        }
        
        return {
            "system_stats": system_stats,
            "update_history": latest_stats,
            "updater_status": "running" if data_updater.is_running else "stopped"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@api_router.get("/system/health")
async def system_health_check():
    """System health check endpoint"""
    try:
        # Check database connectivity
        db_status = "healthy"
        try:
            await db.admin.command("ping")
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Check external API integrator
        integrator_status = "healthy" if costa_rica_integrator.session is None or not costa_rica_integrator.session.closed else "session_active"
        
        # Check data updater
        updater_status = "running" if data_updater.is_running else "stopped"
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow(),
            "services": {
                "database": db_status,
                "external_integrator": integrator_status,
                "data_updater": updater_status
            },
            "version": "2.0.0"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

# Include the router in the main app
app.include_router(api_router)

# Admin Panel Endpoints
@api_router.get("/admin/dashboard/stats", response_model=AdminPanelModels.SystemStats)
async def get_admin_dashboard_stats(current_user=Depends(get_current_user)):
    """Obtener estadísticas completas para el panel de administración"""
    admin_manager = get_admin_manager(db)
    return await admin_manager.get_system_statistics()

@api_router.post("/admin/extraction/start")
async def start_data_extraction(
    request: AdminPanelModels.StartExtractionRequest,
    current_user=Depends(get_current_user)
):
    """Iniciar extracción de datos desde Daticos original"""
    admin_manager = get_admin_manager(db)
    task_id = await admin_manager.start_daticos_extraction(request)
    return {"task_id": task_id, "message": "Extracción iniciada", "status": "started"}

@api_router.get("/admin/extraction/tasks", response_model=List[AdminPanelModels.ExtractionTaskModel])
async def get_extraction_tasks(current_user=Depends(get_current_user)):
    """Obtener lista de tareas de extracción"""
    admin_manager = get_admin_manager(db)
    return await admin_manager.get_extraction_tasks()

@api_router.delete("/admin/extraction/tasks/{task_id}")
async def cancel_extraction_task(task_id: str, current_user=Depends(get_current_user)):
    """Cancelar tarea de extracción en curso"""
    admin_manager = get_admin_manager(db)
    success = await admin_manager.cancel_extraction_task(task_id)
    if success:
        return {"message": "Tarea cancelada exitosamente"}
    raise HTTPException(status_code=404, detail="Tarea no encontrada o no se puede cancelar")

@api_router.get("/admin/database/analysis", response_model=AdminPanelModels.DatabaseAnalysis)
async def analyze_database_quality(current_user=Depends(get_current_user)):
    """Realizar análisis de calidad de la base de datos"""
    admin_manager = get_admin_manager(db)
    return await admin_manager.analyze_database_quality()

@api_router.post("/admin/database/cleanup")
async def cleanup_database(current_user=Depends(get_current_user)):
    """Limpiar registros duplicados de la base de datos"""
    admin_manager = get_admin_manager(db)
    results = await admin_manager.clean_duplicate_records()
    return {
        "message": "Limpieza completada",
        "removed_records": results,
        "total_removed": results['fisica_removed'] + results['juridica_removed']
    }

@api_router.get("/admin/daticos/test-connection")
async def test_daticos_connection(current_user=Depends(get_current_user)):
    """Probar conexión con Daticos original"""
    try:
        login_success = await daticos_extractor.login()
        if login_success:
            # Obtener estructura del sistema
            structure = await daticos_extractor.discover_system_structure()
            await daticos_extractor.close_session()
            
            return {
                "connection_status": "success",
                "message": "Conexión exitosa con Daticos",
                "system_structure": structure,
                "credentials_valid": True
            }
        else:
            return {
                "connection_status": "failed",
                "message": "No se pudo conectar con Daticos - credenciales inválidas",
                "credentials_valid": False
            }
    except Exception as e:
        logger.error(f"Error testing Daticos connection: {e}")
        return {
            "connection_status": "error",
            "message": f"Error en la conexión: {str(e)}",
            "error": str(e)
        }

@api_router.post("/admin/daticos/extract-sample")
async def extract_daticos_sample(
    cedula: str,
    current_user=Depends(get_current_user)
):
    """Extraer datos de muestra de una cédula específica desde Daticos original"""
    try:
        if not await daticos_extractor.login():
            raise HTTPException(status_code=401, detail="No se pudo conectar con Daticos")
        
        result = await daticos_extractor.extract_consultation_by_cedula(cedula)
        await daticos_extractor.close_session()
        
        return {
            "extraction_successful": result.get('found', False),
            "cedula": cedula,
            "data": result,
            "message": "Extracción de muestra completada"
        }
    except Exception as e:
        logger.error(f"Error extracting sample from Daticos: {e}")
        raise HTTPException(status_code=500, detail=f"Error en extracción: {str(e)}")

# Endpoint para obtener representantes legales (nueva funcionalidad solicitada)
@api_router.get("/search/cedula/{cedula}/representantes")
async def get_legal_representatives(cedula: str, current_user=Depends(get_current_user)):
    """Obtener representantes legales de una persona jurídica"""
    try:
        # Buscar persona jurídica
        persona_juridica = await db.personas_juridicas.find_one({"cedula_juridica": cedula})
        
        if not persona_juridica:
            raise HTTPException(status_code=404, detail="Persona jurídica no encontrada")
        
        # Buscar representantes legales en una colección específica o datos enriquecidos
        representantes = await db.representantes_legales.find({"cedula_juridica": cedula}).to_list(100)
        
        return {
            "cedula_juridica": cedula,
            "nombre_comercial": persona_juridica.get("nombre_comercial", "N/A"),
            "representantes": representantes or [],
            "total_representantes": len(representantes) if representantes else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting legal representatives: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo representantes: {str(e)}")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create indexes for faster queries
@app.on_event("startup")
async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Indexes for personas_fisicas
        await db.personas_fisicas.create_index("cedula", unique=True)
        await db.personas_fisicas.create_index([("nombre", 1), ("primer_apellido", 1), ("segundo_apellido", 1)])
        await db.personas_fisicas.create_index("telefono")
        await db.personas_fisicas.create_index([("provincia_id", 1), ("canton_id", 1), ("distrito_id", 1)])
        
        # Indexes for personas_juridicas
        await db.personas_juridicas.create_index("cedula_juridica", unique=True)
        await db.personas_juridicas.create_index([("nombre_comercial", 1), ("razon_social", 1)])
        await db.personas_juridicas.create_index("telefono")
        await db.personas_juridicas.create_index("sector_negocio")
        await db.personas_juridicas.create_index([("provincia_id", 1), ("canton_id", 1), ("distrito_id", 1)])
        
        # Location indexes
        await db.provincias.create_index("codigo", unique=True)
        await db.cantones.create_index([("provincia_id", 1), ("codigo", 1)])
        await db.distritos.create_index([("canton_id", 1), ("codigo", 1)])
        
        logger.info("Database indexes created successfully")
        
        # Start the data updater service
        start_data_updater()
        logger.info("Data updater service started")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    data_updater.stop_scheduler()
    await costa_rica_integrator.close_session()
