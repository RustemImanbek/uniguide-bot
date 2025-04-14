from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
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

# 3. Получаем embedding через MiniLM
print("🤖 Получаем embedding через MiniLM (HuggingFace)...")
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. Сохраняем или загружаем FAISS
index_path = "faiss_index"
if os.path.exists(index_path):
    db = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)
    print("🔁 Индекс загружен.")
else:
    db = FAISS.from_documents(chunks, embedding)
    db.save_local(index_path)
    print("✅ Индекс сохранён!")
