import sqlite3
import hashlib

def init_database():
    # Conectar a la base de datos
    conn = sqlite3.connect('/tmp/cpx_users.db')
    cursor = conn.cursor()
    
    # Crear tabla users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    
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
    
    # Crear usuario admin
    password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute("DELETE FROM users WHERE username = 'admin'")
    cursor.execute('''
    INSERT INTO users (username, email, password_hash, is_admin, is_active)
    VALUES ('admin', 'admin@cpx.com', ?, 1, 1)
    ''', (password_hash,))
    
    conn.commit()
    
    # Verificar
    cursor.execute("SELECT id, username, is_admin FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    print(f"✅ Admin creado: {admin}")
    
    conn.close()
    print("✅ Base de datos inicializada correctamente")

if __name__ == '__main__':
    init_database()