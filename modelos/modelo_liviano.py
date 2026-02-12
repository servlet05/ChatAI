# Modelo de IA ultra liviano para PCs de bajos recursos
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

class ChatModeloLiviano:
    def __init__(self):
        # Usando DistilGPT2 - solo 82M parámetros
        self.model_name = "distilgpt2"
        self.tokenizer = None
        self.model = None
        self.cargado = False
        self.max_length = 50  # Reducido al mínimo
        
    def cargar(self):
        """Cargar modelo de forma optimizada"""
        try:
            print("🔄 Cargando modelo DistilGPT2 (82M parámetros)...")
            
            # Configurar para CPU y bajo consumo
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                padding_side='left'
            )
            
            # Añadir token de padding si no existe
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Usar float32 para compatibilidad
                low_cpu_mem_usage=True
            )
            
            # Modo evaluación para menor consumo
            self.model.eval()
            
            self.cargado = True
            print("✅ Modelo cargado exitosamente!")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False
    
    def generar_respuesta(self, mensaje, historial=[]):
        """Generar respuesta con mínimo consumo de recursos"""
        if not self.cargado:
            return "Error: Modelo no cargado"
        
        try:
            # Construir contexto simple
            contexto = ""
            for h in historial[-3:]:  # Solo últimos 3 mensajes
                contexto += f"{h['usuario']}: {h['mensaje']}\n"
            
            entrada = f"{contexto}Usuario: {mensaje}\nAsistente:"
            
            # Tokenizar
            inputs = self.tokenizer.encode(
                entrada, 
                return_tensors='pt',
                truncation=True,
                max_length=200
            )
            
            # Generar sin gradient para ahorrar memoria
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=self.max_length,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.2
                )
            
            # Decodificar respuesta
            respuesta = self.tokenizer.decode(
                outputs[0], 
                skip_special_tokens=True
            )
            
            # Extraer solo la parte del asistente
            if "Asistente:" in respuesta:
                respuesta = respuesta.split("Asistente:")[-1].strip()
            
            # Limpiar respuesta
            lineas = respuesta.split('\n')
            respuesta = lineas[0].strip()
            
            if not respuesta:
                respuesta = "Entendido. ¿Algo más?"
            
            return respuesta
            
        except Exception as e:
            print(f"Error generando respuesta: {e}")
            return "Lo siento, tuve un problema procesando eso."

# Instancia global del modelo
modelo_ia = ChatModeloLiviano()
