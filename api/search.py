from http.server import BaseHTTPRequestHandler
import json
import os
import traceback
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Lista de modelos compatibles a probar en orden
CANDIDATE_MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.5-flash']

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            if not GEMINI_API_KEY:
                raise Exception("Falta la variable GEMINI_API_KEY en Vercel.")

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_query = data.get('query', '')

            prompt = f"""
            Eres un erudito e historiador experto en el Igrot Kodesh (las cartas del Rebbe de Lubavitch, Rabbi Menachem Mendel Schneerson).
            El usuario busca cartas sobre el tema o consulta: "{user_query}".

            Trae 2 o 3 cartas relevantes que el Rebbe escribió sobre este tema exacto o conceptos directamente relacionados. 
            Si hay cartas famosas de Igrot Kodesh sobre esto, cita sus volúmenes y fechas aproximadas/exactas.

            Devuelve la respuesta ÚNICAMENTE en formato JSON con la siguiente estructura exacta:
            [
              {{
                "letter_id": "Volumen X - Carta #XXXX",
                "hebrew_date": "Fecha en hebreo",
                "original_text": "Texto extracto en hebreo o idish original relevante de la carta",
                "translated_text": "Traducción clara, fiel y explicativa en español del mensaje del Rebbe"
              }}
            ]
            NO agregues ningún texto fuera del arreglo JSON.
            """

            client = genai.Client(api_key=GEMINI_API_KEY)

            response = None
            last_err = None

            # Probar cada modelo hasta que uno responda con éxito
            for model_name in CANDIDATE_MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        break
                except Exception as e:
                    last_err = e
                    continue

            if not response or not response.text:
                raise Exception(f"No se pudo consultar ningún modelo. Último error: {last_err}")

            raw_text = response.text.strip()

            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3].strip()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(raw_text.encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([{
                "letter_id": "Error de SDK/API",
                "hebrew_date": "Detalle Técnico",
                "original_text": str(e),
                "translated_text": "Traceback: " + traceback.format_exc()
            }]).encode('utf-8'))

app = handler
