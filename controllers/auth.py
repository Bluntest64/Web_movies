from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        contrasena = request.form.get('contrasena', '')
        user = Usuario.verificar_contrasena(email, contrasena)
        if user:
            session['user_id'] = user['id']
            session['user_nombre'] = user['nombre']
            session['user_rol'] = user['rol']
            flash('¡Bienvenido, ' + user['nombre'] + '!', 'success')
            if user['rol'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.index'))
        flash('Correo o contraseña incorrectos.', 'error')
    return render_template('auth/login.html')


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        contrasena = request.form.get('contrasena', '')
        confirmar = request.form.get('confirmar', '')
        if not nombre or not email or not contrasena:
            flash('Todos los campos son obligatorios.', 'error')
        elif contrasena != confirmar:
            flash('Las contraseñas no coinciden.', 'error')
        elif len(contrasena) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
        else:
            try:
                Usuario.crear(nombre, email, contrasena)
                flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
                return redirect(url_for('auth.login'))
            except Exception:
                flash('El correo ya está registrado.', 'error')
    return render_template('auth/registro.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))
