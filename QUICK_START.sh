#!/bin/bash
# Quick Start Guide - Solo copiar y pegar

# 1. Verificar requisitos (5 segundos)
python3 check-requirements.py

# 2. Copiar configuración (1 segundo)
cp .env.example .env

# 3. Iniciar con Docker (30 segundos)
docker-compose up --build

# 4. En otra terminal: Cargar usuarios (2 segundos)
psql -h localhost -U ce_user -d consumo_estrategico -f scripts/insert_users.sql

# 5. Abrir navegador (1 segundo)
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8000/docs

# Credenciales por defecto:
# admin@consumo.local / Consumo2024!
