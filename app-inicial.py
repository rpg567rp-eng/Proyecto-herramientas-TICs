"""
=============================================================
  DC - Sistema de Gestión de Producción
  Versión 1.0 (Base Mínima)
  Solo pedidos básicos, sin inventario, sin IA, sin exportaciones
=============================================================
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = 'pedidos.json'

# Cargar datos iniciales si no existen
def inicializar_datos():
    if not os.path.exists(DATA_FILE):
        datos_iniciales = {
            "pedidos": [],
            "contador": 0
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos_iniciales, f, ensure_ascii=False, indent=2)

def cargar_datos():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_datos(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

# Obtener todos los pedidos
@app.route('/api/pedidos', methods=['GET'])
def get_pedidos():
    data = cargar_datos()
    return jsonify({"pedidos": data['pedidos']})

# Crear nuevo pedido
@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    data = cargar_datos()
    body = request.get_json()
    
    data['contador'] += 1
    nuevo_id = f"DC-{data['contador']:04d}"
    ahora = datetime.now().isoformat()
    
    nuevo_pedido = {
        "id": nuevo_id,
        "cliente": body['cliente'],
        "producto": body['producto'],
        "cantidad": body['cantidad'],
        "fechaEntrega": body['fechaEntrega'],
        "estado": "pendiente",
        "creadoEn": ahora,
        "actualizadoEn": ahora
    }
    
    data['pedidos'].append(nuevo_pedido)
    guardar_datos(data)
    
    return jsonify({"success": True, "pedido": nuevo_pedido, "id": nuevo_id}), 201

# Actualizar estado de pedido
@app.route('/api/pedidos/<pedido_id>', methods=['PUT'])
def actualizar_pedido(pedido_id):
    data = cargar_datos()
    body = request.get_json()
    pedido = next((p for p in data['pedidos'] if p['id'] == pedido_id), None)
    
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    
    if 'estado' in body:
        pedido['estado'] = body['estado']
    pedido['actualizadoEn'] = datetime.now().isoformat()
    
    guardar_datos(data)
    return jsonify({"success": True, "pedido": pedido})

# Eliminar pedido
@app.route('/api/pedidos/<pedido_id>', methods=['DELETE'])
def eliminar_pedido(pedido_id):
    data = cargar_datos()
    data['pedidos'] = [p for p in data['pedidos'] if p['id'] != pedido_id]
    guardar_datos(data)
    return jsonify({"success": True})

if __name__ == '__main__':
    inicializar_datos()
    print("\n🍬 DC — Servidor iniciando (Versión Básica)...")
    print("   Abre tu navegador en: http://localhost:5000")
    print("   Presiona Ctrl+C para detener\n")
    app.run(debug=True, port=5000)