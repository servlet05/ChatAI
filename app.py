# Servidor web minimalista para chat IA
from flask import Flask, render_template, request, jsonify
from modelos.modelo_liviano import modelo_ia
import threading
import time

app = Flask(__name__)

# Historial de conversaciones (en memoria para simplicidad)
conversaciones = {}
modelo_listo = False

@app.route('/')
def index():
    """Página principal del chat"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint del chat"""
    global modelo_listo
    
    data = request.json
    mensaje = data.get('mensaje', '')
    sesion_id = data.get('sesion_id', 'default')
    
    if not mensaje:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    # Inicializar historial si no existe
    if sesion_id not in conversaciones:
        conversaciones[sesion_id] = []
    
    # Agregar mensaje del usuario
    conversaciones[sesion_id].append({
        'tipo': 'usuario',
        'mensaje': mensaje,
        'timestamp': time.time()
    })
    
    # Generar respuesta solo si el modelo está cargado
    if modelo_listo:
        respuesta = modelo_ia.generar_respuesta(
            mensaje, 
            conversaciones[sesion_id]
        )
    else:
        respuesta = "⏳ El modelo aún se está cargando. Espera un momento..."
    
    # Agregar respuesta al historial
    conversaciones[sesion_id].append({
        'tipo': 'asistente',
        'mensaje': respuesta,
        'timestamp': time.time()
    })
    
    # Limitar historial para ahorrar memoria
    if len(conversaciones[sesion_id]) > 20:
        conversaciones[sesion_id] = conversaciones[sesion_id][-20:]
    
    return jsonify({
        'respuesta': respuesta,
        'sesion_id': sesion_id
    })

@app.route('/api/status', methods=['GET'])
def status():
    """Verificar estado del modelo"""
    return jsonify({
        'modelo_cargado': modelo_listo,
        'conversaciones_activas': len(conversaciones)
    })

def cargar_modelo_background():
    """Cargar modelo en segundo plano"""
    global modelo_listo
    time.sleep(1)  # Pequeña espera para que la web cargue primero
    modelo_listo = modelo_ia.cargar()

if __name__ == '__main__':
    # Iniciar carga del modelo en segundo plano
    thread = threading.Thread(target=cargar_modelo_background)
    thread.daemon = True
    thread.start()
    
    # Iniciar servidor web
    print("🌐 Servidor web iniciado en http://localhost:5000")
    print("📦 Modelo cargándose en segundo plano...")
    app.run(host='0.0.0.0', port=5000, debug=False)
