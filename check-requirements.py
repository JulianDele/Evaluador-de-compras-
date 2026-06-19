#!/usr/bin/env python3
"""
Script de validación de dependencias — Consumo Estratégico
Verifica que todos los requisitos estén instalados antes de iniciar
"""
import subprocess
import sys
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def check_command(cmd, min_version=None):
    """Verifica si un comando está disponible y opcionalmente su versión"""
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
        version = result.stdout.strip() + result.stderr.strip()
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}OK{Colors.RESET} {cmd} instalado")
            if version:
                print(f"  → {version[:80]}")
            return True
        else:
            print(f"{Colors.RED}ERROR{Colors.RESET} {cmd} no está disponible")
            return False
    except FileNotFoundError:
        print(f"{Colors.RED}ERROR{Colors.RESET} {cmd} no encontrado en PATH")
        return False


def check_directory_exists(path, description):
    """Verifica que un directorio existe"""
    if Path(path).exists():
        print(f"{Colors.GREEN}OK{Colors.RESET} {description}: {path}")
        return True
    else:
        print(f"{Colors.RED}ERROR{Colors.RESET} {description} no existe: {path}")
        return False


def check_python_package(package_name):
    """Verifica si un paquete Python está instalado"""
    try:
        __import__(package_name)
        print(f"{Colors.GREEN}OK{Colors.RESET} Paquete Python '{package_name}' instalado")
        return True
    except ImportError:
        print(f"{Colors.RED}ERROR{Colors.RESET} Paquete Python '{package_name}' NO instalado")
        return False


def check_env_file(env_path, description):
    """Verifica que un archivo .env existe"""
    if Path(env_path).exists():
        print(f"{Colors.GREEN}OK{Colors.RESET} {description}: {env_path}")
        return True
    else:
        print(f"{Colors.YELLOW}WARNING{Colors.RESET} {description} no existe (puede ser normal): {env_path}")
        return False


