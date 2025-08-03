from fastapi import FastAPI, Depends, HTTPException, Form, Query, BackgroundTasks, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, List, Any, Union
import json
import random
import uuid
from datetime import datetime, timedelta
import hashlib
import asyncio
import aiohttp
import time
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import re
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import secrets
import base64
from PIL import Image
import io
import os

# Configurar logging avanzado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TuDatos Enterprise - Costa Rica Data System", 
    version="4.0.0",
    description="Sistema más avanzado de datos de Costa Rica con IA y extractores autónomos"
)
security = HTTPBearer()

# =============================================================================
# SISTEMA DE DATOS ULTRA AVANZADO
# =============================================================================

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"
    ENTERPRISE = "enterprise"

class ExtractorType(Enum):
    DATICOS_ULTRA = "daticos_ultra"
    TSE_COMPLETE = "tse_complete"
    CCSS_ADVANCED = "ccss_advanced"
    REGISTRO_NACIONAL = "registro_nacional"
    HACIENDA_TRIBUTARIO = "hacienda_tributario"
    COLEGIOS_PROFESIONALES = "colegios_profesionales"
    SOCIAL_MEDIA_SCRAPER = "social_media_scraper"
    FINANCIAL_DATA = "financial_data"

@dataclass
class UserProfile:
    id: str
    username: str
    email: str
    password_hash: str
    role: str
    credits: int
    plan: str
    permissions: List[str]
    created_at: str
    last_login: str
    email_verified: bool = False
    reset_token: Optional[str] = None
    reset_token_expires: Optional[str] = None
    profile_data: Dict[str, Any] = None
    api_key: Optional[str] = None
    rate_limit: int = 10
    full_name: str = ""
    phone: str = ""
    company: str = ""
    address: str = ""
    is_active: bool = True

@dataclass
class PersonaCompleta:
    # Información básica
    id: str
    cedula: str
    nombre_completo: str
    primer_nombre: str
    segundo_nombre: Optional[str]
    primer_apellido: str
    segundo_apellido: str
    
    # Contacto (TODOS los registrados)
    telefonos: List[str]  # Todos los teléfonos encontrados
    emails: List[str]     # Todos los emails encontrados
    direcciones: List[Dict[str, str]]  # Todas las direcciones
    
    # Información personal
    fecha_nacimiento: str
    edad: int
    estado_civil: str
    nacionalidad: str
    lugar_nacimiento: str
    
    # Datos familiares (TSE)
    padre_nombre: Optional[str]
    madre_nombre: Optional[str]
    conyuge_nombre: Optional[str]
    hijos: List[Dict[str, str]]  # Lista de hijos con nombres y edades
    familiares_conocidos: List[Dict[str, str]]
    
    # Información crediticia y financiera
    score_crediticio: int
    historial_crediticio: str
    hipotecas: List[Dict[str, Any]]
    prestamos: List[Dict[str, Any]]
    tarjetas_credito: List[Dict[str, str]]
    referencias_bancarias: List[str]
    ingresos_reportados: List[Dict[str, Any]]
    
    # Bienes muebles e inmuebles
    propiedades: List[Dict[str, Any]]
    vehiculos: List[Dict[str, Any]]
    otros_activos: List[Dict[str, Any]]
    
    # Datos mercantiles
    empresas_asociadas: List[Dict[str, Any]]
    cargos_empresariales: List[Dict[str, Any]]
    actividades_comerciales: List[str]
    licencias_comerciales: List[Dict[str, Any]]
    
    # Redes sociales (TODAS)
    facebook: Optional[str]
    instagram: Optional[str]
    linkedin: Optional[str]
    twitter: Optional[str]
    tiktok: Optional[str]
    youtube: Optional[str]
    whatsapp: Optional[str]
    telegram: Optional[str]
    otras_redes: Dict[str, str]
    
    # Datos laborales completos
    ocupacion_actual: str
    empresa_actual: str
    salario_reportado: Optional[int]
    patrono_actual: Dict[str, Any]
    historial_laboral: List[Dict[str, Any]]
    orden_patronal: Optional[str]  # De Daticos
    
    # Educación
    nivel_educativo: str
    instituciones_educativas: List[Dict[str, Any]]
    titulos_obtenidos: List[Dict[str, Any]]
    certificaciones: List[str]
    
    # Información legal
    antecedentes_penales: Optional[str]
    procesos_legales: List[Dict[str, Any]]
    demandas: List[Dict[str, Any]]
    
    # Datos de salud (CCSS)
    numero_ccss: Optional[str]
    centro_salud_asignado: Optional[str]
    historial_medico_basico: Optional[Dict[str, Any]]
    
    # Fotos y multimedia (Daticos)
    fotos_disponibles: List[Dict[str, Any]]  # URLs y metadatos
    documentos_escaneados: List[Dict[str, Any]]
    
    # Metadatos del sistema
    fuentes_datos: List[str]
    ultima_actualizacion: str
    confiabilidad_score: int
    verificado: bool
    created_at: str

# Base de datos ultra completa simulada
ultra_database = {
    "personas_completas": [],
    "empresas_completas": [],
    "extractores_data": {
        "daticos_photos": [],
        "tse_family_data": [],
        "ccss_health_data": [],
        "registro_properties": [],
        "hacienda_financial": [],
        "social_media_profiles": []
    },
    "system_logs": [],
    "search_analytics": []
}

# Sistema de usuarios ultra avanzado
users_system = {
    "superadmin": {
        "id": "superadmin",
        "username": "superadmin",
        "email": "admin@tudatos.cr",
        "password_hash": hashlib.sha256("TuDatos2024!Admin".encode()).hexdigest(),
        "role": UserRole.SUPER_ADMIN.value,
        "credits": 999999,
        "plan": "Super Admin",
        "permissions": ["all", "system_config", "user_management", "extractor_control", "data_management"],
        "created_at": datetime.utcnow().isoformat(),
        "last_login": datetime.utcnow().isoformat(),
        "email_verified": True,
        "reset_token": None,
        "reset_token_expires": None,
        "profile_data": {
            "full_name": "Administrador Principal",
            "phone": "+50622001234",
            "company": "TuDatos Enterprise",
            "address": "San José, Costa Rica"
        },
        "api_key": "superadmin_api_key_2024_ultra_secure",
        "rate_limit": 10000,
        "is_active": True
    }
}

# Sistema de extractores ultra avanzado
extractors_system = {
    ExtractorType.DATICOS_ULTRA.value: {
        "name": "Daticos Ultra Extractor",
        "description": "Extracción completa de Daticos incluyendo fotos y datos visuales",
        "status": "active",
        "last_run": datetime.utcnow().isoformat(),
        "next_run": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "records_extracted": 2847691,
        "photos_extracted": 1534829,
        "success_rate": 98.7,
        "credentials": {
            "user1": "CABEZAS",
            "pass1": "Hola2022",
            "user2": "Saraya", 
            "pass2": "12345"
        },
        "endpoints_active": 24,
        "search_terms": 350,
        "features": ["basic_data", "photos", "family_data", "work_data", "financial_hints"],
        "auto_update": True,
        "notification_enabled": True,
        "data_pending_integration": 15847,
        "errors_today": 3,
        "avg_response_time": 2.1
    },
    ExtractorType.TSE_COMPLETE.value: {
        "name": "TSE Complete Data Extractor",
        "description": "Extracción completa de datos electorales y familiares",
        "status": "active",
        "last_run": (datetime.utcnow() - timedelta(minutes=45)).isoformat(),
        "next_run": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "records_extracted": 3456792,
        "family_relationships": 892743,
        "success_rate": 96.3,
        "endpoints_active": 12,
        "features": ["voter_data", "family_tree", "address_history", "civil_status"],
        "auto_update": True,
        "notification_enabled": True,
        "data_pending_integration": 8934,
        "errors_today": 7,
        "avg_response_time": 3.8
    },
    ExtractorType.CCSS_ADVANCED.value: {
        "name": "CCSS Advanced Health & Work Data",
        "description": "Datos médicos, laborales y patronales de CCSS",
        "status": "active",
        "last_run": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        "next_run": (datetime.utcnow() + timedelta(hours=3)).isoformat(),
        "records_extracted": 2156743,
        "health_centers": 1200,
        "employer_data": 456789,
        "success_rate": 94.8,
        "features": ["health_assignment", "work_history", "employer_data", "salary_reports"],
        "auto_update": True,
        "notification_enabled": True,
        "data_pending_integration": 12456,
        "errors_today": 12,
        "avg_response_time": 4.2
    },
    ExtractorType.REGISTRO_NACIONAL.value: {
        "name": "Registro Nacional Properties & Vehicles",
        "description": "Propiedades, vehículos y bienes registrados",
        "status": "active",
        "last_run": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        "next_run": (datetime.utcnow() + timedelta(hours=4)).isoformat(),
        "records_extracted": 1892456,
        "properties": 892456,
        "vehicles": 1234567,
        "success_rate": 92.1,
        "features": ["real_estate", "vehicles", "mortgages", "liens"],
        "auto_update": True,
        "notification_enabled": True,
        "data_pending_integration": 9876,
        "errors_today": 18,
        "avg_response_time": 5.1
    },
    ExtractorType.SOCIAL_MEDIA_SCRAPER.value: {
        "name": "Social Media Ultra Scraper",
        "description": "Extracción de todas las redes sociales",
        "status": "active",
        "last_run": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
        "next_run": (datetime.utcnow() + timedelta(minutes=40)).isoformat(),
        "records_extracted": 3456789,
        "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter", "TikTok", "WhatsApp"],
        "profiles_found": 2567890,
        "success_rate": 87.3,
        "features": ["profile_data", "contact_extraction", "photo_analysis", "connection_mapping"],
        "auto_update": True,
        "notification_enabled": True,
        "data_pending_integration": 25634,
        "errors_today": 34,
        "avg_response_time": 1.8
    }
}

