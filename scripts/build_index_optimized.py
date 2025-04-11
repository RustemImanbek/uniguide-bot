import os
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain.docstore.document import Document
from keybert import KeyBERT

INDEX_DIR = "faiss_index"
DOCS_DIR = "data/rag_docs"
MODEL_NAME = "mistral"  # или bge-small, nomic, и т.д.

kw_model = KeyBERT(model='all-MiniLM-L6-v2')


def enrich_keywords_if_missing(docs):
    enriched = 0
    for doc in docs:
        content = doc.page_content.lower()
        if "ключевые слова:" not in content:
            keywords = kw_model.extract_keywords(doc.page_content, top_n=5)
            tags = ", ".join([kw[0] for kw in keywords])
            doc.page_content += f"\n\nКлючевые слова: {tags}"
            enriched += 1
    print(f"🧠 Документов дополнено ключевыми словами: {enriched}")
    return docs


def load_documents():
    loader = DirectoryLoader(
        DOCS_DIR,
        glob="**/*.md",
        loader_cls=UnstructuredMarkdownLoader,
        show_progress=True
    )
    raw_docs = loader.load()
    raw_docs = enrich_keywords_if_missing(raw_docs)
    return raw_docs


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )
    return splitter.split_documents(documents)


def build_faiss_index():
    print("📥 Загружаем и обогащаем документы...")
    raw_docs = load_documents()
    print(f"✅ Загружено документов: {len(raw_docs)}")

    chunks = split_documents(raw_docs)
    print(f"✂️ Чанков после разбиения: {len(chunks)}")

    print("🔗 Подключаем embedding модель...")
    embeddings = OllamaEmbeddings(model=MODEL_NAME)

    print("🧱 Строим и сохраняем FAISS индекс...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_DIR)
    print(f"✅ Индекс сохранён в: {INDEX_DIR}")


if __name__ == "__main__":
    build_faiss_index()
