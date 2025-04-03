import json
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Загрузка модели и лемматизатора
nlp = spacy.load("ru_core_news_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

def preprocess_text(text):
    doc = nlp(text.lower().strip())
    return " ".join([token.lemma_ for token in doc if not token.is_punct])

def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts, metadata = [], []
    for section in data["content"]:
        for para in section.get("paragraphs", []):
            texts.append(para.get("text", ""))
            metadata.append({"id": para.get("id"), "section": section.get("id")})
    return texts, metadata

def find_best_answer(question, texts, top_k=1):
    query = preprocess_text(question)
    query_vec = model.encode([query])
    text_vecs = model.encode(texts)
    sims = cosine_similarity(query_vec, text_vecs)[0]
    top_indices = sims.argsort()[-top_k:][::-1]
    return [texts[i] for i in top_indices]

if __name__ == "__main__":
    path_to_json = "data/JSON/Processed_Main_Page.json"
    texts, metadata = load_data(path_to_json)

    while True:
        question = input("\n❓ Вопрос: ").strip()
        if not question:
            break

        answers = find_best_answer(question, texts)
        print("\n📌 Ответ:")
        print(answers[0])
