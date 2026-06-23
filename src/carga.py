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
            
            df.dropna(how='all', inplace=True)
            
            for _, fila in df.iterrows():
                doc_dueno = str(fila['documento_dueno']).strip().split('.')[0]
                
                dueno = Perfil.query.filter_by(numero_documento=doc_dueno).first()
                if dueno:
                    nueva_mascota = Mascota(
                        nombre=str(fila['nombre']).strip(),
                        especie=str(fila['especie']).strip(),
                        raza=str(fila['raza']).strip(),
                        genero=str(fila['genero']).strip(),
                        id_dueno=dueno.id_perfil
                    )
                    db.session.add(nueva_mascota)
            
            db.session.commit()
            flash("success:¡Inserción masiva completada con éxito!")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR EN CARGA MASIVA: {e}")
            flash(f"error:Hubo un problema al procesar el Excel: {str(e)}")
        
        return redirect(url_for('carga.gestionar_carga'))

    return render_template('carga/carga.html')