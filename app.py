def init_db():
    with app.app_context():
        try:
            # Ejecutar el script de inicialización
            import subprocess
            subprocess.run(['python3', 'init_db.py'], check=True)
            print('✅ Base de datos inicializada desde init_db.py')
        except Exception as e:
            print(f'❌ Error al inicializar la base de datos: {e}')