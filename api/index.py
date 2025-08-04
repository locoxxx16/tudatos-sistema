import sys
import os

# Agregar el directorio padre al path para poder importar main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel serverless handler
handler = app

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)