def main():
    print_header("Validación de Dependencias — Consumo Estratégico")
    
    all_ok = True
    
    # ─── Requisitos Globales ─────────────────────────────────────────────────
    print(f"{Colors.BOLD}Requisitos Globales:{Colors.RESET}\n")
    
    if not check_command('git'):
        all_ok = False
    
    if not check_command('docker'):
        print(f"  {Colors.YELLOW}INFO{Colors.RESET} Docker no es necesario si usas instalación local")
    
    if not check_command('docker-compose'):
        print(f"  {Colors.YELLOW}INFO{Colors.RESET} Docker Compose no es necesario si usas instalación local")
    
    # ─── Backend — Python ────────────────────────────────────────────────────
    print(f"\n{Colors.BOLD}Backend — Python:{Colors.RESET}\n")
    
    if not check_command('python3') and not check_command('python'):
        all_ok = False
        print(f"  {Colors.RED}ERROR: Python 3.11+ es requerido{Colors.RESET}")
        print(f"  Descárgalo desde: https://www.python.org/downloads/")
    else:
        # Verificar versión de Python
        try:
            result = subprocess.run(['python3', '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            major, minor = map(int, version.split('.'))
            if major == 3 and minor >= 11:
                print(f"  {Colors.GREEN}OK{Colors.RESET} Versión: Python {version} (OK)")
            else:
                print(f"  {Colors.RED}✗{Colors.RESET} Python {version} es menor a 3.11")
                all_ok = False
        except:
            pass
    
    # Verificar que exista el directorio backend
    check_directory_exists('backend', 'Directorio backend')
    check_directory_exists('backend/app', 'Directorio backend/app')
    
    # Verificar requirements.txt
    if Path('backend/requirements.txt').exists():
        print(f"{Colors.GREEN}OK{Colors.RESET} backend/requirements.txt existe")
    else:
        print(f"{Colors.RED}✗{Colors.RESET} backend/requirements.txt no encontrado")
        all_ok = False
    
    # ─── Frontend — Node.js ──────────────────────────────────────────────────
    print(f"\n{Colors.BOLD}📦 Frontend — Node.js:{Colors.RESET}\n")
    
    if not check_command('node'):
        all_ok = False
        print(f"  {Colors.RED}ERROR: Node.js 18+ es requerido{Colors.RESET}")
        print(f"  Descárgalo desde: https://nodejs.org/")
    else:
        # Verificar versión de Node
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            version = result.stdout.strip().replace('v', '')
            major = int(version.split('.')[0])
            if major >= 18:
                print(f"  {Colors.GREEN}OK{Colors.RESET} Versión: Node.js {version} (OK)")
            else:
                print(f"  {Colors.RED}✗{Colors.RESET} Node.js {version} es menor a 18")
                all_ok = False
        except:
            pass
    
    check_command('npm')
    
    # Verificar que exista el directorio frontend
    check_directory_exists('frontend', 'Directorio frontend')
    check_directory_exists('frontend/src', 'Directorio frontend/src')
    
    # Verificar package.json
    if Path('frontend/package.json').exists():
        print(f"{Colors.GREEN}OK{Colors.RESET} frontend/package.json existe")
    else:
        print(f"{Colors.RED}✗{Colors.RESET} frontend/package.json no encontrado")
        all_ok = False
    
    # ─── Base de Datos ───────────────────────────────────────────────────────
    print(f"\n{Colors.BOLD}🐘 Base de Datos — PostgreSQL:{Colors.RESET}\n")
    
    if not check_command('psql'):
        print(f"  {Colors.YELLOW}⚠{Colors.RESET} psql no encontrado (necesario si NO usas Docker)")
        print(f"  Descargar desde: https://www.postgresql.org/download/")
    else:
        # Verificar versión
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            print(f"  → {result.stdout.strip()}")
        except:
            pass
    
    # ─── Variables de Entorno ────────────────────────────────────────────────
    print(f"\n{Colors.BOLD}Variables de Entorno:{Colors.RESET}\n")
    
    check_env_file('.env', 'Archivo .env raíz')
    check_env_file('backend/.env', 'Archivo backend/.env')
    check_env_file('frontend/.env.local', 'Archivo frontend/.env.local')
    
    # ─── Archivos Críticos ───────────────────────────────────────────────────
    print(f"\n{Colors.BOLD}Archivos Criticos:{Colors.RESET}\n")
    
    critical_files = [
        ('scripts/schema.sql', 'Esquema de base de datos'),
        ('scripts/seed_data.py', 'Script de datos iniciales'),
        ('backend/requirements.txt', 'Dependencias Python'),
        ('frontend/package.json', 'Dependencias Node.js'),
        ('docker-compose.yml', 'Orquestación Docker'),
    ]
    
    for path, description in critical_files:
        if Path(path).exists():
            print(f"{Colors.GREEN}OK{Colors.RESET} {description}: {path}")
        else:
            print(f"{Colors.RED}✗{Colors.RESET} {description} no encontrado: {path}")
            all_ok = False
    
    # ─── Resumen Final ───────────────────────────────────────────────────────
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    
    if all_ok:
        print(f"\n{Colors.GREEN}{Colors.BOLD}OK TODO ESTA CORRECTAMENTE CONFIGURADO{Colors.RESET}\n")
        print(f"Próximos pasos:")
        print(f"  1. Configura .env con tus valores")
        print(f"  2. Ejecuta: {Colors.BOLD}docker-compose up --build{Colors.RESET} (con Docker)")
        print(f"     O: {Colors.BOLD}./start-dev.sh{Colors.RESET} (instalación local)")
        print()
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ HAY PROBLEMAS DE CONFIGURACIÓN{Colors.RESET}\n")
        print(f"Por favor:")
        print(f"  1. Instala los paquetes faltantes (ver arriba)")
        print(f"  2. Consulta: SETUP.md")
        print(f"  3. O ejecuta nuevamente después de instalar\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
