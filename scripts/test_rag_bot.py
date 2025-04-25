import time
import pandas as pd
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Вопросы и ключевые слова
test_questions = [
    {"query": "Где найти часто задаваемые вопросы по системе?", "keywords": ["Часто задаваемые вопросы", "ссылка", "значок", "ответ"]},
    {"query": "Как добавить вопрос в экзамен?", "keywords": ["вопросник", "добавить", "экзамен", "редактировать"]},
    {"query": "Кто может просматривать расписание группы?", "keywords": ["группа", "расписание", "просматривать", "куратор"]},
    {"query": "Как отправить заявку на поступление?", "keywords": ["заявка", "специальность", "подать", "заполнить"]},
    {"query": "Какие документы нужны для зачисления?", "keywords": ["документы", "паспорт", "аттестат", "медсправка"]},
    {"query": "Как изменить пароль в системе?", "keywords": ["пароль", "изменить", "профиль", "безопасность"]},
    {"query": "Где можно скачать учебный план?", "keywords": ["учебный план", "скачать", "специальность", "документ"]},
    {"query": "Куда обращаться при технических проблемах?", "keywords": ["техническая поддержка", "ошибка", "контакт", "администратор"]},
    {"query": "Можно ли редактировать загруженные файлы?", "keywords": ["редактировать", "загрузка", "файлы", "документ"]},
    {"query": "Как узнать результат экзамена?", "keywords": ["результат", "экзамен", "оценка", "просмотр"]}
]

# Инструкция для модели (system prompt)
system_prompt = """
Ты — интеллектуальный помощник пользователей системы UNIVER.
Отвечай только на русском языке. Отвечай кратко, чётко и по делу.
Используй только приведённый ниже контекст. Не выдумывай.
Обязательно используй термины, встречающиеся в вопросе.
"""

# Prompt шаблон
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=system_prompt + "\n\nКонтекст:\n{context}\n\nВопрос: {question}\nОтвет:"
)

# Модель и цепочка
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local("../faiss_index", embedding, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_kwargs={"k": 2})
llm = Ollama(model="mistral", temperature=0)

llm_chain = LLMChain(llm=llm, prompt=prompt_template)
combine_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="context")
qa = RetrievalQA(combine_documents_chain=combine_chain, retriever=retriever)

# Оценка по ключевым словам
def evaluate_answer(answer, keywords):
    return sum(1 for word in keywords if word.lower() in answer.lower()), len(keywords)

# Прогон
results = []
for item in test_questions:
    query = item["query"]
    expected_keywords = item["keywords"]
    start = time.time()
    response = qa.invoke({"query": query})
    end = time.time()
    answer = response["result"]
    duration = round(end - start, 2)
    score, total = evaluate_answer(answer, expected_keywords)

    results.append({
        "model": "Mistral Q4_K_M + Prompt",
        "question": query,
        "duration_sec": duration,
        "score": f"{score}/{total}",
        "answer": answer
    })

# Сохранение результата
df = pd.DataFrame(results)
df.to_excel("rag_prompted_results.xlsx", index=False)
print(df[["model", "question", "score", "duration_sec"]])
