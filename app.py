import streamlit as st
from src.pdf_parser import extract_text_from_pdf_bytes
from src.ner_extractor import extract_contacts, check_grammar, extract_nlp_entities
from src.ai_analyzer import ResumeAnalyzerLLM

st.set_page_config(page_title="AI HR Assistant | VK Education", page_icon="💼", layout="wide")

st.title("🤖 Нейросеть для автоматического анализа резюме")
st.markdown("Сервис анализирует резюме, извлекает сущности (NLP), находит ошибки и использует LLM для рекомендаций.")

@st.cache_resource
def load_llm():
    return ResumeAnalyzerLLM()

llm = load_llm() 

st.sidebar.header("Загрузка резюме")

target_job = st.sidebar.text_input("На какую должность претендуете?", value="Junior Business Analyst")

uploaded_file = st.sidebar.file_uploader("Загрузите PDF-файл резюме", type=["pdf"])

if uploaded_file is not None:
    with st.spinner('Извлечение текста...'):
        resume_text = extract_text_from_pdf_bytes(uploaded_file.read())
        
    if resume_text:
        st.success("Текст успешно извлечен!")
        
        tab1, tab2, tab3 = st.tabs(["📊 NLP и Контакты", "📝 Орфография", "🧠 AI-Анализ (LLM)"])
        
        with tab1:
            st.subheader("Извлеченные данные")
            contacts = extract_contacts(resume_text)
            entities = extract_nlp_entities(resume_text)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Email", contacts['email'] if contacts['email'] else "❌ Не указан")
            col2.metric("Телефон", contacts['phone'] if contacts['phone'] else "❌ Не указан")
            col3.metric("Ссылка", contacts['portfolio'] if contacts['portfolio'] else "❌ Не указано")
            
            st.markdown("**Найденные персоны (NER):** " + (", ".join(entities['names']) if entities['names'] else "Не найдено"))
            st.markdown("**Упомянутые компании/технологии (NER):** " + (", ".join(entities['orgs']) if entities['orgs'] else "Не найдено"))
            
            with st.expander("Посмотреть сырой текст резюме"):
                st.text(resume_text)

        with tab2:
            st.subheader("Проверка грамматики (Яндекс.Спеллер)")
            with st.spinner("Проверка орфографии..."):
                errors = check_grammar(resume_text)
                
            if errors:
                st.warning(f"Найдено ошибок: {len(errors)} (показаны первые 5)")
                for err in errors:
                    st.markdown(f"**Ошибка:** {err['message']}")
                    st.markdown(f"> *Контекст:* {err['context']}")
            else:
                st.success("Орфографических ошибок не найдено!")

        with tab3:
            st.subheader("🤖 Рекомендации нейросети (HR-эксперт)")
            if st.button("Запустить AI-анализ"):
                with st.spinner(f'Сравниваем ваше резюме с идеальным для должности: {target_job}...'):
                    ai_response = llm.analyze_resume(resume_text, target_job)
                    st.info(ai_response)
    else:
        st.error("Не удалось извлечь текст.")
else:
    st.info("👈 Загрузите PDF-файл в боковом меню, чтобы начать работу.")