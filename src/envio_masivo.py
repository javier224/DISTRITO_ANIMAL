from flask import Blueprint, flash, redirect, url_for, current_app
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from extensiones import mysql

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
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            flash("Error: No se encontró la variable SENDGRID_API_KEY en el servidor.", "danger")
            return redirect(url_for('cita_bp.cita'))

        cur = mysql.connection.cursor()
        cur.execute(query)
        citas = cur.fetchall() 
        cur.close()

        if not citas:
            flash("No hay citas programadas para los próximos 3 días.", "info")
            return redirect(url_for('cita_bp.cita'))

        sg = SendGridAPIClient(api_key)
        contador_enviados = 0

        for cita in citas:
            fecha_formateada = cita[3].strftime('%d/%m/%Y a las %H:%M')
        
            contenido_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #006400; text-align: center;">¡Hola {cita[1]}!</h2>
                <p>Te recordamos desde <strong>Distrito Animal</strong> que tu mascota <strong>{cita[2]}</strong> tiene una cita médica programada.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 1.1em; text-align: center; background-color: #f4fbf4; padding: 15px; border-radius: 5px; color: #006400;">
                    📅 <strong>Fecha y Hora:</strong> {fecha_formateada}
                </p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="text-align: center; color: #666;">¡Los esperamos con los brazos abiertos! 🐾</p>
            </div>
            """

            message = Mail(
                from_email='distritoanimal2011@gmail.com', 
                to_emails=cita[0],                     
                subject=f"Recordatorio de Cita: {cita[2]} 🐾", 
                html_content=contenido_html
            )
            
            response = sg.send(message)
            
            if response.status_code in [200, 202]:
                contador_enviados += 1

        flash(f"Se han enviado {contador_enviados} recordatorios exitosamente vía SendGrid.", "success")
        
    except Exception as e:
        print(f"❌ Error en envio masivo SendGrid: {e}")
        flash(f"Ocurrió un error al procesar el envío: {str(e)}", "danger")
        
    return redirect(url_for('cita_bp.cita'))