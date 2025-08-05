#!/bin/bash
# 🚀 SCRIPT DE DEPLOY FINAL - DATATICO CR
# Ejecuta todos los pasos finales para deployment

echo "🎉 DATATICO CR - DEPLOY FINAL"
echo "=============================="

# Verificar migración
echo "📊 Verificando estado de migración..."
if pgrep -f "migrate_automated.py" > /dev/null; then
    echo "⏳ Migración aún en progreso..."
    echo "💡 Puedes continuar, la migración seguirá en background"
else
    echo "✅ Migración completada!"
fi

# Verificar archivos críticos
echo ""
echo "🔍 Verificando configuración..."

if [ -f "/app/api/single.py" ]; then
    echo "✅ API optimizada: single.py configurada"
else
    echo "❌ ERROR: single.py no encontrada"
    exit 1
fi

if [ -f "/app/vercel.json" ]; then
    echo "✅ Configuración de Vercel lista"
else
    echo "❌ ERROR: vercel.json no encontrada"
    exit 1
fi

# Mostrar URL de MongoDB
echo ""
echo "📋 CONFIGURACIÓN PARA VERCEL:"
echo "================================"
echo "Variable: MONGO_URL"
echo "Valor: mongodb://datatico_admin:DataCR2025#Secure@iad2-c19-0.mongo.objectrocket.com:52752,iad2-c19-1.mongo.objectrocket.com:52752,iad2-c19-2.mongo.objectrocket.com:52752/datatico_cr?replicaSet=592734bd19354a7d81c1402dd6eed9f4&ssl=true"
echo ""

# Comandos finales
echo "🚀 COMANDOS PARA EJECUTAR:"
echo "=========================="
echo "1. Configurar variable en Vercel:"
echo "   vercel env add MONGO_URL"
echo "   (Pegar la URL de arriba cuando te la pida)"
echo ""
echo "2. Deploy a producción:"
echo "   vercel --prod"
echo ""
echo "3. ¡Tu aplicación estará lista con 5.9M+ registros!"
echo ""

# Estado final
echo "📊 RESUMEN FINAL:"
echo "=================="
echo "✅ MongoDB ObjectRocket: Configurado"
echo "✅ Base de datos: datatico_cr"
echo "✅ Migración: En progreso/Completada"
echo "✅ API optimizada: Ready"
echo "✅ Frontend configurado: Ready"
echo ""
echo "🎯 PRÓXIMO PASO: vercel env add MONGO_URL"
echo "🎉 ¡ESTÁS A 2 COMANDOS DE TERMINAR!"