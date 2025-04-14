from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

import re

# 1. Загружаем embedding
print("🤖 Загружаем MiniLM embedding...")
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. Загружаем FAISS индекс
print("📂 Загружаем FAISS индекс...")
db = FAISS.load_local("faiss_index", embedding, allow_dangerous_deserialization=True)

# 3. Настраиваем LLM
llm = Ollama(model="mistral")

# 4. Retrieval QA
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=db.as_retriever(search_kwargs={"k": 10}),
    return_source_documents=True
)

print("✅ Готово! Введите вопрос или 'exit' для выхода.\n")

while True:
    query = input("🔹 Вопрос: ")
    if query.lower() in ["exit", "выход"]:
        break

    result = qa.invoke({"query": query})

    docs = result.get("source_documents", [])
    answer = result.get("result", "").strip()

    if not docs:
        print("⚠️ Не удалось найти релевантные документы.")
        continue

    print("\n📚 Контекст, переданный в модель:\n")
    for i, doc in enumerate(docs, 1):
        text = doc.page_content.strip()
        preview = text[:1000] + ("..." if len(text) > 1000 else "")
        print(f"--- Документ {i} ---")
        print(preview)
        print()

    print("💬 Ответ:\n", answer, "\n")