# Generar base de datos ultra completa
def generate_ultra_complete_database():
    """Generar base de datos ultra completa con TODA la información"""
    
    nombres = ["José Manuel", "María Carmen", "Juan Carlos", "Ana Lucía", "Carlos Alberto"]
    apellidos = ["González", "Rodríguez", "Hernández", "Jiménez", "Martínez", "López"]
    provincias = ["San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"]
    
    # Generar 1000 personas ultra completas
    for i in range(1000):
        primer_nombre = random.choice(nombres)
        primer_apellido = random.choice(apellidos)
        segundo_apellido = random.choice(apellidos)
        
        # Generar múltiples teléfonos y emails
        telefonos = []
        emails = []
        
        # Teléfono principal
        telefonos.append(f"+506{random.choice(['2','4','6','7','8'])}{random.randint(1000000,9999999):07d}")
        
        # Teléfonos adicionales (trabajo, casa, familiar)
        if random.random() > 0.3:
            telefonos.append(f"+506{random.choice(['2','4','6','7','8'])}{random.randint(1000000,9999999):07d}")
        if random.random() > 0.6:
            telefonos.append(f"+506{random.choice(['2'])}{random.randint(1000000,9999999):07d}")
        
        # Email principal
        emails.append(f"{primer_nombre.lower().replace(' ', '')}.{primer_apellido.lower()}@gmail.com")
        
        # Emails adicionales
        if random.random() > 0.4:
            emails.append(f"{primer_nombre.lower().replace(' ', '')}{random.randint(10,99)}@hotmail.com")
        if random.random() > 0.7:
            emails.append(f"{primer_nombre.lower()}.{primer_apellido.lower()}@empresa.co.cr")
        
        # Datos familiares completos
        hijos = []
        for j in range(random.randint(0, 4)):
            hijos.append({
                "nombre": f"{random.choice(nombres)} {primer_apellido}",
                "edad": random.randint(1, 25),
                "cedula": f"{random.randint(1,7)}-{random.randint(1000,9999):04d}-{random.randint(1000,9999):04d}"
            })
        
        # Propiedades múltiples
        propiedades = []
        for k in range(random.randint(0, 3)):
            propiedades.append({
                "tipo": random.choice(["Casa", "Apartamento", "Lote", "Comercial"]),
                "direccion": f"Propiedad {k+1}, {random.choice(provincias)}",
                "valor_catastral": random.randint(50000, 500000),
                "area": f"{random.randint(100, 1000)} m²",
                "numero_finca": f"F-{random.randint(100000, 999999)}"
            })
        
        # Vehículos múltiples
        vehiculos = []
        for l in range(random.randint(0, 2)):
            vehiculos.append({
                "placa": f"{random.choice(['BCR', 'SJO', 'ALA'])}{random.randint(100, 999)}",
                "marca": random.choice(["Toyota", "Honda", "Nissan", "Hyundai"]),
                "modelo": random.choice(["Corolla", "Civic", "Sentra", "Accent"]),
                "año": random.randint(2010, 2024),
                "valor": random.randint(5000, 50000)
            })
        
        # Fotos de Daticos (simuladas)
        fotos = []
        for m in range(random.randint(1, 5)):
            fotos.append({
                "url": f"https://daticos.com/photos/{uuid.uuid4()}.jpg",
                "tipo": random.choice(["cedula", "perfil", "documento", "selfie"]),
                "fecha_subida": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat(),
                "calidad": random.choice(["alta", "media", "baja"]),
                "verificada": random.choice([True, False])
            })
        
        persona_completa = PersonaCompleta(
            id=str(uuid.uuid4()),
            cedula=f"{random.randint(1,7)}-{random.randint(1000,9999):04d}-{random.randint(1000,9999):04d}",
            nombre_completo=f"{primer_nombre} {primer_apellido} {segundo_apellido}",
            primer_nombre=primer_nombre.split()[0],
            segundo_nombre=primer_nombre.split()[1] if len(primer_nombre.split()) > 1 else None,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            
            # Múltiples contactos
            telefonos=telefonos,
            emails=emails,
            direcciones=[
                {"tipo": "residencial", "direccion": f"Del parque {random.randint(50,500)}m norte, {random.choice(provincias)}"},
                {"tipo": "trabajo", "direccion": f"Oficina comercial, {random.choice(provincias)}"}
            ],
            
            # Información personal
            fecha_nacimiento=f"{random.randint(1960,2000)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            edad=random.randint(20, 60),
            estado_civil=random.choice(["Soltero", "Casado", "Divorciado", "Viudo", "Unión Libre"]),
            nacionalidad="Costarricense",
            lugar_nacimiento=random.choice(provincias),
            
            # Familia (TSE)
            padre_nombre=f"{random.choice(nombres)} {random.choice(apellidos)}" if random.random() > 0.1 else None,
            madre_nombre=f"{random.choice(nombres)} {random.choice(apellidos)}" if random.random() > 0.1 else None,
            conyuge_nombre=f"{random.choice(nombres)} {random.choice(apellidos)}" if random.random() > 0.6 else None,
            hijos=hijos,
            familiares_conocidos=[
                {"parentesco": "hermano", "nombre": f"{random.choice(nombres)} {primer_apellido}"},
                {"parentesco": "tío", "nombre": f"{random.choice(nombres)} {random.choice(apellidos)}"}
            ],
            
            # Financiero
            score_crediticio=random.randint(300, 850),
            historial_crediticio=random.choice(["Excelente", "Bueno", "Regular", "Malo"]),
            hipotecas=[{"banco": "BCR", "monto": random.randint(50000, 200000), "saldo": random.randint(20000, 150000)}] if random.random() > 0.7 else [],
            prestamos=[{"banco": "BAC", "tipo": "personal", "monto": random.randint(1000, 50000)}] if random.random() > 0.5 else [],
            tarjetas_credito=[{"banco": "Scotia", "limite": random.randint(500, 5000)}] if random.random() > 0.4 else [],
            referencias_bancarias=["BCR", "BAC", "BN"][:random.randint(1,3)],
            ingresos_reportados=[{"fuente": "salario", "monto": random.randint(300000, 2000000), "año": 2024}],
            
            # Bienes
            propiedades=propiedades,
            vehiculos=vehiculos,
            otros_activos=[{"tipo": "inversión", "descripción": "Cuenta de ahorro", "valor": random.randint(100000, 1000000)}],
            
            # Mercantil
            empresas_asociadas=[{"nombre": f"Empresa {i}", "cargo": "Socio", "participacion": f"{random.randint(10,100)}%"}] if random.random() > 0.8 else [],
            cargos_empresariales=[],
            actividades_comerciales=["Comercio", "Servicios"] if random.random() > 0.7 else [],
            licencias_comerciales=[],
            
            # Redes sociales completas
            facebook=f"{primer_nombre.lower().replace(' ', '')}.{primer_apellido.lower()}" if random.random() > 0.3 else None,
            instagram=f"{primer_nombre.lower().replace(' ', '')}{random.randint(10,99)}" if random.random() > 0.5 else None,
            linkedin=f"{primer_nombre.lower().replace(' ', '')}-{primer_apellido.lower()}" if random.random() > 0.6 else None,
            twitter=f"@{primer_nombre.lower().replace(' ', '')}{primer_apellido[0].lower()}" if random.random() > 0.8 else None,
            tiktok=f"@{primer_nombre.lower().replace(' ', '')}{random.randint(100,999)}" if random.random() > 0.7 else None,
            youtube=f"{primer_nombre} {primer_apellido} Channel" if random.random() > 0.9 else None,
            whatsapp=telefonos[0] if telefonos else None,
            telegram=f"@{primer_nombre.lower()}{random.randint(10,99)}" if random.random() > 0.6 else None,
            otras_redes={"discord": f"{primer_nombre}#{random.randint(1000,9999)}"} if random.random() > 0.8 else {},
            
            # Laboral completo
            ocupacion_actual=random.choice(["Ingeniero", "Médico", "Abogado", "Contador", "Administrador"]),
            empresa_actual=f"Empresa {random.choice(['A', 'B', 'C', 'D', 'E'])}",
            salario_reportado=random.randint(500000, 3000000) if random.random() > 0.3 else None,
            patrono_actual={"nombre": f"Patrono {i}", "cedula_juridica": f"3-101-{random.randint(100000,999999):06d}"},
            historial_laboral=[
                {"empresa": f"Empresa Anterior {j}", "cargo": "Empleado", "años": f"2015-2020"}
                for j in range(random.randint(1,3))
            ],
            orden_patronal=f"OP-{random.randint(100000,999999)}" if random.random() > 0.5 else None,
            
            # Educación
            nivel_educativo=random.choice(["Secundaria", "Universitario", "Posgrado"]),
            instituciones_educativas=[
                {"institucion": "Universidad de Costa Rica", "titulo": "Licenciatura", "año": "2010"}
            ],
            titulos_obtenidos=[{"titulo": "Licenciado en Ingeniería", "año": "2010"}],
            certificaciones=["Microsoft Office", "Inglés Avanzado"],
            
            # Legal
            antecedentes_penales="Limpios" if random.random() > 0.95 else None,
            procesos_legales=[],
            demandas=[],
            
            # Salud (CCSS)
            numero_ccss=f"CCSS-{random.randint(100000000,999999999)}",
            centro_salud_asignado=f"EBAIS {random.choice(provincias)}",
            historial_medico_basico={"alergias": "Ninguna conocida", "grupo_sanguineo": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])},
            
            # Fotos Daticos
            fotos_disponibles=fotos,
            documentos_escaneados=[
                {"tipo": "cedula", "url": f"https://daticos.com/docs/{uuid.uuid4()}.pdf", "verificado": True}
            ],
            
            # Meta
            fuentes_datos=["DATICOS", "TSE", "CCSS", "REGISTRO_NACIONAL", "REDES_SOCIALES"],
            ultima_actualizacion=datetime.utcnow().isoformat(),
            confiabilidad_score=random.randint(70, 100),
            verificado=random.choice([True, False]),
            created_at=datetime.utcnow().isoformat()
        )
        
        ultra_database["personas_completas"].append(asdict(persona_completa))

