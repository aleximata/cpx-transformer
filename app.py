from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import os
import hashlib
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# ===== CONFIGURACIÓN =====
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/cpx_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ===== BASE DE DATOS =====
db = SQLAlchemy(app)

# ===== MODELOS =====
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def get_id(self):
        return str(self.id)

class LinkHistory(db.Model):
    __tablename__ = 'link_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_link = db.Column(db.Text, nullable=False)
    transformed_link = db.Column(db.Text, nullable=False)
    pa_value = db.Column(db.String(10))
    status_changed = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ===== LOGIN MANAGER =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== FORMULARIOS =====
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarme')

class LinkTransformForm(FlaskForm):
    original_link = TextAreaField('Link Original', validators=[DataRequired()])
    submit = SubmitField('Transformar Link')

# ===== FUNCIÓN DE TRANSFORMACIÓN =====
def transformar_link(link_original):
    try:
        parsed = urlparse(link_original)
        params = parse_qs(parsed.query)
        params_clean = {k: v[0] if v else '' for k, v in params.items()}
        pa = params_clean.get('pa', '')
        transformado = False
        cambios = []
        
        if pa == '38':
            if 'status' in params_clean and params_clean['status'] != 'c':
                params_clean['status'] = 'c'
                transformado = True
                cambios.append('status: t → c')
            if 'TermedQuotaID' in params_clean:
                del params_clean['TermedQuotaID']
                transformado = True
            if 'isc' in params_clean and params_clean['isc'] != '1000':
                params_clean['isc'] = '1000'
                transformado = True
        elif pa == '30':
            if 'disposition' in params_clean and params_clean['disposition'] != '1':
                params_clean['disposition'] = '1'
                transformado = True
            if 'status' in params_clean and params_clean['status'] != '1':
                params_clean['status'] = '1'
                transformado = True
        elif pa == '43':
            if 'status' in params_clean and params_clean['status'] != '1':
                params_clean['status'] = '1'
                transformado = True
        elif pa == '16':
            if 'status' in params_clean and params_clean['status'] != 'complete':
                params_clean['status'] = 'complete'
                transformado = True
        elif pa == '41':
            if 'status' in params_clean and params_clean['status'] == 't':
                params_clean['status'] = 'c'
                transformado = True
            elif 'status' in params_clean and params_clean['status'] != 'c':
                del params_clean['status']
                transformado = True
        elif pa == '29':
            for param in ['redirect_status_position', 'qualification_term_question_id', 
                         'qualification_term_question_key', 'matched_qouta_id', 
                         'reason_id', 'trans_id', 'disqualify_reason']:
                if param in params_clean:
                    del params_clean[param]
                    transformado = True
        elif pa == '11':
            if 'status' in params_clean and params_clean['status'] == 'T':
                params_clean['status'] = 'S'
                transformado = True
            if 'id' in params_clean and params_clean['id'] == '44':
                params_clean['id'] = '10'
                transformado = True
        elif pa == '7':
            if 'status' in params_clean and params_clean['status'] == 'quality_terminate':
                params_clean['status'] = 'quality_complete'
                transformado = True
        
        nueva_query = urlencode(params_clean, doseq=False)
        nueva_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                               parsed.params, nueva_query, parsed.fragment))
        
        return {
            'original': link_original,
            'transformado': nueva_url,
            'success': transformado,
            'cambios': cambios,
            'pa': pa
        }
    except Exception as e:
        return {
            'error': str(e),
            'original': link_original,
            'transformado': link_original,
            'success': False,
            'cambios': [],
            'pa': 'error'
        }

# ===== RUTAS =====

@app.route('/')
@login_required
def index():
    form = LinkTransformForm()
    return render_template('index.html', form=form, user=current_user)

@app.route('/transform', methods=['POST'])
@login_required
def transform():
    form = LinkTransformForm()
    if form.validate_on_submit():
        link_original = form.original_link.data.strip()
        
        if 'redirect.cpx-research.com' not in link_original:
            flash('❌ El link no parece ser de CPX-Research.', 'warning')
            return redirect(url_for('index'))
        
        resultado = transformar_link(link_original)
        
        try:
            historial = LinkHistory(
                user_id=current_user.id,
                original_link=resultado['original'],
                transformed_link=resultado['transformado'],
                pa_value=resultado['pa'],
                status_changed=', '.join(resultado['cambios']) if resultado['cambios'] else 'Sin cambios'
            )
            db.session.add(historial)
            db.session.commit()
        except Exception as e:
            print(f'Error guardando historial: {e}')
            db.session.rollback()
        
        if resultado['success']:
            flash(f'✅ Link transformado: {", ".join(resultado["cambios"])}', 'success')
        else:
            flash('ℹ️ No se encontraron cambios para aplicar.', 'info')
        
        return render_template('index.html', form=form, resultado=resultado, user=current_user)
    
    return render_template('index.html', form=form, user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('❌ Tu cuenta está desactivada.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'✅ ¡Bienvenido, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('❌ Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        is_first_user = User.query.count() == 0
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=is_first_user,
            is_active=True
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        if is_first_user:
            flash('✅ ¡Eres el primer usuario! Has sido asignado como administrador.', 'success')
        else:
            flash('✅ Registro exitoso.', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 Has cerrado sesión.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    historial = LinkHistory.query.filter_by(user_id=current_user.id).order_by(LinkHistory.created_at.desc()).limit(50).all()
    return render_template('profile.html', user=current_user, historial=historial)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('❌ No tienes permisos.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin.html', users=users, user=current_user)

@app.route('/admin/user/<int:user_id>/<action>')
@login_required
def admin_user_action(user_id, action):
    if not current_user.is_admin:
        flash('❌ No tienes permisos.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('⚠️ No puedes modificar tu propio usuario.', 'warning')
        return redirect(url_for('admin'))
    
    if action == 'activate':
        user.is_active = True
        flash(f'✅ Usuario {user.username} activado.', 'success')
    elif action == 'deactivate':
        user.is_active = False
        flash(f'⚠️ Usuario {user.username} desactivado.', 'warning')
    elif action == 'make_admin':
        user.is_admin = True
        flash(f'✅ Usuario {user.username} ahora es administrador.', 'success')
    elif action == 'remove_admin':
        user.is_admin = False
        flash(f'ℹ️ Usuario {user.username} ya no es administrador.', 'info')
    else:
        flash('❌ Acción no válida.', 'danger')
    
    db.session.commit()
    return redirect(url_for('admin'))

# ===== RUTAS DE DIAGNÓSTICO =====

@app.route('/test')
def test():
    return "✅ Servidor OK"

@app.route('/init')
def init():
    try:
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@cpx.com', is_admin=True, is_active=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        return "✅ Base de datos lista"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route('/fix-db')
def fix_db():
    try:
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@cpx.com', is_admin=True, is_active=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        return "✅ Base de datos reparada"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ===== INICIALIZAR =====
def init_db():
    with app.app_context():
        try:
            db.create_all()
            print('✅ Tablas creadas')
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@cpx.com', is_admin=True, is_active=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print('✅ Admin creado')
            else:
                print('✅ Admin ya existe')
        except Exception as e:
            print(f'❌ Error: {e}')

# ===== EJECUTAR =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    init_db()
    print(f'🚀 Servidor ejecutándose en puerto {port}')
    app.run(debug=False, host='0.0.0.0', port=port)