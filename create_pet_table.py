#!/usr/bin/env python
"""
Force create the pet portrait submission table
Run this once to fix the missing table issue
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

# SQL to create the table
sql = """
CREATE TABLE IF NOT EXISTS pages_petportraitsubmission (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    customer_email VARCHAR(254) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL DEFAULT '',
    pet_name VARCHAR(100) NOT NULL,
    pet_photo VARCHAR(100) NOT NULL,
    additional_notes TEXT NOT NULL DEFAULT '',
    portrait_size VARCHAR(50) NOT NULL DEFAULT '8x10',
    stripe_payment_intent_id VARCHAR(200),
    stripe_session_id VARCHAR(200),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    amount_paid NUMERIC(10, 2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'submitted'
);
"""

migration_sql = """
INSERT INTO django_migrations (app, name, applied) 
VALUES ('pages', '0001_initial', NOW())
ON CONFLICT DO NOTHING;
"""

with connection.cursor() as cursor:
    print("Creating pages_petportraitsubmission table...")
    cursor.execute(sql)
    print("Table created successfully!")
    
    print("Marking migration as applied...")
    cursor.execute(migration_sql)
    print("Migration marked as applied!")

print("Done! The pet portrait feature should now work.")