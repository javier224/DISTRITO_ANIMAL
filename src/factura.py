from flask import request, jsonify, Blueprint, render_template, session, redirect, url_for, flash
from extensiones import mysql
import MySQLdb.cursors

factura_bp = Blueprint('factura', __name__, url_prefix='/factura')

@factura_bp.route("/")
def home():
    if session.get('id_rol') not in [1, 2]:
        return "Acceso denegado. Solo personal autorizado puede crear facturas.", 403
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT MAX(numero_consecutivo) FROM factura")
    ultimo = cursor.fetchone()[0]
    cursor.close()

    if ultimo:
        prefijo, numero_str = ultimo.split('-')
        nuevo_numero = int(numero_str) + 1
        siguiente = f"{prefijo}-{str(nuevo_numero).zfill(3)}"
    else:
        siguiente = "FAC-001"

    return render_template('Factura/index.html', consecutivo=siguiente)

@factura_bp.route('/agregarFactura', methods=['POST'])
def agregarFactura():
    if session.get('id_rol') not in [1, 2]:
        return jsonify({"status": "error", "message": "No tienes permiso para realizar esta acción"}), 403

    datos = request.json
    encabezado = datos['encabezado']
    detalles = datos['detalles']

    cursor = mysql.connection.cursor()
    try: 
        sql_encabezado = '''INSERT INTO factura(numero_consecutivo, fecha_expedicion, 
                            estado_pago, metodo_pago, total,fk_usuario, total_Sin_Iva, total_Iva) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        valores_factura = (encabezado['consecutivo'], encabezado['fecha'], encabezado['estado'],
                           encabezado['metodo'], encabezado['total'], encabezado['fk_usuario'], encabezado['total_sin_iva'], encabezado['total_iva'])
        cursor.execute(sql_encabezado, valores_factura)

        factura_id = cursor.lastrowid

        sql_detalle =  '''INSERT INTO detalle_factura(cantidad, precio_unitario, subtotal, 
                            fk_factura, fk_catalogo, porcentaje_iva, total_iva, subtotal_Sin_Iva) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        
        sql_update_stock = ''' UPDATE catalogo
                             SET stock = stock - %s
                             WHERE id = %s AND stock >= %s '''

        for item in detalles:
            valores_detalle = (item['cantidad'], item['precio'], item['subtotal'], 
                               factura_id, item['id_producto'],item['porcentaje_iva'], item['iva_total'], item['subtotal_sin_iva'])
            cursor.execute(sql_detalle, valores_detalle)

        cursor.execute("SELECT tipo_item FROM catalogo WHERE id = %s", (item['id_producto'],))
        tipo_item = cursor.fetchone()[0]

        if tipo_item != 'SERVICIO':
             #Acá descontamos el stock normalmente a los demás items
            valores_update = (item['cantidad'], item['id_producto'], item['cantidad'])
            cursor.execute(sql_update_stock, valores_update)

            #Se verifica si el descuento se realizó correctamente

        if cursor.rowcount == 0:
            mysql.connection.rollback()
            return jsonify({"Status": "error",
                                        
            "message": f"No hay suficiente stock para el producto {item['id_producto']}"

            }), 400

                # Confirmamos la transacción completa
        mysql.connection.commit()
        
        return jsonify({"status": "success", "message": "¡Factura agregada satisfactoriamente!"}), 201
    
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error al insertar factura: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()

@factura_bp.route('/obtenerCatalogo', methods=['GET'])
def obtenerCatalogo():
    try: 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
            SELECT id, nombre, CAST(precio AS FLOAT) as precio, stock, tipo_item, aplica_iva
            FROM catalogo 
            WHERE (tipo_item = 'SERVICIO') 
            OR (tipo_item IN ('VACUNA', 'ALIMENTO', 'DESPARASITANTE') AND stock > 0)
        """
        cursor.execute(query)
        productos = cursor.fetchall()
        cursor.close()
        return jsonify(productos)
    except Exception as err:
        return jsonify({"error": str(err)}), 500

@factura_bp.route('/obtenerUsuarios', methods=['GET'])
def obtenerUsarios():
    if session.get('id_rol') not in [1, 2]:
        return jsonify({"error": "No autorizado"}), 403

    try: 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
            SELECT u.id_usuario, u.correo, u.esta_verificado, p.nombre_completo
            FROM usuario u
            LEFT JOIN perfil p ON u.id_usuario = p.fk_usuario;
        """
        cursor.execute(query)
        clientes = cursor.fetchall()
        cursor.close()
        return jsonify(clientes)
    except Exception as err:
        return jsonify({"error": str(err)}), 500

@factura_bp.route('/listaFactura')
def lista_factura():
    usuario_id = session.get('id_usuario')
    id_rol = session.get('id_rol')
    search = request.args.get('search', '').strip()

    if not usuario_id:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    sql = """SELECT 
                f.id, f.numero_consecutivo, f.fecha_expedicion,
                f.estado_pago, f.metodo_pago, f.total, f.fk_usuario, f.total_Sin_Iva,
                f.total_iva,
                p.nombre_completo AS nombre_Clientes
            FROM factura f
            LEFT JOIN usuario u ON f.fk_usuario = u.id_usuario
            LEFT JOIN perfil p ON u.id_usuario = p.fk_usuario
          """
    
    params = []
    condiciones = []

    #LÓGICA DE BÚSQUEDA MULTICRITERIO 
    if search:
        condiciones.append("(f.numero_consecutivo LIKE %s OR f.estado_pago LIKE %s OR f.metodo_pago LIKE %s OR p.nombre_completo LIKE %s)")
        search_val = f"%{search}%"
        params.extend([search_val, search_val, search_val, search_val])

    # FILTRADO POR ROL 
    if id_rol == 3: 
        condiciones.append("f.fk_usuario = %s")
        params.append(usuario_id)

    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)

    sql += " ORDER BY f.id DESC"
    
    cursor.execute(sql, tuple(params))
    facturas = cursor.fetchall() 
    cursor.close()

    return render_template('Factura/facturas.html', facturas=facturas, search_query=search)

@factura_bp.route('/detallesFactura/<int:id>')
def detallesFactura(id):
    usuario_id = session.get('id_usuario')
    id_rol = session.get('id_rol')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if id_rol == 3:
        cursor.execute("SELECT fk_usuario FROM factura WHERE id = %s", (id,))
        factura = cursor.fetchone()
        if not factura or factura['fk_usuario'] != usuario_id:
            cursor.close()
            return jsonify({"error": "No tienes permiso para ver estos detalles"}), 403

    sql = """
        SELECT d.cantidad, d.precio_unitario, d.subtotal, d.porcentaje_iva, d.total_iva, d.subtotal_Sin_Iva, c.nombre 
        FROM detalle_factura d 
        JOIN catalogo c ON d.fk_catalogo = c.id 
        WHERE d.fk_factura = %s
    """
    cursor.execute(sql, (id,))
    detalles = cursor.fetchall()
    cursor.close()
    return jsonify(detalles)

@factura_bp.route('/cambiarEstado/<int:id>', methods = ["POST"])
def cambiarEstado(id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    nuevo_estado = request.form.get("estado_pago") #valor actual del select

    
    sql = "UPDATE factura SET estado_pago = %s WHERE id = %s"

    cursor.execute(sql, (nuevo_estado, id))
    mysql.connection.commit()

    cursor.close()

    flash("Estado de la factura actualizado correctamente", "success")

    return redirect(url_for("factura.lista_factura"))