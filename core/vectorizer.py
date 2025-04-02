# core/vectorizer.py

import json
import faiss
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from config import PROCESSED_JSON

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_json():
    with open(PROCESSED_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["content"]

def index_data():
    content = load_json()

    texts = []
    metadata = []
    section_titles = []
    section_metadata = []
    keyword_phrases = []
    keyword_metadata = defaultdict(list)

    for section in content:
        section_id = section.get("id")
        section_title = section.get("title", "")
        section_titles.append(section_title)
        section_metadata.append({"section": section_id, "title": section_title})

        for para in section.get("paragraphs", []):
            text = para.get("text", "")
            texts.append(text)
            metadata.append({"id": para.get("id"), "section": section_id})

        for kw in section.get("keywords", []):
            keyword_phrases.append(kw)
            keyword_metadata[section_id].append(kw)

    # Векторизация
    text_vecs = np.array(model.encode(texts), dtype=np.float32)
    section_vecs = np.array(model.encode(section_titles), dtype=np.float32)
    keyword_vecs = np.array(model.encode(keyword_phrases), dtype=np.float32)

    # Индексы
    text_index = faiss.IndexFlatL2(text_vecs.shape[1])
    section_index = faiss.IndexFlatL2(section_vecs.shape[1])
    keyword_index = faiss.IndexFlatL2(keyword_vecs.shape[1])

    text_index.add(text_vecs)
    section_index.add(section_vecs)
    keyword_index.add(keyword_vecs)

    print(f"\U0001F4CC Загружено и проиндексировано {len(texts)} фрагментов")

    return text_index, texts, metadata, section_index, section_metadata, keyword_index, dict(keyword_metadata)
