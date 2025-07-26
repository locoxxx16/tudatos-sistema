import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
from faker import Faker
import uuid

# Initialize Faker for Spanish/Costa Rica
fake = Faker('es_ES')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Costa Rica geographical data
COSTA_RICA_DATA = {
    "San José": {
        "codigo": "SJ",
        "cantones": {
            "San José": ["Carmen", "Merced", "Hospital", "Catedral", "Zapote", "San Francisco de Dos Ríos"],
            "Escazú": ["Escazú", "San Antonio", "San Rafael"],
            "Desamparados": ["Desamparados", "San Miguel", "San Juan de Dios", "San Rafael Arriba", "San Antonio"],
            "Puriscal": ["Santiago", "Mercedes Sur", "Barbacoas", "Grifo Alto", "San Rafael"],
            "Tarrazú": ["San Marcos", "San Lorenzo", "San Carlos"],
            "Aserrí": ["Aserrí", "Tarbaca", "Vuelta de Jorco", "San Gabriel"],
            "Mora": ["Colón", "Guayabo", "Tabarcia", "Piedras Negras"],
            "Goicoechea": ["Guadalupe", "San Francisco", "Calle Blancos", "Mata de Plátano", "Ipís", "Rancho Redondo"],
            "Santa Ana": ["Santa Ana", "Salitral", "Pozos", "Uruca", "Piedades", "Brasil"],
            "Alajuelita": ["Alajuelita", "San Josecito", "San Antonio", "Concepción"],
            "Vázquez de Coronado": ["San Isidro", "San Rafael", "Dulce Nombre de Jesús", "Patalillo", "Cascajal"],
            "Acosta": ["San Ignacio", "Guaitil", "Palmichal", "Cangrejal", "Sabanillas"],
            "Tibás": ["San Juan", "Cinco Esquinas", "Anselmo Llorente", "León XIII", "Colima"],
            "Moravia": ["San Vicente", "San Jerónimo", "La Trinidad"],
            "Montes de Oca": ["San Pedro", "Sabanilla", "Mercedes", "San Rafael"],
            "Turrubares": ["San Pablo", "San Pedro", "San Juan de Mata", "San Luis", "Carara"],
            "Dota": ["Santa María", "Jardín", "Copey"],
            "Curridabat": ["Curridabat", "Granadilla", "Sánchez", "Tirrases"],
            "Pérez Zeledón": ["San Isidro de El General", "El General", "Daniel Flores", "Rivas", "San Pedro", "Platanares", "Pejibaye", "Cajón", "Barú", "Río Nuevo", "Páramo"]
        }
    },
    "Alajuela": {
        "codigo": "AJ",
        "cantones": {
            "Alajuela": ["Alajuela", "San José", "Carrizal", "San Antonio", "Guácima", "San Isidro", "Sabanilla", "San Rafael", "Río Segundo", "Desamparados", "Turrúcares", "Tambor", "Garita", "Sarapiquí"],
            "San Ramón": ["San Ramón", "Santiago", "San Juan", "Piedades Norte", "Piedades Sur", "San Rafael", "San Isidro", "Ángeles", "Alfaro", "Volio", "Concepción", "Zapotal", "Peñas Blancas"],
            "Grecia": ["Grecia", "San Isidro", "San José", "San Roque", "Tacares", "Río Cuarto", "Puente Piedra", "Bolívar"],
            "San Mateo": ["San Mateo", "Desmonte", "Jesús María"],
            "Atenas": ["Atenas", "Jesús", "Mercedes", "San Isidro", "Concepción", "San José", "Santa Eulalia", "Escobal"],
            "Naranjo": ["Naranjo", "San Miguel", "San José", "Cirrí Sur", "San Jerónimo", "San Juan", "El Rosario", "Palmitos"],
            "Palmares": ["Palmares", "Zaragoza", "Buenos Aires", "Santiago", "Candelaria", "Esquipulas", "La Granja"],
            "Poás": ["San Pedro", "San Juan", "San Rafael", "Carrillos", "Sabana Redonda"],
            "Orotina": ["Orotina", "El Mastate", "Hacienda Vieja", "Coyolar", "La Ceiba"],
            "San Carlos": ["Quesada", "Florencia", "Buenavista", "Aguas Zarcas", "Venecia", "Pital", "La Fortuna", "La Tigra", "La Palmera", "Venado", "Cutris", "Monterrey", "Pocosol"]
        }
    },
    "Cartago": {
        "codigo": "CA",
        "cantones": {
            "Cartago": ["Oriental", "Occidental", "Carmen", "San Nicolás", "Aguacaliente", "Guadalupe", "Corralillo", "Tierra Blanca", "Dulce Nombre", "Llano Grande", "Quebradilla"],
            "Paraíso": ["Paraíso", "Santiago", "Orosi", "Cachí", "Llanos de Santa Lucía"],
            "La Unión": ["Tres Ríos", "San Diego", "San Juan", "San Rafael", "Concepción", "Dulce Nombre", "San Ramón", "Río Azul"],
            "Jiménez": ["Juan Viñas", "Tucurrique", "Pejibaye"],
            "Turrialba": ["Turrialba", "La Suiza", "Peralta", "Santa Cruz", "Santa Teresita", "Pavones", "Tuis", "Tayutic", "Santa Rosa", "Tres Equis", "La Isabel", "Chirripó"],
            "Alvarado": ["Pacayas", "Cervantes", "Capellades"],
            "Oreamuno": ["San Rafael", "Cot", "Potrero Cerrado", "Cipreses", "Santa Rosa"],
            "El Guarco": ["El Tejar", "San Isidro", "Tobosi", "Patio de Agua"]
        }
    },
    "Heredia": {
        "codigo": "HE",
        "cantones": {
            "Heredia": ["Heredia", "Mercedes", "San Francisco", "Ulloa", "Varablanca"],
            "Barva": ["Barva", "San Pedro", "San Pablo", "San Roque", "Santa Lucía", "San José de la Montaña"],
            "Santo Domingo": ["Santo Domingo", "San Vicente", "San Miguel", "Paracito", "Santo Tomás", "Santa Rosa", "Tures", "Pará"],
            "Santa Bárbara": ["Santa Bárbara", "San Pedro", "San Juan", "Jesús", "Santo Domingo", "Purabá"],
            "San Rafael": ["San Rafael", "San Josecito", "Santiago", "Ángeles", "Concepción"],
            "San Isidro": ["San Isidro", "San José", "Concepción", "San Francisco"],
            "Belén": ["San Antonio", "La Ribera", "La Asunción"],
            "Flores": ["San Joaquín", "Barrantes", "Llorente"],
            "San Pablo": ["San Pablo", "Rincón de Sabanilla"],
            "Sarapiquí": ["Puerto Viejo", "La Virgen", "Horquetas", "Llanuras del Gaspar", "Cureña"]
        }
    },
    "Guanacaste": {
        "codigo": "GU",
        "cantones": {
            "Liberia": ["Liberia", "Cañas Dulces", "Mayorga", "Nacascolo", "Curubandé"],
            "Nicoya": ["Nicoya", "Mansión", "San Antonio", "Quebrada Honda", "Sámara", "Nosara", "Belén de Nosarita"],
            "Santa Cruz": ["Santa Cruz", "Bolsón", "Veintisiete de Abril", "Tempate", "Cartagena", "Cuajiniquil", "Diriá", "Cabo Velas", "Tamarindo"],
            "Bagaces": ["Bagaces", "La Fortuna", "Mogote", "Río Naranjo"],
            "Carrillo": ["Filadelfia", "Palmira", "Sardinal", "Belén"],
            "Cañas": ["Cañas", "Palmira", "San Miguel", "Bebedero", "Porozal"],
            "Abangares": ["Las Juntas", "Sierra", "San Juan", "Colorado"],
            "Tilarán": ["Tilarán", "Quebrada Grande", "Tronadora", "Santa Rosa", "Líbano", "Tierras Morenas", "Arenal"],
            "Nandayure": ["Carmona", "Santa Rita", "Zapotal", "San Pablo", "Porvenir", "Bejuco"],
            "La Cruz": ["La Cruz", "Santa Cecilia", "La Garita", "Santa Elena"],
            "Hojancha": ["Hojancha", "Monte Romo", "Puerto Carrillo", "Huacas"]
        }
    },
    "Puntarenas": {
        "codigo": "PU",
        "cantones": {
            "Puntarenas": ["Puntarenas", "Pitahaya", "Chomes", "Lepanto", "Paquera", "Manzanillo", "Guacimal", "Barranca", "Monte Verde", "Isla del Coco", "Cóbano", "Chacarita", "Chira", "Acapulco", "El Roble", "Arancibia"],
            "Esparza": ["Espíritu Santo", "San Juan Grande", "Macacona", "San Rafael", "San Jerónimo", "Caldera"],
            "Buenos Aires": ["Buenos Aires", "Volcán", "Potrero Grande", "Boruca", "Pilas", "Colinas", "Chánguena", "Biolley", "Brunka"],
            "Montes de Oro": ["Miramar", "La Unión", "San Isidro"],
            "Osa": ["Puerto Cortés", "Palmar", "Sierpe", "Bahía Ballena", "Piedras Blancas"],
            "Quepos": ["Quepos", "Savegre", "Naranjito"],
            "Golfito": ["Golfito", "Puerto Jiménez", "Guaycará", "Pavón"],
            "Coto Brus": ["San Vito", "Sabalito", "Aguabuena", "Limoncito", "Pittier"],
            "Parrita": ["Parrita"],
            "Corredores": ["Corredor", "La Cuesta", "Canoas", "Laurel"],
            "Garabito": ["Jacó", "Tárcoles"]
        }
    },
    "Limón": {
        "codigo": "LI",
        "cantones": {
            "Limón": ["Limón", "Valle La Estrella", "Río Blanco", "Matama"],
            "Pococí": ["Guápiles", "Jiménez", "Rita", "Roxana", "Cariari", "Colorado", "La Colonia"],
            "Siquirres": ["Siquirres", "Pacuarito", "Florida", "Germania", "El Cairo", "Alegría"],
            "Talamanca": ["Bratsi", "Sixaola", "Cahuita", "Telire"],
            "Matina": ["Matina", "Batán", "Carrandi"],
            "Guácimo": ["Guácimo", "Mercedes", "Pocora", "Río Jiménez", "Duacarí"]
        }
    }
}

