from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime

from config import Config
from models import db, User, LinkHistory
from forms import LoginForm, RegisterForm, LinkTransformForm
from transform import transformar_link

# Crear la aplicación
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar la base de datos
db.init_app(app)

# Configurar Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicia sesión para continuar.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
            print(f'Error: {e}')
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
            flash('✅ Registro exitoso. Espera a que un administrador active tu cuenta.', 'success')
        
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

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# ===== INICIALIZAR BASE DE DATOS =====
def init_db():
    with app.app_context():
        db.create_all()
        
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@cpx.com')
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            admin_user = User(
                username='admin',
                email=admin_email,
                is_admin=True,
                is_active=True
            )
            admin_user.set_password(app.config.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin_user)
            db.session.commit()
            print('✅ Usuario administrador creado')
            print(f'   Email: {admin_email}')
            print(f'   Contraseña: {app.config.get("ADMIN_PASSWORD", "admin123")}')

# ===== EJECUTAR =====
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)