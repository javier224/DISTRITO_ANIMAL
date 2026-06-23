from flask import Blueprint, flash, redirect, url_for, current_app
from flask_mail import Message
from extensiones import mail, mysql

envio_blueprint = Blueprint('envio_masivo', __name__)

@envio_blueprint.route('/enviar-recordatorios-masivos', methods=['POST'])
def enviar_recordatorios():
    query = """
        SELECT 
            u.correo, 
            p.nombre_completo, 
            m.nombre AS nombre_mascota, 
            c.inicio AS fecha_cita
        FROM cita c
        JOIN mascota m ON c.id_mascota = m.id
        JOIN perfil p ON m.id_dueno = p.id_perfil
        JOIN usuario u ON p.fk_usuario = u.id_usuario
        WHERE c.estado = 'PENDIENTE'
        AND c.inicio BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 3 DAY)
    """
    
    try:
   
        cur = mysql.connection.cursor()
        cur.execute(query)
        citas = cur.fetchall() 
        cur.close()

        if not citas:
            flash("No hay citas programadas para los próximos 3 días.", "info")
            return redirect(url_for('cita_bp.cita'))

        #  conexión SMTP
        with mail.connect() as conn:
            for cita in citas:
                msg = Message(
                    subject=f"Recordatorio de Cita: {cita[2]} 🐾",
                    recipients=[cita[0]]
                )
                
                fecha_formateada = cita[3].strftime('%d/%m/%Y a las %H:%M')
                
                msg.body = f"""
Hola {cita[1]},

Te recordamos que tu mascota {cita[2]} tiene una cita 
programada en Distrito Animal para el día: {fecha_formateada}.

¡Los esperamos!
                """
                conn.send(msg)

        flash(f"Se han enviado {len(citas)} recordatorios exitosamente.", "success")
        
    except Exception as e:
        flash(f"Ocurrió un error al procesar el envío: {str(e)}", "danger")
        
    return redirect(url_for('cita_bp.cita'))