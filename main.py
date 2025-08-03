from fastapi import FastAPI, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, List
import json
import random
import uuid
from datetime import datetime, timedelta
import hashlib
import asyncio

app = FastAPI(title="TuDatos Sistema Profesional", version="2.0.0")
security = HTTPBearer()

# Sistema de usuarios y créditos
users_db = {
    "admin": {
        "id": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "credits": 999999,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": datetime.utcnow().isoformat()
    },
    "demo": {
        "id": "demo", 
        "password": hashlib.sha256("demo123".encode()).hexdigest(),
        "role": "user",
        "credits": 50,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": datetime.utcnow().isoformat()
    }
}

# Base de datos simulada avanzada
advanced_database = {
    "personas_fisicas": [
        {
            "id": str(uuid.uuid4()),
            "cedula": "1-1234-5678",
            "nombre": "José Manuel",
            "primer_apellido": "González",
            "segundo_apellido": "Rodríguez", 
            "telefono": "+50622001234",
            "email": "jgonzalez@gmail.com",
            "provincia": "San José",
            "canton": "Central",
            "distrito": "Carmen",
            "direccion": "Del ICE 200m este",
            "ocupacion": "Ingeniero Civil",
            "estado_civil": "Soltero",
            "fecha_nacimiento": "1985-03-15",
            "nivel_educativo": "Universitario",
            "ingresos_estimados": "$2500",
            "tipo_vivienda": "Propia",
            "vehiculos": ["Toyota Corolla 2020"],
            "redes_sociales": {
                "facebook": "jose.gonzalez.cr",
                "linkedin": "jose-gonzalez-ing"
            },
            "referencias_comerciales": ["BAC San José", "Auto Mercado"],
            "historial_crediticio": "Excelente",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "cedula": "2-5678-9012",
            "nombre": "María Carmen",
            "primer_apellido": "Jiménez",
            "segundo_apellido": "López",
            "telefono": "+50687654321",
            "email": "mjimenez@hotmail.com",
            "provincia": "Alajuela",
            "canton": "Central", 
            "distrito": "Alajuela",
            "direccion": "Barrio San José, casa 45",
            "ocupacion": "Doctora Medicina General",
            "estado_civil": "Casada",
            "fecha_nacimiento": "1980-07-22",
            "nivel_educativo": "Posgrado",
            "ingresos_estimados": "$4000",
            "tipo_vivienda": "Propia",
            "vehiculos": ["Honda CR-V 2019", "Nissan Sentra 2018"],
            "redes_sociales": {
                "facebook": "maria.jimenez.dr",
                "instagram": "dra_maria_cr"
            },
            "referencias_comerciales": ["Hospital Clínica Bíblica", "Farmacia Fischel"],
            "historial_crediticio": "Excelente",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
    ],
    "personas_juridicas": [
        {
            "id": str(uuid.uuid4()),
            "cedula_juridica": "3-101-234567",
            "razon_social": "Comercial Santa Fe Sociedad Anónima",
            "nombre_comercial": "Santa Fe Store",
            "telefono": "+50622567890",
            "email": "info@santafe.co.cr",
            "sitio_web": "www.santafe.co.cr",
            "provincia": "San José",
            "canton": "Escazú",
            "distrito": "Escazú Centro",
            "direccion": "Centro Comercial Multiplaza, Local 123",
            "sector_negocio": "Retail/Comercio",
            "fecha_constitucion": "2010-05-15",
            "capital_social": "$500000",
            "numero_empleados": 45,
            "representante_legal": "Juan Carlos Mora Sánchez",
            "cedula_representante": "1-0987-6543",
            "actividades_economicas": ["Venta al por menor", "Importación"],
            "proveedores": ["Walmart Internacional", "Procter & Gamble"],
            "clientes_principales": "Consumidor final",
            "ingresos_anuales": "$2500000",
            "estado_tributario": "Al día",
            "referencias_bancarias": ["Banco Nacional", "BCR"],
            "calificacion_crediticia": "AAA",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
    ],
    "profesionales": [
        {
            "id": str(uuid.uuid4()),
            "cedula": "1-1234-5678",
            "nombre_completo": "Dr. José Manuel González Rodríguez",
            "profesion": "Médico Cirujano",
            "especialidad": "Cardiología",
            "colegio_profesional": "Colegio de Médicos de Costa Rica",
            "numero_colegiado": "MD-12345",
            "consultorio": "Hospital Clínica Bíblica",
            "telefono_consultorio": "+50622001234",
            "horarios_atencion": "L-V 8:00-17:00",
            "anos_experiencia": 15,
            "educacion": "Universidad de Costa Rica, Harvard Medical School",
            "certificaciones": ["Cardiología Intervencionista", "Ecocardiografía"],
            "idiomas": ["Español", "Inglés", "Francés"],
            "seguros_aceptados": ["INS", "Sagicor", "BMI"],
            "created_at": datetime.utcnow().isoformat()
        }
    ],
    "vehiculos": [
        {
            "placa": "BCR123",
            "propietario_cedula": "1-1234-5678",
            "marca": "Toyota",
            "modelo": "Corolla",
            "año": "2020",
            "color": "Blanco",
            "tipo": "Sedan",
            "combustible": "Gasolina",
            "transmision": "Automática",
            "cilindrada": "1800cc",
            "valor_estimado": "$18000",
            "estado": "Activo",
            "ultimo_riteve": "2024-06-15",
            "seguro": "INS",
            "multas_pendientes": 0,
            "created_at": datetime.utcnow().isoformat()
        }
    ],
    "propiedades": [
        {
            "numero_finca": "F-123456",
            "propietario_cedula": "1-1234-5678",
            "tipo_propiedad": "Casa de habitación",
            "provincia": "San José",
            "canton": "Central", 
            "distrito": "Carmen",
            "direccion": "Del ICE 200m este, casa portón verde",
            "area_terreno": "250 m²",
            "area_construccion": "180 m²",
            "valor_catastral": "$85000",
            "valor_mercado": "$120000",
            "año_construccion": "2015",
            "servicios": ["Agua", "Electricidad", "Internet", "Cable"],
            "estado": "Excelente",
            "hipotecas": [],
            "impuestos_al_dia": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ]
}

# Estadísticas del sistema
system_stats = {
    "total_records": 2000121,
    "personas_fisicas": 1600097,
    "personas_juridicas": 400024,
    "profesionales": 150000,
    "vehiculos": 800000,
    "propiedades": 300000,
    "last_update": datetime.utcnow().isoformat(),
    "queries_today": 1247,
    "active_users": 89,
    "success_rate": 98.7
}

def verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar autenticación de usuario"""
    token = credentials.credentials
    # Simulación simple de JWT
    if token in ["admin_token", "demo_token"]:
        return "admin" if token == "admin_token" else "demo"
    raise HTTPException(status_code=401, detail="Invalid authentication")

@app.get("/")
async def root():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TuDatos Pro - Sistema Profesional Costa Rica</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .glass-effect { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); }
        .logo-animate { animation: logoFloat 3s ease-in-out infinite; }
        @keyframes logoFloat { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
        .pulse-slow { animation: pulse 3s infinite; }
        .slide-in { animation: slideIn 0.5s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header Navigation -->
    <nav class="bg-white shadow-lg border-b border-gray-200" x-data="{ isOpen: false, isLoggedIn: false }">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <!-- Logo Dinámico Extraordinario -->
                    <div class="flex-shrink-0 flex items-center space-x-3">
                        <div class="logo-animate">
                            <svg class="w-10 h-10" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                                <defs>
                                    <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                                        <stop offset="50%" style="stop-color:#764ba2;stop-opacity:1" />
                                        <stop offset="100%" style="stop-color:#f093fb;stop-opacity:1" />
                                    </linearGradient>
                                    <filter id="glow">
                                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                                        <feMerge> 
                                            <feMergeNode in="coloredBlur"/>
                                            <feMergeNode in="SourceGraphic"/>
                                        </feMerge>
                                    </filter>
                                </defs>
                                <!-- Círculo exterior con efecto de datos -->
                                <circle cx="50" cy="50" r="45" fill="none" stroke="url(#logoGrad)" stroke-width="2" opacity="0.3">
                                    <animate attributeName="stroke-dasharray" values="0 283;283 0;0 283" dur="3s" repeatCount="indefinite"/>
                                </circle>
                                <!-- Círculo central -->
                                <circle cx="50" cy="50" r="30" fill="url(#logoGrad)" filter="url(#glow)" opacity="0.8"/>
                                <!-- Icono de búsqueda estilizado -->
                                <circle cx="42" cy="42" r="12" fill="none" stroke="white" stroke-width="2.5"/>
                                <path d="M52 52L62 62" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                                <!-- Puntos de datos animados -->
                                <circle cx="25" cy="25" r="2" fill="#667eea">
                                    <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" begin="0s"/>
                                </circle>
                                <circle cx="75" cy="25" r="2" fill="#764ba2">
                                    <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" begin="0.7s"/>
                                </circle>
                                <circle cx="25" cy="75" r="2" fill="#f093fb">
                                    <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" begin="1.4s"/>
                                </circle>
                                <circle cx="75" cy="75" r="2" fill="#667eea">
                                    <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" begin="2.1s"/>
                                </circle>
                            </svg>
                        </div>
                        <div>
                            <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                TuDatos Pro
                            </h1>
                            <p class="text-xs text-gray-500">Sistema Profesional Costa Rica</p>
                        </div>
                    </div>
                </div>
                
                <!-- Navegación Desktop -->
                <div class="hidden md:flex items-center space-x-8">
                    <a href="#buscar" class="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors">
                        <i class="fas fa-search mr-2"></i>Buscar
                    </a>
                    <a href="#estadisticas" class="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors">
                        <i class="fas fa-chart-bar mr-2"></i>Estadísticas
                    </a>
                    <a href="#admin" class="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors">
                        <i class="fas fa-cog mr-2"></i>Admin
                    </a>
                    <div class="flex items-center space-x-4">
                        <div class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                            <i class="fas fa-coins mr-1"></i>50 Créditos
                        </div>
                        <button onclick="showLogin()" class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all">
                            <i class="fas fa-sign-in-alt mr-2"></i>Iniciar Sesión
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="gradient-bg text-white py-20">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <div class="slide-in">
                <h1 class="text-5xl md:text-6xl font-bold mb-6">
                    La Base de Datos Más
                    <span class="text-yellow-300">Completa</span> de Costa Rica
                </h1>
                <p class="text-xl md:text-2xl mb-8 opacity-90">
                    Más de <span class="font-bold text-yellow-300">2,000,121</span> registros actualizados en tiempo real
                </p>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
                    <div class="glass-effect rounded-xl p-4">
                        <div class="text-3xl font-bold">1.6M+</div>
                        <div class="text-sm opacity-80">Personas Físicas</div>
                    </div>
                    <div class="glass-effect rounded-xl p-4">
                        <div class="text-3xl font-bold">400K+</div>
                        <div class="text-sm opacity-80">Empresas</div>
                    </div>
                    <div class="glass-effect rounded-xl p-4">
                        <div class="text-3xl font-bold">150K+</div>
                        <div class="text-sm opacity-80">Profesionales</div>
                    </div>
                    <div class="glass-effect rounded-xl p-4">
                        <div class="text-3xl font-bold">98.7%</div>
                        <div class="text-sm opacity-80">Precisión</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Búsqueda Avanzada -->
    <section id="buscar" class="py-16 bg-white">
        <div class="max-w-4xl mx-auto px-4">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold text-gray-900 mb-4">Búsqueda Inteligente</h2>
                <p class="text-xl text-gray-600">Encuentra cualquier información con nuestra IA avanzada</p>
            </div>
            
            <div class="bg-white rounded-2xl shadow-2xl border border-gray-200 p-8" x-data="{ searchType: 'general', loading: false, results: [] }">
                <!-- Tabs de Búsqueda -->
                <div class="flex flex-wrap gap-2 mb-6">
                    <button @click="searchType = 'general'" :class="searchType === 'general' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'" 
                            class="px-4 py-2 rounded-lg font-medium transition-all">
                        <i class="fas fa-search mr-2"></i>General
                    </button>
                    <button @click="searchType = 'cedula'" :class="searchType === 'cedula' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'" 
                            class="px-4 py-2 rounded-lg font-medium transition-all">
                        <i class="fas fa-id-card mr-2"></i>Por Cédula
                    </button>
                    <button @click="searchType = 'empresa'" :class="searchType === 'empresa' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'" 
                            class="px-4 py-2 rounded-lg font-medium transition-all">
                        <i class="fas fa-building mr-2"></i>Empresas
                    </button>
                    <button @click="searchType = 'profesional'" :class="searchType === 'profesional' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'" 
                            class="px-4 py-2 rounded-lg font-medium transition-all">
                        <i class="fas fa-user-md mr-2"></i>Profesionales
                    </button>
                    <button @click="searchType = 'vehiculo'" :class="searchType === 'vehiculo' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'" 
                            class="px-4 py-2 rounded-lg font-medium transition-all">
                        <i class="fas fa-car mr-2"></i>Vehículos
                    </button>
                    <button @click="searchType = 'propiedad'" :class="searchType === 'propiedad' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'" 
                            class="px-4 py-2 rounded-lg font-medium transition-all">
                        <i class="fas fa-home mr-2"></i>Propiedades
                    </button>
                </div>

                <!-- Campo de Búsqueda -->
                <div class="relative mb-6">
                    <input type="text" id="searchInput" 
                           class="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none pr-24"
                           :placeholder="getPlaceholder(searchType)">
                    <button onclick="performSearch()" 
                            class="absolute right-2 top-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg font-medium hover:shadow-lg transition-all">
                        <i class="fas fa-search mr-2"></i>Buscar
                    </button>
                </div>

                <!-- Filtros Avanzados -->
                <div class="border-t pt-6 mb-6">
                    <h3 class="text-lg font-semibold mb-4 text-gray-900">Filtros Avanzados</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <select class="px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none">
                            <option value="">Provincia</option>
                            <option value="san-jose">San José</option>
                            <option value="alajuela">Alajuela</option>
                            <option value="cartago">Cartago</option>
                            <option value="heredia">Heredia</option>
                            <option value="guanacaste">Guanacaste</option>
                            <option value="puntarenas">Puntarenas</option>
                            <option value="limon">Limón</option>
                        </select>
                        <select class="px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none">
                            <option value="">Rango de Edad</option>
                            <option value="18-25">18-25 años</option>
                            <option value="26-35">26-35 años</option>
                            <option value="36-50">36-50 años</option>
                            <option value="51+">51+ años</option>
                        </select>
                        <select class="px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none">
                            <option value="">Sector</option>
                            <option value="salud">Salud</option>
                            <option value="educacion">Educación</option>
                            <option value="comercio">Comercio</option>
                            <option value="tecnologia">Tecnología</option>
                            <option value="construccion">Construcción</option>
                        </select>
                    </div>
                </div>

                <!-- Resultados -->
                <div id="searchResults" style="display: none;" class="border-t pt-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-xl font-semibold text-gray-900">Resultados de Búsqueda</h3>
                        <div class="flex space-x-2">
                            <button class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                                <i class="fas fa-download mr-2"></i>Exportar CSV
                            </button>
                            <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                <i class="fas fa-file-pdf mr-2"></i>Exportar PDF
                            </button>
                        </div>
                    </div>
                    <div id="resultsContainer"></div>
                </div>
            </div>
        </div>
    </section>

    <!-- Sistema de Créditos Moderno -->
    <section class="py-16 bg-gradient-to-br from-purple-50 to-blue-50">
        <div class="max-w-6xl mx-auto px-4">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold text-gray-900 mb-4">Sistema de Créditos Inteligente</h2>
                <p class="text-xl text-gray-600">Paga solo por lo que usas con nuestro sistema avanzado de créditos</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                <!-- Plan Básico -->
                <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-all">
                    <div class="text-center">
                        <div class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="fas fa-search text-2xl text-blue-600"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-gray-900 mb-2">Plan Básico</h3>
                        <div class="text-4xl font-bold text-blue-600 mb-4">100<span class="text-lg text-gray-500">/créditos</span></div>
                        <div class="text-gray-600 mb-6">$19.99</div>
                        <ul class="text-left text-gray-600 mb-8 space-y-2">
                            <li><i class="fas fa-check text-green-500 mr-2"></i>100 consultas de personas</li>
                            <li><i class="fas fa-check text-green-500 mr-2"></i>50 consultas de empresas</li>
                            <li><i class="fas fa-check text-green-500 mr-2"></i>Búsqueda básica</li>
                            <li><i class="fas fa-check text-green-500 mr-2"></i>Soporte por email</li>
                        </ul>
                        <button class="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors">
                            Adquirir Plan
                        </button>
                    </div>
                </div>

                <!-- Plan Profesional -->
                <div class="bg-gradient-to-br from-purple-600 to-blue-600 rounded-2xl shadow-xl border border-purple-200 p-8 transform scale-105 hover:scale-110 transition-all text-white relative">
                    <div class="absolute -top-4 left-1/2 transform -translate-x-1/2">
                        <span class="bg-yellow-400 text-yellow-900 px-4 py-1 rounded-full text-sm font-bold">MÁS POPULAR</span>
                    </div>
                    <div class="text-center">
                        <div class="bg-white bg-opacity-20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="fas fa-crown text-2xl text-yellow-300"></i>
                        </div>
                        <h3 class="text-2xl font-bold mb-2">Plan Profesional</h3>
                        <div class="text-4xl font-bold mb-4">500<span class="text-lg opacity-75">/créditos</span></div>
                        <div class="opacity-75 mb-6">$79.99</div>
                        <ul class="text-left mb-8 space-y-2 opacity-90">
                            <li><i class="fas fa-check text-yellow-300 mr-2"></i>500 consultas de personas</li>
                            <li><i class="fas fa-check text-yellow-300 mr-2"></i>300 consultas de empresas</li>
                            <li><i class="fas fa-check text-yellow-300 mr-2"></i>Búsqueda avanzada + IA</li>
                            <li><i class="fas fa-check text-yellow-300 mr-2"></i>Exportación ilimitada</li>
                            <li><i class="fas fa-check text-yellow-300 mr-2"></i>API Access</li>
                            <li><i class="fas fa-check text-yellow-300 mr-2"></i>Soporte prioritario</li>
                        </ul>
                        <button class="w-full bg-white text-purple-600 py-3 rounded-xl font-semibold hover:bg-gray-100 transition-colors">
                            Adquirir Plan
                        </button>
                    </div>
                </div>

                <!-- Plan Empresarial -->
                <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 hover:shadow-xl transition-all">
                    <div class="text-center">
                        <div class="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="fas fa-building text-2xl text-gray-600"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-gray-900 mb-2">Plan Empresarial</h3>
                        <div class="text-4xl font-bold text-gray-900 mb-4">∞<span class="text-lg text-gray-500">/créditos</span></div>
                        <div class="text-gray-600 mb-6">$299.99</div>
                        <ul class="text-left text-gray-600 mb-8 space-y-2">
                            <li><i class="fas fa-check text-green-500 mr-2"></i>Consultas ilimitadas</li>
                            <li><i class="fas fa-check text-green-500 mr-2"></i>Múltiples usuarios</li>
                            <li><i class="fas fa-check text-green-500 mr-2"></i>Dashboard personalizado</li>
                            <li><i class="fas fa-check text-green-500 mr-2"></i>API ilimitada</li>
                            <li><i class="fas fa-check text-green-500 mr-2"></i>Integración CRM</li>
                            <li><i class="fas fa-check text-green-500 mr-2"></i>Soporte 24/7</li>
                        </ul>
                        <button class="w-full bg-gray-900 text-white py-3 rounded-xl font-semibold hover:bg-gray-800 transition-colors">
                            Contactar Ventas
                        </button>
                    </div>
                </div>
            </div>

            <!-- Monitor de Créditos en Tiempo Real -->
            <div class="bg-white rounded-2xl shadow-lg p-8">
                <h3 class="text-2xl font-bold text-gray-900 mb-6 text-center">Tu Cuenta de Créditos</h3>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div class="text-center">
                        <div class="text-3xl font-bold text-blue-600">50</div>
                        <div class="text-gray-600">Créditos Disponibles</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-green-600">23</div>
                        <div class="text-gray-600">Usados Hoy</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-purple-600">156</div>
                        <div class="text-gray-600">Total del Mes</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-orange-600">$2.30</div>
                        <div class="text-gray-600">Costo Promedio</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Modal de Login -->
    <div id="loginModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden">
        <div class="flex items-center justify-center min-h-screen p-4">
            <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 transform transition-all">
                <div class="text-center mb-8">
                    <h2 class="text-3xl font-bold text-gray-900">Iniciar Sesión</h2>
                    <p class="text-gray-600 mt-2">Accede a tu cuenta profesional</p>
                </div>
                <form id="loginForm">
                    <div class="mb-6">
                        <label class="block text-gray-700 text-sm font-semibold mb-2">Usuario</label>
                        <input type="text" id="username" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none" placeholder="admin / demo">
                    </div>
                    <div class="mb-6">
                        <label class="block text-gray-700 text-sm font-semibold mb-2">Contraseña</label>
                        <input type="password" id="password" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none" placeholder="admin123 / demo123">
                    </div>
                    <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all mb-4">
                        Iniciar Sesión
                    </button>
                </form>
                <div class="text-center">
                    <p class="text-sm text-gray-600">
                        Demo: admin/admin123 | demo/demo123
                    </p>
                    <button onclick="hideLogin()" class="text-blue-600 hover:text-blue-800 text-sm font-medium mt-2">
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Panel de Administración -->
    <section id="admin" class="py-16 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold text-gray-900 mb-4">Panel de Administración Profesional</h2>
                <p class="text-xl text-gray-600">Control total de tu sistema TuDatos Pro</p>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <!-- Sidebar Admin -->
                <div class="bg-white rounded-2xl shadow-lg p-6">
                    <nav class="space-y-2">
                        <a href="#" class="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-colors">
                            <i class="fas fa-tachometer-alt mr-3"></i>Dashboard
                        </a>
                        <a href="#" class="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-colors">
                            <i class="fas fa-users mr-3"></i>Usuarios
                        </a>
                        <a href="#" class="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-colors">
                            <i class="fas fa-database mr-3"></i>Base de Datos
                        </a>
                        <a href="#" class="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-colors">
                            <i class="fas fa-download mr-3"></i>Extractores
                        </a>
                        <a href="#" class="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-colors">
                            <i class="fas fa-chart-line mr-3"></i>Analíticas
                        </a>
                        <a href="#" class="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-colors">
                            <i class="fas fa-coins mr-3"></i>Créditos
                        </a>
                        <a href="#" class="flex items-center px-4 py-3 text-gray-700 rounded-xl hover:bg-blue-50 hover:text-blue-600 transition-colors">
                            <i class="fas fa-cog mr-3"></i>Configuración
                        </a>
                    </nav>
                </div>

                <!-- Contenido Principal Admin -->
                <div class="lg:col-span-3 space-y-8">
                    <!-- Dashboard Stats -->
                    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                        <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl p-6 text-white">
                            <div class="flex items-center justify-between">
                                <div>
                                    <p class="text-blue-100">Total Registros</p>
                                    <p class="text-3xl font-bold">2.1M</p>
                                </div>
                                <i class="fas fa-database text-3xl text-blue-200"></i>
                            </div>
                        </div>
                        <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-2xl p-6 text-white">
                            <div class="flex items-center justify-between">
                                <div>
                                    <p class="text-green-100">Usuarios Activos</p>
                                    <p class="text-3xl font-bold">89</p>
                                </div>
                                <i class="fas fa-users text-3xl text-green-200"></i>
                            </div>
                        </div>
                        <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
                            <div class="flex items-center justify-between">
                                <div>
                                    <p class="text-purple-100">Consultas Hoy</p>
                                    <p class="text-3xl font-bold">1,247</p>
                                </div>
                                <i class="fas fa-search text-3xl text-purple-200"></i>
                            </div>
                        </div>
                        <div class="bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl p-6 text-white">
                            <div class="flex items-center justify-between">
                                <div>
                                    <p class="text-orange-100">Ingresos Mes</p>
                                    <p class="text-3xl font-bold">$5.2K</p>
                                </div>
                                <i class="fas fa-dollar-sign text-3xl text-orange-200"></i>
                            </div>
                        </div>
                    </div>

                    <!-- Controles de Extractores -->
                    <div class="bg-white rounded-2xl shadow-lg p-8">
                        <h3 class="text-2xl font-bold text-gray-900 mb-6">Control de Extractores</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="border border-gray-200 rounded-xl p-6">
                                <div class="flex items-center justify-between mb-4">
                                    <h4 class="text-lg font-semibold text-gray-900">Ultra Deep Extractor</h4>
                                    <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Activo</span>
                                </div>
                                <p class="text-gray-600 mb-4">Extracción profunda de Daticos con credenciales CABEZAS/Hola2022</p>
                                <div class="flex space-x-2">
                                    <button onclick="startExtractor('ultra-deep')" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                        <i class="fas fa-play mr-2"></i>Iniciar
                                    </button>
                                    <button onclick="stopExtractor('ultra-deep')" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                                        <i class="fas fa-stop mr-2"></i>Detener
                                    </button>
                                    <button onclick="getExtractorStatus('ultra-deep')" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                                        <i class="fas fa-info mr-2"></i>Estado
                                    </button>
                                </div>
                            </div>
                            
                            <div class="border border-gray-200 rounded-xl p-6">
                                <div class="flex items-center justify-between mb-4">
                                    <h4 class="text-lg font-semibold text-gray-900">Mega Extractor</h4>
                                    <span class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">Pausado</span>
                                </div>
                                <p class="text-gray-600 mb-4">Extracción masiva de TSE, CCSS, Ministerios</p>
                                <div class="flex space-x-2">
                                    <button onclick="startExtractor('mega')" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                        <i class="fas fa-play mr-2"></i>Iniciar
                                    </button>
                                    <button onclick="stopExtractor('mega')" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                                        <i class="fas fa-stop mr-2"></i>Detener
                                    </button>
                                    <button onclick="getExtractorStatus('mega')" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                                        <i class="fas fa-info mr-2"></i>Estado
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Gestión de Usuarios y Créditos -->
                    <div class="bg-white rounded-2xl shadow-lg p-8">
                        <h3 class="text-2xl font-bold text-gray-900 mb-6">Gestión de Usuarios</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full table-auto">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Créditos</th>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    <tr>
                                        <td class="px-4 py-4 whitespace-nowrap">
                                            <div class="flex items-center">
                                                <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">A</div>
                                                <div class="ml-4">
                                                    <div class="text-sm font-medium text-gray-900">Admin</div>
                                                    <div class="text-sm text-gray-500">admin@tudatos.cr</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900">∞</td>
                                        <td class="px-4 py-4 whitespace-nowrap">
                                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                                                Administrador
                                            </span>
                                        </td>
                                        <td class="px-4 py-4 whitespace-nowrap">
                                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                Activo
                                            </span>
                                        </td>
                                        <td class="px-4 py-4 whitespace-nowrap text-sm font-medium">
                                            <button class="text-blue-600 hover:text-blue-900 mr-4">Editar</button>
                                            <button class="text-red-600 hover:text-red-900">Suspender</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="px-4 py-4 whitespace-nowrap">
                                            <div class="flex items-center">
                                                <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">D</div>
                                                <div class="ml-4">
                                                    <div class="text-sm font-medium text-gray-900">Demo User</div>
                                                    <div class="text-sm text-gray-500">demo@tudatos.cr</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                                            <div class="flex items-center">
                                                <span class="mr-2">50</span>
                                                <button onclick="addCredits('demo', 25)" class="text-green-600 hover:text-green-900 text-xs">
                                                    <i class="fas fa-plus"></i>
                                                </button>
                                            </div>
                                        </td>
                                        <td class="px-4 py-4 whitespace-nowrap">
                                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                                Básico
                                            </span>
                                        </td>
                                        <td class="px-4 py-4 whitespace-nowrap">
                                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                Activo
                                            </span>
                                        </td>
                                        <td class="px-4 py-4 whitespace-nowrap text-sm font-medium">
                                            <button class="text-blue-600 hover:text-blue-900 mr-4">Editar</button>
                                            <button class="text-red-600 hover:text-red-900">Suspender</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
        <div class="max-w-7xl mx-auto px-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                    <div class="flex items-center space-x-3 mb-4">
                        <div class="w-8 h-8">
                            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="50" cy="50" r="45" fill="none" stroke="url(#logoGrad)" stroke-width="2"/>
                                <circle cx="50" cy="50" r="30" fill="url(#logoGrad)"/>
                                <circle cx="42" cy="42" r="12" fill="none" stroke="white" stroke-width="2.5"/>
                                <path d="M52 52L62 62" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                            </svg>
                        </div>
                        <span class="text-xl font-bold">TuDatos Pro</span>
                    </div>
                    <p class="text-gray-400">La plataforma más avanzada de datos de Costa Rica</p>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-4">Servicios</h3>
                    <ul class="space-y-2 text-gray-400">
                        <li><a href="#" class="hover:text-white transition-colors">Búsqueda de Personas</a></li>
                        <li><a href="#" class="hover:text-white transition-colors">Datos Empresariales</a></li>
                        <li><a href="#" class="hover:text-white transition-colors">Verificación de Identidad</a></li>
                        <li><a href="#" class="hover:text-white transition-colors">API Integración</a></li>
                    </ul>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-4">Soporte</h3>
                    <ul class="space-y-2 text-gray-400">
                        <li><a href="#" class="hover:text-white transition-colors">Centro de Ayuda</a></li>
                        <li><a href="#" class="hover:text-white transition-colors">Documentación API</a></li>
                        <li><a href="#" class="hover:text-white transition-colors">Contacto</a></li>
                        <li><a href="#" class="hover:text-white transition-colors">Estado del Sistema</a></li>
                    </ul>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-4">Contacto</h3>
                    <div class="space-y-2 text-gray-400">
                        <p><i class="fas fa-envelope mr-2"></i>info@tudatos.cr</p>
                        <p><i class="fas fa-phone mr-2"></i>+506 2234-5678</p>
                        <p><i class="fas fa-map-marker-alt mr-2"></i>San José, Costa Rica</p>
                    </div>
                </div>
            </div>
            <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
                <p>&copy; 2024 TuDatos Pro. Todos los derechos reservados. Sistema desarrollado en Costa Rica.</p>
            </div>
        </div>
    </footer>

    <script>
        // Funciones JavaScript avanzadas
        function getPlaceholder(searchType) {
            const placeholders = {
                'general': 'Buscar por nombre, cédula, teléfono, email...',
                'cedula': 'Ej: 1-1234-5678',
                'empresa': 'Nombre o cédula jurídica de la empresa',
                'profesional': 'Nombre del profesional o especialidad',
                'vehiculo': 'Número de placa',
                'propiedad': 'Dirección o finca'
            };
            return placeholders[searchType] || 'Buscar...';
        }

        function showLogin() {
            document.getElementById('loginModal').classList.remove('hidden');
        }

        function hideLogin() {
            document.getElementById('loginModal').classList.add('hidden');
        }

        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const result = await response.json();
                if (result.success) {
                    hideLogin();
                    showNotification('Login exitoso', 'success');
                    localStorage.setItem('token', result.token);
                    updateUIAfterLogin(result.user);
                } else {
                    showNotification('Credenciales incorrectas', 'error');
                }
            } catch (error) {
                showNotification('Error de conexión', 'error');
            }
        });

        async function performSearch() {
            const query = document.getElementById('searchInput').value;
            if (!query.trim()) {
                showNotification('Por favor ingrese un término de búsqueda', 'warning');
                return;
            }

            showLoading(true);
            
            try {
                const response = await fetch(`/api/search/advanced?q=${encodeURIComponent(query)}`);
                const results = await response.json();
                
                displaySearchResults(results);
                document.getElementById('searchResults').style.display = 'block';
                
            } catch (error) {
                showNotification('Error realizando búsqueda', 'error');
            } finally {
                showLoading(false);
            }
        }

        function displaySearchResults(results) {
            const container = document.getElementById('resultsContainer');
            if (!results.data || results.data.length === 0) {
                container.innerHTML = '<div class="text-center py-8 text-gray-500">No se encontraron resultados</div>';
                return;
            }

            let html = '';
            results.data.forEach(item => {
                html += `
                    <div class="bg-gray-50 rounded-xl p-6 mb-4 hover:shadow-md transition-shadow">
                        <div class="flex justify-between items-start mb-4">
                            <h4 class="text-lg font-semibold text-gray-900">${item.nombre || item.razon_social || 'N/A'}</h4>
                            <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">${item.type || 'Persona'}</span>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                            <div><strong>Cédula:</strong> ${item.cedula || item.cedula_juridica || 'N/A'}</div>
                            <div><strong>Teléfono:</strong> ${item.telefono || 'N/A'}</div>
                            <div><strong>Email:</strong> ${item.email || 'N/A'}</div>
                            <div><strong>Provincia:</strong> ${item.provincia || 'N/A'}</div>
                            <div><strong>Ocupación:</strong> ${item.ocupacion || item.sector_negocio || 'N/A'}</div>
                            <div><strong>Estado:</strong> <span class="text-green-600">Verificado</span></div>
                        </div>
                        <div class="mt-4 flex space-x-2">
                            <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
                                <i class="fas fa-eye mr-2"></i>Ver Detalles
                            </button>
                            <button class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm">
                                <i class="fas fa-download mr-2"></i>Descargar
                            </button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        async function startExtractor(type) {
            try {
                const response = await fetch(`/api/admin/extractor/${type}/start`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                const result = await response.json();
                showNotification(`Extractor ${type} iniciado`, 'success');
            } catch (error) {
                showNotification('Error iniciando extractor', 'error');
            }
        }

        async function stopExtractor(type) {
            try {
                const response = await fetch(`/api/admin/extractor/${type}/stop`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                const result = await response.json();
                showNotification(`Extractor ${type} detenido`, 'warning');
            } catch (error) {
                showNotification('Error deteniendo extractor', 'error');
            }
        }

        async function addCredits(userId, amount) {
            try {
                const response = await fetch(`/api/admin/users/${userId}/credits`, {
                    method: 'POST',
                    headers: { 
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ amount })
                });
                const result = await response.json();
                showNotification(`${amount} créditos agregados a ${userId}`, 'success');
                location.reload(); // Recargar para actualizar la tabla
            } catch (error) {
                showNotification('Error agregando créditos', 'error');
            }
        }

        function showNotification(message, type = 'info') {
            const colors = {
                success: 'bg-green-500',
                error: 'bg-red-500',
                warning: 'bg-yellow-500',
                info: 'bg-blue-500'
            };
            
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }

        function showLoading(show) {
            const button = document.querySelector('button[onclick="performSearch()"]');
            if (show) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Buscando...';
                button.disabled = true;
            } else {
                button.innerHTML = '<i class="fas fa-search mr-2"></i>Buscar';
                button.disabled = false;
            }
        }

        // Inicialización
        document.addEventListener('DOMContentLoaded', function() {
            // Verificar si hay token guardado
            const token = localStorage.getItem('token');
            if (token) {
                // Actualizar UI para usuario logueado
            }

            // Búsqueda con Enter
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });
        });
    </script>
</body>
</html>
    """)

@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Sistema de autenticación mejorado"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if username in users_db and users_db[username]["password"] == password_hash:
        user = users_db[username]
        token = f"{username}_token"
        
        # Actualizar último login
        users_db[username]["last_login"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user["id"],
                "role": user["role"],
                "credits": user["credits"]
            }
        }
    
    return {"success": False, "message": "Credenciales incorrectas"}

@app.get("/api/search/advanced")
async def advanced_search(q: str, type: Optional[str] = None, provincia: Optional[str] = None):
    """Búsqueda avanzada con múltiples filtros"""
    results = []
    query_lower = q.lower()
    
    # Buscar en personas físicas
    for persona in advanced_database["personas_fisicas"]:
        if (query_lower in persona.get("nombre", "").lower() or 
            query_lower in persona.get("cedula", "").lower() or
            query_lower in persona.get("telefono", "").lower() or
            query_lower in persona.get("email", "").lower()):
            
            if not provincia or persona.get("provincia", "").lower() == provincia.lower():
                persona_copy = persona.copy()
                persona_copy["type"] = "Persona Física"
                results.append(persona_copy)
    
    # Buscar en personas jurídicas
    for empresa in advanced_database["personas_juridicas"]:
        if (query_lower in empresa.get("razon_social", "").lower() or 
            query_lower in empresa.get("cedula_juridica", "").lower() or
            query_lower in empresa.get("telefono", "").lower()):
            
            if not provincia or empresa.get("provincia", "").lower() == provincia.lower():
                empresa_copy = empresa.copy()
                empresa_copy["type"] = "Empresa"
                results.append(empresa_copy)
    
    # Buscar en profesionales
    for prof in advanced_database["profesionales"]:
        if (query_lower in prof.get("nombre_completo", "").lower() or 
            query_lower in prof.get("especialidad", "").lower()):
            
            prof_copy = prof.copy()
            prof_copy["type"] = "Profesional"
            results.append(prof_copy)
    
    # Simular deducción de créditos
    return {
        "success": True,
        "data": results[:20],  # Limitar resultados
        "total": len(results),
        "credits_used": min(len(results), 1),
        "query": q,
        "filters_applied": {"provincia": provincia, "type": type}
    }

@app.get("/api/stats/advanced")
async def get_advanced_stats():
    """Estadísticas avanzadas del sistema"""
    return {
        "sistema": system_stats,
        "extractores": {
            "ultra_deep": {
                "estado": "activo",
                "ultimo_run": datetime.utcnow().isoformat(),
                "registros_extraidos_hoy": 1247,
                "tiempo_promedio": "2.3 min"
            },
            "mega_extractor": {
                "estado": "pausado", 
                "ultimo_run": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "registros_extraidos_hoy": 856,
                "tiempo_promedio": "5.7 min"
            }
        },
        "usuarios": {
            "total": len(users_db),
            "activos_hoy": 23,
            "creditos_consumidos_hoy": 2341,
            "ingresos_dia": 278.45
        },
        "rendimiento": {
            "tiempo_respuesta_promedio": "0.8s",
            "disponibilidad": "99.9%",
            "consultas_por_segundo": 45,
            "precision_datos": "98.7%"
        }
    }

@app.post("/api/admin/extractor/{extractor_type}/start")
async def start_extractor_endpoint(extractor_type: str, current_user: str = Depends(verify_user)):
    """Iniciar extractor específico"""
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Simulación de inicio de extractor
    return {
        "success": True,
        "message": f"Extractor {extractor_type} iniciado correctamente",
        "extractor": extractor_type,
        "status": "running",
        "estimated_time": "30 minutos",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/admin/extractor/{extractor_type}/stop")
async def stop_extractor_endpoint(extractor_type: str, current_user: str = Depends(verify_user)):
    """Detener extractor específico"""
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    return {
        "success": True,
        "message": f"Extractor {extractor_type} detenido correctamente",
        "extractor": extractor_type,
        "status": "stopped",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/admin/users/{user_id}/credits")
async def add_user_credits(user_id: str, amount: int = Form(...), current_user: str = Depends(verify_user)):
    """Agregar créditos a usuario"""
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    if user_id in users_db:
        users_db[user_id]["credits"] += amount
        return {
            "success": True,
            "message": f"{amount} créditos agregados a {user_id}",
            "new_balance": users_db[user_id]["credits"]
        }
    
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.get("/api/admin/users")
async def get_all_users(current_user: str = Depends(verify_user)):
    """Obtener todos los usuarios"""
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    return {
        "success": True,
        "users": [
            {
                "id": user_id,
                "role": user_data["role"],
                "credits": user_data["credits"],
                "created_at": user_data["created_at"],
                "last_login": user_data["last_login"]
            }
            for user_id, user_data in users_db.items()
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "database": "connected",
        "services": {
            "search": "operational",
            "extractors": "operational", 
            "auth": "operational"
        }
    }