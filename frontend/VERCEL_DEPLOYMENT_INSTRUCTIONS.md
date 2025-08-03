
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
