from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.pelicula import Pelicula
from models.funcion import Funcion
from models.asiento import Asiento
from models.tiquete import Tiquete
from functools import wraps

main_bp = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@main_bp.route('/')
def index():
    peliculas = Pelicula.listar(solo_activas=True)
    funciones = Funcion.listar(solo_disponibles=True)
    return render_template('index.html', peliculas=peliculas, funciones=funciones)


@main_bp.route('/cartelera')
def cartelera():
    peliculas = Pelicula.listar(solo_activas=True)
    return render_template('cartelera.html', peliculas=peliculas)


@main_bp.route('/pelicula/<int:pid>')
def pelicula_detalle(pid):
    pelicula = Pelicula.buscar_por_id(pid)
    if not pelicula:
        flash('Película no encontrada.', 'error')
        return redirect(url_for('main.cartelera'))
    funciones = Funcion.listar(pelicula_id=pid, solo_disponibles=True)
    return render_template('movies/detalle.html', pelicula=pelicula, funciones=funciones)


@main_bp.route('/funcion/<int:fid>/asientos')
def asientos(fid):
    funcion = Funcion.buscar_por_id(fid)
    if not funcion:
        flash('Función no encontrada.', 'error')
        return redirect(url_for('main.cartelera'))
    asientos = Asiento.listar_con_estado_funcion(fid)
    return render_template('functions/asientos.html', funcion=funcion, asientos=asientos)


@main_bp.route('/api/funcion/<int:fid>/asientos')
def api_asientos(fid):
    asientos = Asiento.listar_con_estado_funcion(fid)
    return jsonify([dict(a) for a in asientos])


@main_bp.route('/comprar', methods=['POST'])
@login_required
def comprar():
    funcion_id = request.form.get('funcion_id', type=int)
    asiento_ids = request.form.getlist('asiento_ids', type=int)
    if not funcion_id or not asiento_ids:
        flash('Debes seleccionar al menos un asiento.', 'error')
        return redirect(url_for('main.cartelera'))
    funcion = Funcion.buscar_por_id(funcion_id)
    if not funcion:
        flash('Función no válida.', 'error')
        return redirect(url_for('main.cartelera'))
    try:
        resultado = Tiquete.comprar(
            funcion_id=funcion_id,
            asiento_ids=asiento_ids,
            usuario_id=session['user_id'],
            precio_unitario=float(funcion['precio'])
        )
        flash('¡Compra exitosa!', 'success')
        return redirect(url_for('main.tiquete_detalle', tid=resultado['id']))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.asientos', fid=funcion_id))
    except Exception as e:
        flash('Error al procesar la compra. Intenta de nuevo.', 'error')
        return redirect(url_for('main.asientos', fid=funcion_id))


@main_bp.route('/tiquete/<int:tid>')
@login_required
def tiquete_detalle(tid):
    tiquete = Tiquete.buscar_por_id(tid)
    if not tiquete or (tiquete['usuario_id'] != session['user_id'] and session.get('user_rol') != 'admin'):
        flash('Tiquete no encontrado o sin acceso.', 'error')
        return redirect(url_for('main.mis_tiquetes'))
    asientos = Tiquete.detalle_asientos(tid)
    return render_template('tickets/detalle.html', tiquete=tiquete, asientos=asientos)


@main_bp.route('/mis-tiquetes')
@login_required
def mis_tiquetes():
    tiquetes = Tiquete.listar_por_usuario(session['user_id'])
    return render_template('tickets/mis_tiquetes.html', tiquetes=tiquetes)


@main_bp.route('/validar', methods=['GET', 'POST'])
def validar():
    resultado = None
    tiquete = None
    asientos = None
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip().upper()
        if codigo:
            tiquete, estado = Tiquete.validar(codigo)
            resultado = estado
            if tiquete:
                asientos = Tiquete.detalle_asientos(tiquete['id'])
    return render_template('tickets/validar.html', resultado=resultado, tiquete=tiquete, asientos=asientos)