# Business sectors for companies
BUSINESS_SECTORS = [
    "comercio", "servicios", "industria", "tecnologia", "educacion",
    "salud", "construccion", "turismo", "agricultura", "otros"
]

async def populate_locations():
    """Populate provinces, cantons and districts"""
    print("Populating locations...")
    
    # Clear existing data
    await db.provincias.delete_many({})
    await db.cantones.delete_many({})
    await db.distritos.delete_many({})
    
    for prov_name, prov_data in COSTA_RICA_DATA.items():
        # Insert province
        provincia_id = str(uuid.uuid4())
        provincia = {
            "id": provincia_id,
            "nombre": prov_name,
            "codigo": prov_data["codigo"]
        }
        await db.provincias.insert_one(provincia)
        
        for canton_name, distritos in prov_data["cantones"].items():
            # Insert canton
            canton_id = str(uuid.uuid4())
            canton = {
                "id": canton_id,
                "nombre": canton_name,
                "codigo": f"{prov_data['codigo']}-{canton_name[:3].upper()}",
                "provincia_id": provincia_id
            }
            await db.cantones.insert_one(canton)
            
            # Insert districts
            for i, distrito_name in enumerate(distritos):
                distrito = {
                    "id": str(uuid.uuid4()),
                    "nombre": distrito_name,
                    "codigo": f"{canton['codigo']}-{i+1:02d}",
                    "canton_id": canton_id
                }
                await db.distritos.insert_one(distrito)
    
    print(f"Created {len(COSTA_RICA_DATA)} provinces with all cantons and districts")

