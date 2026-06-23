        /**
         * Función que se ejecuta al intentar enviar el formulario de registro.
         * Valida que los campos 'regPass' y 'regPassConfirm' sean idénticos.
         * @returns {boolean} Retorna false para detener el envío, true para enviarlo.
         */
        function validatePassword() {
            // Obtiene los valores de los campos de contraseña
            const password = document.getElementById('regPass').value;
            const confirmPassword = document.getElementById('regPassConfirm').value;
            
            // Obtiene el elemento del mensaje de error
            const errorMsg = document.getElementById('passError');

            // Verifica si las contraseñas son diferentes
            if (password !== confirmPassword) {
                // Muestra el mensaje de error
                errorMsg.style.display = 'block';
                // Detiene el envío del formulario
                return false;
            } else {
                // Oculta el mensaje de error si ya estaba visible
                errorMsg.style.display = 'none';
                // Permite el envío del formulario
                return true;
            }
        }
        
        // --- CÓDIGO ADICIONAL PARA EL COMPORTAMIENTO TOGGLE (Registro/Login) ---
        
        const container = document.getElementById('container');
        const registerBtn = document.getElementById('register');
        const loginBtn = document.getElementById('login');

        // Si tienes las clases 'active' definidas en tu CSS para el efecto toggle, 
        // este código te permite cambiar entre los paneles.
        if (registerBtn && loginBtn && container) {
            registerBtn.addEventListener('click', () => {
                container.classList.add("active");
            });

            loginBtn.addEventListener('click', () => {
                container.classList.remove("active");
            });
        }

        // Función para validar la seguridad de la contraseña
function isPasswordSecure(password) {
    // La contraseña debe tener:
    // 1. Al menos 8 caracteres
    // 2. Al menos una letra mayúscula (?=.*[A-Z])
    // 3. Al menos una letra minúscula (?=.*[a-z])
    // 4. Al menos un dígito (?=.*\d)
    // 5. Al menos un carácter especial (?=.*[@$!%*?&])
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
}

// Función para validar el Login
function validateLogin() {
    let isValid = true;
    
    // Ocultar todos los errores de login
    document.getElementById('logEmailError').style.display = 'none';
    document.getElementById('logPassError').style.display = 'none';

    const email = document.getElementById('logEmail').value;
    const password = document.getElementById('logPass').value;

    // Validación de Correo Electrónico (no vacío ya lo hace required, pero verificamos formato)
    if (email.trim() === "" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        document.getElementById('logEmailError').textContent = "Ingresa un correo electrónico válido.";
        document.getElementById('logEmailError').style.display = 'block';
        isValid = false;
    }

    // Validación de Contraseña Segura (para Login)
    if (!isPasswordSecure(password)) {
        document.getElementById('logPassError').style.display = 'block';
        isValid = false;
    }

    return isValid;
}


// Función para validar el Registro
function validateRegister() {
    let isValid = true;

    // Ocultar todos los errores de registro
    document.getElementById('regDocError').style.display = 'none';
    document.getElementById('regEmailError').style.display = 'none';
    document.getElementById('regTelError').style.display = 'none';
    document.getElementById('regPassError').style.display = 'none';
    document.getElementById('regPassConfirmError').style.display = 'none';

    const doc = document.getElementById('regDoc').value;
    const email = document.getElementById('regEmail').value;
    const tel = document.getElementById('regTel').value;
    const pass = document.getElementById('regPass').value;
    const confirmPass = document.getElementById('regPassConfirm').value;
    
    // **1. Validación de Documento de Identidad (Mínimo 6)**
    if (doc.length < 6) {
        document.getElementById('regDocError').style.display = 'block';
        isValid = false;
    }

    // **2. Validación de Correo Electrónico (Formato)**
    if (email.trim() === "" || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        document.getElementById('regEmailError').textContent = "Ingresa un correo electrónico válido.";
        document.getElementById('regEmailError').style.display = 'block';
        isValid = false;
    }

    // **3. Validación de Teléfono (Mínimo 10)**
    if (tel.length < 10) {
        document.getElementById('regTelError').style.display = 'block';
        isValid = false;
    }

    // **4. Validación de Contraseña Segura**
    if (!isPasswordSecure(pass)) {
        document.getElementById('regPassError').style.display = 'block';
        isValid = false;
    }

    // **5. Validación de Confirmación de Contraseña**
    if (pass !== confirmPass) {
        document.getElementById('regPassConfirmError').style.display = 'block';
        isValid = false;
    }

    // El atributo `required` ya valida que no estén vacíos. Si pasa las validaciones de longitud/seguridad/match, se permite el envío.
    return isValid;
}

// **Código para cambiar entre formularios (si lo tenías en script_login.js)**


if (registerBtn) {
    registerBtn.addEventListener('click', () => {
        container.classList.add("active");
    });
}

if (loginBtn) {
    loginBtn.addEventListener('click', () => {
        container.classList.remove("active");
    });
}
        