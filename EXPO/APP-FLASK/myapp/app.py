from flask import Flask, render_template, request, session, redirect
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Davila'
app.config['MYSQL_PASSWORD'] = 'Davila12'
app.config['MYSQL_DB'] = 'tecsup'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Inicialización de las extensiones
bcrypt = Bcrypt(app)
mysql = MySQL(app)

# Configuración de la clave secreta para las sesiones
app.secret_key = 'tu_clave_secreta'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect('/menu')
        else:
            return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        telefono = request.form['telefono']

        # Verificar si el email ya está registrado en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user:
            return render_template('register.html', error='El email ya está registrado')

        # Verificar si las contraseñas coinciden
        if password != confirm_password:
            return render_template('register.html', error='Las contraseñas no coinciden')

        # Insertar el nuevo usuario en la base de datos
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (nombre, apellidos, email, password, telefono) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, apellidos, email, hashed_password, telefono))
        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/menu')
def menu():
    if 'user_id' in session:
        return render_template('menu.html')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
