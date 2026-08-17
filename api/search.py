from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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

            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }

            req = urllib.request.Request(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload).encode('utf-8')
            )

            with urllib.request.urlopen(req) as response:
                res_body = response.read()
                res_json = json.loads(res_body.decode('utf-8'))
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()

                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:-3].strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:-3].strip()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(raw_text.encode('utf-8'))

        except urllib.error.HTTPError as err:
            err_body = err.read().decode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([{
                "letter_id": f"Error API ({err.code})",
                "hebrew_date": "Respuesta Google",
                "original_text": err_body,
                "translated_text": "Revisa los detalles técnicos en la columna izquierda."
            }]).encode('utf-8'))
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([{
                "letter_id": "Error de Configuración",
                "hebrew_date": "Atención",
                "original_text": str(e),
                "translated_text": "Verifica que GEMINI_API_KEY esté correctamente guardada en Vercel."
            }]).encode('utf-8'))

# Asignación explícita para que el detector de Vercel encuentre la aplicación
app = handler