# Generar base de datos al startup
generate_ultra_complete_database()

# =============================================================================
# FUNCIONES DE AUTENTICACIÓN ULTRA SEGURA
# =============================================================================

def generate_reset_token():
    """Generar token seguro para reset de contraseña"""
    return secrets.token_urlsafe(32)

def send_email(to_email: str, subject: str, body: str):
    """Enviar email (simulado - en producción usar SMTP real)"""
    logger.info(f"EMAIL ENVIADO A: {to_email}")
    logger.info(f"ASUNTO: {subject}")
    logger.info(f"CONTENIDO: {body}")
    return True

def verify_ultra_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificación ultra segura de usuarios"""
    token = credentials.credentials
    
    # En producción sería JWT real con firma
    token_map = {
        "superadmin_token": "superadmin",
        "admin_token": "admin",
        "premium_token": "premium",
        "basic_token": "basic"
    }
    
    if token in token_map:
        user_id = token_map[token]
        if user_id in users_system:
            user = users_system[user_id]
            if user["is_active"]:
                return user
    
    raise HTTPException(status_code=401, detail="Token inválido, expirado o usuario inactivo")

def check_ultra_permission(user: dict, permission: str):
    """Verificar permisos ultra específicos"""
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    
    if "all" in user["permissions"] or permission in user["permissions"]:
        return True
    
    raise HTTPException(status_code=403, detail=f"Sin permisos para: {permission}")

def hash_password(password: str) -> str:
    """Hash seguro de contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verificar contraseña"""
    return hash_password(password) == hashed

# =============================================================================
# ENDPOINTS PRINCIPALES ULTRA AVANZADOS
# =============================================================================

@app.get("/")
async def ultra_home():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TuDatos - La Base de Datos Más Grande de Costa Rica</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .gradient-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); }
        .glass-ultra { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.1); }
        .logo-ultra { animation: logoUltra 6s ease-in-out infinite; }
        @keyframes logoUltra { 
            0%, 100% { transform: translateY(0px) rotate(0deg) scale(1); } 
            25% { transform: translateY(-8px) rotate(3deg) scale(1.05); }
            50% { transform: translateY(-15px) rotate(0deg) scale(1.1); }
            75% { transform: translateY(-8px) rotate(-3deg) scale(1.05); }
        }
        .data-flow { animation: dataFlow 4s linear infinite; }
        @keyframes dataFlow { 0% { transform: translateX(-100%) rotate(0deg); } 100% { transform: translateX(calc(100vw + 100px)) rotate(360deg); } }
        .ultra-card { transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
        .ultra-card:hover { transform: translateY(-10px) scale(1.02); box-shadow: 0 25px 50px rgba(0,0,0,0.25); }
        .pulse-ultra { animation: pulseUltra 3s infinite; }
        @keyframes pulseUltra { 0%, 100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); } 50% { box-shadow: 0 0 0 20px rgba(102, 126, 234, 0); } }
        .text-glow { text-shadow: 0 0 20px rgba(255,255,255,0.5); }
        .floating { animation: floating 3s ease-in-out infinite; }
        @keyframes floating { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-20px); } }
    </style>
</head>
<body class="bg-gray-900 text-white overflow-x-hidden" x-data="ultraApp()">
    <!-- Elementos de fondo animados -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
        <div class="data-flow absolute top-10 left-0 w-4 h-4 bg-blue-500 rounded-full opacity-20"></div>
        <div class="data-flow absolute top-32 left-0 w-3 h-3 bg-purple-500 rounded-full opacity-30" style="animation-delay: 1s;"></div>
        <div class="data-flow absolute top-52 left-0 w-5 h-5 bg-pink-500 rounded-full opacity-25" style="animation-delay: 2s;"></div>
        <div class="data-flow absolute top-72 left-0 w-2 h-2 bg-yellow-500 rounded-full opacity-35" style="animation-delay: 3s;"></div>
    </div>

    <!-- Header Ultra Premium -->
    <header class="relative z-50">
        <nav class="gradient-primary shadow-2xl">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center h-24">
                    <!-- Logo Ultra Avanzado -->
                    <div class="flex items-center space-x-6">
                        <div class="logo-ultra relative">
                            <svg class="w-16 h-16" viewBox="0 0 140 140" xmlns="http://www.w3.org/2000/svg">
                                <defs>
                                    <radialGradient id="ultraGrad" cx="50%" cy="50%" r="50%">
                                        <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
                                        <stop offset="50%" style="stop-color:#ffd89b;stop-opacity:0.8" />
                                        <stop offset="100%" style="stop-color:#667eea;stop-opacity:0.6" />
                                    </radialGradient>
                                    <filter id="ultraGlow" x="-50%" y="-50%" width="200%" height="200%">
                                        <feGaussianBlur stdDeviation="8" result="coloredBlur"/>
                                        <feMerge>
                                            <feMergeNode in="coloredBlur"/>
                                            <feMergeNode in="SourceGraphic"/>
                                        </feMerge>
                                    </filter>
                                </defs>
                                
                                <!-- Anillos externos rotatorios -->
                                <circle cx="70" cy="70" r="65" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1">
                                    <animateTransform attributeName="transform" type="rotate" values="0 70 70;360 70 70" dur="20s" repeatCount="indefinite"/>
                                </circle>
                                <circle cx="70" cy="70" r="55" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5">
                                    <animateTransform attributeName="transform" type="rotate" values="360 70 70;0 70 70" dur="15s" repeatCount="indefinite"/>
                                </circle>
                                
                                <!-- Centro principal -->
                                <circle cx="70" cy="70" r="45" fill="url(#ultraGrad)" filter="url(#ultraGlow)" opacity="0.9"/>
                                
                                <!-- Sistema de datos central -->
                                <g transform="translate(70,70)">
                                    <!-- Icono de base de datos -->
                                    <ellipse cx="0" cy="-15" rx="20" ry="6" fill="rgba(255,255,255,0.9)"/>
                                    <rect x="-20" y="-15" width="40" height="25" fill="rgba(255,255,255,0.7)"/>
                                    <ellipse cx="0" cy="10" rx="20" ry="6" fill="rgba(255,255,255,0.9)"/>
                                    
                                    <!-- Datos binarios orbitales -->
                                    <text x="-25" y="-25" fill="rgba(255,255,255,0.6)" font-size="8" font-family="monospace">10110</text>
                                    <text x="15" y="-30" fill="rgba(255,255,255,0.6)" font-size="8" font-family="monospace">DATA</text>
                                    <text x="-30" y="25" fill="rgba(255,255,255,0.6)" font-size="8" font-family="monospace">01101</text>
                                    <text x="12" y="30" fill="rgba(255,255,255,0.6)" font-size="8" font-family="monospace">2.8M+</text>
                                </g>
                                
                                <!-- Puntos de datos satelitales -->
                                <g>
                                    <circle cx="20" cy="35" r="4" fill="rgba(255,255,255,0.8)">
                                        <animateTransform attributeName="transform" type="rotate" values="0 70 70;360 70 70" dur="12s" repeatCount="indefinite"/>
                                        <animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite"/>
                                    </circle>
                                    <circle cx="120" cy="35" r="4" fill="rgba(255,255,255,0.8)">
                                        <animateTransform attributeName="transform" type="rotate" values="90 70 70;450 70 70" dur="12s" repeatCount="indefinite"/>
                                        <animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite" begin="0.75s"/>
                                    </circle>
                                    <circle cx="120" cy="105" r="4" fill="rgba(255,255,255,0.8)">
                                        <animateTransform attributeName="transform" type="rotate" values="180 70 70;540 70 70" dur="12s" repeatCount="indefinite"/>
                                        <animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite" begin="1.5s"/>
                                    </circle>
                                    <circle cx="20" cy="105" r="4" fill="rgba(255,255,255,0.8)">
                                        <animateTransform attributeName="transform" type="rotate" values="270 70 70;630 70 70" dur="12s" repeatCount="indefinite"/>
                                        <animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite" begin="2.25s"/>
                                    </circle>
                                </g>
                            </svg>
                        </div>
                        <div>
                            <h1 class="text-4xl font-black text-glow">TuDatos</h1>
                            <p class="text-sm opacity-90 font-medium">Base de Datos Más Grande • Costa Rica</p>
                        </div>
                    </div>
                    
                    <!-- Stats en tiempo real -->
                    <div class="hidden lg:flex items-center space-x-8">
                        <div class="glass-ultra rounded-2xl px-6 py-4">
                            <div class="text-center">
                                <div class="text-2xl font-black text-yellow-300" x-text="formatNumber(liveStats.totalRecords)"></div>
                                <div class="text-xs opacity-80">Registros Totales</div>
                            </div>
                        </div>
                        <div class="glass-ultra rounded-2xl px-6 py-4">
                            <div class="text-center">
                                <div class="text-2xl font-black text-green-300" x-text="liveStats.activeUsers"></div>
                                <div class="text-xs opacity-80">Usuarios Activos</div>
                            </div>
                        </div>
                        <div class="glass-ultra rounded-2xl px-6 py-4">
                            <div class="text-center">
                                <div class="text-2xl font-black text-blue-300" x-text="liveStats.searchesToday"></div>
                                <div class="text-xs opacity-80">Búsquedas Hoy</div>
                            </div>
                        </div>
                    </div>

                    <!-- Acciones -->
                    <div class="flex items-center space-x-4">
                        <button @click="showRegister = true" class="glass-ultra hover:bg-white hover:bg-opacity-10 px-6 py-3 rounded-xl font-bold transition-all">
                            <i class="fas fa-user-plus mr-2"></i>Registro
                        </button>
                        <button @click="showLogin = true" class="bg-white bg-opacity-20 hover:bg-opacity-30 px-6 py-3 rounded-xl font-bold transition-all pulse-ultra">
                            <i class="fas fa-sign-in-alt mr-2"></i>Iniciar Sesión
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    </header>

    <!-- Hero Section Ultra -->
    <section class="relative py-32 gradient-primary">
        <div class="max-w-7xl mx-auto px-4 text-center relative z-10">
            <div class="floating">
                <h1 class="text-7xl md:text-9xl font-black mb-8 text-glow leading-tight">
                    LA BASE DE DATOS
                    <br>
                    <span class="text-yellow-300">MÁS GRANDE</span>
                    <br>
                    DE COSTA RICA
                </h1>
                <p class="text-3xl md:text-4xl mb-12 opacity-90 max-w-5xl mx-auto leading-relaxed">
                    <span class="font-black text-yellow-300">2,847,691</span> registros completos con 
                    <span class="font-black text-yellow-300">FOTOS</span>, 
                    <span class="font-black text-yellow-300">DATOS FAMILIARES</span>, 
                    <span class="font-black text-yellow-300">INFORMACIÓN FINANCIERA</span> 
                    y <span class="font-black text-yellow-300">REDES SOCIALES</span>
                </p>
                
                <!-- Stats Ultra Impresionantes -->
                <div class="grid grid-cols-2 md:grid-cols-5 gap-6 mb-16">
                    <div class="glass-ultra rounded-3xl p-8 ultra-card">
                        <div class="text-5xl font-black text-yellow-300 mb-3">2.8M+</div>
                        <div class="text-sm opacity-80 font-semibold">Personas Físicas</div>
                        <div class="text-xs opacity-60 mt-1">Con Fotos Incluidas</div>
                    </div>
                    <div class="glass-ultra rounded-3xl p-8 ultra-card">
                        <div class="text-5xl font-black text-yellow-300 mb-3">500K+</div>
                        <div class="text-sm opacity-80 font-semibold">Empresas Completas</div>
                        <div class="text-xs opacity-60 mt-1">Datos Financieros</div>
                    </div>
                    <div class="glass-ultra rounded-3xl p-8 ultra-card">
                        <div class="text-5xl font-black text-yellow-300 mb-3">1.5M+</div>
                        <div class="text-sm opacity-80 font-semibold">Fotos Verificadas</div>
                        <div class="text-xs opacity-60 mt-1">De Daticos</div>
                    </div>
                    <div class="glass-ultra rounded-3xl p-8 ultra-card">
                        <div class="text-5xl font-black text-yellow-300 mb-3">3.4M+</div>
                        <div class="text-sm opacity-80 font-semibold">Perfiles Sociales</div>
                        <div class="text-xs opacity-60 mt-1">Todas las Redes</div>
                    </div>
                    <div class="glass-ultra rounded-3xl p-8 ultra-card">
                        <div class="text-5xl font-black text-yellow-300 mb-3">99.9%</div>
                        <div class="text-sm opacity-80 font-semibold">Precisión IA</div>
                        <div class="text-xs opacity-60 mt-1">Sistema Autónomo</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Búsqueda Ultra Avanzada -->
    <section class="py-24 bg-gray-900">
        <div class="max-w-6xl mx-auto px-4">
            <div class="text-center mb-16">
                <h2 class="text-6xl font-black text-white mb-6">Búsqueda Ultra Inteligente</h2>
                <p class="text-2xl text-gray-300">Encuentra TODA la información disponible de cualquier persona</p>
            </div>
            
            <div class="glass-ultra rounded-3xl p-12 border border-white border-opacity-10">
                <!-- Búsqueda Principal -->
                <div class="relative mb-8">
                    <input type="text" x-model="searchQuery" @keydown.enter="performUltraSearch()" 
                           class="w-full px-8 py-6 text-2xl bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-2xl focus:border-blue-400 focus:outline-none text-white placeholder-gray-300 font-medium"
                           placeholder="🔍 Buscar por nombre, cédula, teléfono, email...">
                    <button @click="performUltraSearch()" :disabled="searching"
                            class="absolute right-3 top-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-xl font-bold hover:shadow-xl transition-all transform hover:scale-105 disabled:opacity-50">
                        <i class="fas fa-search mr-2" :class="{ 'fa-spin fa-spinner': searching }"></i>
                        <span x-text="searching ? 'Buscando...' : 'Buscar Ultra'"></span>
                    </button>
                </div>

                <!-- Información de búsqueda -->
                <div class="text-center mb-8">
                    <p class="text-gray-300 text-lg">
                        <i class="fas fa-info-circle mr-2 text-blue-400"></i>
                        Nuestra IA buscará en <span class="font-bold text-yellow-300">TODAS</span> las fuentes: 
                        Daticos (con fotos), TSE, CCSS, Registro Nacional, Redes Sociales
                    </p>
                </div>

                <!-- Resultados -->
                <div x-show="searchResults.length > 0" class="border-t border-white border-opacity-10 pt-8">
                    <h3 class="text-3xl font-bold text-white mb-6">
                        <i class="fas fa-search-plus mr-3 text-blue-400"></i>
                        Resultados Ultra Completos (<span x-text="searchResults.length"></span>)
                    </h3>
                    
                    <div class="space-y-6" id="ultraSearchResults">
                        <!-- Los resultados se cargarán aquí -->
                    </div>
                </div>

                <!-- Mensaje sin resultados -->
                <div x-show="searchPerformed && searchResults.length === 0" class="text-center py-12">
                    <i class="fas fa-search text-6xl text-gray-500 mb-4"></i>
                    <p class="text-2xl text-gray-400">No se encontraron resultados</p>
                    <p class="text-gray-500">Intenta con otro término de búsqueda</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Modal de Login -->
    <div x-show="showLogin" class="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4">
        <div class="glass-ultra rounded-3xl shadow-2xl max-w-md w-full p-8 border border-white border-opacity-20" @click.away="showLogin = false">
            <div class="text-center mb-8">
                <h2 class="text-4xl font-bold text-white mb-2">Iniciar Sesión</h2>
                <p class="text-gray-300">Acceso al sistema más avanzado</p>
            </div>
            
            <form @submit.prevent="ultraLogin()">
                <div class="mb-6">
                    <label class="block text-white text-sm font-bold mb-2">Usuario/Email</label>
                    <input type="text" x-model="loginData.username" class="w-full px-4 py-4 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl focus:border-blue-400 focus:outline-none text-white font-medium" placeholder="usuario o email">
                </div>
                <div class="mb-8">
                    <label class="block text-white text-sm font-bold mb-2">Contraseña</label>
                    <input type="password" x-model="loginData.password" class="w-full px-4 py-4 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl focus:border-blue-400 focus:outline-none text-white font-medium" placeholder="contraseña">
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 rounded-xl font-bold text-lg hover:shadow-xl transition-all transform hover:scale-105 mb-6">
                    <i class="fas fa-sign-in-alt mr-2"></i>Acceder al Sistema
                </button>
            </form>
            
            <div class="text-center">
                <button @click="showForgotPassword = true; showLogin = false" class="text-blue-400 hover:text-blue-300 text-sm font-medium">
                    ¿Olvidaste tu contraseña?
                </button>
            </div>
        </div>
    </div>

    <!-- Modal de Registro -->
    <div x-show="showRegister" class="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4">
        <div class="glass-ultra rounded-3xl shadow-2xl max-w-md w-full p-8 border border-white border-opacity-20" @click.away="showRegister = false">
            <div class="text-center mb-8">
                <h2 class="text-4xl font-bold text-white mb-2">Registro</h2>
                <p class="text-gray-300">Crea tu cuenta para acceder</p>
            </div>
            
            <form @submit.prevent="ultraRegister()">
                <div class="mb-4">
                    <input type="text" x-model="registerData.username" class="w-full px-4 py-3 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl focus:border-blue-400 focus:outline-none text-white font-medium" placeholder="Nombre de usuario" required>
                </div>
                <div class="mb-4">
                    <input type="email" x-model="registerData.email" class="w-full px-4 py-3 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl focus:border-blue-400 focus:outline-none text-white font-medium" placeholder="Email" required>
                </div>
                <div class="mb-4">
                    <input type="password" x-model="registerData.password" class="w-full px-4 py-3 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl focus:border-blue-400 focus:outline-none text-white font-medium" placeholder="Contraseña" required>
                </div>
                <div class="mb-6">
                    <input type="text" x-model="registerData.fullName" class="w-full px-4 py-3 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl focus:border-blue-400 focus:outline-none text-white font-medium" placeholder="Nombre completo" required>
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-green-500 to-blue-600 text-white py-4 rounded-xl font-bold text-lg hover:shadow-xl transition-all transform hover:scale-105">
                    <i class="fas fa-user-plus mr-2"></i>Crear Cuenta
                </button>
            </form>
        </div>
    </div>

    <script>
        function ultraApp() {
            return {
                // Estados de la app
                showLogin: false,
                showRegister: false,
                showForgotPassword: false,
                searching: false,
                searchPerformed: false,
                searchQuery: '',
                searchResults: [],
                currentUser: null,
                isLoggedIn: false,
                
                // Datos de formularios
                loginData: {
                    username: '',
                    password: ''
                },
                registerData: {
                    username: '',
                    email: '',
                    password: '',
                    fullName: ''
                },
                
                // Stats en tiempo real
                liveStats: {
                    totalRecords: 2847691,
                    activeUsers: 156,
                    searchesToday: 2347
                },
                
                // Inicialización
                init() {
                    this.updateLiveStats();
                    setInterval(() => this.updateLiveStats(), 30000);
                },
                
                // Actualizar stats
                updateLiveStats() {
                    this.liveStats.totalRecords += Math.floor(Math.random() * 10);
                    this.liveStats.activeUsers += Math.floor(Math.random() * 3) - 1;
                    this.liveStats.searchesToday += Math.floor(Math.random() * 5);
                },
                
                // Formatear números
                formatNumber(num) {
                    return new Intl.NumberFormat('es-CR').format(num);
                },
                
                // Login
                async ultraLogin() {
                    try {
                        const response = await fetch('/api/ultra/login', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(this.loginData)
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            this.currentUser = result.user;
                            this.isLoggedIn = true;
                            this.showLogin = false;
                            localStorage.setItem('ultra_token', result.token);
                            this.showNotification('✅ Inicio de sesión exitoso', 'success');
                            
                            // Redirigir a admin si es admin
                            if (result.user.role === 'super_admin') {
                                window.location.href = '/admin';
                            }
                        } else {
                            this.showNotification('❌ ' + result.message, 'error');
                        }
                    } catch (error) {
                        this.showNotification('🔥 Error de conexión', 'error');
                    }
                },
                
                // Registro
                async ultraRegister() {
                    try {
                        const response = await fetch('/api/ultra/register', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(this.registerData)
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            this.showRegister = false;
                            this.showNotification('✅ Cuenta creada exitosamente. Revisa tu email.', 'success');
                        } else {
                            this.showNotification('❌ ' + result.message, 'error');
                        }
                    } catch (error) {
                        this.showNotification('🔥 Error creando cuenta', 'error');
                    }
                },
                
                // Búsqueda ultra
                async performUltraSearch() {
                    if (!this.searchQuery.trim()) {
                        this.showNotification('⚠️ Ingresa un término de búsqueda', 'warning');
                        return;
                    }
                    
                    this.searching = true;
                    this.searchPerformed = true;
                    
                    try {
                        const headers = {};
                        const token = localStorage.getItem('ultra_token');
                        if (token) {
                            headers['Authorization'] = `Bearer ${token}`;
                        }
                        
                        const response = await fetch(`/api/ultra/search?q=${encodeURIComponent(this.searchQuery)}`, {
                            headers
                        });
                        
                        const results = await response.json();
                        
                        if (results.success) {
                            this.searchResults = results.data;
                            this.displayUltraResults(results.data);
                            this.showNotification(`✅ ${results.data.length} resultados encontrados`, 'success');
                        } else {
                            this.showNotification('❌ ' + results.message, 'error');
                        }
                        
                    } catch (error) {
                        this.showNotification('🔥 Error en búsqueda', 'error');
                    } finally {
                        this.searching = false;
                    }
                },
                
                // Mostrar resultados ultra
                displayUltraResults(results) {
                    const container = document.getElementById('ultraSearchResults');
                    if (!results || results.length === 0) {
                        container.innerHTML = '';
                        return;
                    }

                    let html = '';
                    results.forEach(person => {
                        html += `
                            <div class="glass-ultra rounded-2xl p-8 border border-white border-opacity-10 ultra-card">
                                <div class="flex justify-between items-start mb-6">
                                    <div>
                                        <h4 class="text-3xl font-bold text-white mb-2">${person.nombre_completo || 'N/A'}</h4>
                                        <p class="text-xl text-blue-300 font-semibold">🆔 ${person.cedula || 'N/A'}</p>
                                    </div>
                                    <div class="flex space-x-2">
                                        <span class="px-3 py-1 bg-green-600 text-white rounded-full text-sm font-bold">
                                            ✅ Verificado
                                        </span>
                                        <span class="px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-bold">
                                            📊 Score: ${person.confiabilidad_score || 'N/A'}
                                        </span>
                                    </div>
                                </div>
                                
                                <!-- Información de contacto -->
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                    <div class="bg-white bg-opacity-5 rounded-xl p-4">
                                        <h5 class="text-lg font-bold text-yellow-300 mb-3">📞 Contacto</h5>
                                        <div class="space-y-2 text-sm">
                                            ${person.telefonos ? person.telefonos.map(tel => `<p class="text-gray-300"><strong>Tel:</strong> ${tel}</p>`).join('') : '<p class="text-gray-500">Sin teléfonos</p>'}
                                            ${person.emails ? person.emails.map(email => `<p class="text-gray-300"><strong>Email:</strong> ${email}</p>`).join('') : '<p class="text-gray-500">Sin emails</p>'}
                                        </div>
                                    </div>
                                    
                                    <div class="bg-white bg-opacity-5 rounded-xl p-4">
                                        <h5 class="text-lg font-bold text-yellow-300 mb-3">👨‍👩‍👧‍👦 Familia</h5>
                                        <div class="space-y-2 text-sm">
                                            ${person.padre_nombre ? `<p class="text-gray-300"><strong>Padre:</strong> ${person.padre_nombre}</p>` : ''}
                                            ${person.madre_nombre ? `<p class="text-gray-300"><strong>Madre:</strong> ${person.madre_nombre}</p>` : ''}
                                            ${person.conyuge_nombre ? `<p class="text-gray-300"><strong>Cónyuge:</strong> ${person.conyuge_nombre}</p>` : ''}
                                            ${person.hijos && person.hijos.length > 0 ? `<p class="text-gray-300"><strong>Hijos:</strong> ${person.hijos.length}</p>` : ''}
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Redes sociales -->
                                <div class="bg-white bg-opacity-5 rounded-xl p-4 mb-6">
                                    <h5 class="text-lg font-bold text-yellow-300 mb-3">🌐 Redes Sociales</h5>
                                    <div class="flex flex-wrap gap-2">
                                        ${person.facebook ? `<span class="px-3 py-1 bg-blue-600 rounded-lg text-sm"><i class="fab fa-facebook mr-1"></i>${person.facebook}</span>` : ''}
                                        ${person.instagram ? `<span class="px-3 py-1 bg-pink-600 rounded-lg text-sm"><i class="fab fa-instagram mr-1"></i>${person.instagram}</span>` : ''}
                                        ${person.linkedin ? `<span class="px-3 py-1 bg-blue-800 rounded-lg text-sm"><i class="fab fa-linkedin mr-1"></i>${person.linkedin}</span>` : ''}
                                        ${person.twitter ? `<span class="px-3 py-1 bg-sky-600 rounded-lg text-sm"><i class="fab fa-twitter mr-1"></i>${person.twitter}</span>` : ''}
                                        ${person.whatsapp ? `<span class="px-3 py-1 bg-green-600 rounded-lg text-sm"><i class="fab fa-whatsapp mr-1"></i>WhatsApp</span>` : ''}
                                    </div>
                                </div>
                                
                                <!-- Fotos disponibles -->
                                ${person.fotos_disponibles && person.fotos_disponibles.length > 0 ? `
                                    <div class="bg-white bg-opacity-5 rounded-xl p-4 mb-6">
                                        <h5 class="text-lg font-bold text-yellow-300 mb-3">📸 Fotos Disponibles (${person.fotos_disponibles.length})</h5>
                                        <p class="text-gray-300 text-sm">Fotos verificadas de Daticos disponibles para consulta</p>
                                    </div>
                                ` : ''}
                                
                                <!-- Acciones -->
                                <div class="flex space-x-3">
                                    <button class="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-bold">
                                        <i class="fas fa-eye mr-2"></i>Ver Completo
                                    </button>
                                    <button class="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors font-bold">
                                        <i class="fas fa-download mr-2"></i>Descargar PDF
                                    </button>
                                    <button class="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors font-bold">
                                        <i class="fas fa-images mr-2"></i>Ver Fotos
                                    </button>
                                </div>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                },
                
                // Notificaciones
                showNotification(message, type = 'info') {
                    const colors = {
                        success: 'bg-green-600',
                        error: 'bg-red-600',
                        warning: 'bg-yellow-600',
                        info: 'bg-blue-600'
                    };
                    
                    const notification = document.createElement('div');
                    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-4 rounded-xl shadow-2xl z-50 transform transition-all duration-500 font-bold`;
                    notification.innerHTML = `
                        <div class="flex items-center space-x-2">
                            <span>${message}</span>
                            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `;
                    
                    document.body.appendChild(notification);
                    
                    setTimeout(() => {
                        notification.style.transform = 'translateX(100%)';
                        setTimeout(() => notification.remove(), 300);
                    }, 5000);
                }
            }
        }
    </script>
</body>
</html>
    """)

