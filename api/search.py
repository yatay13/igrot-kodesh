from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Leer el tema buscado por el usuario
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        user_query = data.get('query', '')

        # Instrucción para que GPT identifique, busque o traduzca cartas del Rebbe
        prompt = f"""
        Eres un erudito e historiador experto en el Igrot Kodesh (las cartas del Rebbe de Lubavitch, Rabbi Menachem Mendel Schneerson).
        El usuario busca cartas sobre el tema o consulta: "{user_query}".

        Trae 2 o 3 cartas relevantes que el Rebbe escribió sobre este tema exacto o conceptos directamente relacionados. 
        Si hay cartas famosas de Igrot Kodesh sobre esto, cita sus volúmenes y fechas aproximadas/exactas.

        Devuelve la respuesta ÚNICAMENTE en formato JSON con la siguiente estructura exacta:
        [
          {{
            "letter_id": "Volumen X - Carta #XXXX",
            "hebrew_date": "Fecha en hebreo (ej: כ"ד אלול תשכ"ב)",
            "original_text": "Texto extracto en hebreo o idish original relevante de la carta",
            "translated_text": "Traducción clara, fiel y explicativa en español del mensaje del Rebbe"
          }}
        ]
        NO agregues ningún texto fuera del arreglo JSON.
        """

        # Enviar petición a OpenAI
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            data=json.dumps({
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }).encode('utf-8')
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read()
                res_json = json.loads(res_body.decode('utf-8'))
                content = res_json['choices'][0]['message']['content'].strip()
                
                # Limpiar la respuesta si trae formato markdown
                if content.startswith("```json"):
                    content = content[7:-3].strip()
                elif content.startswith("```"):
                    content = content[3:-3].strip()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
