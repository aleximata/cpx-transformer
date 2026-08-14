def init_db():
    with app.app_context():
        try:
            print('🔄 Inicializando base de datos...')
            # Ejecutar el script de inicialización
            import subprocess
            import sys
            result = subprocess.run([sys.executable, 'init_db.py'], capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f'❌ Errores: {result.stderr}')
            print('✅ Base de datos inicializada desde init_db.py')
        except Exception as e:
            print(f'❌ Error al inicializar la base de datos: {e}')
            # Intentar crear las tablas directamente con SQLAlchemy
            try:
                db.create_all()
                print('✅ Tablas creadas con SQLAlchemy')
                
                # Crear admin manualmente
                admin = User.query.filter_by(username='admin').first()
                if not admin:
                    admin = User(username='admin', email='admin@cpx.com', is_admin=True, is_active=True)
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    print('✅ Usuario admin creado con SQLAlchemy')
            except Exception as e2:
                print(f'❌ Error en SQLAlchemy: {e2}')