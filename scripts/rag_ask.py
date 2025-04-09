from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

import os

# 1. Загружаем документы
print("\U0001F4E5 Загружаем документы...")
loader = DirectoryLoader(path="data/rag_docs", glob="**/*.md")
docs = loader.load()
print(f"✅ Загружено документов: {len(docs)}")

# 2. Разбиваем на чанки
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f"✂️ Чанков получено: {len(chunks)}")

# 3. Получаем embedding через Ollama
print("\U0001F916 Получаем embedding через Ollama...")
embedding = OllamaEmbeddings(model="mistral")

# 4. Сохраняем или загружаем FAISS
index_path = "faiss_index"

if os.path.exists(index_path):
    print("\U0001F4E6 Загружаем сохранённый индекс FAISS...")
    vectorstore = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)
else:
    print("\U0001F9F1 Строим индекс FAISS...")
    vectorstore = FAISS.from_documents(chunks, embedding)
    vectorstore.save_local(index_path)
    print("✅ Индекс сохранён!")

# 5. Настраиваем LLM + Retrieval Chain
print("\U0001F9E0 Настраиваем LLM и RetrievalQA...")
llm = Ollama(model="mistral")
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# 6. Диалог
print("\n✅ Готово! Введите вопрос или 'exit' для выхода.")
while True:
    question = input("\n🔹 Вопрос: ")
    if question.lower() in ["exit", "quit"]:
        print("👋 До свидания!")
        break

    # 🧠 Переформулировка вопроса (примитивная логика)
    lowered = question.lower()
    if any(keyword in lowered for keyword in ["faq", "вопросы", "часто задаваемые", "поддержка"]):
        question += " Где находится раздел с часто задаваемыми вопросами (FAQ) в системе?"

    # 📡 Получаем документы из ретривера с оценками
    results = vectorstore.similarity_search_with_score(question, k=10)
    filtered_docs = [doc for doc, score in results if score > 0.7]

    if not filtered_docs:
        print("\n⚠️ Не найдено релевантных документов.")
        continue

    print("\n📚 Контекст, переданный в модель:")
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n--- Документ {i} (score={score:.2f}) ---")
        print(doc.page_content[:1000])

    print("\n🤖 Генерация ответа...")
    response = qa_chain.invoke({"query": question})
    print(f"\n💬 Ответ:\n{response['result']}")