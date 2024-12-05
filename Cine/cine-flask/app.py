from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import pymysql
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar flash messages

# Configuración de conexión a la base de datos
db = pymysql.connect(host='localhost', user='root', password='', database='cine')
cursor = db.cursor()

@app.route('/cartelera')
def cartelera():
    return render_template('cartelera.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/precios')
def precios():
    return render_template('precios.html')

@app.route('/compra', methods=['GET', 'POST'])
def compra():
    if request.method == 'POST':
        pelicula = request.form['pelicula']
        cantidad = request.form['cantidad']
        nombre_banco = request.form['nombre_banco']
        numero_cuenta = request.form['numero_cuenta']

        # Insertar en la base de datos la compra de boletos
        query = "INSERT INTO boletos (pelicula, cantidad) VALUES (%s, %s)"
        cursor.execute(query, (pelicula, cantidad))
        db.commit()

        # Obtener el ID de la compra reciente
        id_boletos = cursor.lastrowid

        # Guardar los datos de pago en la base de datos
        query_pago = "INSERT INTO pagos (id_boletos, nombre_banco, numero_cuenta) VALUES (%s, %s, %s)"
        cursor.execute(query_pago, (id_boletos, nombre_banco, numero_cuenta))
        db.commit()

        # Generar el ticket en formato PDF
        return generar_ticket(pelicula, cantidad)

    return render_template('compra.html')

@app.route('/noticias')
def noticias():
    return render_template('noticias.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']

        # Crear el mensaje de correo (simulado)
        flash('Mensaje enviado exitosamente', 'success')

        # Aquí podrías guardar en la base de datos o realizar otras acciones

        return redirect(url_for('contacto'))  # Redirige de vuelta a la página de contacto

    return render_template('contacto.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        # Hash de la contraseña antes de verificarla
        hashed_password = hashlib.sha256(contraseña.encode()).hexdigest()

        # Verificar las credenciales
        query = "SELECT * FROM usuarios WHERE email = %s AND contraseña = %s"
        cursor.execute(query, (email, hashed_password))
        usuario = cursor.fetchone()

        if usuario:
            flash('¡Bienvenido de nuevo!', 'success')
            return redirect(url_for('index'))  # Redirige al inicio después de iniciar sesión
        else:
            flash('Credenciales incorrectas. Intenta nuevamente.', 'error')

    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contraseña = request.form['contraseña']
        confirmar_contraseña = request.form['confirmar_contraseña']

        # Validación de contraseñas
        if contraseña != confirmar_contraseña:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('registro'))

        # Hash de la contraseña antes de guardarla
        hashed_password = hashlib.sha256(contraseña.encode()).hexdigest()

        # Insertar en la base de datos
        try:
            query = "INSERT INTO usuarios (nombre, email, contraseña) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, email, hashed_password))
            db.commit()
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('index'))  # Redirige al home después del registro
        except Exception as e:
            flash(f'Error al registrar el usuario: {e}', 'error')
            return redirect(url_for('registro'))

    return render_template('registro.html')

@app.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    # Obtener los datos del formulario
    nombre = request.form['nombre']
    email = request.form['email']
    mensaje = request.form['mensaje']

    # Aquí puedes agregar la lógica para guardar en la base de datos o enviar un correo
    # Si usas un correo, puedes usar el código de la función de contacto que ya tienes

    # Simulación de mensaje enviado
    flash('Mensaje enviado exitosamente', 'success')

    return redirect(url_for('contacto'))  # Redirige de vuelta a la página de contacto

def generar_ticket(pelicula, cantidad):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Diseño básico del ticket
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Cine Profesional")
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, "------------------------------------------------")
    c.drawString(100, 680, f"Ticket de Compra")
    c.drawString(100, 660, f"Película: {pelicula}")
    c.drawString(100, 640, f"Cantidad de Boletos: {cantidad}")
    c.drawString(100, 620, "------------------------------------------------")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 600, "¡Gracias por su compra!")
    c.setFont("Helvetica", 10)
    c.drawString(100, 580, "Este ticket es válido únicamente para el día de la compra.")
    c.drawString(100, 560, "Cine Profesional - Todos los derechos reservados.")

    c.save()

    # Movemos el cursor a la posición de inicio
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="ticket.pdf")

if __name__ == '__main__':
    app.run(debug=True)
