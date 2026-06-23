import os
import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, redirect, url_for, flash, session
import MySQLdb.cursors
import random
import string
from sqlalchemy import text
from src.extensiones import mysql, bcrypt, mail
from src.models import db

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'distrito_animal_secret_2026')

database_url = os.environ.get('DATABASE_URL')

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/distrito_animal'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_PORT'] = 3309
app.config['MYSQL_DB'] = 'distrito_animal'

# 3. CONFIGURACIÓN DE CORREO 

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'distritoanimal2011@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'obry zjtz naln imaf')
app.config['MAIL_DEFAULT_SENDER'] = ('Distrito Animal', app.config['MAIL_USERNAME'])


mysql.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)
db.init_app(app)


from src.catalogo import catalogo_bp
from src.servicio import servicio_bp
from src.vacuna import vacuna_bp
from src.desparasitante import desparasitante_bp
from src.alimento import alimento_bp
from src.factura import factura_bp
from src.factura_pdf import factura_pdf_pb
from src.veterinario import veterinario_bp
from src.mascota import mascota_bp
from src.cita import cita_bp
from src.factura_estadistico import estadisticas_bp
from src.envio_masivo import envio_blueprint
from src.carga import carga_bp


# Registro de Blueprints
app.register_blueprint(catalogo_bp)
app.register_blueprint(servicio_bp)
app.register_blueprint(vacuna_bp)
app.register_blueprint(desparasitante_bp)
app.register_blueprint(alimento_bp)
app.register_blueprint(factura_bp)
app.register_blueprint(factura_pdf_pb)
app.register_blueprint(veterinario_bp)
app.register_blueprint(mascota_bp)
app.register_blueprint(cita_bp)
app.register_blueprint(estadisticas_bp)
app.register_blueprint(envio_blueprint)
app.register_blueprint(carga_bp)


with app.app_context():
    try:
        db.create_all()
        print("¡Base de datos PostgreSQL estructurada con éxito!")
    except Exception as e:
        print(f"Error al estructurar la base de datos: {e}")

# 6. FUNCIONES DE APOYO

def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def enviar_correo(user_email, asunto, contenido_html):
    try:
        from flask_mail import Message
        msg = Message(asunto, recipients=[user_email])
        msg.html = contenido_html
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar correo: {e}")

def verificar_perfil_completo(id_usuario):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM perfil WHERE fk_usuario = %s", (id_usuario,))
    return cursor.fetchone() is not None

#  RUTAS DE NAVEGACIÓN

@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/servicios')
def servicios():
    return render_template('servicio.html')

@app.route('/contactanos')
def contactanos():
    return render_template('contactanos.html')

