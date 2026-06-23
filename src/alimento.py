from flask import Blueprint, render_template, request, redirect, url_for
from catalogo import obtener_catalogo
from extensiones import mysql
import MySQLdb.cursors

alimento_bp = Blueprint('alimento', __name__, url_prefix='/alimento')

@alimento_bp.route('/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM alimento')
    inyeccion_datos = cursor.fetchall()
    cursor.close()

    catalogo = obtener_catalogo()

    return render_template('Alimento/index.html', info=inyeccion_datos, catalogo=catalogo)

@alimento_bp.route('/agregarAlimento', methods=['POST'])
def agregarAlimento():
    id_alimento = request.form['id']
    fecha_vencimiento = request.form['fecha_vencimiento']
    lote = request.form['lote']
    tipo_alimento = request.form['tipo_alimento']
    peso_contenido = request.form['peso_contenido']
    indicacion_especifica = request.form['indicacion_especifica']

    if id_alimento and fecha_vencimiento and lote and tipo_alimento and peso_contenido:
        cursor = mysql.connection.cursor()
        sql = '''INSERT INTO alimento(id, fecha_vencimiento, lote, tipo_alimento, 
                 peso_contenido, indicacion_especifica) VALUES (%s, %s, %s, %s, %s, %s)'''
        info = (id_alimento, fecha_vencimiento, lote, tipo_alimento, peso_contenido, indicacion_especifica)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('alimento.home'))

@alimento_bp.route('/eliminarAlimento/<int:id>')
def eliminarAlimento(id):
    cursor = mysql.connection.cursor()
    sql = 'DELETE FROM alimento WHERE id = %s'
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('alimento.home'))

@alimento_bp.route('/editarAlimento/<int:id>', methods=['POST'])
def editarAlimento(id):
    fecha_vencimiento = request.form['fecha_vencimiento']
    lote = request.form['lote']
    tipo_alimento = request.form['tipo_alimento']
    peso_contenido = request.form['peso_contenido']
    indicacion_especifica = request.form['indicacion_especifica']

    if fecha_vencimiento and lote and tipo_alimento and peso_contenido:
        cursor = mysql.connection.cursor()
        sql = '''UPDATE alimento SET fecha_vencimiento = %s, lote = %s, tipo_alimento = %s, 
                 peso_contenido = %s, indicacion_especifica = %s WHERE id = %s'''
        info = (fecha_vencimiento, lote, tipo_alimento, peso_contenido, indicacion_especifica, id)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('alimento.home'))