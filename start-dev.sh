#!/bin/bash
# ============================================================================
# Script de Inicio — Consumo Estratégico (macOS / Linux)
# ============================================================================
# Uso: chmod +x start-dev.sh && ./start-dev.sh
# ============================================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                   Consumo Estratégico — Inicio Rápido                  ║"
echo "║                         Modo Desarrollo                                ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar si Docker está disponible
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Docker detectado. Usando Docker Compose..."
    echo ""
    echo "Instrucciones:"
    echo "  1. Verifica que Docker esté corriendo"
    echo "  2. Ejecuta: docker-compose up --build"
    echo "  3. Espera a que termine"
    echo "  4. Abre: http://localhost:3000"
    echo ""
    read -p "¿Continuar con Docker Compose? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        docker-compose up --build
        exit 0
    fi
fi

echo "Iniciando instalación local..."
echo ""

# Crear .env si no existe
if [ ! -f backend/.env ]; then
    echo "Creando backend/.env..."
    cp backend/.env.example backend/.env
    echo "OK Archivo creado: backend/.env"
    echo "  WARNING EDITA backend/.env con tus valores antes de continuar"
fi

if [ ! -f frontend/.env.local ]; then
    echo "Creando frontend/.env.local..."
    cp frontend/.env.example frontend/.env.local
    echo "OK Archivo creado: frontend/.env.local"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                         BACKEND (Terminal 1)                            ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

cd backend

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.11+ no encontrado"
    echo "   Instálalo con:"
    echo "   macOS:  brew install python3"
    echo "   Linux:  sudo apt install python3.11"
    exit 1
fi

echo "OK Python detectado: $(python3 --version)"
echo ""

# Crear venv si no existe
if [ ! -d venv ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "OK Entorno virtual creado"
    echo ""
fi

# Activar venv
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias Python..."
pip install -q -r requirements.txt

echo ""
echo "✓ Backend listo"
echo ""
echo "🚀 Iniciando servidor FastAPI en puerto 8000..."
echo "   Documentación: http://localhost:8000/docs"
echo ""

# Iniciar backend en background
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Espera 5 segundos..."
sleep 5

cd ..

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                         FRONTEND (Terminal 2)                           ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

cd frontend

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js 18+ no encontrado"
    echo "   Instálalo con:"
    echo "   macOS:  brew install node"
    echo "   Linux:  sudo apt install nodejs npm"
    kill $BACKEND_PID
    exit 1
fi

echo "OK Node.js detectado: $(node --version)"
echo ""

echo "📦 Instalando dependencias Node.js..."
npm install --silent

echo "✓ Frontend listo"
echo ""
echo "🚀 Iniciando servidor Vite en puerto 5173..."
echo "   Acceso: http://localhost:5173"
echo ""

# Iniciar frontend en background
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                      OK TODO LISTO                                      ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Accesos:"
echo "   Frontend:        http://localhost:5173"
echo "   Backend:         http://localhost:8000"
echo "   API Docs:        http://localhost:8000/docs"
echo ""
echo "⏹️  Para detener: Presiona Ctrl+C"
echo ""

# Esperar a que alguno de los dos procesos termine
wait
