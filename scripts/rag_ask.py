from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

import os

# 1. Загружаем документы
print("📥 Загружаем документы...")
loader = DirectoryLoader(path="data/rag_docs", glob="**/*.md")
docs = loader.load()
print(f"✅ Загружено документов: {len(docs)}")

# 2. Разбиваем на чанки
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f"✂️ Чанков получено: {len(chunks)}")

# 3. Получаем embedding через Ollama
print("🤖 Получаем embedding через Ollama...")
embedding = OllamaEmbeddings(model="mistral")

# 4. Сохраняем или загружаем FAISS
index_path = "faiss_index"

if os.path.exists(index_path):
    print("📦 Загружаем сохранённый индекс FAISS...")
    vectorstore = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)
else:
    print("🧱 Строим индекс FAISS...")
    vectorstore = FAISS.from_documents(chunks, embedding)
    vectorstore.save_local(index_path)
    print("✅ Индекс сохранён!")

# 5. Настраиваем LLM + Retrieval Chain
print("🧠 Настраиваем LLM и RetrievalQA...")
llm = Ollama(model="mistral")
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# 6. Диалог
print("\n✅ Готово! Введите вопрос или 'exit' для выхода.")
while True:
    question = input("\n🔹 Вопрос: ")
    if question.lower() in ["exit", "quit"]:
        print("👋 До свидания!")
        break
    answer = qa_chain.run(question)
    print(f"\n💬 Ответ:\n{answer}")
