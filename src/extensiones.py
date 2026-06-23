from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# Instancias compartidas
mysql = MySQL()
bcrypt = Bcrypt()
mail = Mail()