# AUTENTICACIÓN 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('correo')
        password_candidate = request.form.get('contra')
        
        query = text("""
            SELECT u.*, r.nombre AS rol_nombre 
            FROM usuario u 
            JOIN rol r ON u.fk_rol = r.id 
            WHERE u.correo = :email
        """)
        
        result = db.session.execute(query, {"email": email})

        user_row = result.mappings().first()

        if user_row:
            user = dict(user_row)
            
            if not user['esta_verificado']:
                flash('Por favor, verifica tu cuenta primero.', 'warning')
                return render_template('login.html')
            
            if bcrypt.check_password_hash(user['contra'], password_candidate):
                session.update({
                    'loggedin': True,
                    'id_usuario': user['id_usuario'],
                    'rol': user['rol_nombre'],
                    'id_rol': user['fk_rol'],
                    'email': user['correo']
                })
                
                if user['rol_nombre'] == 'Administrador': return redirect(url_for('admin_dashboard'))
                elif user['rol_nombre'] == 'Veterinario': return redirect(url_for('vet_dashboard'))
                else: return redirect(url_for('cliente_dashboard'))
            else:
                flash('Contraseña incorrecta.', 'error')
        else:
            flash('Usuario no encontrado.', 'error')
            
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        token = generar_codigo()
        
        query_select = text("SELECT * FROM usuario WHERE correo = :email")
        result = db.session.execute(query_select, {"email": email})
        user_row = result.mappings().first()
        
        if user_row:
            query_update = text("""
                UPDATE usuario 
                SET token_verificacion = :token 
                WHERE correo = :email
            """)
            db.session.execute(query_update, {"token": token, "email": email})
            
            db.session.commit()
            
            link = url_for('reset_password', token=token, email=email, _external=True)
            
            contenido = f"""
            <div style="font-family: sans-serif; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                <h2 style="color: #2563eb;">Recuperación de Contraseña</h2>
                <p>Has solicitado restablecer tu contraseña en <b>Distrito Animal</b>.</p>
                <p>Haz clic en el siguiente botón para continuar:</p>
                <a href="{link}" style="background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Restablecer Contraseña</a>
                <p style="margin-top: 20px; font-size: 12px; color: #666;">Si no solicitaste esto, puedes ignorar este correo.</p>
            </div>
            """
            enviar_correo(email, "Restablece tu contraseña - Distrito Animal", contenido)
            flash('Se ha enviado un enlace a tu correo.', 'success')
        else:
            flash('El correo no está registrado.', 'error')
            
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>/<email>', methods=['GET', 'POST'])
def reset_password(token, email):
    if request.method == 'POST':
        nueva_contra = request.form.get('nueva_contra')
        confirm_contra = request.form.get('confirm_contra')
        
        if nueva_contra != confirm_contra:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('reset_password.html', token=token, email=email)
        
        hashed_pw = bcrypt.generate_password_hash(nueva_contra).decode('utf-8')
        
        query_select = text("""
            SELECT * FROM usuario 
            WHERE correo = :email AND token_verificacion = :token
        """)
        result = db.session.execute(query_select, {"email": email, "token": token})
        user = result.mappings().first()
        
        if user:
            query_update = text("""
                UPDATE usuario 
                SET contra = :contra, token_verificacion = NULL 
                WHERE correo = :email
            """)
            db.session.execute(query_update, {"contra": hashed_pw, "email": email})
            
            db.session.commit()
            
            flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('El enlace ha expirado o es inválido.', 'error')
            return redirect(url_for('login'))
            
    return render_template('reset_password.html', token=token, email=email)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('correo')
        password = request.form.get('contra')
        confirm = request.form.get('confirm_contra')

        if password != confirm:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('login.html')
        
        id_rol = 1 if "@admin." in email else 2 if "@vet." in email else 3
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        es_personal = "@admin." in email or "@vet." in email
        esta_verificado = 1 if es_personal else 0
        token = None if es_personal else generar_codigo()

        try:
            query = text("""
                INSERT INTO usuario (correo, contra, token_verificacion, esta_verificado, fk_rol) 
                VALUES (:correo, :contra, :token, :esta_verificado, :fk_rol)
            """)
            
            db.session.execute(query, {
                "correo": email,
                "contra": hashed_pw,
                "token": token,
                "esta_verificado": esta_verificado,
                "fk_rol": id_rol
            })
            
            db.session.commit()
            
            if not es_personal:
                contenido_html = f"""
                <div style="font-family: sans-serif; max-width: 450px; margin: 20px auto; border-radius: 10px; border: 1px solid #ddd; text-align: center; padding: 20px;">
                    <h2 style="color: #2563eb; margin-bottom: 10px;">¡Hola! 🐾</h2>
                    <p style="color: #555; font-size: 15px;">Usa este código para activar tu cuenta en <b>Distrito Animal</b>:</p>
                    <div style="margin: 25px 0;">
                        <span style="background: #f0f7ff; color: #2563eb; font-size: 28px; font-weight: bold; padding: 10px 25px; border-radius: 8px; border: 1px solid #2563eb; letter-spacing: 3px;">
                            {token}
                        </span>
                    </div>
                    <p style="color: #888; font-size: 12px; margin-top: 20px;">Si no creaste esta cuenta, ignora este mensaje.</p>
                </div>
                """
                enviar_correo(email, "Código de activación 🐾", contenido_html)
                return render_template('verify.html', email=email)

            flash('Registro exitoso de personal. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            print(f"Error en registro: {e}")
            flash('El correo ya existe o hubo un problema con la base de datos.', 'error')
            
    return render_template('login.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        email = request.form.get('email')
        token_ing = request.form.get('codigo')
        
        query_select = text("SELECT * FROM usuario WHERE correo = :email AND token_verificacion = :token")
        result = db.session.execute(query_select, {"email": email, "token": token_ing})
        if result.mappings().first():
            query_update = text("UPDATE usuario SET esta_verificado = 1, token_verificacion = NULL WHERE correo = :email")
            db.session.execute(query_update, {"email": email})
            db.session.commit()
            
            flash('Cuenta activada.', 'success')
            return redirect(url_for('login'))
        
        flash('Código inválido.', 'error')
    return render_template('verify.html')


@app.route('/guardar_perfil', methods=['POST'])
def guardar_perfil():
    if not session.get('loggedin'): 
        return redirect(url_for('login'))
    
    nombre = request.form.get('nombre_completo')
    tel = request.form.get('telefono')
    tipo_doc = request.form.get('tipo_documento')
    num_doc = request.form.get('numero_documento')
    direccion = request.form.get('direccion_residencial')
    id_usu = session.get('id_usuario')

    if not id_usu:
        return redirect(url_for('login'))

    try:
        is_postgres = "postgresql" in app.config['SQLALCHEMY_DATABASE_URI']

        if is_postgres:
            query = text("""
                INSERT INTO perfil 
                (nombre_completo, telefono, tipo_documento, numero_documento, direccion_residencial, fk_usuario) 
                VALUES (:nombre, :tel, :tipo_doc, :num_doc, :direccion, :id_usu)
                ON CONFLICT (fk_usuario) DO UPDATE SET 
                nombre_completo = EXCLUDED.nombre_completo,
                telefono = EXCLUDED.telefono,
                tipo_documento = EXCLUDED.tipo_documento,
                numero_documento = EXCLUDED.numero_documento,
                direccion_residencial = EXCLUDED.direccion_residencial
            """)
        else:
            query = text("""
                INSERT INTO perfil 
                (nombre_completo, telefono, tipo_documento, numero_documento, direccion_residencial, fk_usuario) 
                VALUES (:nombre, :tel, :tipo_doc, :num_doc, :direccion, :id_usu)
                ON DUPLICATE KEY UPDATE 
                nombre_completo = VALUES(nombre_completo),
                telefono = VALUES(telefono),
                tipo_documento = VALUES(tipo_documento),
                numero_documento = VALUES(numero_documento),
                direccion_residencial = VALUES(direccion_residencial)
            """)
        
        db.session.execute(query, {
            "nombre": nombre, "tel": tel, "tipo_doc": tipo_doc, 
            "num_doc": num_doc, "direccion": direccion, "id_usu": id_usu
        })
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR EN PERFIL: {e}")
        flash('Hubo un problema al guardar el perfil.', 'error')

    # Redirección según el rol
    rol = session.get('rol')
    if rol == 'Administrador': return redirect(url_for('admin_dashboard'))
    elif rol == 'Veterinario': return redirect(url_for('vet_dashboard'))
    else: return redirect(url_for('cliente_dashboard'))

#  DASHBOARDS 

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('loggedin'): 
        return redirect(url_for('login'))
    
    id_usu = session.get('id_usuario')
    
    query_perfil = text("SELECT * FROM perfil WHERE fk_usuario = :id_usu")
    perfil_row = db.session.execute(query_perfil, {"id_usu": id_usu}).mappings().first()
    perfil_existente = dict(perfil_row) if perfil_row else None
    
    mostrar_modal = True if not perfil_existente else False

    query_alimentos = text("""
        SELECT SUM(df.subtotal) as total 
        FROM detalle_factura df
        JOIN catalogo c ON df.fk_catalogo = c.id
        WHERE c.tipo_item = 'ALIMENTO'
    """)
    res_ventas = db.session.execute(query_alimentos).mappings().first()
    ventas_alimentos = res_ventas['total'] if res_ventas and res_ventas['total'] else 0

    query_vets = text("SELECT COUNT(*) as total FROM veterinario")
    res_vets = db.session.execute(query_vets).mappings().first()
    total_vets = res_vets['total'] if res_vets else 0

    query_trabajadores = text("SELECT COUNT(*) as total FROM usuario WHERE fk_rol IN (1, 2)")
    res_trabajadores = db.session.execute(query_trabajadores, {"roles": (1, 2)}).mappings().first()
    total_trabajadores = res_trabajadores['total'] if res_trabajadores else 0

    meta_staff = 8
    porcentaje_staff = (total_trabajadores / meta_staff) * 100 if meta_staff > 0 else 0
    
    return render_template('admin/adminHome.html', 
                           perfil=perfil_existente, 
                           mostrar_modal=mostrar_modal,
                           ventas_alimentos=ventas_alimentos,
                           total_vets=total_vets,
                           total_trabajadores=total_trabajadores,
                           porcentaje_staff=porcentaje_staff)
    

@app.route('/vet/dashboard')
def vet_dashboard():
    if session.get('loggedin') and session.get('rol') == 'Veterinario':
        id_usu = session.get('id_usuario')
        
        query_perfil = text("SELECT * FROM perfil WHERE fk_usuario = :id_usu")
        perfil_row = db.session.execute(query_perfil, {"id_usu": id_usu}).mappings().first()
        perfil_data = dict(perfil_row) if perfil_row else None
        
        query_vet_reg = text("""
            SELECT id FROM veterinario 
            WHERE id_perfil = (SELECT id_perfil FROM perfil WHERE fk_usuario = :id_usu)
        """)
        vet_row = db.session.execute(query_vet_reg, {"id_usu": id_usu}).mappings().first()
        
        citas_hoy = 0
        total_pacientes = 0
        
        if vet_row:
            id_vet = vet_row['id']
            
            query_citas = text("""
                SELECT COUNT(*) as total 
                FROM cita 
                WHERE id_veterinario = :id_vet AND DATE(inicio) = CURRENT_DATE
            """)
            res_citas = db.session.execute(query_citas, {"id_vet": id_vet}).mappings().first()
            citas_hoy = res_citas['total'] if res_citas else 0
            
            query_pacientes = text("""
                SELECT COUNT(DISTINCT id_mascota) as total 
                FROM cita 
                WHERE id_veterinario = :id_vet
            """)
            res_pacientes = db.session.execute(query_pacientes, {"id_vet": id_vet}).mappings().first()
            total_pacientes = res_pacientes['total'] if res_pacientes else 0
        
        return render_template('vet/vetHome.html', 
                               perfil=perfil_data, 
                               mostrar_modal=not perfil_data,
                               citas_hoy=citas_hoy,
                               total_pacientes=total_pacientes)
    
    return redirect(url_for('login'))

@app.route('/cliente/dashboard')
def cliente_dashboard():
    if session.get('loggedin') and session.get('rol') == 'Cliente':
        id_usu = session.get('id_usuario')
        
        query_perfil = text("SELECT * FROM perfil WHERE fk_usuario = :id_usu")
        perfil_row = db.session.execute(query_perfil, {"id_usu": id_usu}).mappings().first()
        perfil_data = dict(perfil_row) if perfil_row else None
        
        mis_mascotas = 0
        proximas_citas = 0
        
        if perfil_data:
            id_perfil = perfil_data['id_perfil']
            
            query_mascotas = text("SELECT COUNT(*) as total FROM mascota WHERE id_dueno = :id_dueno")
            res_mascotas = db.session.execute(query_mascotas, {"id_dueno": id_perfil}).mappings().first()
            mis_mascotas = res_mascotas['total'] if res_mascotas else 0
            
            query_citas = text("""
                SELECT COUNT(*) as total FROM cita c
                JOIN mascota m ON c.id_mascota = m.id
                WHERE m.id_dueno = :id_dueno AND c.inicio >= CURRENT_TIMESTAMP
            """)
            res_citas = db.session.execute(query_citas, {"id_dueno": id_perfil}).mappings().first()
            proximas_citas = res_citas['total'] if res_citas else 0
        
        return render_template('cliente/clienteHome.html', 
                               perfil=perfil_data, 
                               mostrar_modal=not perfil_data,
                               mis_mascotas=mis_mascotas,
                               proximas_citas=proximas_citas)
    
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)