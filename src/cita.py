from flask import Blueprint, render_template, request, redirect, session, url_for, flash, jsonify
import MySQLdb.cursors
from datetime import datetime, timedelta
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from extensiones import mysql

cita_bp = Blueprint('cita_bp', __name__)

# ==========================================
# 1. RUTA PARA CONFIRMAR LA CITA (CLIENTE)
# ==========================================
@cita_bp.route('/confirmar/<int:id_cita>')
def confirmar_cita_cliente(id_cita):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    sql_info = """
        SELECT c.inicio, m.nombre AS nombre_mascota, p.nombre_completo AS nombre_veterinario
        FROM cita c
        JOIN mascota m ON c.id_mascota = m.id
        JOIN veterinario v ON c.id_veterinario = v.id
        JOIN perfil p ON v.id_perfil = p.id_perfil
        WHERE c.id = %s
    """
    cursor.execute(sql_info, (id_cita,))
    datos = cursor.fetchone()

    if datos:
        sql_update = "UPDATE cita SET estado = 'CONFIRMADA' WHERE id = %s"
        cursor.execute(sql_update, (id_cita,))
        mysql.connection.commit()
        cursor.close()

        fecha_obj = datos['inicio']
        
        return render_template('Cita/confirmacionCita.html', 
                            fecha=fecha_obj.strftime('%d de %B, %Y'),
                            hora=fecha_obj.strftime('%I:%M %p'),
                            mascota=datos['nombre_mascota'],
                            veterinario=datos['nombre_veterinario'])
    
    cursor.close()
    return "<h1>Error: Cita no encontrada</h1>", 404


# ==========================================
# 2. VISTA GENERAL DE CITAS
# ==========================================
@cita_bp.route('/Cita')
def cita():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT c.id, c.inicio, c.fin, c.motivo, c.estado, 
        m.nombre AS nombre_mascota, 
        p.nombre_completo AS nombre_veterinario
        FROM cita c
        JOIN mascota m ON c.id_mascota = m.id
        JOIN veterinario v ON c.id_veterinario = v.id
        JOIN perfil p ON v.id_perfil = p.id_perfil
    """
    cursor.execute(sql)
    myresult = cursor.fetchall()
    cursor.close()
    return render_template('Cita/cita.html', data=myresult)


# ==========================================
# 3. MÉTODO AGREGAR CITA Y ENVIAR SENDGRID
# ==========================================
@cita_bp.route('/agregarCita', methods=['POST'])
def addCita():
    id_mascota = request.form.get('id_mascota')
    id_veterinario = request.form.get('id_veterinario')
    inicio_str = request.form.get('inicio')
    fin_str = request.form.get('fin')
    motivo = request.form.get('motivo')
    correo_cliente = request.form.get('correo_cliente') 
    estado = 'PENDIENTE' 

    ahora = datetime.now()
    fecha_inicio = datetime.strptime(inicio_str, '%Y-%m-%dT%H:%M')
    fecha_fin = datetime.strptime(fin_str, '%Y-%m-%dT%H:%M')
    
    # Validaciones de horario corporativo
    if fecha_inicio < ahora:
        flash("No puedes agendar citas en fechas pasadas.", "danger")
        return redirect(url_for('cita_bp.formulario_cita')) 

    if fecha_inicio.hour < 8 or fecha_fin.hour > 18:
        flash("El horario de atención es de 08:00 a 18:00.", "info")
        return redirect(url_for('cita_bp.formulario_cita'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Validación de cruce de horarios para el veterinario elegido
    sql_cruce = "SELECT id FROM cita WHERE id_veterinario = %s AND (%s < fin AND %s > inicio)"
    cursor.execute(sql_cruce, (id_veterinario, inicio_str, fin_str))
    if cursor.fetchone():
        cursor.close()
        flash("El veterinario ya tiene una cita en ese horario.", "danger")
        return redirect(url_for('cita_bp.formulario_cita'))

    # Guardado de la cita en la base de datos
    sql_insert = "INSERT INTO cita (inicio, fin, motivo, estado, id_mascota, id_veterinario) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql_insert, (inicio_str, fin_str, motivo, estado, id_mascota, id_veterinario))
    mysql.connection.commit()
    
    # Envío transaccional del correo de confirmación
    try:
        id_nueva_cita = cursor.lastrowid 
        api_key = os.environ.get('SENDGRID_API_KEY')
        
        if not api_key:
            flash("Cita guardada, pero el servidor no tiene configurada la llave de SendGrid.", "warning")
        else:
            # Enlace apuntando al dominio de producción en Render
            enlace_confirmacion = f"https://distrito-animal.onrender.com/confirmar/{id_nueva_cita}"
            fecha_correo = fecha_inicio.strftime('%d/%m/%Y a las %I:%M %p')

            contenido_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #006400; text-align: center;">¡Tu cita ha sido agendada! 🐾</h2>
                <p>Gracias por confiar en <strong>Distrito Animal</strong>. Hemos registrado tu solicitud médica para el día <strong>{fecha_correo}</strong>.</p>
                <p>Para confirmar tu asistencia y asegurar el espacio con el especialista, por favor presiona el siguiente botón:</p>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{enlace_confirmacion}" style="background-color: #006400; color: white; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 5px; display: inline-block;">
                        Confirmar Asistencia
                    </a>
                </p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 0.85em; color: #777; text-align: center;">Si no solicitaste este servicio, puedes ignorar este mensaje.</p>
            </div>
            """

            message = Mail(
                from_email='distritoanimal2011@gmail.com', # Cuenta verificada Single Sender
                to_emails=correo_cliente,
                subject="Confirma tu cita en Distrito Animal 🐾",
                html_content=contenido_html
            )

            sg = SendGridAPIClient(api_key)
            sg.send(message)
            flash("Cita registrada y correo de confirmación enviado exitosamente.", "success")

    except Exception as e:
        print(f"❌ Error al despachar correo individual SendGrid: {e}")
        flash(f"Cita guardada en el sistema, pero ocurrió un problema al notificar por correo: {str(e)}", "warning")

    cursor.close()
    return redirect(url_for('cita_bp.cita'))

