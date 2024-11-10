from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from fpdf import FPDF

app = Flask(__name__)
DATABASE = 'reparaciones.db'

# Función para crear la tabla si no existe
def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            telefono_cliente TEXT,
            email_cliente TEXT,
            marca TEXT,
            modelo TEXT,
            tipo TEXT,
            numero_serie TEXT,
            descripcion TEXT,
            estado TEXT DEFAULT 'En revisión',
            empresa_derivadora TEXT,
            novedades TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Ruta principal para mostrar los equipos
@app.route('/')
def index():
    create_table()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipos')
    equipos = cursor.fetchall()
    conn.close()
    return render_template('index.html', equipos=equipos)

# Ruta para agregar un nuevo equipo
@app.route('/nuevo_equipo', methods=['GET', 'POST'])
def nuevo_equipo():
    create_table()
    if request.method == 'POST':
        nombre_cliente = request.form['nombre_cliente']
        telefono_cliente = request.form['telefono_cliente']
        email_cliente = request.form['email_cliente']
        marca = request.form['marca']
        modelo = request.form['modelo']
        tipo = request.form['tipo']
        numero_serie = request.form['numero_serie']
        descripcion = request.form['descripcion']
        empresa_derivadora = request.form['empresa_derivadora']  # Verificar que se capture correctamente

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO equipos (nombre_cliente, telefono_cliente, email_cliente, marca, modelo, tipo, numero_serie, descripcion, empresa_derivadora)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre_cliente, telefono_cliente, email_cliente, marca, modelo, tipo, numero_serie, descripcion, empresa_derivadora))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('nuevo_equipo.html')

#Editar equipo

@app.route('/editar_equipo/<int:id>', methods=['GET', 'POST'])
def editar_equipo(id):
    create_table()
    if request.method == 'POST':
        nombre_cliente = request.form['nombre_cliente']
        telefono_cliente = request.form['telefono_cliente']
        email_cliente = request.form['email_cliente']
        marca = request.form['marca']
        modelo = request.form['modelo']
        tipo = request.form['tipo']
        numero_serie = request.form['numero_serie']
        descripcion = request.form['descripcion']
        empresa_derivadora = request.form['empresa_derivadora']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE equipos
            SET nombre_cliente = ?, telefono_cliente = ?, email_cliente = ?, marca = ?, modelo = ?, tipo = ?, numero_serie = ?, descripcion = ?, empresa_derivadora = ?
            WHERE id = ?
        ''', (nombre_cliente, telefono_cliente, email_cliente, marca, modelo, tipo, numero_serie, descripcion, empresa_derivadora, id))
        conn.commit()
        conn.close()
        return redirect(url_for('consulta', id=id))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipos WHERE id = ?', (id,))
    equipo = cursor.fetchone()
    conn.close()
    return render_template('editar_equipo.html', equipo=equipo)

# Ruta para consultar detalles de un equipo
@app.route('/consulta/<int:id>')
def consulta(id):
    create_table()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipos WHERE id = ?', (id,))
    equipo = cursor.fetchone()
    conn.close()
    return render_template('consulta.html', equipo=equipo)

# Ruta para actualizar el estado de un equipo
@app.route('/actualizar_estado/<int:id>', methods=['POST'])
def actualizar_estado(id):
    create_table()
    nuevo_estado = request.form['estado']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE equipos SET estado = ? WHERE id = ?', (nuevo_estado, id))
    conn.commit()
    conn.close()
    return redirect(url_for('consulta', id=id))

# Ruta para emitir un remito en PDF
@app.route('/emitir_remito/<int:id>')
def emitir_remito(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipos WHERE id = ?', (id,))
    equipo = cursor.fetchone()
    conn.close()

    if equipo:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Remito de Retiro", ln=True, align="C")
        pdf.cell(200, 10, txt=f"ID del equipo: {equipo[0]}", ln=True)
        pdf.cell(200, 10, txt=f"Cliente: {equipo[1]}", ln=True)
        pdf.cell(200, 10, txt=f"Marca: {equipo[4]}", ln=True)
        pdf.cell(200, 10, txt=f"Modelo: {equipo[5]}", ln=True)
        pdf.cell(200, 10, txt=f"Descripción: {equipo[7]}", ln=True)
        pdf.output(f"static/remito_{id}.pdf")
        return redirect(f"/static/remito_{id}.pdf")
    return "Equipo no encontrado"

# Ruta para que los clientes verifiquen el estado de su equipo
@app.route('/verificar', methods=['GET', 'POST'])
def verificar():
    if request.method == 'POST':
        numero_serie = request.form['numero_serie']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM equipos WHERE numero_serie = ?', (numero_serie,))
        equipo = cursor.fetchone()
        conn.close()
        if equipo:
            return render_template('consulta.html', equipo=equipo)
        else:
            return "No se encontró un equipo con ese número de serie."
    return render_template('verificar.html')

# Ruta para agregar una novedad sobre un equipo
@app.route('/agregar_novedad/<int:id>', methods=['POST'])
def agregar_novedad(id):
    novedad = request.form['novedad']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE equipos SET novedades = COALESCE(novedades, "") || ? WHERE id = ?', (f"{novedad}\n", id))
    conn.commit()
    conn.close()
    return redirect(url_for('consulta', id=id))

#Eliminar equipo
@app.route('/eliminar_equipo/<int:id>', methods=['POST'])
def eliminar_equipo(id):
    create_table()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM equipos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
