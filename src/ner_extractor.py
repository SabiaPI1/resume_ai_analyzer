import re
import spacy
import requests

try:
    nlp = spacy.load("ru_core_news_sm")
except OSError:
    nlp = None
    print("Внимание: модель ru_core_news_sm не найдена. Скачайте: python -m spacy download ru_core_news_sm")

def extract_contacts(text):
    """Извлекает email, телефон и ссылку (только профессиональные ресурсы)."""
    # Очищаем текст от мусорных пробелов
    clean_text = text.replace(" .", ".").replace(" @", "@").replace("@ ", "@")
    clean_text_for_url = text.replace("\n", "").replace(" ", "")

    # Регулярки для почты и телефона
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"(\+7|8)?\s*\(?\d{3}\)?\s*\d{3}[-\s]?\d{2}[-\s]?\d{2}"
    
    # СТРОГИЙ ПАТТЕРН: ищем только GitHub, LinkedIn, GitLab
    url_pattern = r"(?:https?://)?(?:www\.)?(?:github\.com|linkedin\.com|gitlab\.com)[a-zA-Z0-9./_-]+"
    
    email_match = re.search(email_pattern, clean_text)
    phone_match = re.search(phone_pattern, text)
    url_match = re.search(url_pattern, clean_text_for_url)
    
    return {
        "email": email_match.group() if email_match else None,
        "phone": phone_match.group() if phone_match else None,
        "portfolio": url_match.group() if url_match else None
    }

def extract_nlp_entities(text):
    """Извлекает имена и организации с помощью SpaCy (NLP)"""
    if not nlp:
        return {"names": [], "orgs":[]}
    
    # 1. ПРЕПРОЦЕССИНГ: меняем переносы строк на точки. 
    # Так SpaCy поймет, где заканчивается строка 
    clean_text = text.replace('\n', '. ').replace('..', '.')
    doc = nlp(clean_text[:2000]) 
    
    # 2. ПОСТПРОЦЕССИНГ: список стоп-слов (False Positives), типичных для структуры резюме
    stop_words = {"Нету", "Обо", "Опыт", "Навыки", "Резюме", "Образование", "Контакты"}
    
    names = []
    orgs =[]
    
    for ent in doc.ents:
        # Убираем случайные точки и пробелы по краям
        ent_text = ent.text.strip('. ')
        
        if ent.label_ == "PER":
            # Фильтруем мусорные слова из найденного имени 
            filtered_words =[w for w in ent_text.split() if w not in stop_words]
            clean_name = " ".join(filtered_words).strip()
            
            # Добавляем, только если длина больше 2 букв и это не пустое слово
            if len(clean_name) > 2 and clean_name not in stop_words:
                names.append(clean_name)
                
        elif ent.label_ == "ORG":
            if ent_text not in stop_words and len(ent_text) > 2:
                orgs.append(ent_text)
    
    return {"names": list(set(names)), "orgs": list(set(orgs))}

def check_grammar(text):
    """Проверяет орфографию с помощью API Яндекс.Спеллера."""
    clean_text = text.replace(" .", ".").replace(" ,", ",")
    
    url = "https://speller.yandex.net/services/spellservice.json/checkText"
    
    try:
        params = {
            'text': clean_text[:1500],
            'lang': 'ru,en',
            'options': 20
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if not result:
                return [] 
                
            errors = []
            for item in result[:5]:
                replacements = ", ".join(item['s']) if item['s'] else "нет вариантов"
                errors.append({
                    "message": f"Опечатка: «{item['word']}». Замена: {replacements}",
                    "context": f"... {item['word']} ..."
                })
            return errors
        else:
            return[{"message": f"Ошибка сервера Яндекс. Код: {response.status_code}", "context": ""}]
            
    except Exception as e:
        return[{"message": f"Не удалось подключиться к Спеллеру: {str(e)}", "context": ""}]