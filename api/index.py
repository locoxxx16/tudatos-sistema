"""
HANDLER PARA VERCEL - Aplicación ligera serverless
Evita problemas de importación y base de datos pesada
"""
import sys
import os

# Configurar path para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Importar aplicación ligera para Vercel
    from vercel_app import app
    print("✅ Aplicación Vercel ligera importada exitosamente")
except ImportError as e:
    print(f"❌ Error importando vercel_app: {e}")
    # Fallback a aplicación principal si es necesario
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    from main import app
    print("⚠️ Usando aplicación principal como fallback")

# Handler para Vercel serverless
handler = app

# También exportar como 'app' para compatibilidad
app_handler = app

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor de desarrollo...")
    uvicorn.run(app, host="0.0.0.0", port=8000)