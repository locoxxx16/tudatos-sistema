# 🚀 GUÍA SÚPER DETALLADA - RAILWAY DEPLOYMENT

## 📋 PREPARATIVOS (5 MINUTOS)

### 1. **Verificar tu GitHub:**
- Ir a: https://github.com/tu-usuario
- Crear nuevo repositorio: "tudatos-sistema"
- Configuración: Público o Privado (recomiendo Privado)

### 2. **Preparar archivos locales:**
```bash
# En tu computadora, crear carpeta
mkdir tudatos-sistema
cd tudatos-sistema

# Inicializar Git
git init
git branch -M main
```

## 📦 ARCHIVOS A CREAR EN TU REPOSITORIO

### **Estructura necesaria:**
```
tudatos-sistema/
├── backend/
│   ├── requirements.txt
│   ├── server.py
│   ├── ultra_deep_extractor.py
│   ├── mega_aggressive_extractor.py
│   ├── ultra_optimized_extractor_v2.py
│   ├── daticos_extractor.py
│   ├── autonomous_scheduler.py
│   └── start_ultra_deep_now.py
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   └── public/
├── railway.json
├── docker-compose.yml
├── .env.example
├── README.md
└── netlify.toml (para frontend)
```

## 🔧 CONFIGURACIÓN RAILWAY (PASO A PASO)

### **Paso 1: Subir código a GitHub (10 minutos)**

1. **Copiar TODOS los archivos del backend:**
```bash
# Desde /app/backend/ copiar:
- server.py
- ultra_deep_extractor.py
- mega_aggressive_extractor.py
- ultra_optimized_extractor_v2.py
- daticos_extractor.py
- autonomous_scheduler.py
- requirements.txt
- start_ultra_deep_now.py
```

2. **Copiar TODOS los archivos del frontend:**
```bash
# Desde /app/frontend/ copiar:
- package.json
- src/App.js (con modal mejorado)
- src/App.css
- src/index.js
- src/index.css
- public/ (carpeta completa)
```

3. **Subir a GitHub:**
```bash
git add .
git commit -m "Sistema tudatos completo - 3 extractores + IA"
git remote add origin https://github.com/tu-usuario/tudatos-sistema.git
git push -u origin main
```

### **Paso 2: Configurar Railway (15 minutos)**

1. **Ir a Railway Dashboard:**
   - https://railway.app/dashboard
   - Click "New Project"

2. **Conectar GitHub:**
   - "Deploy from GitHub repo"
   - Seleccionar: "tudatos-sistema"
   - Click "Deploy Now"

3. **Configurar Backend Service:**
   - Railway detectará automáticamente FastAPI
   - En settings → Root Directory: `backend`
   - En settings → Start Command: `python server.py`

4. **Configurar Frontend Service:**
   - Add new service → GitHub repo → mismo repo
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Start Command: `npm start`

5. **Configurar Base de Datos MongoDB:**
   - Add service → Database → MongoDB
   - Railway creará automáticamente

### **Paso 3: Variables de Entorno (5 minutos)**

**En Backend Service → Variables:**
```env
MONGO_URL=${{MongoDB.MONGO_URL}}
DB_NAME=tudatos_production
SECRET_KEY=tu_clave_super_segura_aqui_32chars
ENVIRONMENT=production
PORT=8001
```

**En Frontend Service → Variables:**
```env
REACT_APP_BACKEND_URL=${{backend.RAILWAY_PUBLIC_DOMAIN}}
PORT=3000
```

### **Paso 4: Dominio Personalizado (5 minutos)**

1. **En Frontend Service:**
   - Settings → Domains
   - Add Domain: `tudatos.com`
   - Configurar DNS en tu proveedor de dominio:
     ```
     CNAME www tudatos.com.railway.app
     CNAME tudatos tudatos.com.railway.app
     ```

2. **SSL automático:**
   - Railway configura SSL automáticamente
   - Esperar 5-10 minutos

### **Paso 5: Deploy y Verificación (10 minutos)**

1. **Verificar Deploy:**
   - Ver logs en Railway dashboard
   - Frontend: https://tu-frontend.railway.app
   - Backend: https://tu-backend.railway.app/api/system/health

2. **Test completo:**
   - Abrir tudatos.com
   - Probar búsqueda
   - Verificar modal con toda la información
   - Comprobar que sistemas de extracción funcionen

## 🔄 MIGRACIÓN DE BASE DE DATOS (15 minutos)

### **Exportar datos actuales:**
```bash
# En /app/backend ejecutar:
mongodump --host localhost:27017 --db test_database --out backup_completo
tar -czf tudatos_backup.tar.gz backup_completo/
```

### **Importar a Railway MongoDB:**
```bash
# Obtener URL de MongoDB de Railway
# En variables: MONGO_URL

# Importar datos:
mongorestore --uri "tu_railway_mongo_url" backup_completo/test_database/ --nsFrom="test_database.*" --nsTo="tudatos_production.*"
```

## ⚡ ACTIVAR SISTEMAS DE EXTRACCIÓN

### **Configurar Cron Jobs en Railway:**

1. **Add service → Cron**
2. **Configurar horarios:**
```cron
# Ultra Deep diario 5AM
0 5 * * * python backend/start_ultra_deep_now.py

# Mega Aggressive cada 6 horas
0 */6 * * * python backend/mega_aggressive_extractor.py

# V2.0 con IA cada 4 horas
0 */4 * * * python backend/ultra_optimized_extractor_v2.py

# Limpieza y backup semanal
0 2 * * 0 python backend/maintenance_script.py
```

## 🎯 VERIFICACIÓN FINAL

### **Checklist completo:**
- [ ] tudatos.com carga correctamente
- [ ] Sistema de búsqueda funciona
- [ ] Modal muestra toda la información
- [ ] Backend responde en /api/system/health
- [ ] MongoDB conectado y con datos
- [ ] Sistemas de extracción activos
- [ ] SSL configurado
- [ ] Logs sin errores

## 🚨 SOLUCIÓN DE PROBLEMAS COMUNES

### **Error: Build failed**
```bash
# Verificar package.json en frontend
# Verificar requirements.txt en backend
# Revisar logs en Railway dashboard
```

### **Error: Database connection**
```bash
# Verificar MONGO_URL en variables
# Comprobar que MongoDB service esté running
# Revisar formato de URL de conexión
```

### **Error: Domain not working**
```bash
# Verificar configuración DNS
# Esperar propagación (hasta 24h)
# Comprobar SSL certificate status
```

## 📞 PUNTOS DE VERIFICACIÓN

**Después de cada paso, verificar:**
1. ✅ Código subido a GitHub
2. ✅ Railway detecta el proyecto
3. ✅ Build exitoso (ver logs)
4. ✅ Services running (verde en dashboard)
5. ✅ Variables configuradas correctamente
6. ✅ Base de datos conectada
7. ✅ Dominio apuntando correctamente
8. ✅ SSL activo (candado verde)
9. ✅ Sistema funcionando end-to-end

---

**🎯 RESULTADO FINAL:**
- tudatos.com funcionando 24/7
- 3 sistemas de extracción masiva activos
- Base de datos con 310,840+ registros (y creciendo)
- Sistema IA optimizándose automáticamente
- Control total de tu plataforma de datos

**⏱️ TIEMPO TOTAL: 45-60 minutos**