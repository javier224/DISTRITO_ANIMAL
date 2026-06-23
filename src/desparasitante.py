from flask import Blueprint, render_template, request, redirect, url_for
from catalogo import obtener_catalogo
from extensiones import mysql
import MySQLdb.cursors

desparasitante_bp = Blueprint('desparasitante', __name__, url_prefix='/desparasitante')

@desparasitante_bp.route('/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM desparasitante')
    inyeccion_datos = cursor.fetchall()
    cursor.close()
    
    catalogo = obtener_catalogo()

    return render_template('Desparasitante/index.html', info=inyeccion_datos, catalogo=catalogo)

@desparasitante_bp.route('/agregarDesparasitante', methods=['POST'])
def agregarDesparasitante():
    id_desparasitante = request.form['id']
    descripcion = request.form['descripcion']
    via_administracion = request.form['via_administracion']
    rango_peso = request.form['rango_peso']

    if id_desparasitante and descripcion and via_administracion and rango_peso:
        cursor = mysql.connection.cursor()
        sql = 'INSERT INTO desparasitante(id, descripcion, via_administracion, rango_peso) VALUES (%s, %s, %s, %s)'
        info = (id_desparasitante, descripcion, via_administracion, rango_peso)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('desparasitante.home'))

@desparasitante_bp.route('/eliminarDesparasitante/<int:id>')
def eliminarDesparasitante(id):
    cursor = mysql.connection.cursor()
    sql = 'DELETE FROM desparasitante WHERE id = %s'
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('desparasitante.home'))

@desparasitante_bp.route('/editarDesparasitante/<int:id>', methods=['POST'])
def editarDesparasitante(id):
    descripcion = request.form['descripcion']
    via_administracion = request.form['via_administracion']
    rango_peso = request.form['rango_peso']

    if descripcion and via_administracion and rango_peso:
        cursor = mysql.connection.cursor()
        sql = 'UPDATE desparasitante SET descripcion = %s, via_administracion = %s, rango_peso = %s WHERE id = %s'
        info = (descripcion, via_administracion, rango_peso, id)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('desparasitante.home'))