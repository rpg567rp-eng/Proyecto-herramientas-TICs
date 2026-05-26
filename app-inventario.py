"""
=============================================================
  DC - Sistema de Gestión de Producción
  Versión 2.0 (Con inventario)
  Agrega gestión de inventario y validación de stock
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

def inicializar_datos():
    if not os.path.exists(DATA_FILE):
        datos_iniciales = {
            "pedidos": [],
            "inventario": [
                {"id": 1, "nombre": "Kit Cumpleaños", "emoji": "🎂", "stock": 20, "stockMinimo": 5, "stockInicial": 20},
                {"id": 2, "nombre": "Kinder Box", "emoji": "🍫", "stock": 15, "stockMinimo": 5, "stockInicial": 15},
                {"id": 3, "nombre": "Caja Hershey's", "emoji": "🍬", "stock": 8, "stockMinimo": 5, "stockInicial": 8},
                {"id": 4, "nombre": "Kit Corporativo", "emoji": "🎁", "stock": 10, "stockMinimo": 3, "stockInicial": 10},
                {"id": 5, "nombre": "Box Personalizado", "emoji": "✨", "stock": 3, "stockMinimo": 2, "stockInicial": 3}
            ],
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

# ==================== PEDIDOS ====================
@app.route('/api/pedidos', methods=['GET'])
def get_pedidos():
    data = cargar_datos()
    return jsonify({"pedidos": data['pedidos']})

@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    data = cargar_datos()
    body = request.get_json()
    
    # Verificar stock
    producto_nombre = body['producto']
    cantidad = int(body['cantidad'])
    prod = next((p for p in data['inventario'] if p['nombre'] == producto_nombre), None)
    
    if not prod:
        return jsonify({"error": "Producto no encontrado"}), 404
    if prod['stock'] < cantidad:
        return jsonify({"error": f"Stock insuficiente: solo quedan {prod['stock']} unidades"}), 400
    
    # Descontar stock
    prod['stock'] -= cantidad
    
    # Crear pedido
    data['contador'] += 1
    nuevo_id = f"DC-{data['contador']:04d}"
    ahora = datetime.now().isoformat()
    
    nuevo_pedido = {
        "id": nuevo_id,
        "cliente": body['cliente'],
        "telefono": body.get('telefono', ''),
        "producto": producto_nombre,
        "cantidad": cantidad,
        "fechaEntrega": body['fechaEntrega'],
        "estado": "pendiente",
        "notas": body.get('notas', ''),
        "creadoEn": ahora,
        "actualizadoEn": ahora
    }
    
    data['pedidos'].append(nuevo_pedido)
    guardar_datos(data)
    
    return jsonify({"success": True, "pedido": nuevo_pedido, "id": nuevo_id}), 201

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

@app.route('/api/pedidos/<pedido_id>', methods=['DELETE'])
def eliminar_pedido(pedido_id):
    data = cargar_datos()
    pedido = next((p for p in data['pedidos'] if p['id'] == pedido_id), None)
    
    # Devolver stock si no está despachado
    if pedido and pedido['estado'] != 'despachado':
        inv = next((p for p in data['inventario'] if p['nombre'] == pedido['producto']), None)
        if inv:
            inv['stock'] += pedido['cantidad']
    
    data['pedidos'] = [p for p in data['pedidos'] if p['id'] != pedido_id]
    guardar_datos(data)
    return jsonify({"success": True})

# ==================== INVENTARIO ====================
@app.route('/api/inventario', methods=['GET'])
def get_inventario():
    data = cargar_datos()
    return jsonify({"inventario": data['inventario']})

@app.route('/api/inventario/<int:prod_id>', methods=['PUT'])
def actualizar_stock(prod_id):
    data = cargar_datos()
    body = request.get_json()
    prod = next((p for p in data['inventario'] if p['id'] == prod_id), None)
    
    if not prod:
        return jsonify({"error": "Producto no encontrado"}), 404
    
    if 'stock' in body:
        prod['stock'] = int(body['stock'])
    
    guardar_datos(data)
    return jsonify({"success": True, "producto": prod})

if __name__ == '__main__':
    inicializar_datos()
    print("\n🍬 DC — Servidor iniciando (Versión con Inventario)...")
    print("   Abre tu navegador en: http://localhost:5000")
    print("   Presiona Ctrl+C para detener\n")
    app.run(debug=True, port=5000)