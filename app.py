from flask import Flask, session
from config import Config
from controllers.auth import auth_bp
from controllers.main import main_bp
from controllers.admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)


@app.context_processor
def inject_user():
    """Inyecta datos del usuario en todos los templates"""
    return {
        'current_user': {
            'id': session.get('user_id'),
            'nombre': session.get('user_nombre'),
            'rol': session.get('user_rol'),
            'is_authenticated': 'user_id' in session,
            'is_admin': session.get('user_rol') == 'admin'
        }
    }


@app.template_filter('currency')
def currency_filter(value):
    try:
        return f"${float(value):,.0f}"
    except (ValueError, TypeError):
        return value


@app.template_filter('duracion')
def duracion_filter(minutos):
    try:
        h = int(minutos) // 60
        m = int(minutos) % 60
        if h:
            return f"{h}h {m:02d}min"
        return f"{m}min"
    except Exception:
        return f"{minutos} min"


if __name__ == '__main__':
    app.run(debug=Config.DEBUG)
