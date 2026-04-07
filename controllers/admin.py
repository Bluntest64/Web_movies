from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.pelicula import Pelicula
from models.funcion import Funcion
from models.asiento import Asiento
from models.tiquete import Tiquete
from models.usuario import Usuario
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión.', 'error')
            return redirect(url_for('auth.login'))
        if session.get('user_rol') != 'admin':
            flash('Acceso restringido a administradores.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ──────────────────────────────────────────────
@admin_bp.route('/')
@admin_required
def dashboard():
    total_ventas = Tiquete.total_ventas()
    funciones = Funcion.listar()
    ventas_dia = Tiquete.ventas_por_dia()
    peliculas_top = Pelicula.mas_vistas()
    tiquetes_recientes = Tiquete.listar_todos()[:10]
    return render_template('admin/dashboard.html',
        total_ventas=total_ventas,
        funciones=funciones,
        ventas_dia=ventas_dia,
        peliculas_top=peliculas_top,
        tiquetes_recientes=tiquetes_recientes
    )


# ── Películas ───────────────────────────────────────────────
@admin_bp.route('/peliculas')
@admin_required
def peliculas():
    lista = Pelicula.listar()
    return render_template('admin/peliculas.html', peliculas=lista)


@admin_bp.route('/peliculas/nueva', methods=['GET', 'POST'])
@admin_required
def pelicula_nueva():
    if request.method == 'POST':
        try:
            Pelicula.crear(
                titulo=request.form['titulo'].strip(),
                descripcion=request.form.get('descripcion', ''),
                duracion=int(request.form['duracion']),
                genero=request.form.get('genero', ''),
                clasificacion=request.form.get('clasificacion', ''),
                imagen_url=request.form.get('imagen_url', ''),
                trailer_url=request.form.get('trailer_url', ''),
                estado=request.form.get('estado', 'activa')
            )
            flash('Película creada correctamente.', 'success')
            return redirect(url_for('admin.peliculas'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('admin/pelicula_form.html', pelicula=None, accion='Crear')


@admin_bp.route('/peliculas/<int:pid>/editar', methods=['GET', 'POST'])
@admin_required
def pelicula_editar(pid):
    pelicula = Pelicula.buscar_por_id(pid)
    if not pelicula:
        flash('Película no encontrada.', 'error')
        return redirect(url_for('admin.peliculas'))
    if request.method == 'POST':
        try:
            Pelicula.actualizar(
                pid=pid,
                titulo=request.form['titulo'].strip(),
                descripcion=request.form.get('descripcion', ''),
                duracion=int(request.form['duracion']),
                genero=request.form.get('genero', ''),
                clasificacion=request.form.get('clasificacion', ''),
                imagen_url=request.form.get('imagen_url', ''),
                trailer_url=request.form.get('trailer_url', ''),
                estado=request.form.get('estado', 'activa')
            )
            flash('Película actualizada.', 'success')
            return redirect(url_for('admin.peliculas'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('admin/pelicula_form.html', pelicula=pelicula, accion='Editar')


@admin_bp.route('/peliculas/<int:pid>/eliminar', methods=['POST'])
@admin_required
def pelicula_eliminar(pid):
    try:
        Pelicula.eliminar(pid)
        flash('Película eliminada.', 'success')
    except Exception:
        flash('No se puede eliminar: tiene funciones asociadas.', 'error')
    return redirect(url_for('admin.peliculas'))


# ── Funciones ───────────────────────────────────────────────
@admin_bp.route('/funciones')
@admin_required
def funciones():
    lista = Funcion.listar()
    return render_template('admin/funciones.html', funciones=lista)


@admin_bp.route('/funciones/nueva', methods=['GET', 'POST'])
@admin_required
def funcion_nueva():
    peliculas = Pelicula.listar(solo_activas=True)
    if request.method == 'POST':
        try:
            Funcion.crear(
                pelicula_id=int(request.form['pelicula_id']),
                fecha=request.form['fecha'],
                hora=request.form['hora'],
                sala=request.form.get('sala', 'Sala 1'),
                precio=float(request.form['precio']),
                estado=request.form.get('estado', 'disponible')
            )
            flash('Función creada correctamente.', 'success')
            return redirect(url_for('admin.funciones'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('admin/funcion_form.html', funcion=None, peliculas=peliculas, accion='Crear')


@admin_bp.route('/funciones/<int:fid>/editar', methods=['GET', 'POST'])
@admin_required
def funcion_editar(fid):
    funcion = Funcion.buscar_por_id(fid)
    peliculas = Pelicula.listar(solo_activas=True)
    if not funcion:
        flash('Función no encontrada.', 'error')
        return redirect(url_for('admin.funciones'))
    if request.method == 'POST':
        try:
            Funcion.actualizar(
                fid=fid,
                pelicula_id=int(request.form['pelicula_id']),
                fecha=request.form['fecha'],
                hora=request.form['hora'],
                sala=request.form.get('sala', 'Sala 1'),
                precio=float(request.form['precio']),
                estado=request.form.get('estado', 'disponible')
            )
            flash('Función actualizada.', 'success')
            return redirect(url_for('admin.funciones'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('admin/funcion_form.html', funcion=funcion, peliculas=peliculas, accion='Editar')


@admin_bp.route('/funciones/<int:fid>/eliminar', methods=['POST'])
@admin_required
def funcion_eliminar(fid):
    try:
        Funcion.eliminar(fid)
        flash('Función eliminada.', 'success')
    except Exception:
        flash('No se puede eliminar: tiene tiquetes vendidos.', 'error')
    return redirect(url_for('admin.funciones'))


@admin_bp.route('/funciones/<int:fid>/asientos')
@admin_required
def funcion_asientos(fid):
    funcion = Funcion.buscar_por_id(fid)
    asientos = Asiento.listar_con_estado_funcion(fid)
    ocupacion = Funcion.ocupacion(fid)
    return render_template('admin/funcion_asientos.html',
        funcion=funcion, asientos=asientos, ocupacion=ocupacion)


# ── Tiquetes ─────────────────────────────────────────────────
@admin_bp.route('/tiquetes')
@admin_required
def tiquetes():
    lista = Tiquete.listar_todos()
    return render_template('admin/tiquetes.html', tiquetes=lista)


@admin_bp.route('/tiquetes/<int:tid>')
@admin_required
def tiquete_detalle(tid):
    tiquete = Tiquete.buscar_por_id(tid)
    asientos = Tiquete.detalle_asientos(tid)
    return render_template('admin/tiquete_detalle.html', tiquete=tiquete, asientos=asientos)


# ── Usuarios ─────────────────────────────────────────────────
@admin_bp.route('/usuarios')
@admin_required
def usuarios():
    lista = Usuario.listar()
    return render_template('admin/usuarios.html', usuarios=lista)
