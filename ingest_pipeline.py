import re
import json

class IgrosKodeshProcessor:
    def __init__(self):
        # Detecta los patrones típicos donde empieza y termina una carta del Rebbe
        self.start_pattern = r'(?=\bב"ה\b|\bבחי\s*ש\b)'

    def split_letters(self, text_from_pdf: str, volume_number: int):
        """ Divide un PDF continuo de cientos de páginas en cartas independientes """
        raw_letters = re.split(self.start_pattern, text_from_pdf)
        processed_letters = []

        for index, letter_raw in enumerate(raw_letters):
            letter_raw = letter_raw.strip()
            if len(letter_raw) < 40: # Ignorar páginas vacías o saltos
                continue

            # Extraer la fecha hebrea automáticamente si existe
            date_search = re.search(r'(\d{1,2}\s+[א-ת]+\s+[א-ת"]+)', letter_raw)
            hebrew_date = date_search.group(1) if date_search else "Fecha no especificada"

            processed_letters.append({
                "letter_id": f"Volumen {volume_number} - Carta #{index + 1}",
                "volume": volume_number,
                "hebrew_date": hebrew_date,
                "original_text": letter_raw
            })

        print(f"✅ Se procesaron {len(processed_letters)} cartas del Volumen {volume_number}.")
        return processed_letters

# Ejemplo de prueba local
if __name__ == "__main__":
    processor = IgrosKodeshProcessor()
    print("Módulo de lectura de Libros listo.")