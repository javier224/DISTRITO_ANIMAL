from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from models import db  

catalogo_bp = Blueprint("catalogo", __name__, url_prefix="/catalogo")

@catalogo_bp.route('/insertarCatalogo')
def insertarCatalogo():
    return render_template('Catalogo/crear.html')

def obtener_catalogo():
    query = text("SELECT * FROM catalogo")
    result = db.session.execute(query)
    return [dict(row) for row in result.mappings().all()]


@catalogo_bp.route('/')
def home():
    info = obtener_catalogo()
    return render_template('Catalogo/index.html', info=info)


@catalogo_bp.route('/agregarCatalogo', methods=['POST'])
def agregarCatalogo():
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    stock = request.form.get('stock')
    opcionCatalogo = request.form.get('opcionCatalogo')

    if nombre and precio and stock and opcionCatalogo:
        try:
            sql = text("""
                INSERT INTO catalogo (nombre, precio, tipo_item, stock) 
                VALUES (:nombre, :precio, :tipo_item, :stock)
            """)
            db.session.execute(sql, {
                "nombre": nombre,
                "precio": precio,
                "tipo_item": opcionCatalogo,
                "stock": stock
            })
            db.session.commit()
            flash('Item agregado al catálogo correctamente.', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error al agregar catálogo: {e}")
            flash('Error al guardar en el catálogo.', 'error')
            
    return redirect(url_for('catalogo.home'))


@catalogo_bp.route('/eliminarCatalogo/<int:id>')
def eliminarCatalogo(id):
    try:
        sql = text('DELETE FROM catalogo WHERE id = :id')
        db.session.execute(sql, {"id": id})
        db.session.commit()
        flash('Item eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar catálogo: {e}")
        flash('No se pudo eliminar el item.', 'error')
        
    return redirect(url_for('catalogo.home'))


@catalogo_bp.route('/formularioEditar/<int:id>', methods=['GET'])
def formularioEditar(id):
    query = text("SELECT * FROM catalogo WHERE id = :id")
    result = db.session.execute(query, {"id": id}).mappings().first()
    
    resultado = dict(result) if result else None
    return render_template('Catalogo/editar.html', info=resultado)


@catalogo_bp.route('/editarCatalogo/<int:id>', methods=['POST'])
def editarCatalogo(id):
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    stock = request.form.get('stock')
    opcionCatalogo = request.form.get('opcionCatalogo')

    if nombre and precio and stock and opcionCatalogo:
        try:
            sql = text("""
                UPDATE catalogo 
                SET nombre = :nombre, precio = :precio, tipo_item = :tipo_item, stock = :stock 
                WHERE id = :id
            """)
            db.session.execute(sql, {
                "nombre": nombre,
                "precio": precio,
                "tipo_item": opcionCatalogo,
                "stock": stock,
                "id": id
            })
            db.session.commit()
            flash('Catálogo actualizado correctamente.', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error al editar catálogo: {e}")
            flash('Error al actualizar el catálogo.', 'error')
            
    return redirect(url_for('catalogo.home'))