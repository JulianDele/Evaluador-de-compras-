#!/usr/bin/env python3
"""Generate correct passlib bcrypt hash for testing."""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
password = "Consumo2024!"

hashed = pwd_context.hash(password)
print(f"Passlib bcrypt hash: {hashed}")
print(f"Hash length: {len(hashed)}")

# Verify it can validate
is_valid = pwd_context.verify(password, hashed)
print(f"Validation result: {is_valid}")
