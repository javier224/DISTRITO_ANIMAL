from flask import Blueprint, render_template, request, flash, redirect, url_for
import pandas as pd
from models import db, Mascota, Perfil

carga_bp = Blueprint('carga', __name__)

@carga_bp.route('/carga', methods=['GET', 'POST'])
def gestionar_carga():
    if request.method == 'POST':
        archivo = request.files.get('file')
        if not archivo:
            flash("error:Selecciona un archivo válido.")
            return redirect(url_for('carga.gestionar_carga'))

        try:
            df = pd.read_excel(archivo)
            for _, fila in df.iterrows():
                dueno = Perfil.query.filter_by(numero_documento=str(fila['documento_dueno'])).first()
                if dueno:
                    nueva_mascota = Mascota(
                        nombre=fila['nombre'],
                        especie=fila['especie'],
                        raza=fila['raza'],
                        genero=fila['genero'],
                        id_dueno=dueno.id_perfil
                    )
                    db.session.add(nueva_mascota)
            
            db.session.commit()
            # Enviamos un mensaje específico para activar el modal
            flash("success:¡Inserción masiva completada con éxito!")
        except Exception as e:
            db.session.rollback()
            flash(f"error:Hubo un problema al procesar el Excel: {str(e)}")
        
        return redirect(url_for('carga.gestionar_carga'))

    # Si es GET, simplemente muestra la página
    return render_template('carga/carga.html')