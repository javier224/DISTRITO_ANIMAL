import io
import os 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Blueprint, session, send_file, current_app
from fpdf import FPDF
from extensiones import mysql
import MySQLdb.cursors

estadisticas_bp = Blueprint('estadisticas', __name__)

@estadisticas_bp.route('/reporte-ventas-pdf')
def generar_reporte_torta():
    if session.get('id_rol') != 1:
        return "Acceso denegado", 403

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        query = """
            SELECT c.nombre, SUM(d.cantidad) as unidades
            FROM detalle_factura d
            JOIN catalogo c ON d.fk_catalogo = c.id
            GROUP BY c.id
            ORDER BY unidades DESC
            LIMIT 6
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
    finally:
        cursor.close()

    if not resultados:
        return "No hay datos suficientes para generar estadísticas.", 404

    # Generación del Gráfico 
    nombres = [r['nombre'] for r in resultados]
    unidades = [int(r['unidades']) for r in resultados]

    plt.figure(figsize=(7, 7))
    colores = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6']
    
    plt.pie(unidades, labels=nombres, autopct='%1.1f%%', startangle=140, colors=colores)
    plt.title('Distribución de Productos y Servicios más Vendidos')
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()

    # Generación del PDF 
    pdf = FPDF()
    pdf.add_page()
    
    # LOGO DISTRITO ANIMAL 
    ruta_logo = os.path.join(current_app.root_path, 'static', 'img', 'DA.IMG.jpg')
    
    if os.path.exists(ruta_logo):
        pdf.image(ruta_logo, x=10, y=8, w=25)

    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(44, 62, 80) 
    pdf.cell(0, 15, "DISTRITO ANIMAL - REPORTE ESTADÍSTICO", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 5, "Informe de rotación de inventario y servicios", ln=True, align='C')
    pdf.cell(0, 5, "Sede Bogotá, Colombia", ln=True, align='C') # Referencia local
    pdf.ln(10)

    pdf.image(img_buffer, x=25, y=50, w=160)
    
    pdf.set_y(190)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(120, 10, "Producto / Servicio", border=1, fill=True)
    pdf.cell(40, 10, "Unidades", border=1, ln=True, fill=True, align='C')

    pdf.set_font("Arial", '', 11)
    for r in resultados:
        pdf.cell(120, 10, f" {r['nombre']}", border=1)
        pdf.cell(40, 10, str(r['unidades']), border=1, ln=True, align='C')


    pdf_content = pdf.output(dest='S')
    return send_file(
        io.BytesIO(pdf_content),
        mimetype='application/pdf',
        as_attachment=False,
        download_name='reporte_distrito_animal.pdf'
    )
