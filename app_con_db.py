from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/prueba.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

@app.route('/')
def home():
    return "✅ app con DB funcionando"

@app.route('/init')
def init():
    try:
        db.create_all()
        return "✅ Base de datos creada"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route('/test')
def test():
    return "✅ Test OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f'🚀 Servidor ejecutándose en puerto {port}')
    app.run(debug=False, host='0.0.0.0', port=port)