async def populate_personas_fisicas(count=1000):
    """Generate sample physical persons"""
    print(f"Generating {count} personas físicas...")
    
    await db.personas_fisicas.delete_many({})
    
    # Get all districts for random assignment
    distritos = await db.distritos.find().to_list(1000)
    cantones_map = {}
    provincias_map = {}
    
    # Build location maps
    for distrito in distritos:
        canton = await db.cantones.find_one({"id": distrito["canton_id"]})
        provincia = await db.provincias.find_one({"id": canton["provincia_id"]})
        cantones_map[distrito["id"]] = canton
        provincias_map[canton["id"]] = provincia
    
    personas = []
    for i in range(count):
        distrito = random.choice(distritos)
        canton = cantones_map[distrito["id"]]
        provincia = provincias_map[canton["id"]]
        
        # Generate Costa Rican ID (cedula)
        cedula = f"{random.randint(1, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}"
        
        persona = {
            "id": str(uuid.uuid4()),
            "cedula": cedula,
            "nombre": fake.first_name(),
            "primer_apellido": fake.last_name(),
            "segundo_apellido": fake.last_name() if random.choice([True, False]) else None,
            "fecha_nacimiento": fake.date_time_between(start_date='-80y', end_date='-18y'),
            "telefono": f"+506 {random.randint(2000, 9999)}-{random.randint(1000, 9999)}",
            "email": fake.email() if random.choice([True, False, False]) else None,
            "provincia_id": provincia["id"],
            "canton_id": canton["id"],
            "distrito_id": distrito["id"],
            "direccion_exacta": f"{fake.street_address()}, {distrito['nombre']}",
            "ocupacion": fake.job(),
            "created_at": fake.date_time_between(start_date='-2y', end_date='now')
        }
        personas.append(persona)
        
        if len(personas) >= 100:
            await db.personas_fisicas.insert_many(personas)
            personas = []
    
    if personas:
        await db.personas_fisicas.insert_many(personas)
    
    print(f"Created {count} personas físicas")