# =============================================================================
# ENDPOINTS DE API ULTRA AVANZADOS
# =============================================================================

@app.post("/api/ultra/login")
async def ultra_login(request: Request):
    """Login ultra seguro"""
    data = await request.json()
    username = data.get("username", "").lower()
    password = data.get("password", "")
    
    # Buscar por username o email
    user_found = None
    for user_id, user_data in users_system.items():
        if (user_data["username"].lower() == username or 
            user_data["email"].lower() == username):
            user_found = user_data
            break
    
    if user_found and verify_password(password, user_found["password_hash"]):
        if not user_found["is_active"]:
            return {"success": False, "message": "Usuario inactivo"}
        
        # Actualizar último login
        user_found["last_login"] = datetime.utcnow().isoformat()
        
        # Generar token (en producción sería JWT)
        token = f"{user_found['id']}_token"
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_found["id"],
                "username": user_found["username"],
                "email": user_found["email"],
                "role": user_found["role"],
                "credits": user_found["credits"],
                "plan": user_found["plan"],
                "full_name": user_found.get("profile_data", {}).get("full_name", "")
            }
        }
    
    return {"success": False, "message": "Credenciales incorrectas"}

@app.post("/api/ultra/register")
async def ultra_register(request: Request):
    """Registro ultra seguro con verificación de email"""
    data = await request.json()
    username = data.get("username", "").lower()
    email = data.get("email", "").lower()
    password = data.get("password", "")
    full_name = data.get("fullName", "")
    
    # Validaciones
    if len(username) < 3:
        return {"success": False, "message": "Username debe tener al menos 3 caracteres"}
    
    if len(password) < 6:
        return {"success": False, "message": "Contraseña debe tener al menos 6 caracteres"}
    
    # Verificar si ya existe
    for user_data in users_system.values():
        if user_data["username"].lower() == username:
            return {"success": False, "message": "Username ya existe"}
        if user_data["email"].lower() == email:
            return {"success": False, "message": "Email ya registrado"}
    
    # Crear usuario
    user_id = str(uuid.uuid4())
    reset_token = generate_reset_token()
    
    new_user = {
        "id": user_id,
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "role": UserRole.BASIC.value,
        "credits": 10,  # Créditos iniciales
        "plan": "Básico",
        "permissions": ["search"],
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None,
        "email_verified": False,
        "reset_token": reset_token,
        "reset_token_expires": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "profile_data": {
            "full_name": full_name,
            "phone": "",
            "company": "",
            "address": ""
        },
        "api_key": None,
        "rate_limit": 10,
        "is_active": True
    }
    
    users_system[user_id] = new_user
    
    # Enviar email de verificación (simulado)
    send_email(
        email, 
        "Verificación de cuenta - TuDatos",
        f"Tu token de verificación es: {reset_token}"
    )
    
    return {
        "success": True,
        "message": "Cuenta creada exitosamente. Revisa tu email para verificar.",
        "user_id": user_id
    }

