from flask import Blueprint, render_template, request, redirect, url_for
from catalogo import obtener_catalogo
from extensiones import mysql
import MySQLdb.cursors

vacuna_bp = Blueprint('vacuna', __name__, url_prefix='/vacuna')

@vacuna_bp.route('/')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM vacuna')
    inyeccion_datos = cursor.fetchall()
    cursor.close()

    catalogo = obtener_catalogo()
    
    return render_template('Vacuna/index.html', info=inyeccion_datos, catalogo=catalogo)
    
@vacuna_bp.route('/agregarVacuna', methods=['POST'])
def agregarVacuna():
    id_vacuna = request.form['id']
    descripcion = request.form['descripcion']
    laboratorio = request.form['laboratorio']
    periodo_refuerzo = request.form['periodo_refuerzo']

    if id_vacuna and descripcion and laboratorio and periodo_refuerzo:
        cursor = mysql.connection.cursor()
        sql = 'INSERT INTO vacuna (id, descripcion, laboratorio, periodo_refuerzo) VALUES (%s, %s, %s, %s)'
        info = (id_vacuna, descripcion, laboratorio, periodo_refuerzo)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('vacuna.home'))

@vacuna_bp.route('/eliminarVacuna/<int:id>')
def eliminarVacuna(id):
    cursor = mysql.connection.cursor()
    sql = 'DELETE FROM vacuna WHERE id = %s'
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('vacuna.home'))

@vacuna_bp.route('/editarVacuna/<int:id>', methods=['POST'])
def editarVacuna(id):
    descripcion = request.form['descripcion']
    laboratorio = request.form['laboratorio']
    periodo_refuerzo = request.form['periodo_refuerzo']

    if descripcion and laboratorio and periodo_refuerzo:
        cursor = mysql.connection.cursor()
        sql = 'UPDATE vacuna SET descripcion = %s, laboratorio = %s, periodo_refuerzo = %s WHERE id = %s'
        info = (descripcion, laboratorio, periodo_refuerzo, id)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('vacuna.home'))