from flask import Response, Blueprint, current_app  
from fpdf import FPDF
from extensiones import mysql
import MySQLdb.cursors
import os

factura_pdf_pb = Blueprint('facturaPdf', __name__, url_prefix='/facturaPdf')

@factura_pdf_pb.route('/descargarPdf/<int:id>')
def descargarPdf(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql_factura = """SELECT 
                        f.id,
                        f.numero_consecutivo,
                        f.fecha_expedicion,
                        f.estado_pago,
                        f.metodo_pago,
                        f.total,
                        f.fk_usuario,
                        f.total_Sin_Iva,
                        f.total_iva,
                        p.nombre_completo AS nombre_Cliente,
                        p.tipo_documento,
                        p.numero_documento,
                        p.telefono
                    FROM factura f
                    LEFT JOIN usuario u ON f.fk_usuario = u.id_usuario
                    LEFT JOIN perfil p ON u.id_usuario = p.fk_usuario
                    WHERE f. id = %s ;
            """
    cursor.execute(sql_factura, (id,))
    datos_factura = cursor.fetchone()

    if not datos_factura:
        cursor.close()
        return "Factura no encontrada", 404

    query_detalles = """
        SELECT d.cantidad, d.precio_unitario, d.subtotal, d.porcentaje_iva, d.total_iva, d.subtotal_Sin_Iva, c.nombre
        FROM detalle_factura d
        JOIN catalogo c ON d.fk_catalogo = c.id
        WHERE d.fk_factura = %s
    """
    cursor.execute(query_detalles, (id,))
    detalles = cursor.fetchall()
    cursor.close()

    pdf = FPDF("L")
    pdf.add_page()

    LOGO_PATH = os.path.join(current_app.root_path, 'static', 'img', 'logo.png')

    logo_width = 30  
    page_width = pdf.w - 2*pdf.l_margin 
    x_center_logo = (page_width - logo_width) / 2 + pdf.l_margin

    try:
        pdf.image(LOGO_PATH, x=x_center_logo, y=8, w=logo_width)
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo cargar el logo en el PDF: {e}")


    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 100, 0) 

    pdf.ln(35) 
    pdf.cell(0, 10, "DISTRITO ANIMAL - COMPROBANTE", ln=True, align="C")

    pdf.ln(15)  

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(240, 255, 240)  

    total_width = 95 + 95  
    page_width = pdf.w - 2*pdf.l_margin  
    start_x = (page_width - total_width) / 2 + pdf.l_margin

    pdf.set_x(start_x)
    pdf.cell(95, 8, f"Nombre cliente: {datos_factura['nombre_Cliente']}", ln=0, border=1, fill=True)
    pdf.cell(95, 8, f"Consecutivo: {datos_factura['numero_consecutivo']}", ln=1, border=1, fill=True)

    pdf.set_x(start_x)
    pdf.cell(95, 8, f"Tipo documento: {datos_factura['tipo_documento']}", ln=0, border=1, fill=True)
    pdf.cell(95, 8, f"Fecha expedición: {datos_factura['fecha_expedicion']}", ln=1, border=1, fill=True)

    pdf.set_x(start_x)
    pdf.cell(95, 8, f"Número documento: {datos_factura['numero_documento']}", ln=0, border=1, fill=True)
    pdf.cell(95, 8, f"Estado de pago: {datos_factura['estado_pago']}", ln=1, border=1, fill=True)

    pdf.set_x(start_x)
    pdf.cell(95, 8, f"Teléfono cliente: {datos_factura['telefono']}", ln=0, border=1, fill=True)
    pdf.cell(95, 8, f"Método de pago: {datos_factura['metodo_pago']}", ln=1, border=1, fill=True)

    pdf.ln(10)

    pdf.set_fill_color(0, 100, 0)  
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)

    pdf.cell(50, 10, "Producto", border=1, fill=True)