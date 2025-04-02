import numpy as np
import spacy
from sentence_transformers import SentenceTransformer

nlp = spacy.load("ru_core_news_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

SECTION_ALIASES = {
    "сообщение": "section_6",
    "сообщения": "section_6",
    "переписка": "section_6",
    "отправить сообщение": "section_6",
    "техподдержка": "section_2",
    "заявка в техподдержку": "section_2",
    "анкета": "section_8",
    "анкетирование": "section_8",
    "профиль": "section_9",
    "редактировать профиль": "section_9",
    "личный профиль": "section_9",
    "изменить профиль": "section_9",
    "профайл": "section_9",
    "документы": "section_7",
    "скачать документ": "section_7",
    "новости": "section_4",
    "блок новостей": "section_4",
    "публикуется в новостях": "section_4",
    "публикации": "section_4",
    "часто задаваемые вопросы": "section_5",
    "faq": "section_5",
    "главная страница": "section_1",
    "функции системы": "section_1",
    "доступные функции": "section_1"
}

def preprocess_text(text):
    doc = nlp(text.lower().strip())
    return " ".join([token.lemma_ for token in doc if not token.is_punct])

def find_best_answer(query, index, texts, metadata,
                     section_index, section_metadata,
                     keyword_index, keywords_metadata,
                     top_k=5, debug=False):
    query_proc = preprocess_text(query)
    query_vec = np.array(model.encode(query_proc), dtype=np.float32)

    # 🔍 Поиск по фрагментам
    D_text, I_text = index.search(query_vec.reshape(1, -1), top_k * 5)

    # 📌 Анализ всех разделов по ключевым словам (лемматизация)
    query_lemmas = set(query_proc.split())
    section_scores = {}
    section_densities = {}
    for meta in section_metadata:
        sec_id = meta["section"]
        keywords = keywords_metadata.get(sec_id, [])
        norm_keywords = set(preprocess_text(" ".join(keywords)).split())
        match_count = sum(1 for kw in norm_keywords if any(kw in lemma or lemma in kw for lemma in query_lemmas))
        density = match_count / len(norm_keywords) if norm_keywords else 0.0
        section_scores[sec_id] = match_count
        section_densities[sec_id] = density

    # 🧠 Переопределение по синонимам (лемматизированное)
    best_section = None
    for alias, sec_id in SECTION_ALIASES.items():
        alias_lemmas = preprocess_text(alias)
        if alias_lemmas in query_proc:
            best_section = sec_id
            if debug:
                print(f"📌 Переопределён раздел по синониму: '{alias}' → {sec_id}")
            break

    # Если не найден по синониму — использовать плотность и счёт
    if not best_section:
        best_section = max(section_densities.items(), key=lambda x: (x[1], section_scores[x[0]]), default=(None, 0))[0]

    if debug:
        print(f"🔍 Анализ ключевых слов по разделам:")
        for s_id in section_scores:
            print(f"   Раздел {s_id} — {section_scores[s_id]} совпадений, плотность: {section_densities[s_id]:.2f}")
        print(f"📌 Выбран приоритетный раздел: {best_section}")

    candidates = []
    for score, i in zip(D_text[0], I_text[0]):
        section = metadata[i]['section']
        text = texts[i]

        # 🚀 Расширяем короткие фрагменты, если надо
        extended_text = text
        if len(text.split()) < 20:
            if i + 1 < len(texts) and metadata[i + 1]['section'] == section:
                extended_text += " " + texts[i + 1]

        boost = 0.3 if section == best_section else 0.0
        kw_score = section_scores.get(section, 0) * 0.05  # динамическое усиление
        final_score = score + boost + kw_score

        candidates.append((extended_text, final_score, section))

    # 🧠 Жесткий фильтр по выбранному разделу
    filtered = [c for c in candidates if c[2] == best_section]
    final = filtered if filtered else candidates

    final.sort(key=lambda x: -x[1])
    best_chunks = [c[0] for c in final[:top_k]]

    if debug:
        print("📌 Выбранные фрагменты:")
        for i, chunk in enumerate(best_chunks):
            print(f"{i+1}.", chunk[:100], "...")

    return best_chunks
