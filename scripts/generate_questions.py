# scripts/generate_questions.py

import json
from pathlib import Path
from transformers import pipeline
from config import PROCESSED_JSON, GENERATED_QUESTIONS

paraphraser = pipeline("text2text-generation", model="cointegrated/rut5-base-paraphraser", max_length=128)


def generate_complex_questions():
    with open(PROCESSED_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = {}

    for section in data.get("content", []):
        section_title = section.get("title", "Раздел")
        keywords = section.get("keywords", [])
        paragraphs = section.get("paragraphs", [])

        questions = []
        for kw in keywords:
            context = paragraphs[0].get("text", "") if paragraphs else ""
            base = f"На основе текста: '{context}' — расскажите подробнее про '{kw}'"
            paraphrased = paraphraser(base, num_return_sequences=1)[0]['generated_text']
            questions.append({
                "keyword": kw,
                "original_question": base,
                "complex_question": paraphrased
            })

        results[section_title] = questions

    with open(GENERATED_QUESTIONS, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"✅ Сложные вопросы сохранены в {GENERATED_QUESTIONS}")
