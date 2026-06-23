from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contra = db.Column(db.String(255), nullable=False)
    fk_rol = db.Column(db.Integer, db.ForeignKey('rol.id'))

class Perfil(db.Model):
    __tablename__ = 'perfil'
    id_perfil = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150))
    numero_documento = db.Column(db.String(20), unique=True)
    fk_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

class Mascota(db.Model):
    __tablename__ = 'mascota'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50))
    raza = db.Column(db.String(50))
    genero = db.Column(db.String(20))
    id_dueno = db.Column(db.Integer, db.ForeignKey('perfil.id_perfil'), nullable=False)