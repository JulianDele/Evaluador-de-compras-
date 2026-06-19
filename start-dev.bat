@echo off
REM ============================================================================
REM Script de Inicio — Consumo Estratégico (Windows)
REM ============================================================================
REM Uso: start-dev.bat
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                   Consumo Estratégico — Inicio Rápido                  ║
echo ║                         Modo Desarrollo                                ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Verificar si Docker está disponible (para docker-compose)
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo 🐳 Docker detectado. Usando Docker Compose...
    echo.
    echo Instrucciones:
    echo   1. Verifica que Docker Desktop esté corriendo
    echo   2. Ejecuta: docker-compose up --build
    echo   3. Espera a que termine
    echo   4. Abre: http://localhost:3000
    echo.
    timeout /t 3 >nul
    echo Iniciando Docker Compose...
    echo.
    docker-compose up --build
    exit /b
)

echo 🛠️  Docker no detectado. Iniciando instalación local...
echo.

REM Crear .env si no existe
if not exist backend\.env (
    echo ⚙️  Creando backend\.env...
    copy backend\.env.example backend\.env >nul
    echo ✓ Archivo creado: backend\.env
    echo   ⚠️  EDITA backend\.env con tus valores antes de continuar
)

if not exist frontend\.env.local (
    echo ⚙️  Creando frontend\.env.local...
    copy frontend\.env.example frontend\.env.local >nul
    echo ✓ Archivo creado: frontend\.env.local
)

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                         BACKEND (Terminal 1)                            ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

cd backend

REM Verificar Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python 3.11+ no encontrado
    echo    Descárgalo desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python detectado
echo.

REM Crear venv si no existe
if not exist venv (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    echo ✓ Entorno virtual creado
    echo.
)

REM Activar venv
echo 📦 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📦 Instalando dependencias Python...
pip install -r requirements.txt >nul

echo.
echo ✓ Backend listo
echo.
echo 🚀 Iniciando servidor FastAPI en puerto 8000...
echo    Documentación: http://localhost:8000/docs
echo.

REM Iniciar en terminal separada
start "Backend - Consumo Estratégico" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Espera 5 segundos...
timeout /t 5 >nul

cd ..

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                         FRONTEND (Terminal 2)                           ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

cd frontend

REM Verificar Node.js
node --version >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Node.js 18+ no encontrado
    echo    Descárgalo desde: https://nodejs.org/
    pause
    exit /b 1
)

echo ✓ Node.js detectado: 
node --version

echo.
echo 📦 Instalando dependencias Node.js...
call npm install >nul

echo ✓ Frontend listo
echo.
echo 🚀 Iniciando servidor Vite en puerto 5173...
echo    Acceso: http://localhost:5173
echo.

REM Iniciar en terminal separada
start "Frontend - Consumo Estratégico" cmd /k "npm run dev"

cd ..

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                      ✅ TODO LISTO                                      ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo 📍 Accesos:
echo    Frontend:        http://localhost:5173
echo    Backend:         http://localhost:8000
echo    API Docs:        http://localhost:8000/docs
echo.
echo ⏹️  Para detener: Cierra las 2 ventanas de terminal o presiona Ctrl+C
echo.
pause
