import io
import PyPDF2
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_text_from_pdf_bytes(pdf_bytes):
    """
    Извлекает текст из PDF файла с помощью PyPDF2 (без OCR).
    Подходит для стандартных резюме, сгенерированных в Word/HH/Google Docs.
    """
    try:
        # Читаем байты как PDF файл
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        
        extracted_text = ""
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
                
        return extracted_text.strip()
    except Exception as e:
        logging.error(f"Ошибка при чтении PDF: {e}")
        return None