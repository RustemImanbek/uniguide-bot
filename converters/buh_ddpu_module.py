from docx import Document
import json
import re
from datetime import date
import os

# === Пути ===
base = os.path.abspath(os.path.join(os.getcwd(), ".."))
input_path = os.path.join(base, "data", "NewRaw", "buh_ddpu_module.docx")
output_path = os.path.join(base, "data", "NewJson", "buh_ddpu_module.json")

# === Загрузка документа ===
doc = Document(input_path)
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# === Ключевые заголовки ===
function_keywords = [
    "Поиск студентов", "Стоимость обучения", "Кредиты",
    "Повторное обучение", "Пересдача FX", "Повышение GPA",
    "Справочники", "Отчет Kaspi", "Отчет по задолжникам по оплате"
]
heading_pattern = re.compile(rf"^({'|'.join(re.escape(k) for k in function_keywords)})\b", re.IGNORECASE)

# === Чистка текста
def clean_description(text):
    lines = text.split("\n")
    cleaned = []
    skip = re.compile(r"(рисунок\s*\d+|скаченн|ввод стоимости|количество кредитов|карточка студента)", re.IGNORECASE)
    seen = set()
    for line in lines:
        line = line.strip()
        if not line or skip.search(line) or line.lower() in seen:
            continue
        cleaned.append(line)
        seen.add(line.lower())
    return "\n".join(cleaned)

# === Шаги
def extract_steps(text):
    verbs = r"(?:нажмите|выберите|перейдите|введите|заполните|появится|откройте|сохраните|отправьте|загрузите)"
    matches = re.findall(rf"{verbs}[^.\n]{{10,}}", text, re.IGNORECASE)
    return [s.strip().capitalize() for s in matches]

# === Аннотация
def extract_summary(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    for s in sentences:
        if len(s) > 30:
            return s.strip()[:200]
    return text[:200]

# === Ключевые слова
def extract_keywords(text):
    base = [
        "заявка", "оплата", "договор", "услуга", "отчет", "контроль",
        "согласование", "стоимость", "студент", "кредит", "GPA",
        "повторное", "пересдача", "поиск"
    ]
    return sorted(set(w for w in base if re.search(rf"\b{w}\b", text, re.IGNORECASE)))

# === Сбор блоков
blocks = []
current_name = None
buffer = ""

for para in paragraphs:
    if heading_pattern.match(para):
        if current_name and buffer:
            blocks.append({"name": current_name, "text": buffer.strip()})
        current_name = heading_pattern.match(para).group(1).strip()
        buffer = para
    else:
        buffer += "\n" + para

if current_name and buffer:
    blocks.append({"name": current_name, "text": buffer.strip()})

# === Функции
function_names = [b["name"] for b in blocks]
functions = []

for block in blocks:
    name = block["name"]
    raw = block["text"]
    desc = clean_description(raw)
    steps = extract_steps(desc)
    summary = extract_summary(desc)
    keywords = extract_keywords(desc)
    links = [{"url": u, "purpose": "см. подробнее", "type": "external"} for u in re.findall(r"https?://[^\s]+", desc)]
    desc = re.sub(r"https?://[^\s]+", "", desc)

    related = sorted([
        other for other in function_names
        if other != name and re.search(rf"\b{re.escape(other)}\b", desc, re.IGNORECASE)
    ])

    functions.append({
        "name": name,
        "summary": summary,
        "description": desc,
        "steps": steps,
        "keywords": keywords,
        "links": links,
        "related_functions": related
    })

# === JSON
result = {
    "metadata": {
        "file_name": "Модуль Бухгалтерия и Договоры ДДПУ",
        "section_title": "Модуль Бухгалтерия и Договоры ДДППУ",
        "source_type": "university_documentation",
        "last_updated": str(date.today()),
        "language": "ru",
        "document_version": "1.3",
        "doc_id": "module_buh_ddpu",
        "tags": ["бухгалтерия", "договора", "оплаты", "платные услуги", "заявки", "ДППУ"],
        "audience": "staff_only",
        "restricted": True
    },
    "section": "Модуль Бухгалтерия и Договоры ДДПУ",
    "description": "Модуль предназначен для учета и обработки договоров, заявок на оплату, а также формирования и контроля финансовых операций в рамках ДППУ.",
    "roles": ["бухгалтер", "методист", "руководитель подразделения"],
    "functions": functions
}

# === Сохранение
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ Финальный JSON v3 создан:", output_path)
