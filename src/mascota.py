from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import MySQLdb.cursors
from extensiones import mysql

mascota_bp = Blueprint('mascota_bp', __name__)

@mascota_bp.route('/Mascota')
def mascota():
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    rol_usuario = session.get('rol')
    id_usuario = session.get('id_usuario')
    
    # 1. FILTRADO SEGÚN TU REGLA DE NEGOCIO
    if rol_usuario == 'Cliente':
        # Buscamos primero el id_perfil del cliente usando su fk_usuario
        cursor.execute("SELECT id_perfil FROM perfil WHERE fk_usuario = %s", (id_usuario,))
        perfil = cursor.fetchone()
        
        if perfil:
            # Traemos única y exclusivamente sus mascotas
            sql_mascotas = """
                SELECT m.*, p.nombre_completo AS nombre_dueno 
                FROM mascota m 
                JOIN perfil p ON m.id_dueno = p.id_perfil
                WHERE m.id_dueno = %s
            """
            cursor.execute(sql_mascotas, (perfil['id_perfil'],))
            mascotas = cursor.fetchall()
            
            # Pasamos su perfil único para usarlo en el HTML al registrar
            perfiles = [perfil]
        else:
            mascotas = []
            perfiles = []
    else:
        # Administrador y Veterinario ven la lista general de mascotas y perfiles
        sql_mascotas = """
            SELECT m.*, p.nombre_completo AS nombre_dueno 
            FROM mascota m 
            JOIN perfil p ON m.id_dueno = p.id_perfil
        """
        cursor.execute(sql_mascotas)
        mascotas = cursor.fetchall()
        
        cursor.execute("SELECT id_perfil, nombre_completo FROM perfil")
        perfiles = cursor.fetchall()
        
    cursor.close()
    
    return render_template('Mascota/mascota.html', data=mascotas, perfiles=perfiles)


@mascota_bp.route('/agregarMascota', methods=['POST'])
def addMascota():
    nombre = request.form.get('nombre')
    especie = request.form.get('especie')
    raza = request.form.get('raza')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    genero = request.form.get('genero')
    color = request.form.get('color')
    peso = request.form.get('peso')
    observaciones = request.form.get('observaciones')
    id_dueno = request.form.get('id_dueno')  # Se recibe del select o del input oculto
    
    if nombre and id_dueno:
        cursor = mysql.connection.cursor()
        sql = """INSERT INTO mascota 
                (nombre, especie, raza, fecha_nacimiento, genero, color, peso, observaciones, id_dueno) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        data = (nombre, especie, raza, fecha_nacimiento, genero, color, peso, observaciones, id_dueno)
        cursor.execute(sql, data)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('mascota_bp.mascota'))
@mascota_bp.route('/deleteMascota/<string:id>')
def deleteMascota(id):
    cursor = mysql.connection.cursor()
    sql = "DELETE FROM mascota WHERE id=%s"
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('mascota_bp.mascota'))

@mascota_bp.route('/editMascota/<string:id>', methods=['POST'])
def editmascota(id):
    # En el modal de edición solo solemos cambiar datos físicos de la mascota
    peso = request.form.get('peso')
    observaciones = request.form.get('observaciones')
    
    cursor = mysql.connection.cursor()
    # Mantenemos el nombre y dueño fijos, actualizamos lo demás
    sql = """UPDATE mascota SET 
            peso = %s, observaciones = %s 
            WHERE id = %s"""
    cursor.execute(sql, (peso, observaciones, id))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('mascota_bp.mascota'))