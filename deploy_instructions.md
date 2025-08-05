# 🚀 INSTRUCCIONES EXACTAS PARA DEPLOY LIMPIO

## MÉTODO 1: DEPLOY DIRECTO CON VERCEL CLI

### Paso 1: Instalar Vercel CLI
```bash
npm i -g vercel
```

### Paso 2: Login a Vercel
```bash
vercel login
```

### Paso 3: Deploy desde la carpeta raíz
```bash
cd /ruta/a/tu/proyecto
vercel --prod
```

## MÉTODO 2: NUEVO PROYECTO EN VERCEL WEB

### Configuración exacta que debes usar:

**Build Settings:**
- Build Command: (dejar vacío)
- Output Directory: (dejar vacío)  
- Install Command: (dejar vacío)

**Root Directory:** 
- Seleccionar: `.` (raíz del proyecto)

## ARCHIVOS QUE VERCEL DEBE DETECTAR:

✅ vercel.json (140 bytes)
✅ api/single.py (1.5KB)
✅ api/requirements.txt (146 bytes)
✅ .vercelignore (configuración)

**TAMAÑO TOTAL: ~12KB** (no más de 50KB)

## SI FALLA EL DEPLOY:

1. Verifica que el build tome menos de 30 segundos
2. Verifica que no aparezcan archivos como:
   - backend/
   - frontend/node_modules/
   - *.log
   - main.py

3. Error común: "Function too large"
   - Significa que aún se están subiendo archivos pesados
   - Revisa el .vercelignore

## RESULTADO ESPERADO:

- ✅ Deploy exitoso en menos de 1 minuto
- ✅ URL funcional mostrando la página TuDatos
- ✅ Sin errores 404 o 500