from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import plotly
import plotly.graph_objs as go
import json

app = Flask(__name__)

# Database setup
DB_PATH = 'plant_journal.db'

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS plants 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS measurements 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, plant_id INTEGER, 
                 ph REAL, ec REAL, water_temp REAL, 
                 date DATE DEFAULT CURRENT_DATE, FOREIGN KEY(plant_id) REFERENCES plants(id))''')
    conn.commit()
    conn.close()

create_tables()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM plants")
    plants = c.fetchall()
    conn.close()
    return render_template('index.html', plants=plants)

@app.route('/add_measurement', methods=['POST'])
def add_measurement():
    plant_id = request.form['plant_id']
    ph = request.form['ph']
    ec = request.form['ec']
    water_temp = request.form['water_temp']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO measurements (plant_id, ph, ec, water_temp) VALUES (?, ?, ?, ?)",
              (plant_id, ph, ec, water_temp))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/add_plant', methods=['POST'])
def add_plant():
    plant_name = request.form['plant_name']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO plants (name) VALUES (?)", (plant_name,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/dashboard/<int:plant_id>')
def dashboard(plant_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM measurements WHERE plant_id=?", (plant_id,))
    measurements = c.fetchall()

    dates = [m[5] for m in measurements]
    ph_values = [m[2] for m in measurements]
    ec_values = [m[3] for m in measurements]
    water_temp_values = [m[4] for m in measurements]

    # Create graphs
    ph_graph = go.Scatter(x=dates, y=ph_values, mode='lines', name='pH')
    ec_graph = go.Scatter(x=dates, y=ec_values, mode='lines', name='EC')
    water_temp_graph = go.Scatter(x=dates, y=water_temp_values, mode='lines', name='Water Temperature')

    graphs = [ph_graph, ec_graph, water_temp_graph]
    graph_json = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    conn.close()
    return render_template('dashboard.html', graph_json=graph_json)

if __name__ == '__main__':
    app.run(debug=True)