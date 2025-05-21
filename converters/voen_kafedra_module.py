from docx import Document
import json
import re
from datetime import date
import os
import hashlib

# === Пути ===
base = os.path.abspath(os.path.join(os.getcwd(), ".."))
input_path = os.path.join(base, "data", "NewRaw", "voen_kafedra_module.docx")
output_path = os.path.join(base, "data", "NewJson", "voen_kafedra_module.json")

# === Загрузка документа ===
doc = Document(input_path)
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# === Заголовки функций ===
heading_keywords = ["Студенты", "Справочники"]
heading_pattern = re.compile(rf"^({'|'.join(re.escape(h) for h in heading_keywords)})\b", re.IGNORECASE)

# === Нормализация названий функций ===
def normalize_title(title):
    return title.strip().capitalize()

# === Чистка описания ===
def clean_description(text):
    text = re.sub(r"Рисунок\s*\d+[.\d\-]*\s*-*", "", text, flags=re.IGNORECASE)
    lines = text.split("\n")
    cleaned = []
    seen = set()
    skip = re.compile(r"(скаченн|ввод|карточка студента)", re.IGNORECASE)
    for line in lines:
        line = line.strip()
        if not line or skip.search(line) or line.lower() in seen:
            continue
        cleaned.append(line)
        seen.add(line.lower())
    return "\n".join(cleaned)

# === Извлечение шагов ===
def extract_steps(text):
    verbs = r"(нажмите|выберите|перейдите|введите|заполните|появится|откройте|сохраните|отправьте|загрузите|сформируйте)"
    return [line.strip().capitalize() for line in text.split("\n") if re.match(rf"^\s*{verbs}", line, re.IGNORECASE)]

# === Извлечение аннотации ===
def extract_summary(text):
    text = text.replace("\n", " ")
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    for s in sentences:
        if len(s) > 40:
            return s[:200]
    return text[:200]

# === Ключевые слова ===
def extract_keywords(text):
    base = [
        "отчет", "справочник", "удо", "профайл", "военная кафедра",
        "учет", "студенты", "форма", "воинский", "сохранить", "найти"
    ]
    return sorted(set(w for w in base if re.search(rf"\b{w}\b", text, re.IGNORECASE)))

# === Связанные функции ===
def find_related(name, all_names, text):
    desc_lower = text.lower()
    return sorted([
        other for other in all_names
        if other.lower() != name.lower() and other.lower() in desc_lower
    ])

# === Сбор блоков ===
blocks = {}
current_name = None
buffer = []

for para in paragraphs:
    match = heading_pattern.match(para)
    if match:
        norm_name = normalize_title(match.group(1))
        if current_name and buffer:
            blocks.setdefault(current_name, []).extend(buffer)
        current_name = norm_name
        buffer = [para]
    elif buffer:
        buffer.append(para)

if current_name and buffer:
    blocks.setdefault(current_name, []).extend(buffer)

# === Уникальный ID генератор ===
def make_id(name):
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:8]

# === Формирование функций ===
functions = []
for idx, (name, paras) in enumerate(blocks.items()):
    raw = "\n".join(paras).strip()
    desc = clean_description(raw)
    summary = extract_summary(desc)
    steps = extract_steps(desc)
    keywords = extract_keywords(desc)
    links = [{"url": u, "purpose": "см. подробнее", "type": "external"} for u in re.findall(r"https?://[^\s]+", desc)]
    desc = re.sub(r"https?://[^\s]+", "", desc)
    related = find_related(name, blocks.keys(), desc)

    functions.append({
        "function_id": f"{make_id(name)}",
        "name": name,
        "summary": summary,
        "description": desc,
        "steps": steps,
        "keywords": keywords,
        "links": links,
        "related_functions": related
    })

# === Финальный JSON ===
result = {
    "metadata": {
        "file_name": "Модуль Военная кафедра",
        "section_title": "Модуль Военная кафедра",
        "source_type": "university_documentation",
        "last_updated": str(date.today()),
        "language": "ru",
        "document_version": "1.3",
        "doc_id": "module_voen_kafedra",
        "tags": ["военная кафедра", "удо", "учет", "студенты", "отчеты", "форма т-2"],
        "audience": "staff_only",
        "restricted": True
    },
    "section": "Модуль Военная кафедра",
    "description": "Модуль предназначен для ведения учета студентов, обучающихся на военной кафедре, формирования отчетов и работы с УДО.",
    "roles": ["инспектор военной кафедры", "сотрудник отдела учета", "руководитель кафедры"],
    "functions": functions
}

# === Сохранение ===
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ Улучшенный JSON для модуля 'Военная кафедра' создан:", output_path)
