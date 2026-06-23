from flask import Blueprint, render_template, request, redirect, url_for
from catalogo import obtener_catalogo
from extensiones import mysql
import MySQLdb.cursors

servicio_bp = Blueprint("servicio", __name__, url_prefix="/servicio")

def nombre_Catalogo(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT c.nombre AS nombre_item_catalogo FROM servicio s INNER JOIN catalogo c ON s.id = c.id WHERE s.id = %s', (id,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado[0] if resultado else None

@servicio_bp.route('/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM servicio")
    inyeccion_datos = cursor.fetchall()
    cursor.close()

    catalogo = obtener_catalogo()

    fk_nombre_catalogo = request.args.get('fk_nombre_catalogo')

    return render_template('Servicio/index.html', info=inyeccion_datos, catalogo=catalogo, fk_nombre_catalogo=fk_nombre_catalogo)

@servicio_bp.route('/agregarServicio', methods=['POST'])
def agregarServicio():
    id_servicio = request.form['id']
    descripcion = request.form['descripcion']
    duracion_estimada = request.form['duracion_estimada']
    
    if id_servicio and descripcion and duracion_estimada:
        cursor = mysql.connection.cursor()
        sql = 'INSERT INTO servicio (id, descripcion, duracion_estimada) VALUES (%s, %s, %s)'
        info = (id_servicio, descripcion, duracion_estimada)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('servicio.home'))

@servicio_bp.route('/eliminarServicio/<int:id>')
def eliminarServicio(id):
    cursor = mysql.connection.cursor()
    sql = 'DELETE FROM servicio WHERE id = %s'
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('servicio.home'))

@servicio_bp.route('/editarServicio/<int:id>', methods=['POST'])
def editarServicio(id):
    descripcion = request.form['descripcion']
    duracion_estimada = request.form['duracion_estimada']

    if descripcion and duracion_estimada:
        cursor = mysql.connection.cursor()
        sql = "UPDATE servicio SET descripcion = %s, duracion_estimada = %s WHERE id = %s"
        info = (descripcion, duracion_estimada, id)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
        
        fk_nombre_catalogo = nombre_Catalogo(id)
        return redirect(url_for('servicio.home', fk_nombre_catalogo=fk_nombre_catalogo))
    
    return redirect(url_for('servicio.home'))