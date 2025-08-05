"""
ARCHIVO ÚNICO PARA VERCEL - TODO EN UNO
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
@app.get("/{path:path}")
async def catch_all(path: str = ""):
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>TuDatos</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>.gradient-main{background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%)}.glass{background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.1)}</style>
</head><body class="bg-gray-900 text-white">
<header class="gradient-main shadow-2xl"><div class="max-w-7xl mx-auto px-6 py-6">
<h1 class="text-6xl font-black text-center">TuDatos</h1>
<p class="text-2xl text-center mt-4">La Base de Datos Más Grande de Costa Rica</p>
<div class="text-center mt-8"><div class="inline-block glass rounded-xl px-8 py-4">
<div class="text-4xl font-black text-yellow-300">5,947,094</div>
<div>Registros Disponibles</div></div></div></div></header>
<section class="py-20 text-center">
<h2 class="text-5xl font-black mb-8">DATOS COMPLETOS DE COSTA RICA</h2>
<p class="text-2xl mb-8">5,947,094 registros con fotos, contactos y datos familiares</p>
<div class="bg-yellow-500 text-black p-6 rounded-2xl max-w-2xl mx-auto">
<h3 class="text-2xl font-bold mb-4">🚀 Para Acceso Completo</h3>
<p class="text-xl font-bold">📧 jykinternacional@gmail.com</p>
</div></section></body></html>""")

handler = app