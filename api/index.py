import sys
import os

# Agregar el directorio padre al path para poder importar main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from main import app
    print("✅ Aplicación importada exitosamente")
except ImportError as e:
    print(f"❌ Error importando main.py: {e}")
    sys.path.append("/var/task")  # Vercel specific path
    from main import app

# Vercel serverless handler - Esto es lo que Vercel busca
app_handler = app

# También mantener 'app' para compatibilidad
handler = app

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor de desarrollo...")
    uvicorn.run(app, host="0.0.0.0", port=8000)