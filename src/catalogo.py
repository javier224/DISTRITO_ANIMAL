from flask import Blueprint, render_template, request, redirect, url_for
from extensiones import mysql
import MySQLdb.cursors

catalogo_bp = Blueprint("catalogo", __name__, url_prefix="/catalogo")

@catalogo_bp.route('/insertarCatalogo')
def insertarCatalogo():
    return render_template('Catalogo/crear.html')

def obtener_catalogo():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM catalogo")
    resultado = cursor.fetchall()
    cursor.close()
    return resultado

@catalogo_bp.route('/')
def home():
    info = obtener_catalogo()
    return render_template('Catalogo/index.html', info=info)

@catalogo_bp.route('/agregarCatalogo', methods=['POST'])
def agregarCatalogo():
    nombre = request.form['nombre']
    precio = request.form['precio']
    stock = request.form['stock']
    opcionCatalogo = request.form['opcionCatalogo']

    if nombre and precio and stock and opcionCatalogo:
        cursor = mysql.connection.cursor()
        sql = 'INSERT INTO catalogo (nombre, precio, tipo_item, stock) VALUES (%s, %s, %s, %s)'
        info = (nombre, precio, opcionCatalogo, stock)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('catalogo.home'))

@catalogo_bp.route('/eliminarCatalogo/<int:id>')
def eliminarCatalogo(id):
    cursor = mysql.connection.cursor()
    sql = 'DELETE FROM catalogo WHERE id = %s'
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('catalogo.home'))

@catalogo_bp.route('/formularioEditar/<int:id>', methods=['GET'])
def formularioEditar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM catalogo WHERE id = %s", (id,))
    resultado = cursor.fetchone()
    cursor.close()
    return render_template('Catalogo/editar.html', info=resultado)

@catalogo_bp.route('/editarCatalogo/<int:id>', methods=['POST'])
def editarCatalogo(id):
    nombre = request.form['nombre']
    precio = request.form['precio']
    stock = request.form['stock']
    opcionCatalogo = request.form['opcionCatalogo']

    if nombre and precio and stock and opcionCatalogo:
        cursor = mysql.connection.cursor()
        sql = "UPDATE catalogo SET nombre = %s, precio = %s, tipo_item = %s, stock = %s WHERE id = %s"
        info = (nombre, precio, opcionCatalogo, stock, id)
        cursor.execute(sql, info)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('catalogo.home'))