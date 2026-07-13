#!/usr/bin/env python3
"""Update users with correct passlib bcrypt hash - using direct connection."""

from sqlalchemy import create_engine, text

# Use direct database URL from Render
DATABASE_URL = "postgresql://evaluadorcomprasdb_1moi_user:H3kIijyzTYAHFmHBk3rDaj5kEiBOVKbE@dpg-d8sg8t7avr4c73fomscg-a.oregon-postgres.render.com/consumo_estrategico"
CORRECT_HASH = "$2b$12$RU26e7r.aHCNs/spPjS9lu9vDs.MQxpNhHFDEnlyIz0fH4scMQtjy"

# Connect to database
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # First, check current users
        result = conn.execute(text("SELECT id, email, password_hash FROM users ORDER BY id"))
        users_before = result.fetchall()
        print(f"📊 Users before update:")
        for id, email, pwd_hash in users_before:
            print(f"  - {email}: {pwd_hash[:30]}...")
        
        # Update all users with the correct hash
        conn.execute(text("UPDATE users SET password_hash = :hash"), {"hash": CORRECT_HASH})
        conn.commit()
        print(f"\n✅ Updated all users with correct bcrypt hash")
        
        # Verify the update
        result = conn.execute(text("SELECT id, email, password_hash FROM users ORDER BY id"))
        users_after = result.fetchall()
        print(f"\n📊 Users after update:")
        for id, email, pwd_hash in users_after:
            print(f"  - {email}: {pwd_hash[:30]}...")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    engine.dispose()
