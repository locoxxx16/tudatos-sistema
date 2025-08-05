#!/bin/bash
# Script para configurar variables de entorno en Vercel

echo "🚀 Configurando variables de entorno en Vercel..."

# Configurar la URL de MongoDB ObjectRocket
vercel env add MONGO_URL production
# Cuando te pida el valor, usa:
# mongodb://datatico_admin:DataCR2025#Secure@iad2-c19-0.mongo.objectrocket.com:52752,iad2-c19-1.mongo.objectrocket.com:52752,iad2-c19-2.mongo.objectrocket.com:52752/datatico_cr?replicaSet=592734bd19354a7d81c1402dd6eed9f4&ssl=true

echo "✅ Variable MONGO_URL configurada"
echo "🔗 URL: mongodb://datatico_admin:***@iad2-c19-0.mongo.objectrocket.com:52752/datatico_cr"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. La migración de datos debe completarse"
echo "2. Ejecutar: vercel --prod"
echo "3. Tu aplicación estará disponible con 5.9M+ registros"