async def populate_personas_juridicas(count=500):
    """Generate sample legal entities/companies"""
    print(f"Generating {count} personas jurídicas...")
    
    await db.personas_juridicas.delete_many({})
    
    # Get all districts for random assignment
    distritos = await db.distritos.find().to_list(1000)
    cantones_map = {}
    provincias_map = {}
    
    # Build location maps
    for distrito in distritos:
        canton = await db.cantones.find_one({"id": distrito["canton_id"]})
        provincia = await db.provincias.find_one({"id": canton["provincia_id"]})
        cantones_map[distrito["id"]] = canton
        provincias_map[canton["id"]] = provincia
    
    company_types = [
        "S.A.", "S.R.L.", "Ltda.", "Corp.", "Inc.", "Asociación", "Fundación", 
        "Cooperativa", "Empresa Individual"
    ]
    
    personas = []
    for i in range(count):
        distrito = random.choice(distritos)
        canton = cantones_map[distrito["id"]]
        provincia = provincias_map[canton["id"]]
        
        # Generate legal ID (cedula jurídica)
        cedula_juridica = f"3-101-{random.randint(100000, 999999)}"
        
        company_name = fake.company()
        company_type = random.choice(company_types)
        
        persona = {
            "id": str(uuid.uuid4()),
            "cedula_juridica": cedula_juridica,
            "nombre_comercial": f"{company_name}",
            "razon_social": f"{company_name} {company_type}",
            "sector_negocio": random.choice(BUSINESS_SECTORS),
            "telefono": f"+506 {random.randint(2000, 9999)}-{random.randint(1000, 9999)}",
            "email": f"info@{company_name.lower().replace(' ', '')}.cr",
            "website": f"www.{company_name.lower().replace(' ', '')}.cr" if random.choice([True, False]) else None,
            "provincia_id": provincia["id"],
            "canton_id": canton["id"],
            "distrito_id": distrito["id"],
            "direccion_exacta": f"{fake.street_address()}, {distrito['nombre']}",
            "numero_empleados": random.choice([1, 2, 3, 5, 8, 10, 15, 20, 25, 30, 50, 75, 100, 150, 200, 500]),
            "fecha_constitucion": fake.date_between(start_date='-20y', end_date='now'),
            "created_at": fake.date_time_between(start_date='-2y', end_date='now')
        }
        personas.append(persona)
        
        if len(personas) >= 100:
            await db.personas_juridicas.insert_many(personas)
            personas = []
    
    if personas:
        await db.personas_juridicas.insert_many(personas)
    
    print(f"Created {count} personas jurídicas")

async def create_sample_user():
    """Create a demo user"""
    print("Creating sample user...")
    
    await db.users.delete_many({})
    
    user = {
        "id": str(uuid.uuid4()),
        "username": "admin",
        "email": "admin@daticos.cr",
        "full_name": "Administrador Daticos",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user)
    print("Created admin user (username: admin, password: admin123)")

async def main():
    """Main population script"""
    print("Starting database population for Daticos Clone...")
    
    await populate_locations()
    await create_sample_user()
    await populate_personas_fisicas(2000)
    await populate_personas_juridicas(800)
    
    print("\n✅ Database population completed!")
    print("📊 Summary:")
    print(f"   - {len(COSTA_RICA_DATA)} Provinces")
    print(f"   - ~{sum(len(p['cantones']) for p in COSTA_RICA_DATA.values())} Cantons")
    print(f"   - ~{sum(len(distritos) for p in COSTA_RICA_DATA.values() for distritos in p['cantones'].values())} Districts")
    print(f"   - 2,000 Personas Físicas")
    print(f"   - 800 Personas Jurídicas")
    print(f"   - 1 Admin User")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())