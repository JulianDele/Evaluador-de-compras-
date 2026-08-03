#!/usr/bin/env python3
import os
import sys
from passlib.context import CryptContext
import psycopg2

DB_URL = os.environ.get('DATABASE_URL') or 'postgresql://ce_user:JQQujV40beK2iN6njtNajPijvFPHIbJo@db:5432/consumo_estrategico'
PASSWORD = os.environ.get('NEW_PASSWORD') or 'Consumo2024!'

ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    hashed = ctx.hash(PASSWORD)
    print('Generated hash:', hashed)
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("UPDATE users SET password_hash = %s WHERE email IS NOT NULL;", (hashed,))
        conn.commit()
        print('Updated users:', cur.rowcount)
        cur.close()
        conn.close()
    except Exception as e:
        print('ERROR:', e)
        sys.exit(2)

if __name__ == '__main__':
    main()
