from flask import Response, Blueprint
from fpdf import FPDF
from extensiones import mysql
import MySQLdb.cursors
import os

factura_pdf_pb = Blueprint('facturaPdf', __name__, url_prefix='/facturaPdf')

@factura_pdf_pb.route('/descargarPdf/<int:id>')
def descargarPdf(id):
    # Usamos el cursor de la conexión centralizada con DictCursor
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 1. Obtener datos de la cabecera de la factura (ajustado a minúsculas según tu SQL)
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
        return "Factura no encontrada", 404

    # 2. Obtener detalles (ajustado a los nombres de tu tabla detalle_factura)
    query_detalles = """
        SELECT d.cantidad, d.precio_unitario, d.subtotal, d.porcentaje_iva, d.total_iva, d.subtotal_Sin_Iva, c.nombre
        FROM detalle_factura d
        JOIN catalogo c ON d.fk_catalogo = c.id
        WHERE d.fk_factura = %s
    """
    cursor.execute(query_detalles, (id,))
    detalles = cursor.fetchall()
    cursor.close()

    # --- Generación del PDF ---
    pdf = FPDF("L")
    pdf.add_page()

    # Logo

    logo_width = 30  # ancho del logo
    page_width = pdf.w - 2*pdf.l_margin  # ancho útil de la página
    x_center_logo = (page_width - logo_width) / 2 + pdf.l_margin

    pdf.image("static/img/logo.png", x=x_center_logo, y=8, w=logo_width)

    # =========================
    # TÍTULO CENTRADO
    # =========================
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 100, 0)  # Verde oscuro

    pdf.ln(35)  # bajar un poco después del logo
    pdf.cell(0, 10, "DISTRITO ANIMAL - COMPROBANTE", ln=True, align="C")

    pdf.ln(15)  

        # Datos del cliente y factura en columnas
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)

    pdf.set_fill_color(240, 255, 240)  # Verde muy claro

    # Ancho total de las dos celdas
    total_width = 95 + 95  # 190 mm
    page_width = pdf.w - 2*pdf.l_margin  # ancho útil de la página
    start_x = (page_width - total_width) / 2 + pdf.l_margin

    pdf.set_x(start_x)

    pdf.cell(95, 8, f"Nombre cliente: {datos_factura['nombre_Cliente']}", ln=0, border=1, fill=True)
    pdf.cell(95, 8, f"Consecutivo: {datos_factura['numero_consecutivo']}", ln=1, border=1, fill=True)

    # Segunda fila
    pdf.set_x(start_x)

    pdf.cell(95, 8, f"Tipo documento: {datos_factura['tipo_documento']}", ln=0, border=1, fill=True)
    pdf.cell(95, 8, f"Fecha expedición: {datos_factura['fecha_expedicion']}", ln=1, border=1, fill=True)

    # Tercera fila

    pdf.set_x(start_x)
    pdf.cell(95, 8, f"Número documento: {datos_factura['numero_documento']}", ln=0, border=1, fill=True)
    pdf.cell(95, 8, f"Estado de pago: {datos_factura['estado_pago']}", ln=1, border=1, fill=True)

    # Cuarta fila

    pdf.set_x(start_x)

    pdf.cell(95, 8, f"Teléfono cliente: {datos_factura['telefono']}", ln=0, border=1, fill=True)
    pdf.cell(95, 8, f"Método de pago: {datos_factura['metodo_pago']}", ln=1, border=1, fill=True)

    pdf.ln(10)

    # =========================
    # TABLA DE PRODUCTOS
    # =========================
    pdf.set_fill_color(0, 100, 0)  # verde oscuro
    pdf.set_text_color(255, 255, 255)  # blanco
    pdf.set_font("Helvetica", "B", 10)

    # Encabezados
    pdf.cell(50, 10, "Producto", border=1, fill=True)
    pdf.cell(30, 10, "Cantidad", border=1, fill=True, align="C")
    pdf.cell(40, 10, "Precio Unit.", border=1, fill=True, align="C")
    pdf.cell(40, 10, "Porcentaje Iva", border=1, fill=True, align="C")
    pdf.cell(40, 10, "Iva neto", border=1, fill=True, align="C")
    pdf.cell(40, 10, "Subtotal sin iva", border=1, fill=True, align="C")
    pdf.cell(40, 10, "Subtotal", border=1, fill=True, align="C")
    pdf.ln()

    # Contenido
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    for d in detalles:
        pdf.cell(50, 8, str(d['nombre']), border=1)
        pdf.cell(30, 8, str(d['cantidad']), border=1, align="C")
        pdf.cell(40, 8, f"${float(d['precio_unitario']):.2f}", border=1, align="R")
        pdf.cell(40, 8, f"{float(d['porcentaje_iva']):.2f}%", border=1, align="R")
        pdf.cell(40, 8, f"${float(d['total_iva']):.2f}", border=1, align="R")
        pdf.cell(40, 8, f"${float(d['subtotal_Sin_Iva']):.2f}", border=1, align="R")
        pdf.cell(40, 8, f"${float(d['subtotal']):.2f}", border=1, align="R")
        pdf.ln()

    pdf.ln(10)

    # =========================
    # TOTALES EN UNA SOLA FILA
    # =========================
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 100, 0)

    pdf.cell(53, 10, "TOTAL IVA:", border=1, align="C")
    pdf.cell(40, 10, f"${float(datos_factura['total_iva']):.2f}", border=1, align="C")

    pdf.cell(53, 10, "TOTAL SIN IVA:", border=1, align="C")
    pdf.cell(40, 10, f"${float(datos_factura['total_Sin_Iva']):.2f}", border=1, align="C")

    pdf.cell(53, 10, "TOTAL A PAGAR:", border=1, align="C")
    pdf.cell(40, 10, f"${float(datos_factura['total']):.2f}", border=1, align="C")

    pdf.ln(20)

    # =========================
    # PIE DE PÁGINA
    # =========================
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, "Distrito Animal | Tel: 3001234567 | Correo: contacto@distritoanimal.com", align="C")

    # Salida del PDF
    pdf_output = pdf.output(dest='S')

    if isinstance(pdf_output, str):
        pdf_bytes = pdf_output.encode('latin-1')
    else:
        pdf_bytes = bytes(pdf_output)

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=factura_{id}.pdf"
        }
    )
