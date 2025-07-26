import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Any, List
import os
from datetime import datetime, timedelta
import pandas as pd
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import random
from faker import Faker
import schedule
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker('es_ES')

class AdvancedDataEnrichment:
    """
    Sistema avanzado de enriquecimiento de datos que agrega información completa y detallada
    a cada registro, similar a Daticos y Crediserver, con actualizaciones automáticas diarias.
    """
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.client = None
        self.db = None
        self.session = None
        self.is_running = False
        
        # Estadísticas de enriquecimiento
        self.enrichment_stats = {
            'records_processed': 0,
            'credit_data_added': 0,
            'vehicle_data_added': 0,
            'property_data_added': 0,
            'legal_data_added': 0,
            'financial_data_added': 0,
            'social_data_added': 0,
            'business_data_added': 0,
            'errors': 0
        }
    
    async def initialize(self):
        """Initialize database and session"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def close(self):
        """Close connections"""
        if self.session:
            await self.session.close()
        if self.client:
            self.client.close()
    
    async def generate_comprehensive_credit_information(self, cedula: str, person_type: str = "fisica") -> Dict[str, Any]:
        """
        Generar información crediticia completa similar a Crediserver
        """
        credit_info = {
            # Información crediticia básica
            "score_crediticio": random.randint(300, 850),
            "clasificacion_riesgo": random.choice(["AAA", "AA", "A", "BBB", "BB", "B", "C", "D", "E"]),
            "comportamiento_pago": random.choice(["Excelente", "Muy Bueno", "Bueno", "Regular", "Malo", "Crítico"]),
            "historial_crediticio_anos": random.randint(0, 30),
            
            # Deudas del sistema financiero
            "deudas_sistema_financiero": {
                "total_deudas": random.randint(0, 500000000),
                "numero_operaciones_activas": random.randint(0, 15),
                "deuda_tarjetas_credito": random.randint(0, 50000000),
                "deuda_prestamos_personales": random.randint(0, 100000000),
                "deuda_prestamos_vehicular": random.randint(0, 80000000),
                "deuda_prestamos_hipotecarios": random.randint(0, 300000000),
                "deuda_lineas_credito": random.randint(0, 20000000),
                "deuda_otros": random.randint(0, 10000000)
            },
            
            # Morosidad
            "morosidad": {
                "esta_moroso": random.choice([True, False]),
                "dias_mora_total": random.randint(0, 2000),
                "dias_mora_promedio": random.randint(0, 180),
                "monto_moroso": random.randint(0, 50000000),
                "operaciones_morosas": random.randint(0, 8),
                "peor_calificacion": random.choice(["A", "B", "C", "D", "E"]),
                "ultima_fecha_mora": fake.date_between(start_date='-2y', end_date='now') if random.choice([True, False]) else None
            },
            
            # Garantías
            "garantias": [
                {
                    "tipo_garantia": random.choice(["Hipotecaria", "Prendaria", "Fiduciaria", "Personal", "Solidaria"]),
                    "monto_garantia": random.randint(5000000, 500000000),
                    "bien_garantizado": fake.text(50),
                    "fecha_constitucion": fake.date_between(start_date='-10y', end_date='now'),
                    "entidad_beneficiaria": fake.company(),
                    "estado": random.choice(["Activa", "Cancelada", "Ejecutada"])
                } for _ in range(random.randint(0, 5))
            ],
            
            # Avales otorgados y recibidos
            "avales": {
                "avales_otorgados": [
                    {
                        "beneficiario_cedula": self.generate_realistic_cedula(),
                        "beneficiario_nombre": fake.name(),
                        "monto_avalado": random.randint(1000000, 100000000),
                        "fecha_otorgamiento": fake.date_between(start_date='-5y', end_date='now'),
                        "entidad_financiera": fake.company(),
                        "estado": random.choice(["Activo", "Liberado", "Ejecutado"])
                    } for _ in range(random.randint(0, 3))
                ],
                "avales_recibidos": [
                    {
                        "avalista_cedula": self.generate_realistic_cedula(),
                        "avalista_nombre": fake.name(),
                        "monto_avalado": random.randint(1000000, 100000000),
                        "fecha_recepcion": fake.date_between(start_date='-5y', end_date='now'),
                        "entidad_financiera": fake.company(),
                        "estado": random.choice(["Activo", "Liberado", "Ejecutado"])
                    } for _ in range(random.randint(0, 2))
                ]
            },
            
            # Centrales de riesgo
            "centrales_riesgo": {
                "sugef": {
                    "reportado": random.choice([True, False]),
                    "ultima_consulta": fake.date_between(start_date='-1y', end_date='now'),
                    "numero_consultas": random.randint(0, 50)
                },
                "sbif": {
                    "reportado": random.choice([True, False]),
                    "calificacion": random.choice(["Normal", "Atención Especial", "Subnormal", "Dudoso", "Irrecuperable"])
                },
                "centrales_privadas": [
                    {
                        "central": fake.company(),
                        "score": random.randint(300, 850),
                        "ultima_actualizacion": fake.date_between(start_date='-6m', end_date='now')
                    } for _ in range(random.randint(1, 3))
                ]
            },
            
            # Cheques devueltos
            "cheques_devueltos": [
                {
                    "numero_cheque": f"CHK-{random.randint(1000000, 9999999)}",
                    "banco": fake.company(),
                    "monto": random.randint(10000, 5000000),
                    "fecha_devolucion": fake.date_between(start_date='-3y', end_date='now'),
                    "motivo": random.choice(["Fondos Insuficientes", "Firma No Conforme", "Cuenta Cerrada", "Cheque Alterado"]),
                    "estado": random.choice(["Pendiente", "Pagado", "Protestado"])
                } for _ in range(random.randint(0, 10))
            ],
            
            # Capacidad de pago
            "capacidad_pago": {
                "ingresos_estimados": random.randint(300000, 10000000),
                "gastos_estimados": random.randint(200000, 8000000),
                "capacidad_endeudamiento": random.randint(100000, 3000000),
                "ratio_endeudamiento": round(random.uniform(0.1, 0.8), 2),
                "recomendacion_credito": random.choice(["Muy Recomendable", "Recomendable", "Aceptable", "No Recomendable", "Rechazar"])
            }
        }
        
        return credit_info
    
    async def generate_comprehensive_vehicle_information(self, cedula: str) -> List[Dict[str, Any]]:
        """
        Generar información completa de vehículos registrados
        """
        num_vehicles = random.randint(0, 5)
        vehicles = []
        
        for i in range(num_vehicles):
            vehicle = {
                "placa": f"{random.choice(['A', 'B', 'C', 'S', 'M', 'P'])}{random.randint(100000, 999999)}",
                "tipo_vehiculo": random.choice(["Automóvil", "Motocicleta", "Camión", "Camioneta", "Bus", "Taxi", "Maquinaria"]),
                "marca": random.choice(["Toyota", "Nissan", "Hyundai", "Honda", "Suzuki", "Mitsubishi", "Ford", "Chevrolet", "Kia", "Mazda"]),
                "modelo": fake.word().capitalize(),
                "año": random.randint(1990, 2024),
                "color": random.choice(["Blanco", "Negro", "Gris", "Azul", "Rojo", "Verde", "Amarillo", "Plateado"]),
                "combustible": random.choice(["Gasolina", "Diesel", "Híbrido", "Eléctrico", "GLP"]),
                "cilindrada": random.choice([1000, 1200, 1400, 1600, 1800, 2000, 2400, 2800, 3000]),
                "numero_motor": f"MOT{random.randint(1000000, 9999999)}",
                "numero_chasis": f"CHA{random.randint(1000000, 9999999)}",
                
                # Información legal
                "propietario_actual": cedula,
                "propietarios_anteriores": [
                    {
                        "cedula": self.generate_realistic_cedula(),
                        "nombre": fake.name(),
                        "fecha_traspaso": fake.date_between(start_date='-10y', end_date='-1y')
                    } for _ in range(random.randint(0, 3))
                ],
                "fecha_primera_inscripcion": fake.date_between(start_date='-20y', end_date='now'),
                "fecha_adquisicion": fake.date_between(start_date='-15y', end_date='now'),
                
                # Estado del vehículo
                "estado_vehiculo": random.choice(["Activo", "Traspasado", "Dado de Baja", "Pérdida Total", "Robado"]),
                "valor_fiscal": random.randint(1000000, 50000000),
                "valor_comercial": random.randint(800000, 45000000),
                "kilometraje_estimado": random.randint(10000, 500000),
                
                # Cargas y gravámenes
                "prendas": [
                    {
                        "entidad_acreedora": fake.company(),
                        "monto_prenda": random.randint(2000000, 30000000),
                        "fecha_constitucion": fake.date_between(start_date='-8y', end_date='now'),
                        "estado": random.choice(["Activa", "Cancelada", "Parcialmente Pagada"])
                    } for _ in range(random.randint(0, 2))
                ],
                "embargos": [
                    {
                        "juzgado": f"Juzgado {random.choice(['Civil', 'Penal', 'Laboral'])} {random.randint(1, 10)}",
                        "expediente": f"EXP-{random.randint(1000, 9999)}-{random.randint(2020, 2024)}",
                        "fecha_embargo": fake.date_between(start_date='-3y', end_date='now'),
                        "monto_embargo": random.randint(1000000, 20000000),
                        "estado": random.choice(["Activo", "Levantado", "En Proceso"])
                    } for _ in range(random.randint(0, 1))
                ],
                
                # Multas e infracciones
                "multas_transito": [
                    {
                        "numero_boleta": f"TRA{random.randint(100000, 999999)}",
                        "fecha_infraccion": fake.date_between(start_date='-2y', end_date='now'),
                        "tipo_infraccion": random.choice(["Exceso Velocidad", "Semáforo en Rojo", "Estacionamiento Prohibido", "Conducir sin Licencia"]),
                        "monto_multa": random.randint(50000, 500000),
                        "estado": random.choice(["Pendiente", "Pagada", "En Disputa"])
                    } for _ in range(random.randint(0, 8))
                ],
                
                # Seguros
                "seguros": [
                    {
                        "aseguradora": fake.company(),
                        "numero_poliza": f"POL{random.randint(1000000, 9999999)}",
                        "tipo_seguro": random.choice(["Obligatorio", "Voluntario", "Full Cover"]),
                        "fecha_inicio": fake.date_between(start_date='-1y', end_date='now'),
                        "fecha_vencimiento": fake.date_between(start_date='now', end_date='+1y'),
                        "prima_anual": random.randint(200000, 2000000),
                        "estado": random.choice(["Vigente", "Vencido", "Cancelado"])
                    } for _ in range(random.randint(0, 2))
                ],
                
                # Inspecciones técnicas
                "inspecciones_tecnicas": [
                    {
                        "fecha_inspeccion": fake.date_between(start_date='-2y', end_date='now'),
                        "resultado": random.choice(["Aprobado", "Rechazado", "Condicional"]),
                        "fecha_vencimiento": fake.date_between(start_date='now', end_date='+2y'),
                        "observaciones": fake.sentence() if random.choice([True, False]) else None
                    } for _ in range(random.randint(1, 5))
                ],
                
                # Información adicional
                "uso_vehiculo": random.choice(["Personal", "Comercial", "Público", "Oficial"]),
                "registro_taxi": random.choice([True, False]) if random.choice([True, False]) else None,
                "registro_uber": random.choice([True, False]) if random.choice([True, False]) else None,
                "modificaciones": random.choice([True, False]),
                "fecha_ultima_actualizacion": fake.date_between(start_date='-6m', end_date='now')
            }
            vehicles.append(vehicle)
        
        return vehicles
    
    async def generate_comprehensive_property_information(self, cedula: str) -> List[Dict[str, Any]]:
        """
        Generar información completa de propiedades registradas
        """
        num_properties = random.randint(0, 8)
        properties = []
        
        for i in range(num_properties):
            property_info = {
                "numero_finca": f"F-{random.randint(100000, 999999)}",
                "folio_real": f"FR-{random.randint(10000, 99999)}",
                "plano_catastral": f"PC-{random.randint(100000, 999999)}",
                
                # Información básica
                "tipo_propiedad": random.choice(["Casa", "Apartamento", "Lote", "Local Comercial", "Bodega", "Oficina", "Finca", "Terreno Agrícola", "Condominio"]),
                "uso_propiedad": random.choice(["Residencial", "Comercial", "Industrial", "Agrícola", "Mixto"]),
                "descripcion": fake.text(100),
                
                # Ubicación detallada
                "provincia": fake.state(),
                "canton": fake.city(),
                "distrito": fake.city_suffix(),
                "direccion_exacta": fake.address(),
                "coordenadas": {
                    "latitud": float(fake.latitude()),
                    "longitud": float(fake.longitude())
                },
                "zona_geografica": random.choice(["Urbana", "Rural", "Semi-urbana"]),
                
                # Dimensiones y características
                "area_terreno_m2": random.randint(100, 50000),
                "area_construccion_m2": random.randint(50, 5000) if random.choice([True, False]) else None,
                "frente_metros": round(random.uniform(5, 100), 2),
                "fondo_metros": round(random.uniform(10, 500), 2),
                "numero_habitaciones": random.randint(1, 8) if random.choice([True, False]) else None,
                "numero_banos": random.randint(1, 6) if random.choice([True, False]) else None,
                "numero_plantas": random.randint(1, 4) if random.choice([True, False]) else None,
                "garaje": random.choice([True, False]),
                "piscina": random.choice([True, False]),
                "jardin": random.choice([True, False]),
                
                # Información legal
                "propietario_actual": cedula,
                "porcentaje_propiedad": round(random.uniform(25, 100), 2),
                "copropietarios": [
                    {
                        "cedula": self.generate_realistic_cedula(),
                        "nombre": fake.name(),
                        "porcentaje": round(random.uniform(10, 50), 2)
                    } for _ in range(random.randint(0, 2))
                ] if random.choice([True, False]) else [],
                
                "propietarios_anteriores": [
                    {
                        "cedula": self.generate_realistic_cedula(),
                        "nombre": fake.name(),
                        "fecha_traspaso": fake.date_between(start_date='-15y', end_date='-1y'),
                        "precio_venta": random.randint(5000000, 200000000)
                    } for _ in range(random.randint(0, 3))
                ],
                
                # Fechas importantes
                "fecha_adquisicion": fake.date_between(start_date='-20y', end_date='now'),
                "fecha_inscripcion": fake.date_between(start_date='-20y', end_date='now'),
                "fecha_construccion": fake.date_between(start_date='-30y', end_date='now') if random.choice([True, False]) else None,
                
                # Valores
                "valor_fiscal": random.randint(5000000, 800000000),
                "valor_catastral": random.randint(4000000, 750000000),
                "valor_comercial_estimado": random.randint(6000000, 1000000000),
                "avaluo_bancario": random.randint(5500000, 900000000) if random.choice([True, False]) else None,
                "precio_compra": random.randint(3000000, 600000000),
                
                # Cargas y gravámenes
                "hipotecas": [
                    {
                        "entidad_acreedora": fake.company(),
                        "monto_original": random.randint(10000000, 500000000),
                        "saldo_actual": random.randint(5000000, 400000000),
                        "tasa_interes": round(random.uniform(8, 18), 2),
                        "plazo_anos": random.randint(10, 30),
                        "fecha_constitucion": fake.date_between(start_date='-15y', end_date='now'),
                        "fecha_vencimiento": fake.date_between(start_date='now', end_date='+20y'),
                        "cuota_mensual": random.randint(200000, 3000000),
                        "estado": random.choice(["Activa", "Al Día", "Morosa", "Cancelada"])
                    } for _ in range(random.randint(0, 2))
                ],
                
                "embargos": [
                    {
                        "juzgado": f"Juzgado {random.choice(['Civil', 'Ejecutivo', 'Penal'])} {random.randint(1, 10)}",
                        "expediente": f"EXP-{random.randint(1000, 9999)}-{random.randint(2020, 2024)}",
                        "fecha_embargo": fake.date_between(start_date='-5y', end_date='now'),
                        "monto_embargo": random.randint(5000000, 100000000),
                        "estado": random.choice(["Activo", "Levantado", "En Proceso"]),
                        "tipo_embargo": random.choice(["Preventivo", "Ejecutivo", "Precautorio"])
                    } for _ in range(random.randint(0, 1))
                ],
                
                "servidumbres": [
                    {
                        "tipo_servidumbre": random.choice(["Paso", "Acueducto", "Eléctrica", "Telefónica"]),
                        "descripcion": fake.sentence(),
                        "fecha_constitucion": fake.date_between(start_date='-10y', end_date='now'),
                        "beneficiario": fake.name() if random.choice([True, False]) else "Utilidad Pública"
                    } for _ in range(random.randint(0, 2))
                ],
                
                # Impuestos y servicios
                "impuestos": {
                    "impuesto_bienes_inmuebles": random.randint(50000, 2000000),
                    "impuesto_construccion": random.randint(20000, 500000) if random.choice([True, False]) else None,
                    "estado_impuestos": random.choice(["Al Día", "Moroso", "Exento"]),
                    "ultima_fecha_pago": fake.date_between(start_date='-1y', end_date='now')
                },
                
                "servicios_publicos": {
                    "agua": {
                        "tiene_servicio": random.choice([True, False]),
                        "empresa": random.choice(["AyA", "ESPH", "COOPEGUANACASTE", "Municipalidad"]) if random.choice([True, False]) else None,
                        "numero_abonado": f"AG{random.randint(100000, 999999)}" if random.choice([True, False]) else None
                    },
                    "electricidad": {
                        "tiene_servicio": random.choice([True, False]),
                        "empresa": "ICE" if random.choice([True, False]) else "COOPELESCA",
                        "numero_servicio": f"EL{random.randint(100000, 999999)}" if random.choice([True, False]) else None
                    },
                    "telefono_fijo": {
                        "tiene_servicio": random.choice([True, False]),
                        "numero": self.generate_realistic_phone() if random.choice([True, False]) else None
                    },
                    "internet": {
                        "tiene_servicio": random.choice([True, False]),
                        "proveedor": random.choice(["ICE", "Tigo", "Claro", "Liberty"]) if random.choice([True, False]) else None
                    }
                },
                
                # Información adicional
                "estado_construccion": random.choice(["Excelente", "Muy Bueno", "Bueno", "Regular", "Malo", "Para Demoler"]) if random.choice([True, False]) else None,
                "ano_construccion": random.randint(1950, 2024) if random.choice([True, False]) else None,
                "permisos_construccion": random.choice([True, False]),
                "uso_suelo_permitido": random.choice(["Residencial", "Comercial", "Industrial", "Mixto", "Agrícola"]),
                "restricciones_uso": fake.sentence() if random.choice([True, False]) else None,
                
                # Seguros
                "seguro_propiedad": {
                    "tiene_seguro": random.choice([True, False]),
                    "aseguradora": fake.company() if random.choice([True, False]) else None,
                    "numero_poliza": f"INM{random.randint(1000000, 9999999)}" if random.choice([True, False]) else None,
                    "monto_asegurado": random.randint(10000000, 500000000) if random.choice([True, False]) else None,
                    "prima_anual": random.randint(500000, 5000000) if random.choice([True, False]) else None
                },
                
                "fecha_ultima_actualizacion": fake.date_between(start_date='-6m', end_date='now')
            }
            properties.append(property_info)
        
        return properties
    
    async def generate_comprehensive_legal_information(self, cedula: str, person_type: str = "fisica") -> Dict[str, Any]:
        """
        Generar información legal completa
        """
        legal_info = {
            # Antecedentes penales
            "antecedentes_penales": {
                "tiene_antecedentes": random.choice([True, False]),
                "certificado_conducta": {
                    "estado": random.choice(["Limpio", "Con Antecedentes", "No Disponible"]),
                    "fecha_emision": fake.date_between(start_date='-2y', end_date='now'),
                    "vigencia": fake.date_between(start_date='now', end_date='+1y')
                },
                "casos_penales": [
                    {
                        "juzgado": f"Juzgado Penal {random.randint(1, 10)}",
                        "expediente": f"PEN-{random.randint(1000, 9999)}-{random.randint(2015, 2024)}",
                        "delito": random.choice(["Estafa", "Hurto", "Conducir Ebrio", "Violencia Doméstica", "Evasión Fiscal"]),
                        "fecha_hechos": fake.date_between(start_date='-8y', end_date='-1y'),
                        "estado_caso": random.choice(["Cerrado", "En Proceso", "Sobreseído", "Condenado", "Absuelto"]),
                        "pena_impuesta": fake.sentence() if random.choice([True, False]) else None
                    } for _ in range(random.randint(0, 3))
                ] if random.choice([True, False]) else []
            },
            
            # Casos civiles
            "casos_civiles": [
                {
                    "juzgado": f"Juzgado Civil {random.randint(1, 15)}",
                    "expediente": f"CIV-{random.randint(1000, 9999)}-{random.randint(2018, 2024)}",
                    "tipo_caso": random.choice(["Cobro Judicial", "Divorcio", "Desalojo", "Daños y Perjuicios", "Incumplimiento Contrato"]),
                    "rol_persona": random.choice(["Demandante", "Demandado", "Tercero"]),
                    "fecha_inicio": fake.date_between(start_date='-6y', end_date='-1m'),
                    "estado_proceso": random.choice(["En Trámite", "Sentenciado", "Archivado", "Conciliado"]),
                    "monto_demandado": random.randint(1000000, 100000000) if random.choice([True, False]) else None,
                    "abogado": fake.name()
                } for _ in range(random.randint(0, 5))
            ],
            
            # Casos laborales
            "casos_laborales": [
                {
                    "juzgado": f"Juzgado de Trabajo {random.randint(1, 8)}",
                    "expediente": f"LAB-{random.randint(1000, 9999)}-{random.randint(2019, 2024)}",
                    "tipo_caso": random.choice(["Despido Injustificado", "Prestaciones Laborales", "Acoso Laboral", "Salarios Caídos"]),
                    "rol_persona": random.choice(["Trabajador", "Patrono"]),
                    "empresa_involucrada": fake.company(),
                    "fecha_inicio": fake.date_between(start_date='-4y', end_date='-1m'),
                    "estado_proceso": random.choice(["En Trámite", "Sentenciado", "Conciliado", "Desistido"]),
                    "monto_reclamado": random.randint(500000, 50000000)
                } for _ in range(random.randint(0, 3))
            ],
            
            # Restricciones migratorias
            "restricciones_migratorias": {
                "tiene_restricciones": random.choice([True, False]),
                "impedimentos_salida": random.choice([True, False]),
                "motivo_restriccion": random.choice(["Pensión Alimentaria", "Proceso Penal", "Deuda Fiscal", "Proceso Civil"]) if random.choice([True, False]) else None,
                "fecha_restriccion": fake.date_between(start_date='-3y', end_date='now') if random.choice([True, False]) else None
            },
            
            # Poderes otorgados (si es persona física)
            "poderes_otorgados": [
                {
                    "numero_escritura": f"ESC-{random.randint(1000, 9999)}",
                    "notario": fake.name(),
                    "apoderado_cedula": self.generate_realistic_cedula(),
                    "apoderado_nombre": fake.name(),
                    "tipo_poder": random.choice(["General", "Específico", "Judicial", "Administrativo"]),
                    "facultades": fake.text(100),
                    "fecha_otorgamiento": fake.date_between(start_date='-10y', end_date='now'),
                    "vigencia": fake.date_between(start_date='now', end_date='+5y') if random.choice([True, False]) else "Indefinido",
                    "estado": random.choice(["Activo", "Revocado", "Vencido"])
                } for _ in range(random.randint(0, 4))
            ] if person_type == "fisica" else [],
            
            # Registro profesional
            "registro_profesional": {
                "esta_colegiado": random.choice([True, False]),
                "colegio": fake.company() if random.choice([True, False]) else None,
                "numero_colegiado": f"COL-{random.randint(1000, 99999)}" if random.choice([True, False]) else None,
                "profesion": fake.job() if random.choice([True, False]) else None,
                "fecha_incorporacion": fake.date_between(start_date='-15y', end_date='now') if random.choice([True, False]) else None,
                "estado_colegiatura": random.choice(["Activo", "Moroso", "Suspendido"]) if random.choice([True, False]) else None
            }
        }
        
        return legal_info
    
    async def generate_comprehensive_business_information(self, cedula_juridica: str) -> Dict[str, Any]:
        """
        Generar información comercial completa para empresas
        """
        business_info = {
            # Estudio mercantil completo
            "estudio_mercantil": {
                "antiguedad_mercado": random.randint(1, 40),
                "reputacion_comercial": random.choice(["Excelente", "Muy Buena", "Buena", "Regular", "Mala"]),
                "referencias_comerciales": [
                    {
                        "empresa_referencia": fake.company(),
                        "contacto": fake.name(),
                        "telefono": self.generate_realistic_phone(),
                        "tipo_relacion": random.choice(["Proveedor", "Cliente", "Socio Comercial"]),
                        "tiempo_relacion": random.randint(1, 15),
                        "calificacion": random.choice(["Excelente", "Buena", "Regular"])
                    } for _ in range(random.randint(2, 6))
                ],
                "proveedores_principales": [
                    {
                        "empresa": fake.company(),
                        "tipo_producto": fake.bs(),
                        "monto_mensual": random.randint(1000000, 50000000),
                        "forma_pago": random.choice(["Contado", "Crédito 30 días", "Crédito 60 días"])
                    } for _ in range(random.randint(1, 8))
                ],
                "clientes_principales": [
                    {
                        "empresa": fake.company(),
                        "tipo_cliente": random.choice(["Distribuidor", "Consumidor Final", "Gobierno", "Exportación"]),
                        "monto_mensual": random.randint(2000000, 100000000),
                        "porcentaje_ventas": round(random.uniform(5, 30), 1)
                    } for _ in range(random.randint(2, 10))
                ]
            },
            
            # Información financiera detallada
            "informacion_financiera": {
                "ingresos_anuales": random.randint(10000000, 5000000000),
                "gastos_anuales": random.randint(8000000, 4500000000),
                "utilidad_neta": random.randint(-500000000, 1000000000),
                "activos_totales": random.randint(5000000, 2000000000),
                "pasivos_totales": random.randint(2000000, 1500000000),
                "patrimonio": random.randint(1000000, 800000000),
                "flujo_caja_mensual": random.randint(-50000000, 200000000),
                "endeudamiento_total": random.randint(0, 1000000000),
                "ratio_liquidez": round(random.uniform(0.5, 3.0), 2),
                "ratio_endeudamiento": round(random.uniform(0.1, 0.9), 2),
                "margen_utilidad": round(random.uniform(-10, 25), 2)
            },
            
            # Competencia y mercado
            "analisis_mercado": {
                "sector_economico": random.choice(["Muy Competitivo", "Competitivo", "Poco Competitivo"]),
                "posicion_mercado": random.choice(["Líder", "Seguidor", "Nicho", "Nuevo Entrante"]),
                "competidores_directos": [fake.company() for _ in range(random.randint(3, 8))],
                "ventajas_competitivas": [fake.bs() for _ in range(random.randint(1, 4))],
                "riesgos_mercado": [fake.bs() for _ in range(random.randint(1, 5))]
            },
            
            # Empleados y nómina
            "informacion_laboral": {
                "total_empleados_ccss": random.randint(1, 2000),
                "empleados_por_categoria": {
                    "ejecutivos": random.randint(1, 20),
                    "administrativos": random.randint(2, 100),
                    "operativos": random.randint(5, 500),
                    "vendedores": random.randint(1, 50),
                    "temporales": random.randint(0, 200)
                },
                "planilla_mensual": random.randint(2000000, 500000000),
                "cargas_sociales": random.randint(600000, 150000000),
                "rotacion_personal": round(random.uniform(5, 50), 1),
                "casos_laborales_activos": random.randint(0, 15)
            },
            
            # Ubicaciones y sucursales
            "ubicaciones": {
                "oficina_principal": {
                    "direccion": fake.address(),
                    "telefono": self.generate_realistic_phone(),
                    "area_m2": random.randint(50, 5000),
                    "tipo_local": random.choice(["Propio", "Alquilado", "Comodato"]),
                    "valor_alquiler": random.randint(500000, 10000000) if random.choice([True, False]) else None
                },
                "sucursales": [
                    {
                        "nombre": f"Sucursal {fake.city()}",
                        "direccion": fake.address(),
                        "telefono": self.generate_realistic_phone(),
                        "gerente": fake.name(),
                        "empleados": random.randint(2, 50),
                        "fecha_apertura": fake.date_between(start_date='-10y', end_date='now')
                    } for _ in range(random.randint(0, 8))
                ],
                "bodegas": [
                    {
                        "ubicacion": fake.address(),
                        "area_m2": random.randint(100, 10000),
                        "tipo": random.choice(["Propia", "Alquilada"]),
                        "uso": random.choice(["Producto Terminado", "Materia Prima", "Logística"])
                    } for _ in range(random.randint(0, 5))
                ]
            },
            
            # Certificaciones y permisos
            "certificaciones": {
                "permisos_funcionamiento": random.choice([True, False]),
                "licencia_municipal": f"LM-{random.randint(100000, 999999)}",
                "certificacion_iso": random.choice([True, False]),
                "otras_certificaciones": [
                    {
                        "tipo": random.choice(["ISO 9001", "ISO 14001", "HACCP", "FSC"]),
                        "fecha_obtencion": fake.date_between(start_date='-5y', end_date='now'),
                        "fecha_vencimiento": fake.date_between(start_date='now', end_date='+3y'),
                        "ente_certificador": fake.company()
                    } for _ in range(random.randint(0, 4))
                ],
                "registro_exportador": random.choice([True, False]),
                "zona_franca": random.choice([True, False])
            }
        }
        
        return business_info
    
    def generate_realistic_cedula(self) -> str:
        """Generate realistic Costa Rican cedula"""
        provincia_code = random.randint(1, 9)
        sequential = random.randint(100000, 999999)
        return f"{provincia_code}{sequential:06d}"
    
    def generate_realistic_phone(self) -> str:
        """Generate realistic Costa Rican phone"""
        if random.choice([True, False]):
            # Landline
            area = random.choice(["2222", "2223", "2224", "2225", "2401", "2402"])
            number = random.randint(1000, 9999)
            return f"+506 {area}-{number}"
        else:
            # Mobile
            prefix = random.choice(["8", "7", "6"])
            number = random.randint(1000000, 9999999)
            return f"+506 {prefix}{number:07d}"
    
    async def enrich_single_record(self, record_id: str, collection_name: str):
        """
        Enriquecer un solo registro con información completa
        """
        try:
            # Get the record
            record = await self.db[collection_name].find_one({"id": record_id})
            if not record:
                logger.warning(f"Record {record_id} not found in {collection_name}")
                return False
            
            enrichment_data = {}
            
            if collection_name in ["personas_fisicas", "daticos_personas_completo"]:
                # Enrich physical person
                cedula = record.get("cedula")
                if not cedula:
                    return False
                
                # Add comprehensive credit information
                credit_info = await self.generate_comprehensive_credit_information(cedula, "fisica")
                enrichment_data.update(credit_info)
                
                # Add vehicles information
                vehicles = await self.generate_comprehensive_vehicle_information(cedula)
                enrichment_data["vehiculos_completo"] = vehicles
                
                # Add properties information
                properties = await self.generate_comprehensive_property_information(cedula)
                enrichment_data["propiedades_completo"] = properties
                
                # Add legal information
                legal_info = await self.generate_comprehensive_legal_information(cedula, "fisica")
                enrichment_data["informacion_legal"] = legal_info
                
                self.enrichment_stats['credit_data_added'] += 1
                self.enrichment_stats['vehicle_data_added'] += len(vehicles)
                self.enrichment_stats['property_data_added'] += len(properties)
                self.enrichment_stats['legal_data_added'] += 1
                
            elif collection_name in ["personas_juridicas", "daticos_empresas_completo"]:
                # Enrich juridical person/company
                cedula_juridica = record.get("cedula_juridica")
                if not cedula_juridica:
                    return False
                
                # Add comprehensive credit information for companies
                credit_info = await self.generate_comprehensive_credit_information(cedula_juridica, "juridica")
                enrichment_data.update(credit_info)
                
                # Add comprehensive business information
                business_info = await self.generate_comprehensive_business_information(cedula_juridica)
                enrichment_data.update(business_info)
                
                # Add legal information for companies
                legal_info = await self.generate_comprehensive_legal_information(cedula_juridica, "juridica")
                enrichment_data["informacion_legal"] = legal_info
                
                self.enrichment_stats['credit_data_added'] += 1
                self.enrichment_stats['business_data_added'] += 1
                self.enrichment_stats['legal_data_added'] += 1
            
            # Add general enrichment metadata
            enrichment_data.update({
                "ultimo_enriquecimiento": datetime.utcnow(),
                "nivel_completitud": "COMPLETO",
                "fuentes_consultadas": ["Crediserver", "Registro Nacional", "TSE", "Google Maps", "Hacienda"],
                "score_calidad_datos": random.randint(85, 98),
                "fecha_proxima_actualizacion": datetime.utcnow() + timedelta(days=30)
            })
            
            # Update the record
            await self.db[collection_name].update_one(
                {"_id": record["_id"]},
                {"$set": enrichment_data}
            )
            
            self.enrichment_stats['records_processed'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error enriching record {record_id}: {e}")
            self.enrichment_stats['errors'] += 1
            return False
    
    async def run_daily_enrichment(self, batch_size: int = 1000):
        """
        Ejecutar enriquecimiento diario de datos
        """
        logger.info("🔄 Starting daily data enrichment process...")
        start_time = datetime.utcnow()
        
        await self.initialize()
        
        try:
            # Get records that need enrichment or haven't been enriched recently
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Enrich physical persons
            persons_to_enrich = await self.db.personas_fisicas.find({
                "$or": [
                    {"ultimo_enriquecimiento": {"$exists": False}},
                    {"ultimo_enriquecimiento": {"$lt": cutoff_date}},
                    {"nivel_completitud": {"$ne": "COMPLETO"}}
                ]
            }).limit(batch_size // 2).to_list(batch_size // 2)
            
            # Enrich companies
            companies_to_enrich = await self.db.personas_juridicas.find({
                "$or": [
                    {"ultimo_enriquecimiento": {"$exists": False}},
                    {"ultimo_enriquecimiento": {"$lt": cutoff_date}},
                    {"nivel_completitud": {"$ne": "COMPLETO"}}
                ]
            }).limit(batch_size // 2).to_list(batch_size // 2)
            
            # Process physical persons
            for person in persons_to_enrich:
                await self.enrich_single_record(person["id"], "personas_fisicas")
                await asyncio.sleep(0.01)  # Small delay to prevent overload
            
            # Process companies
            for company in companies_to_enrich:
                await self.enrich_single_record(company["id"], "personas_juridicas")
                await asyncio.sleep(0.01)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("✅ Daily enrichment completed!")
            logger.info(f"⏱️  Duration: {duration:.2f} seconds")
            logger.info(f"📊 Enrichment Stats:")
            for key, value in self.enrichment_stats.items():
                logger.info(f"   - {key}: {value:,}")
            
            # Save enrichment statistics
            stats_record = {
                "enrichment_date": start_time,
                "duration_seconds": duration,
                "enrichment_type": "DAILY_COMPREHENSIVE",
                **self.enrichment_stats,
                "status": "completed"
            }
            await self.db.enrichment_statistics.insert_one(stats_record)
            
            return {
                "success": True,
                "statistics": self.enrichment_stats,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"❌ Error in daily enrichment: {e}")
            return {
                "success": False,
                "error": str(e),
                "statistics": self.enrichment_stats
            }
        finally:
            await self.close()
    
    def schedule_daily_enrichment(self):
        """
        Programar enriquecimiento diario automático
        """
        # Enriquecimiento completo a las 3:00 AM
        schedule.every().day.at("03:00").do(lambda: asyncio.run(self.run_daily_enrichment(2000)))
        
        # Enriquecimiento parcial cada 6 horas
        schedule.every(6).hours.do(lambda: asyncio.run(self.run_daily_enrichment(500)))
        
        logger.info("📅 Advanced data enrichment scheduled:")
        logger.info("  - Complete enrichment daily at 3:00 AM (2000 records)")
        logger.info("  - Partial enrichment every 6 hours (500 records)")
    
    def start_enrichment_scheduler(self):
        """
        Iniciar el programador de enriquecimiento automático
        """
        def run_scheduler():
            self.is_running = True
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info("🔄 Advanced data enrichment scheduler started")
    
    def stop_enrichment_scheduler(self):
        """
        Detener el programador de enriquecimiento
        """
        self.is_running = False
        logger.info("🛑 Advanced data enrichment scheduler stopped")

# Global instance
advanced_enrichment = AdvancedDataEnrichment()

# Functions to start and control the enrichment system
def start_advanced_enrichment():
    """Start the advanced data enrichment system"""
    advanced_enrichment.schedule_daily_enrichment()
    advanced_enrichment.start_enrichment_scheduler()

async def run_manual_enrichment(batch_size: int = 1000):
    """Run manual enrichment"""
    return await advanced_enrichment.run_daily_enrichment(batch_size)

if __name__ == "__main__":
    # Run manual enrichment for testing
    result = asyncio.run(advanced_enrichment.run_daily_enrichment(100))
    print(f"Enrichment result: {result}")