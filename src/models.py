from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 1. TABLA: ROL

class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)


# 2. TABLA: USUARIO

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contra = db.Column(db.String(255), nullable=False)
    token_verificacion = db.Column(db.String(100), nullable=True)
    token_recuperacion = db.Column(db.String(100), nullable=True)
    esta_verificado = db.Column(db.Boolean, default=False)
    fk_rol = db.Column(db.Integer, db.ForeignKey('rol.id'))


# 3. TABLA: PERFIL

class Perfil(db.Model):
    __tablename__ = 'perfil'
    id_perfil = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_completo = db.Column(db.String(150))
    telefono = db.Column(db.String(20))
    tipo_documento = db.Column(db.Enum('CC', 'TI', 'CE', 'Pasaporte'))
    numero_documento = db.Column(db.String(20), unique=True)
    direccion_residencial = db.Column(db.String(200))
    fk_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE'), unique=True)


# 4. TABLA: VETERINARIO

class Veterinario(db.Model):
    __tablename__ = 'veterinario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_licencia = db.Column(db.String(50), nullable=False)
    especialidad = db.Column(db.String(100))
    id_perfil = db.Column(db.Integer, nullable=False)

# 5. TABLA: MASCOTA

class Mascota(db.Model):
    __tablename__ = 'mascota'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50))
    raza = db.Column(db.String(50))
    fecha_nacimiento = db.Column(db.Date)
    genero = db.Column(db.String(20))
    color = db.Column(db.String(50))
    peso = db.Column(db.Float)
    observaciones = db.Column(db.Text)
    id_dueno = db.Column(db.Integer, db.ForeignKey('perfil.id_perfil', ondelete='CASCADE'), nullable=False)

# 6. TABLA: CITA

class Cita(db.Model):
    __tablename__ = 'cita'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inicio = db.Column(db.DateTime, nullable=False)
    fin = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.Text)
    estado = db.Column(db.String(50), default='PENDIENTE')
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascota.id', ondelete='CASCADE'), nullable=False)
    id_veterinario = db.Column(db.Integer, db.ForeignKey('veterinario.id', ondelete='CASCADE'), nullable=False)


# 7. TABLA: CATALOGO 

class Catalogo(db.Model):
    __tablename__ = 'catalogo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_item = db.Column(db.Enum('VACUNA', 'ALIMENTO', 'DESPARASITANTE', 'SERVICIO'))
    stock = db.Column(db.Integer)
    aplica_iva = db.Column(db.Enum('SI', 'NO'), nullable=False)


# 8. TABLA: ALIMENTO 

class Alimento(db.Model):
    __tablename__ = 'alimento'
    id = db.Column(db.Integer, db.ForeignKey('catalogo.id', ondelete='CASCADE'), primary_key=True)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    lote = db.Column(db.String(70))
    tipo_alimento = db.Column(db.Enum('SECO', 'HÚMEDO', 'SEMIHÚMEDO', 'SNACKS'))
    peso_contenido = db.Column(db.Numeric(10, 2))
    indicacion_especifica = db.Column(db.Text)

# 9. TABLA: DESPARASITANTE (Hijo de Catalogo)
class Desparasitante(db.Model):
    __tablename__ = 'desparasitante'
    id = db.Column(db.Integer, db.ForeignKey('catalogo.id', ondelete='CASCADE'), primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    via_administracion = db.Column(db.Enum('ORAL', 'TÓPICA', 'INYECTABLE', 'OTICA', 'OFTALMICA'))
    rango_peso = db.Column(db.String(25))


# 10. TABLA: VACUNA

class Vacuna(db.Model):
    __tablename__ = 'vacuna'
    id = db.Column(db.Integer, db.ForeignKey('catalogo.id', ondelete='CASCADE'), primary_key=True)
    descripcion = db.Column(db.Text)
    laboratorio = db.Column(db.String(50))
    periodo_refuerzo = db.Column(db.String(25))

# 11. TABLA: SERVICIO 

class Servicio(db.Model):
    __tablename__ = 'servicio'
    id = db.Column(db.Integer, db.ForeignKey('catalogo.id', ondelete='CASCADE'), primary_key=True)
    descripcion = db.Column(db.Text)
    duracion_estimada = db.Column(db.Time)


# 12. TABLA: FACTURA

class Factura(db.Model):
    __tablename__ = 'factura'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_consecutivo = db.Column(db.String(70), unique=True)
    fecha_expedicion = db.Column(db.Date, nullable=False)
    estado_pago = db.Column(db.Enum('PAGADA', 'PENDIENTE', 'ANULADA'), nullable=False)
    metodo_pago = db.Column(db.Enum('NEQUI', 'DAVIPLATA', 'BANCOLOMBIA', 'DALE', 'BRE-B'), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fk_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE'), nullable=False)
    total_Sin_Iva = db.Column(db.Numeric(10, 0), nullable=False)
    total_iva = db.Column(db.Numeric(10, 0), nullable=False)


# 13. TABLA: DETALLE FACTURA

class DetalleFactura(db.Model):
    __tablename__ = 'detalle_factura'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    fk_factura = db.Column(db.Integer, db.ForeignKey('factura.id', ondelete='CASCADE'), nullable=False)
    fk_catalogo = db.Column(db.Integer, db.ForeignKey('catalogo.id'), nullable=False)
    porcentaje_iva = db.Column(db.Integer, nullable=False)
    total_iva = db.Column(db.Numeric(10, 0), nullable=False)
    subtotal_Sin_Iva = db.Column(db.Numeric(10, 0), nullable=False)