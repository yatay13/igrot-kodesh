from http.server import BaseHTTPRequestHandler
import json
import os
import traceback
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

CANDIDATE_MODELS = [
    'gemini-3.5-flash',
    'gemini-3.1-flash-lite',
    'gemini-2.5-flash-lite'
]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            if not GEMINI_API_KEY:
                raise Exception("Falta la variable GEMINI_API_KEY en Vercel.")

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_query = data.get('query', '')
            selected_letter = data.get('selected_letter', None)

            client = genai.Client(api_key=GEMINI_API_KEY)

            # CASO A: El usuario hizo clic en una carta para ver el detalle completo
            if selected_letter:
                prompt = f"""
                Eres un erudito e historiador experto en el Igrot Kodesh del Rebbe de Lubavitch.
                Proporciona el detalle completo de la siguiente carta:
                Identificador: {selected_letter.get('letter_id')}
                Fecha/Año: {selected_letter.get('hebrew_date')}
                Tema: {selected_letter.get('summary')}

                Devuelve ÚNICAMENTE un JSON con la siguiente estructura exacta:
                {{
                  "letter_id": "{selected_letter.get('letter_id')}",
                  "hebrew_date": "{selected_letter.get('hebrew_date')}",
                  "original_text": "Extracto representativo en hebreo/idish original de la carta",
                  "translated_text": "Traducción fiel, clara y detallada al español de la carta y sus enseñanzas principales"
                }}
                NO agregues ningún texto fuera del JSON.
                """
            # CASO B: Búsqueda general - Devolver entre 10 y 15 cartas (resumen ligero)
            else:
                prompt = f"""
                Eres un erudito e historiador experto en el Igrot Kodesh (las cartas del Rebbe de Lubavitch, Rabbi Menachem Mendel Schneerson).
                El usuario busca cartas sobre: "{user_query}".

                INSTRUCCIONES DE BÚSQUEDA AMPLIA:
                1. Sé flexible e incluyente: busca sinónimos, conceptos jasídicos paralelos y aplicaciones prácticas relacionadas con "{user_query}". 
                2. Encuentra entre 10 y 15 cartas de Igrot Kodesh relevantes a la búsqueda.
                3. Devuelve únicamente metadatos ligeros de cada carta.

                Devuelve ÚNICAMENTE un arreglo JSON con entre 10 y 15 objetos con la siguiente estructura exacta:
                [
                  {{
                    "letter_id": "Volumen X - Carta #XXXX",
                    "hebrew_date": "Año / Fecha hebrea (ej. 5712 / 1952)",
                    "summary": "Breve frase (10 palabras máx) explicando el enfoque de esta carta sobre el tema"
                  }}
                ]
                NO agregues ningún texto fuera del arreglo JSON.
                """

            response = None
            last_err = None

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
                "letter_id": "Error de Servidor",
                "hebrew_date": "Atención",
                "summary": str(e)
            }]).encode('utf-8'))

app = handler