#Metodo eliminar cita

@cita_bp.route('/deleteCita/<string:id>')
def deleteCita(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM cita WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('cita_bp.cita'))



#Metodo editar cita

@cita_bp.route('/editCita/<int:id>', methods=['POST'])
def editcita(id):
    id_mascota = request.form.get('id_mascota')
    id_veterinario = request.form.get('id_veterinario')
    inicio_str = request.form.get('inicio')
    fin_str = request.form.get('fin')
    motivo = request.form.get('motivo')
    estado = request.form.get('estado')

    ahora = datetime.now()
    fecha_inicio = datetime.strptime(inicio_str, '%Y-%m-%dT%H:%M')
    fecha_fin = datetime.strptime(fin_str, '%Y-%m-%dT%H:%M')
    limite_futuro = ahora + timedelta(days=120)

    if fecha_inicio < ahora:
        flash("No puedes mover una cita a una fecha pasada.", "danger")
        return redirect(url_for('cita_bp.formulario_editar_cita', id=id))

    if fecha_inicio > limite_futuro:
        flash("No puedes agendar a más de 4 meses de futuro.", "warning")
        return redirect(url_for('cita_bp.formulario_editar_cita', id=id))

    if fecha_inicio.hour < 8 or fecha_fin.hour > 18:
        flash("El horario de atención es de 08:00 a 18:00.", "info")
        return redirect(url_for('cita_bp.formulario_editar_cita', id=id))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql_cruce = """
        SELECT id FROM cita 
        WHERE id_veterinario = %s 
        AND (%s < fin AND %s > inicio)
        AND id != %s
    """
    cursor.execute(sql_cruce, (id_veterinario, inicio_str, fin_str, id))
    if cursor.fetchone():
        cursor.close()
        flash("Ese veterinario ya tiene otra cita en ese horario.", "danger")
        return redirect(url_for('cita_bp.formulario_editar_cita', id=id))

    fecha_solo_dia = fecha_inicio.strftime('%Y-%m-%d')
    sql_limite = "SELECT COUNT(*) AS total FROM cita WHERE id_veterinario = %s AND DATE(inicio) = %s AND id != %s"
    cursor.execute(sql_limite, (id_veterinario, fecha_solo_dia, id))
    total_hoy = cursor.fetchone()['total']
    
    if total_hoy >= 8:
        cursor.close()
        flash("Cupo lleno para este veterinario en esa fecha (Máx 8).", "warning")
        return redirect(url_for('cita_bp.formulario_editar_cita', id=id))

    sql_update = """
        UPDATE cita 
        SET inicio=%s, fin=%s, motivo=%s, estado=%s, id_mascota=%s, id_veterinario=%s 
        WHERE id=%s
    """
    cursor.execute(sql_update, (inicio_str, fin_str, motivo, estado, id_mascota, id_veterinario, id))
    mysql.connection.commit()
    cursor.close()

    flash("Cita actualizada correctamente.", "success")
    return redirect(url_for('cita_bp.cita'))



