#!/usr/bin/env python3
import sqlite3
import hashlib
import os

def init_database():
    # Asegurar que la carpeta /tmp existe
    os.makedirs('/tmp', exist_ok=True)
    
    # Conectar a la base de datos
    db_path = '/tmp/cpx_users.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    print("✅ Tabla 'users' creada/verificada")
    
    # Crear tabla link_history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS link_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        original_link TEXT NOT NULL,
        transformed_link TEXT NOT NULL,
        pa_value TEXT,
        status_changed TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    print("✅ Tabla 'link_history' creada/verificada")
    
    # Crear usuario admin
    password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    
    # Verificar si admin existe
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if not admin:
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, is_admin, is_active)
        VALUES ('admin', 'admin@cpx.com', ?, 1, 1)
        ''', (password_hash,))
        print("✅ Usuario admin creado")
    else:
        print("✅ Usuario admin ya existe")
    
    # Verificar
    cursor.execute("SELECT id, username, is_admin FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    if admin:
        print(f"📊 Admin: ID={admin[0]}, Usuario={admin[1]}, Admin={admin[2]}")
    else:
        print("❌ Error: Admin no encontrado")
    
    conn.commit()
    conn.close()
    print(f"✅ Base de datos inicializada correctamente en {db_path}")

if __name__ == '__main__':
    init_database()