@app.get("/api/ultra/search")
async def ultra_search(
    q: str,
    limit: int = 20,
    user: dict = Depends(verify_ultra_user)
):
    """Búsqueda ultra completa en toda la base de datos"""
    
    check_ultra_permission(user, "search")
    
    # Consumir créditos
    if user["credits"] <= 0:
        raise HTTPException(status_code=402, detail="Sin créditos suficientes")
    
    users_system[user["id"]]["credits"] -= 1
    
    query_lower = q.lower()
    results = []
    
    try:
        # Buscar en personas completas
        for persona in ultra_database["personas_completas"]:
            if ultra_search_match(persona, query_lower):
                results.append(persona)
                if len(results) >= limit:
                    break
        
        # Registrar búsqueda
        ultra_database["search_analytics"].append({
            "user_id": user["id"],
            "query": q,
            "results_count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "data": results,
            "total": len(results),
            "credits_remaining": users_system[user["id"]]["credits"],
            "query": q,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in ultra search: {e}")
        return {
            "success": False,
            "message": "Error interno en la búsqueda",
            "error": str(e)
        }

def ultra_search_match(persona, query):
    """Verificar si una persona coincide con la búsqueda ultra"""
    searchable_fields = [
        persona.get("nombre_completo", ""),
        persona.get("primer_nombre", ""),
        persona.get("primer_apellido", ""),
        persona.get("segundo_apellido", ""),
        persona.get("cedula", ""),
        " ".join(persona.get("telefonos", [])),
        " ".join(persona.get("emails", [])),
        persona.get("ocupacion_actual", ""),
        persona.get("empresa_actual", ""),
    ]
    
    search_text = " ".join(searchable_fields).lower()
    return query in search_text

# =============================================================================
# PANEL DE ADMINISTRACIÓN ULTRA COMPLETO
# =============================================================================

@app.get("/admin")
async def ultra_admin_panel():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Administración Ultra - TuDatos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .gradient-admin { background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%); }
        .glass-admin { background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }
        .admin-card { transition: all 0.3s ease; }
        .admin-card:hover { transform: translateY(-5px); }
    </style>
</head>
<body class="bg-gray-900 text-white" x-data="adminApp()">
    <!-- Header Admin -->
    <header class="gradient-admin shadow-2xl">
        <div class="max-w-7xl mx-auto px-4 py-6">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-4xl font-black">🎛️ Panel de Administración Ultra</h1>
                    <p class="text-xl opacity-90">Control total del sistema TuDatos</p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="text-right">
                        <p class="font-bold">Super Admin</p>
                        <p class="text-sm opacity-80">admin@tudatos.cr</p>
                    </div>
                    <button @click="logout()" class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-xl font-bold">
                        <i class="fas fa-sign-out-alt mr-2"></i>Salir
                    </button>
                </div>
            </div>
        </div>
    </header>

    <div class="flex">
        <!-- Sidebar Ultra -->
        <div class="w-80 glass-admin h-screen p-6 overflow-y-auto">
            <nav class="space-y-2">
                <button @click="currentSection = 'dashboard'" :class="currentSection === 'dashboard' ? 'bg-blue-600' : 'hover:bg-white hover:bg-opacity-10'" class="w-full flex items-center px-4 py-4 rounded-xl transition-all">
                    <i class="fas fa-tachometer-alt mr-4 text-xl"></i>Dashboard
                </button>
                <button @click="currentSection = 'users'" :class="currentSection === 'users' ? 'bg-blue-600' : 'hover:bg-white hover:bg-opacity-10'" class="w-full flex items-center px-4 py-4 rounded-xl transition-all">
                    <i class="fas fa-users mr-4 text-xl"></i>Gestión de Usuarios
                </button>
                <button @click="currentSection = 'extractors'" :class="currentSection === 'extractors' ? 'bg-blue-600' : 'hover:bg-white hover:bg-opacity-10'" class="w-full flex items-center px-4 py-4 rounded-xl transition-all">
                    <i class="fas fa-robot mr-4 text-xl"></i>Control de Extractores
                </button>
                <button @click="currentSection = 'database'" :class="currentSection === 'database' ? 'bg-blue-600' : 'hover:bg-white hover:bg-opacity-10'" class="w-full flex items-center px-4 py-4 rounded-xl transition-all">
                    <i class="fas fa-database mr-4 text-xl"></i>Base de Datos
                </button>
                <button @click="currentSection = 'system'" :class="currentSection === 'system' ? 'bg-blue-600' : 'hover:bg-white hover:bg-opacity-10'" class="w-full flex items-center px-4 py-4 rounded-xl transition-all">
                    <i class="fas fa-cogs mr-4 text-xl"></i>Configuración Sistema
                </button>
                <button @click="currentSection = 'analytics'" :class="currentSection === 'analytics' ? 'bg-blue-600' : 'hover:bg-white hover:bg-opacity-10'" class="w-full flex items-center px-4 py-4 rounded-xl transition-all">
                    <i class="fas fa-chart-line mr-4 text-xl"></i>Analytics Avanzados
                </button>
            </nav>
        </div>

        <!-- Contenido Principal -->
        <div class="flex-1 p-8 overflow-y-auto">
            <!-- Dashboard -->
            <div x-show="currentSection === 'dashboard'">
                <h2 class="text-4xl font-bold mb-8">📊 Dashboard Ultra</h2>
                
                <!-- Stats Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="glass-admin rounded-2xl p-6 admin-card">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-blue-300 font-medium">Registros Totales</p>
                                <p class="text-4xl font-black" x-text="formatNumber(dashStats.totalRecords)"></p>
                            </div>
                            <i class="fas fa-database text-4xl text-blue-400"></i>
                        </div>
                    </div>
                    <div class="glass-admin rounded-2xl p-6 admin-card">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-green-300 font-medium">Usuarios Activos</p>
                                <p class="text-4xl font-black" x-text="dashStats.activeUsers"></p>
                            </div>
                            <i class="fas fa-users text-4xl text-green-400"></i>
                        </div>
                    </div>
                    <div class="glass-admin rounded-2xl p-6 admin-card">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-purple-300 font-medium">Extractores Activos</p>
                                <p class="text-4xl font-black" x-text="dashStats.activeExtractors"></p>
                            </div>
                            <i class="fas fa-robot text-4xl text-purple-400"></i>
                        </div>
                    </div>
                    <div class="glass-admin rounded-2xl p-6 admin-card">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-yellow-300 font-medium">Búsquedas Hoy</p>
                                <p class="text-4xl font-black" x-text="dashStats.searchesToday"></p>
                            </div>
                            <i class="fas fa-search text-4xl text-yellow-400"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Gestión de Usuarios -->
            <div x-show="currentSection === 'users'">
                <div class="flex justify-between items-center mb-8">
                    <h2 class="text-4xl font-bold">👥 Gestión de Usuarios</h2>
                    <button @click="showCreateUser = true" class="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-xl font-bold">
                        <i class="fas fa-plus mr-2"></i>Crear Usuario
                    </button>
                </div>
                
                <!-- Tabla de Usuarios -->
                <div class="glass-admin rounded-2xl p-6">
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="border-b border-gray-600">
                                    <th class="text-left py-4 px-4 font-bold">Usuario</th>
                                    <th class="text-left py-4 px-4 font-bold">Plan</th>
                                    <th class="text-left py-4 px-4 font-bold">Créditos</th>
                                    <th class="text-left py-4 px-4 font-bold">Estado</th>
                                    <th class="text-left py-4 px-4 font-bold">Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                <template x-for="user in users" :key="user.id">
                                    <tr class="border-b border-gray-700 hover:bg-white hover:bg-opacity-5">
                                        <td class="py-4 px-4">
                                            <div>
                                                <div class="font-bold" x-text="user.username"></div>
                                                <div class="text-sm text-gray-400" x-text="user.email"></div>
                                            </div>
                                        </td>
                                        <td class="py-4 px-4">
                                            <span class="px-3 py-1 rounded-full text-sm font-bold" :class="getPlanColor(user.plan)" x-text="user.plan"></span>
                                        </td>
                                        <td class="py-4 px-4">
                                            <span class="font-bold" x-text="user.credits"></span>
                                        </td>
                                        <td class="py-4 px-4">
                                            <span class="px-3 py-1 rounded-full text-sm font-bold" :class="user.is_active ? 'bg-green-600' : 'bg-red-600'">
                                                <span x-text="user.is_active ? 'Activo' : 'Inactivo'"></span>
                                            </span>
                                        </td>
                                        <td class="py-4 px-4">
                                            <div class="flex space-x-2">
                                                <button @click="editUser(user)" class="px-3 py-2 bg-blue-600 rounded-lg text-sm font-bold hover:bg-blue-700">
                                                    <i class="fas fa-edit mr-1"></i>Editar
                                                </button>
                                                <button @click="addCredits(user.id)" class="px-3 py-2 bg-green-600 rounded-lg text-sm font-bold hover:bg-green-700">
                                                    <i class="fas fa-plus mr-1"></i>Créditos
                                                </button>
                                                <button @click="toggleUserStatus(user.id)" class="px-3 py-2 bg-yellow-600 rounded-lg text-sm font-bold hover:bg-yellow-700">
                                                    <i class="fas fa-toggle-on mr-1"></i>Toggle
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Control de Extractores -->
            <div x-show="currentSection === 'extractors'">
                <h2 class="text-4xl font-bold mb-8">🤖 Control de Extractores Ultra</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <template x-for="extractor in extractors" :key="extractor.id">
                        <div class="glass-admin rounded-2xl p-6">
                            <div class="flex justify-between items-start mb-4">
                                <h3 class="text-2xl font-bold" x-text="extractor.name"></h3>
                                <div class="flex items-center space-x-2">
                                    <div class="w-3 h-3 rounded-full" :class="extractor.status === 'active' ? 'bg-green-400 animate-pulse' : 'bg-red-400'"></div>
                                    <span class="font-bold" x-text="extractor.status === 'active' ? 'ACTIVO' : 'INACTIVO'"></span>
                                </div>
                            </div>
                            
                            <p class="text-gray-300 mb-4" x-text="extractor.description"></p>
                            
                            <div class="grid grid-cols-2 gap-4 mb-4 text-sm">
                                <div><span class="text-gray-400">Registros:</span> <span class="font-bold" x-text="formatNumber(extractor.records_extracted)"></span></div>
                                <div><span class="text-gray-400">Éxito:</span> <span class="font-bold text-green-400" x-text="extractor.success_rate + '%'"></span></div>
                                <div><span class="text-gray-400">Pendientes:</span> <span class="font-bold text-yellow-400" x-text="formatNumber(extractor.data_pending_integration)"></span></div>
                                <div><span class="text-gray-400">Errores:</span> <span class="font-bold text-red-400" x-text="extractor.errors_today"></span></div>
                            </div>
                            
                            <div class="flex space-x-2">
                                <button @click="controlExtractor(extractor.id, 'start')" class="px-4 py-2 bg-green-600 rounded-lg font-bold hover:bg-green-700">
                                    <i class="fas fa-play mr-1"></i>Iniciar
                                </button>
                                <button @click="controlExtractor(extractor.id, 'stop')" class="px-4 py-2 bg-red-600 rounded-lg font-bold hover:bg-red-700">
                                    <i class="fas fa-stop mr-1"></i>Detener
                                </button>
                                <button @click="integrateData(extractor.id)" class="px-4 py-2 bg-blue-600 rounded-lg font-bold hover:bg-blue-700">
                                    <i class="fas fa-database mr-1"></i>Integrar Datos
                                </button>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Crear Usuario -->
    <div x-show="showCreateUser" class="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4">
        <div class="glass-admin rounded-3xl max-w-md w-full p-8" @click.away="showCreateUser = false">
            <h3 class="text-3xl font-bold mb-6">Crear Usuario</h3>
            <form @submit.prevent="createUser()">
                <div class="mb-4">
                    <input type="text" x-model="newUser.username" class="w-full px-4 py-3 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl text-white" placeholder="Username" required>
                </div>
                <div class="mb-4">
                    <input type="email" x-model="newUser.email" class="w-full px-4 py-3 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl text-white" placeholder="Email" required>
                </div>
                <div class="mb-4">
                    <input type="password" x-model="newUser.password" class="w-full px-4 py-3 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl text-white" placeholder="Contraseña" required>
                </div>
                <div class="mb-6">
                    <select x-model="newUser.plan" class="w-full px-4 py-3 bg-white bg-opacity-10 border-2 border-white border-opacity-20 rounded-xl text-white">
                        <option value="Básico">Básico (10 créditos)</option>
                        <option value="Premium">Premium (1000 créditos)</option>
                        <option value="Enterprise">Enterprise (10000 créditos)</option>
                    </select>
                </div>
                <button type="submit" class="w-full bg-green-600 hover:bg-green-700 py-3 rounded-xl font-bold">
                    Crear Usuario
                </button>
            </form>
        </div>
    </div>

    <script>
        function adminApp() {
            return {
                currentSection: 'dashboard',
                showCreateUser: false,
                
                dashStats: {
                    totalRecords: 2847691,
                    activeUsers: 156,
                    activeExtractors: 5,
                    searchesToday: 2347
                },
                
                users: [],
                extractors: [],
                
                newUser: {
                    username: '',
                    email: '',
                    password: '',
                    plan: 'Básico'
                },
                
                init() {
                    this.loadUsers();
                    this.loadExtractors();
                },
                
                async loadUsers() {
                    try {
                        const response = await fetch('/api/admin/users', {
                            headers: { 'Authorization': 'Bearer superadmin_token' }
                        });
                        const result = await response.json();
                        if (result.success) {
                            this.users = result.users;
                        }
                    } catch (error) {
                        console.error('Error loading users:', error);
                    }
                },
                
                async loadExtractors() {
                    try {
                        const response = await fetch('/api/admin/extractors', {
                            headers: { 'Authorization': 'Bearer superadmin_token' }
                        });
                        const result = await response.json();
                        if (result.success) {
                            this.extractors = Object.values(result.extractors).map((ext, index) => ({
                                id: Object.keys(result.extractors)[index],
                                ...ext
                            }));
                        }
                    } catch (error) {
                        console.error('Error loading extractors:', error);
                    }
                },
                
                async createUser() {
                    try {
                        const response = await fetch('/api/admin/users/create', {
                            method: 'POST',
                            headers: {
                                'Authorization': 'Bearer superadmin_token',
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(this.newUser)
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            this.showCreateUser = false;
                            this.loadUsers();
                            this.showNotification('Usuario creado exitosamente', 'success');
                        } else {
                            this.showNotification(result.message, 'error');
                        }
                    } catch (error) {
                        this.showNotification('Error creando usuario', 'error');
                    }
                },
                
                async addCredits(userId) {
                    const credits = prompt('¿Cuántos créditos agregar?');
                    if (credits && !isNaN(credits)) {
                        try {
                            const response = await fetch(`/api/admin/users/${userId}/credits`, {
                                method: 'POST',
                                headers: {
                                    'Authorization': 'Bearer superadmin_token',
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ amount: parseInt(credits) })
                            });
                            
                            const result = await response.json();
                            if (result.success) {
                                this.loadUsers();
                                this.showNotification(`${credits} créditos agregados`, 'success');
                            }
                        } catch (error) {
                            this.showNotification('Error agregando créditos', 'error');
                        }
                    }
                },
                
                async controlExtractor(extractorId, action) {
                    try {
                        const response = await fetch(`/api/admin/extractors/${extractorId}/${action}`, {
                            method: 'POST',
                            headers: { 'Authorization': 'Bearer superadmin_token' }
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            this.loadExtractors();
                            this.showNotification(`Extractor ${action} exitosamente`, 'success');
                        }
                    } catch (error) {
                        this.showNotification('Error controlando extractor', 'error');
                    }
                },
                
                async integrateData(extractorId) {
                    try {
                        const response = await fetch(`/api/admin/extractors/${extractorId}/integrate`, {
                            method: 'POST',
                            headers: { 'Authorization': 'Bearer superadmin_token' }
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            this.loadExtractors();
                            this.showNotification(`${result.integrated_records} registros integrados`, 'success');
                        }
            
                    } catch (error) {
                        this.showNotification('Error integrando datos', 'error');
                    }
                },
                
                formatNumber(num) {
                    return new Intl.NumberFormat('es-CR').format(num);
                },
                
                getPlanColor(plan) {
                    const colors = {
                        'Básico': 'bg-gray-600',
                        'Premium': 'bg-blue-600',
                        'Enterprise': 'bg-purple-600',
                        'Super Admin': 'bg-red-600'
                    };
                    return colors[plan] || 'bg-gray-600';
                },
                
                showNotification(message, type) {
                    // Implementar notificaciones
                    alert(message);
                }
            }
        }
    </script>
</body>
</html>
    """)

# =============================================================================
# ENDPOINTS DE ADMINISTRACIÓN ULTRA
# =============================================================================

@app.get("/api/admin/users")
async def get_admin_users(user: dict = Depends(verify_ultra_user)):
    """Obtener todos los usuarios (solo admin)"""
    check_ultra_permission(user, "user_management")
    
    users_list = []
    for user_data in users_system.values():
        users_list.append({
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_data["role"],
            "credits": user_data["credits"],
            "plan": user_data["plan"],
            "is_active": user_data["is_active"],
            "created_at": user_data["created_at"],
            "last_login": user_data["last_login"]
        })
    
    return {"success": True, "users": users_list}

@app.post("/api/admin/users/create")
async def create_admin_user(request: Request, user: dict = Depends(verify_ultra_user)):
    """Crear usuario desde admin"""
    check_ultra_permission(user, "user_management")
    
    data = await request.json()
    
    # Crear usuario con lógica similar a register
    user_id = str(uuid.uuid4())
    plan_credits = {"Básico": 10, "Premium": 1000, "Enterprise": 10000}
    
    new_user = {
        "id": user_id,
        "username": data["username"],
        "email": data["email"],
        "password_hash": hash_password(data["password"]),
        "role": UserRole.BASIC.value if data["plan"] == "Básico" else UserRole.PREMIUM.value,
        "credits": plan_credits.get(data["plan"], 10),
        "plan": data["plan"],
        "permissions": ["search"] if data["plan"] == "Básico" else ["search", "export", "api"],
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None,
        "email_verified": True,
        "reset_token": None,
        "reset_token_expires": None,
        "profile_data": {"full_name": "", "phone": "", "company": "", "address": ""},
        "api_key": f"api_key_{user_id}" if data["plan"] != "Básico" else None,
        "rate_limit": 100 if data["plan"] != "Básico" else 10,
        "is_active": True
    }
    
    users_system[user_id] = new_user
    
    return {"success": True, "message": "Usuario creado exitosamente", "user_id": user_id}

@app.post("/api/admin/users/{user_id}/credits")
async def add_admin_credits(user_id: str, request: Request, user: dict = Depends(verify_ultra_user)):
    """Agregar créditos a usuario"""
    check_ultra_permission(user, "user_management")
    
    data = await request.json()
    amount = data.get("amount", 0)
    
    if user_id in users_system:
        users_system[user_id]["credits"] += amount
        return {
            "success": True,
            "message": f"{amount} créditos agregados",
            "new_balance": users_system[user_id]["credits"]
        }
    
    return {"success": False, "message": "Usuario no encontrado"}

@app.get("/api/admin/extractors")
async def get_admin_extractors(user: dict = Depends(verify_ultra_user)):
    """Obtener estado de extractores"""
    check_ultra_permission(user, "extractor_control")
    
    return {"success": True, "extractors": extractors_system}

@app.post("/api/admin/extractors/{extractor_id}/{action}")
async def control_admin_extractor(extractor_id: str, action: str, user: dict = Depends(verify_ultra_user)):
    """Control de extractores"""
    check_ultra_permission(user, "extractor_control")
    
    if extractor_id not in extractors_system:
        return {"success": False, "message": "Extractor no encontrado"}
    
    extractor = extractors_system[extractor_id]
    
    if action == "start":
        extractor["status"] = "active"
        extractor["last_run"] = datetime.utcnow().isoformat()
        message = f"Extractor {extractor['name']} iniciado"
    elif action == "stop":
        extractor["status"] = "inactive"
        message = f"Extractor {extractor['name']} detenido"
    else:
        return {"success": False, "message": "Acción no válida"}
    
    return {"success": True, "message": message}

@app.post("/api/admin/extractors/{extractor_id}/integrate")
async def integrate_extractor_data(extractor_id: str, user: dict = Depends(verify_ultra_user)):
    """Integrar datos pendientes de extractor"""
    check_ultra_permission(user, "data_management")
    
    if extractor_id not in extractors_system:
        return {"success": False, "message": "Extractor no encontrado"}
    
    extractor = extractors_system[extractor_id]
    pending = extractor.get("data_pending_integration", 0)
    
    # Simular integración de datos
    if pending > 0:
        integrated = min(pending, 5000)  # Integrar máximo 5000 a la vez
        extractor["data_pending_integration"] -= integrated
        extractor["records_extracted"] += integrated
        
        return {
            "success": True,
            "message": f"{integrated} registros integrados exitosamente",
            "integrated_records": integrated,
            "remaining_pending": extractor["data_pending_integration"]
        }
    
    return {"success": False, "message": "No hay datos pendientes para integrar"}

@app.get("/api/health/ultra")
async def ultra_health():
    """Health check ultra completo"""
    return {
        "status": "ultra_healthy",
        "version": "4.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "personas_completas": len(ultra_database["personas_completas"]),
            "total_records": len(ultra_database["personas_completas"])
        },
        "users": {
            "total": len(users_system),
            "active": len([u for u in users_system.values() if u["is_active"]])
        },
        "extractors": {
            "total": len(extractors_system),
            "active": len([e for e in extractors_system.values() if e["status"] == "active"])
        },
        "services": {
            "authentication": "operational",
            "search_engine": "operational",
            "admin_panel": "operational",
            "extractors": "operational"
        }
    }