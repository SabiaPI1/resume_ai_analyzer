import os
import time
import logging
from dotenv import load_dotenv
from gigachat import GigaChat

logging.basicConfig(level=logging.INFO)
load_dotenv()

class ResumeAnalyzerLLM:
    def __init__(self):
        self.giga_token = os.getenv("GIGACHAT_TOKEN")
        if not self.giga_token:
            logging.error("GIGACHAT_TOKEN не найден в .env!")

    def analyze_resume(self, resume_text, target_job="IT-специалист"):
        if not self.giga_token:
            return "❌ Ошибка: Не указан GIGACHAT_TOKEN. Добавьте его в файл .env."

        truncated_text = resume_text[:3000]

        prompt = f"""Ты опытный IT-рекрутер из компании VK. 
Кандидат претендует на должность: {target_job}.

Твоя задача — проанализировать текст резюме и строго оценить его.
Действуй по следующему плану:
1. ОЦЕНКА: Поставь резюме оценку от 1 до 10 баллов по степени соответствия идеальному кандидату на позицию "{target_job}". (Напиши это крупно в самом начале).
2. АНАЛИЗ НАВЫКОВ: Сравни навыки кандидата с актуальными требованиями работодателей (на основе твоих знаний рынка труда для {target_job}). Напиши, каких ключевых технологий не хватает.
3. ОШИБКИ: Укажи на критические ошибки в тексте (структура, орфография, лишняя вода, нерелевантный опыт).
4. РЕКОМЕНДАЦИИ: Дай 3 четких совета, как улучшить резюме, чтобы точно пройти скрининг.

Текст резюме кандидата:
{truncated_text}
"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with GigaChat(credentials=self.giga_token, verify_ssl_certs=False, scope="GIGACHAT_API_PERS", timeout=60) as giga:
                    response = giga.chat(prompt)
                    return response.choices[0].message.content
            except Exception as e:
                error_msg = str(e)
                logging.warning(f"Попытка {attempt + 1} завершилась ошибкой: {error_msg}")
                if "UNEXPECTED_EOF_WHILE_READING" in error_msg:
                    if attempt == max_retries - 1:
                        return "❌ Ошибка: Сервер Сбербанка разорвал соединение. Проверьте, что VPN отключен."
                    time.sleep(2)
                else:
                    return f"❌ Произошла ошибка при обращении к нейросети GigaChat: {e}"
                    
        return "❌ Не удалось получить ответ от GigaChat."