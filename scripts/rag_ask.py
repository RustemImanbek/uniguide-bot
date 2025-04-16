import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

# 🔧 Настройки
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
llm_model = "mistral"
index_path = "faiss_index"

# 🧠 Инструкция (system prompt)
system_prompt = (
    "Ты — помощник по системе UNIVER. Отвечай строго на русском языке. "
    "Если вопрос требует действий, опиши пошагово. Упоминай модуль, если это важно. "
    "Если нет информации — честно скажи и предложи, где это может быть в интерфейсе."
)

# 📄 Prompt-шаблон для history condense
prompt_template = PromptTemplate.from_template(
    """Вопрос: {question}

Инструкция: {instruction}"""
)

# 📆 Эмбеддинги и FAISS
print("🔍 Загружаем MiniLM embedding...")
embedding = HuggingFaceEmbeddings(model_name=embedding_model)

print("📂 Загружаем FAISS индекс...")
db = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)

# 🧬 LLM и цепочка
llm = Ollama(model=llm_model)

qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=db.as_retriever(search_kwargs={"k": 10}),
    return_source_documents=True,
    condense_question_prompt=prompt_template,
    chain_type="stuff"
)

# 🔊 Диалоговая история
chat_history = []

print("✅ Готово! Введите вопрос (или 'exit' для выхода).\n")

while True:
    query = input("🔹 Вопрос: ").strip()
    if query.lower() in ["exit", "выход"]:
        break

    try:
        result = qa.invoke({
            "question": query,
            "chat_history": chat_history[-15:],
            "instruction": system_prompt
        })

        answer = result.get("answer", "").strip()
        print("\n💬 Ответ:\n", answer)

        # 📃 Контекст
        sources = result.get("source_documents", [])
        if sources:
            print("\n📃 Контекст (top 3):")
            for i, doc in enumerate(sources[:3], 1):
                content = doc.page_content.strip()
                print(f"\n--- Документ {i} ---\n{content[:700]}...")

        # 📅 Сохраняем историю
        chat_history.append((query, answer))

    except Exception as e:
        print("\n️️️️🚧 Ошибка:", e)
