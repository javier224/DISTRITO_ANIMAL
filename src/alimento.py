from flask import Blueprint, render_template, request, redirect, url_for
from catalogo import obtener_catalogo
from extensiones import mysql
import MySQLdb.cursors
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from src.app import db 

alimento_bp = Blueprint('alimento', __name__, url_prefix='/alimento')

@alimento_bp.route('/')
def home():
    query = text('SELECT * FROM alimento')
    result = db.session.execute(query)
    
    inyeccion_datos = [dict(row) for row in result.mappings().all()]

    catalogo = obtener_catalogo()

    return render_template('Alimento/index.html', info=inyeccion_datos, catalogo=catalogo)


@alimento_bp.route('/agregarAlimento', methods=['POST'])
def agregarAlimento():
    id_alimento = request.form.get('id')
    fecha_vencimiento = request.form.get('fecha_vencimiento')
    lote = request.form.get('lote')
    tipo_alimento = request.form.get('tipo_alimento')
    peso_contenido = request.form.get('peso_contenido')
    indicacion_especifica = request.form.get('indicacion_especifica')

    if id_alimento and fecha_vencimiento and lote and tipo_alimento and peso_contenido:
        try:
            sql = text("""
                INSERT INTO alimento (id, fecha_vencimiento, lote, tipo_alimento, peso_contenido, indicacion_especifica) 
                VALUES (:id, :fecha_vencimiento, :lote, :tipo_alimento, :peso_contenido, :indicacion_especifica)
            """)
            
            db.session.execute(sql, {
                "id": id_alimento,
                "fecha_vencimiento": fecha_vencimiento,
                "lote": lote,
                "tipo_alimento": tipo_alimento,
                "peso_contenido": peso_contenido,
                "indicacion_especifica": indicacion_especifica
            })
            
            db.session.commit()
            flash('Alimento agregado correctamente.', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al agregar alimento: {e}")
            flash('Hubo un error al guardar el alimento en la base de datos.', 'error')

    return redirect(url_for('alimento.home'))
@alimento_bp.route('/eliminarAlimento/<int:id>')
def eliminarAlimento(id):
    try:
        sql = text('DELETE FROM alimento WHERE id = :id')
        db.session.execute(sql, {"id": id})

        db.session.commit()
        flash('Alimento eliminado correctamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar alimento: {e}")
        flash('Hubo un error al intentar eliminar el alimento.', 'error')
        
    return redirect(url_for('alimento.home'))


@alimento_bp.route('/editarAlimento/<int:id>', methods=['POST'])
def editarAlimento(id):
    fecha_vencimiento = request.form.get('fecha_vencimiento')
    lote = request.form.get('lote')
    tipo_alimento = request.form.get('tipo_alimento')
    peso_contenido = request.form.get('peso_contenido')
    indicacion_especifica = request.form.get('indicacion_especifica')

    if fecha_vencimiento and lote and tipo_alimento and peso_contenido:
        try:
            sql = text("""
                UPDATE alimento 
                SET fecha_vencimiento = :fecha_vencimiento, 
                    lote = :lote, 
                    tipo_alimento = :tipo_alimento, 
                    peso_contenido = :peso_contenido, 
                    indicacion_especifica = :indicacion_especifica 
                WHERE id = :id
            """)
            
            db.session.execute(sql, {
                "fecha_vencimiento": fecha_vencimiento,
                "lote": lote,
                "tipo_alimento": tipo_alimento,
                "peso_contenido": peso_contenido,
                "indicacion_especifica": indicacion_especifica,
                "id": id
            })
            
            db.session.commit()
            flash('Alimento actualizado correctamente.', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al editar alimento: {e}")
            flash('Hubo un error al actualizar los datos en la base de datos.', 'error')
            
    return redirect(url_for('alimento.home'))