#Vista calendario

@cita_bp.route('/api/eventos')
def api_eventos():
    if not session.get('loggedin'):
        return jsonify([])

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    rol_usuario = session.get('rol')
    id_usuario = session.get('id_usuario')
    
    if rol_usuario == 'Cliente':
        cursor.execute("SELECT id_perfil FROM perfil WHERE fk_usuario = %s", (id_usuario,))
        perfil = cursor.fetchone()
        
        if perfil:
            sql = """
                SELECT c.id, c.inicio, c.fin, c.motivo, c.estado 
                FROM cita c
                JOIN mascota m ON c.id_mascota = m.id
                WHERE m.id_dueno = %s
            """
            cursor.execute(sql, (perfil['id_perfil'],))
            citas = cursor.fetchall()
        else:
            citas = []  
    else:
        sql = "SELECT id, inicio, fin, motivo, estado FROM cita"
        cursor.execute(sql)
        citas = cursor.fetchall()
        
    cursor.close()

    eventos = []
    for c in citas:
        if c['estado'] == 'CONFIRMADA':
            color_evento = '#198754'  
        elif c['estado'] == 'CANCELADA':
            color_evento = '#dc3545'  
        else:
            color_evento = '#ffc107' 

        eventos.append({
            'id': c['id'],
            'title': f"Cita - {c['estado']}",
            'start': c['inicio'].isoformat() if hasattr(c['inicio'], 'isoformat') else str(c['inicio']),
            'end': c['fin'].isoformat() if hasattr(c['fin'], 'isoformat') else str(c['fin']),
            'color': color_evento,
            'extendedProps': {
                'motivo': c['motivo'],
                'estado': c['estado']
            }
        })

    return jsonify(eventos)


#Formulario agregar cita

@cita_bp.route('/Cita/nuevo')
def formulario_cita():
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    rol_usuario = session.get('rol')
    id_usuario = session.get('id_usuario')

    if rol_usuario == 'Cliente':
        cursor.execute("SELECT id_perfil FROM perfil WHERE fk_usuario = %s", (id_usuario,))
        perfil = cursor.fetchone()
        
        if perfil:
            cursor.execute("SELECT id, nombre FROM mascota WHERE id_dueno = %s", (perfil['id_perfil'],))
            mascotas_db = cursor.fetchall()
        else:
            mascotas_db = [] 
    else:
        cursor.execute("SELECT id, nombre FROM mascota")
        mascotas_db = cursor.fetchall() 
    
    sql_vets = """
        SELECT v.id, p.nombre_completo 
        FROM veterinario v 
        JOIN perfil p ON v.id_perfil = p.id_perfil
    """
    cursor.execute(sql_vets)
    vets_db = cursor.fetchall()
    
    cursor.close()
    
    return render_template('Cita/addCita.html', 
                        mascotas=mascotas_db, 
                        veterinarios=vets_db)



#Formulario editar cita
    

@cita_bp.route('/Cita/editar/<int:id>')
def formulario_editar_cita(id):
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    rol_usuario = session.get('rol')
    id_usuario = session.get('id_usuario')
    
    cursor.execute("SELECT * FROM cita WHERE id = %s", (id,))
    cita_data = cursor.fetchone() 
    
    if not cita_data:
        cursor.close()
        flash("La cita no existe.", "danger")
        return redirect(url_for('cita_bp.cita'))

    if rol_usuario == 'Cliente':
        cursor.execute("SELECT id_perfil FROM perfil WHERE fk_usuario = %s", (id_usuario,))
        perfil = cursor.fetchone()
        if perfil:
            cursor.execute("SELECT id, nombre FROM mascota WHERE id_dueno = %s", (perfil['id_perfil'],))
            lista_mascotas = cursor.fetchall()
        else:
            lista_mascotas = []
    else:
        cursor.execute("SELECT id, nombre FROM mascota")
        lista_mascotas = cursor.fetchall()
    
    sql_vets = """
        SELECT v.id, p.nombre_completo 
        FROM veterinario v 
        JOIN perfil p ON v.id_perfil = p.id_perfil
    """
    cursor.execute(sql_vets)
    lista_vets = cursor.fetchall()
    
    cursor.close()
        
    return render_template('Cita/editCita.html', 
                        cita=cita_data, 
                        mascotas=lista_mascotas, 
                        veterinarios=lista_vets)