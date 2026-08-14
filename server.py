from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI(title="Servidor Igrot Kodesh AI")

class SearchQuery(BaseModel):
    query: str

# Base de cartas procesadas (Ejemplo)
BD_CARTAS = [
    {
        "letter_id": "Volumen 18 - Carta #6812",
        "hebrew_date": 'כ"ד אלול ה\'תשכ"ב',
        "topics": ["negocio", "parnasa", "sustento", "trabajo", "fe"],
        "original_text": 'ב"ה. שלום וברכה. במענה למכתבו... בנוגע לעסק ומסחר, הנה המאמין בהשגחה פרטית יודע שפרנסתו קצובה מאת הבורא...',
        "translated_text": "Con la ayuda de D-s. Saludos y bendiciones. En respuesta a su carta respecto al negocio y comercio: Aquel que cree en la Providencia Divina sabe que su sustento está decretado por el Creador Bendito Sea, y el esfuerzo del hombre es solo el recipiente natural para recibir la bendición. Por lo tanto, no hay razón para la desesperación o la ansiedad."
    }
]

@app.post("/api/search")
def search_letters(data: SearchQuery):
    user_query = data.query.lower()
    results = []

    # Búsqueda por coincidencia de palabras clave y temas
    for carta in BD_CARTAS:
        if any(topic in user_query for topic in carta["topics"]) or ("carta" in user_query):
            results.append(carta)

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)