from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import shutil

print("📥 Загружаем документы...")
loader = DirectoryLoader(path="data/rag_docs", glob="**/*.md")
docs = loader.load()
print(f"✅ Загружено документов: {len(docs)}")

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f"✂️ Чанков получено: {len(chunks)}")

print("🤖 Получаем embedding через MiniLM (HuggingFace)...")
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

index_path = "faiss_index"
if os.path.exists(index_path):
    print("🗑 Удаляем старый индекс...")
    shutil.rmtree(index_path)

print("🧱 Строим новый индекс FAISS...")
db = FAISS.from_documents(chunks, embedding)
db.save_local(index_path)
print(f"✅ Новый индекс сохранён в: {index_path}")
