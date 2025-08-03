#!/usr/bin/env python3
"""
VERCEL FRONTEND INTEGRATION - Preparar el frontend para deployment en Vercel
"""

import os
import json
import shutil
from pathlib import Path

def prepare_frontend_for_vercel():
    """Prepara el frontend React para deployment en Vercel"""
    
    frontend_path = Path("/app/frontend")
    
    # 1. Actualizar package.json para Vercel
    package_json_path = frontend_path / "package.json"
    
    if package_json_path.exists():
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
            
        # Agregar scripts de build para Vercel
        package_data["scripts"]["vercel-build"] = "npm run build"
        package_data["scripts"]["start"] = "serve -s build"
        
        # Agregar dependencia serve si no existe
        if "serve" not in package_data.get("dependencies", {}):
            if "devDependencies" not in package_data:
                package_data["devDependencies"] = {}
            package_data["devDependencies"]["serve"] = "^14.0.0"
            
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
            
        print("✅ package.json actualizado para Vercel")
    
    # 2. Crear vercel.json para el frontend
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "package.json",
                "use": "@vercel/static-build",
                "config": {
                    "distDir": "build"
                }
            }
        ],
        "routes": [
            {
                "src": "/static/(.*)",
                "dest": "/static/$1"
            },
            {
                "src": "/(.*)",
                "dest": "/index.html"
            }
        ]
    }
    
    vercel_frontend_path = frontend_path / "vercel.json"
    with open(vercel_frontend_path, 'w') as f:
        json.dump(vercel_config, f, indent=2)
        
    print("✅ vercel.json creado para frontend")
    
    # 3. Actualizar .env para production
    env_path = frontend_path / ".env"
    env_production_path = frontend_path / ".env.production"
    
    # Crear .env.production para Vercel
    with open(env_production_path, 'w') as f:
        f.write("REACT_APP_BACKEND_URL=https://os-sistema.vercel.app\n")
        f.write("GENERATE_SOURCEMAP=false\n")
        f.write("NODE_OPTIONS=--max_old_space_size=4096\n")
        
    print("✅ .env.production creado")
    
    # 4. Crear archivo de instrucciones para el usuario
    instructions = """
# INSTRUCCIONES PARA DEPLOYMENT EN VERCEL - FRONTEND

## Opción 1: Deployment Automático desde GitHub
1. Ve a https://vercel.com
2. Conecta tu repositorio de GitHub
3. Selecciona el directorio `/frontend` como root directory
4. Vercel detectará automáticamente que es una app React
5. Deploy automáticamente

## Opción 2: Deployment Manual
1. Instala Vercel CLI: `npm i -g vercel`
2. En el directorio /frontend, ejecuta: `vercel`
3. Sigue las instrucciones en pantalla
4. Selecciona "No" para vincular a proyecto existente
5. Tu frontend estará en: https://tu-proyecto.vercel.app

## Configuración Importante:
- Root Directory: `frontend`
- Build Command: `npm run build` (automático)
- Output Directory: `build` (automático)
- Environment Variables: Ya configuradas en .env.production

## URLs:
- Backend API: https://os-sistema.vercel.app
- Frontend: Se generará nueva URL en Vercel
"""
    
    instructions_path = frontend_path / "VERCEL_DEPLOYMENT_INSTRUCTIONS.md"
    with open(instructions_path, 'w') as f:
        f.write(instructions)
        
    print("✅ Instrucciones de deployment creadas")
    
    return {
        "success": True,
        "files_created": [
            "vercel.json",
            ".env.production", 
            "VERCEL_DEPLOYMENT_INSTRUCTIONS.md"
        ],
        "package_json_updated": True
    }

if __name__ == "__main__":
    result = prepare_frontend_for_vercel()
    print(f"RESULTADO: {result}")