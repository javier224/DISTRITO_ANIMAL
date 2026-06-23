
//VALIDACIÓN FORMULARIO ALIMENTO
console.log('siuu')
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", function (event) {
        let valid = true;
        let mensajes = [];

        // Validar id
        const id = document.getElementById("id").value;
        if (!id) {
            valid = false;
            mensajes.push("El campo 'Id del catálogo' no puede quedar vacío.");
        }

        // Validar fecha de vencimiento
        const fechaInput = document.querySelector("input[name='fecha_vencimiento']");
        const fechaValor = fechaInput.value;
        if (!fechaValor) {
            valid = false;
            mensajes.push("La fecha de vencimiento es obligatoria.");
        } else {
            const hoy = new Date();
            hoy.setHours(0, 0, 0, 0);
            const fecha = new Date(fechaValor);
            if (fecha < hoy) {
                valid = false;
                mensajes.push("La fecha de vencimiento no puede ser anterior al día de hoy.");
            }
        }

        // Validar lote
        const lote = document.getElementById("lote").value.trim();
        const loteRegex = /^[A-Za-z0-9]{1,15}$/;
        if (!loteRegex.test(lote)) {
            valid = false;
            mensajes.push("El lote debe contener solo letras y números, máximo 15 caracteres.");
        }

        // Validar tipo de alimento
        const tipo = document.getElementById("tipo_alimento").value;
        if (!tipo) {
            valid = false;
            mensajes.push("El tipo de alimento no puede quedar vacío.");
        }

        // Validar peso contenido
        const peso = document.getElementById("peso_contenido").value;
        if (!peso || isNaN(peso) || Number(peso) <= 0) {
            valid = false;
            mensajes.push("El peso contenido debe ser un número válido mayor a 0.");
        }

        // Validar indicación específica
        const indicacion = document.getElementById("indicacion_especifica").value.trim();
        if (indicacion.length > 300) {
            valid = false;
            mensajes.push("La indicación específica no debe superar los 300 caracteres.");
        }

        // Mostrar errores si los hay
        if (!valid) {
            event.preventDefault();
            alert(mensajes.join("\n"));
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", function (event) {
        let valid = true;
        let mensajes = [];

        // Validar nombre
        const nombre = document.getElementById("nombre").value.trim();
        const nombreRegex = /^[A-Za-z\s]+$/; // solo letras y espacios
        if (!nombre) {
            valid = false;
            mensajes.push("El nombre no puede quedar vacío.");
        } else if (!nombreRegex.test(nombre)) {
            valid = false;
            mensajes.push("El nombre no debe contener números ni símbolos.");
        }

        // Validar precio
        const precio = document.getElementById("precio").value.trim();
        if (!precio) {
            valid = false;
            mensajes.push("El precio no puede quedar vacío.");
        } else if (isNaN(precio) || Number(precio) <= 0) {
            valid = false;
            mensajes.push("El precio debe ser un número válido mayor a 0.");
        }

        // Validar stock
        const stock = document.getElementById("stock").value.trim();
        if (!stock) {
            valid = false;
            mensajes.push("El stock no puede quedar vacío.");
        } else if (!/^\d+$/.test(stock)) {
            valid = false;
            mensajes.push("El stock debe ser un número entero.");
        } else if (Number(stock) < 0) {
            valid = false;
            mensajes.push("El stock no puede ser menor que cero.");
        }

        // Validar item
        const item = document.getElementById("opcionCatalogo").value;
        if (!item) {
            valid = false;
            mensajes.push("Debe seleccionar un item del catálogo.");
        }

        // Mostrar errores si los hay
        if (!valid) {
            event.preventDefault();
            alert(mensajes.join("\n"));
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formDesparasitante");

    form.addEventListener("submit", function (event) {
        let valid = true;
        let mensajes = [];

        // Validar catálogo
        const id = document.getElementById("id").value;
        if (!id) {
            valid = false;
            mensajes.push("El catálogo no puede quedar vacío.");
        }

        // Validar descripción
        const descripcion = document.getElementById("descripcion").value.trim();
        if (!descripcion) {
            valid = false;
            mensajes.push("La descripción no puede quedar vacía.");
        } else if (descripcion.length > 200) {
            valid = false;
            mensajes.push("La descripción no debe superar los 200 caracteres.");
        }

        // Validar laboratorio (vía de administración)
        const via = document.getElementById("via_administracion").value;
        if (!via) {
            valid = false;
            mensajes.push("El laboratorio (vía de administración) no puede quedar vacío.");
        }

        // Validar rango de peso
        const rango = document.getElementById("rango_peso").value.trim();
        if (!rango) {
            valid = false;
            mensajes.push("El rango de peso no debe quedar vacío.");
        }

        // Mostrar errores si los hay
        if (!valid) {
            event.preventDefault();
            alert(mensajes.join("\n"));
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formServicio");

    form.addEventListener("submit", function (event) {
        let valid = true;
        let mensajes = [];

        // Validar id del catálogo
        const id = document.getElementById("id").value;
        if (!id) {
            valid = false;
            mensajes.push("El id del catálogo no puede quedar vacío.");
        }

        // Validar descripción
        const descripcion = document.getElementById("descripcion").value.trim();
        if (!descripcion) {
            valid = false;
            mensajes.push("La descripción no puede quedar vacía.");
        } else if (descripcion.length > 200) {
            valid = false;
            mensajes.push("La descripción no debe superar los 200 caracteres.");
        }

        // Validar duración estimada
        const duracion = document.getElementById("duracion_estimada").value;
        if (!duracion) {
            valid = false;
            mensajes.push("La duración estimada no puede quedar vacía.");
        }

        // Mostrar errores si los hay
        if (!valid) {
            event.preventDefault();
            alert(mensajes.join("\n"));
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formVacuna");

    if (!form) {
        console.error("No se encontró el formulario con id 'formVacuna'");
        return;
    }

    form.addEventListener("submit", function (event) {
        let valid = true;
        let mensajes = [];

        // Validar id del catálogo
        const id = document.getElementById("id").value;
        if (!id) {
            valid = false;
            mensajes.push("El id del catálogo no puede quedar vacío.");
        }

        // Validar descripción
        const descripcion = document.getElementById("descripcion").value.trim();
        if (!descripcion) {
            valid = false;
            mensajes.push("La descripción no puede quedar vacía.");
        } else if (descripcion.length > 300) {
            valid = false;
            mensajes.push("La descripción no debe superar los 300 caracteres.");
        }

        // Validar laboratorio
        // OJO: en tu HTML el input tiene id="Laboratorio" con L mayúscula
        const laboratorio = document.getElementById("Laboratorio").value.trim();
        const labRegex = /^[A-Za-z\s\.\,\-]+$/; // letras, espacios y símbolos básicos
        if (!laboratorio) {
            valid = false;
            mensajes.push("El laboratorio no puede quedar vacío.");
        } else if (!labRegex.test(laboratorio)) {
            valid = false;
            mensajes.push("El laboratorio solo debe incluir letras y símbolos, no números.");
        }

        // Validar periodo de refuerzo
        const periodo = document.getElementById("periodo_refuerzo").value.trim();
        if (!periodo) {
            valid = false;
            mensajes.push("El periodo de refuerzo no puede quedar vacío.");
        }
        // Puede contener letras y números, así que no aplicamos restricción adicional

        // Mostrar errores si los hay
        if (!valid) {
            event.preventDefault();
            alert(mensajes.join("\n"));
        }
    });
});


