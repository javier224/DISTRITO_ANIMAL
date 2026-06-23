from flask import Blueprint, render_template, request, redirect, url_for, flash
import MySQLdb.cursors
from extensiones import mysql

veterinario_bp = Blueprint('veterinario_bp', __name__)

@veterinario_bp.route('/Veterinario')
def veterinario():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT v.id, v.numero_licencia, v.especialidad, p.nombre_completo 
        FROM veterinario v 
        JOIN perfil p ON v.id_perfil = p.id_perfil
    """
    cursor.execute(sql)
    myresult = cursor.fetchall()
    
    cursor.execute("SELECT id_perfil, nombre_completo FROM perfil")
    perfiles = cursor.fetchall()
    
    cursor.close()
    return render_template('Veterinario/veterinario.html', data=myresult, perfiles=perfiles)

@veterinario_bp.route('/agregarVeterinario', methods=['POST'])
def addVeterinario():
    numero_licencia = request.form.get('numero_licencia')
    especialidad = request.form.get('especialidad')
    id_perfil = request.form.get('id_perfil') 
    
    if numero_licencia and especialidad and id_perfil:
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO veterinario (numero_licencia, especialidad, id_perfil) VALUES (%s, %s, %s)"
        cursor.execute(sql, (numero_licencia, especialidad, id_perfil))
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('veterinario_bp.veterinario'))

@veterinario_bp.route('/deleteVeterinario/<string:id>')
def deleteVeterinario(id):
    cursor = mysql.connection.cursor()
    sql = "DELETE FROM veterinario WHERE id=%s"
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('veterinario_bp.veterinario'))

@veterinario_bp.route('/editVeterinario/<string:id>', methods=['POST'])
def editVeterinario(id):
    numero_licencia = request.form.get('numero_licencia')
    especialidad = request.form.get('especialidad')
    
    if numero_licencia and especialidad:
        cursor = mysql.connection.cursor()
        sql = "UPDATE veterinario SET numero_licencia = %s, especialidad = %s WHERE id = %s"
        cursor.execute(sql, (numero_licencia, especialidad, id))
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('veterinario_bp.veterinario'))