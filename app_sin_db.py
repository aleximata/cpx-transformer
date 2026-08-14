from flask import Flask
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-12345'

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def home():
    return "✅ app.py sin base de datos funcionando"

@app.route('/test')
def test():
    return "✅ Test OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f'🚀 Servidor ejecutándose en puerto {port}')
    app.run(debug=False, host='0.0.0.0', port=port)