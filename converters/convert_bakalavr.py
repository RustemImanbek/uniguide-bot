from docx import Document
import json
import re
from datetime import date
import os
from collections import defaultdict

# === 1. Пути ===
base = os.path.abspath(os.path.join(os.getcwd(), ".."))
input_path = os.path.join(base, "data", "NewRaw", "bakalavr_module.docx")
output_path = os.path.join(base, "data", "NewJson", "bakalavr_module.json")

# === 2. Загрузка документа ===
doc = Document(input_path)
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# === 3. Ключевые заголовки функций ===
function_keywords = [
    "Личные данные", "Редактирование личных данных", "ИУП", "Регистрация на семестр", "Расписание",
    "Преподаватели", "Оценки", "GPA", "Результаты обучения", "ВОУД", "Портфолио", "Заявки",
    "Задолженности", "Карточка студента", "Форма обучения", "Справки", "Рейтинг", "Анкета",
    "Психологическая поддержка", "Портал трудоустройства", "Профильный предмет ЕНТ", "Подкасты",
    "Подача заявления", "Кураторское сопровождение", "Пересдача FX", "FAQ"
]
function_set = set(function_keywords)
inline_split_pattern = re.compile(rf"\b({'|'.join(re.escape(f) for f in function_keywords)})\b", re.IGNORECASE)

# === 4. Блочная разбивка ===
blocks = []
current_name = None
buffer = ""

for line in paragraphs:
    match = next((kw for kw in function_keywords if line.startswith(kw)), None)
    if match:
        if current_name and buffer:
            blocks.append({"name": current_name, "description": buffer.strip()})
        current_name = match
        buffer = line
    else:
        buffer += "\n" + line

if current_name and buffer:
    blocks.append({"name": current_name, "description": buffer.strip()})

# === 5. Разделение вложенных функций ===
functions_raw = []
for block in blocks:
    parts = inline_split_pattern.split(block["description"])
    current_func = None
    for part in parts:
        if part.strip() in function_set:
            if current_func:
                functions_raw.append(current_func)
            current_func = {
                "name": part.strip(),
                "description": "",
                "links": []
            }
        elif current_func:
            current_func["description"] += "\n" + part.strip()
    if current_func:
        functions_raw.append(current_func)

# === 6. Очистка и объединение ===
merged = defaultdict(lambda: {
    "description": "", "links": [], "keywords": [], "steps": [], "summary": "", "related_functions": []
})
keyword_base = [
    "регистрация", "расписание", "оценка", "дисциплина", "портфолио", "заявка",
    "анкета", "поддержка", "работа", "трудоустройство", "fx", "gpa", "иуп"
]
url_pattern = re.compile(r"https?://[^\s]+", re.IGNORECASE)
step_pattern = re.compile(r"(?:\d+[.)]|выберите|нажмите|откройте|перейдите|введите|загрузите|отправьте|заполните).+?(?=\n|$)", re.IGNORECASE)

def clean_description(desc):
    desc = re.sub(r"\(?рис(унок)?\.?\s*\d+\)?", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"Рисунок\s*\d+\s*–.*(?:\n)?", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"[-–—•]+\s*", "", desc)
    desc = re.sub(r"\s{2,}", " ", desc)
    return desc.strip()

for func in functions_raw:
    name = func["name"]
    desc = clean_description(func["description"])

    urls = url_pattern.findall(desc)
    func["links"].extend({"url": url, "purpose": "см. подробнее", "type": "external"} for url in urls)
    desc = url_pattern.sub("", desc).strip()

    merged[name]["description"] += ("\n\n" if merged[name]["description"] else "") + desc
    merged[name]["links"].extend(func["links"])

# === 7. Финальный список функций ===
functions = []
for name, data in merged.items():
    desc = data["description"].strip()
    found_keywords = sorted(set(
        word for word in keyword_base if re.search(rf"\b{word}\b", desc, re.IGNORECASE)
    ))
    steps = step_pattern.findall(desc)
    summary = desc.split("\n")[0][:200]

    functions.append({
        "name": name,
        "summary": summary.strip(),
        "description": desc,
        "links": data["links"],
        "keywords": found_keywords,
        "steps": steps,
        "related_functions": []  # можно позже автоматически связать через пересечение keywords
    })

# === 8. Финальный JSON ===
result = {
    "metadata": {
        "file_name": "Модуль Бакалавр",
        "section_title": "Модуль Бакалавр",
        "source_type": "university_documentation",
        "last_updated": str(date.today()),
        "language": "ru",
        "document_version": "1.0",
        "doc_id": "module_bakalavr",
        "tags": ["бакалавриат", "оценки", "регистрация", "ИУП", "дисциплины", "FX", "GPA"],
        "audience": "students",
        "restricted": False
    },
    "section": "Модуль Бакалавр",
    "description": "Модуль предоставляет студентам доступ к данным об обучении, заявкам, оценкам, ИУП и другим функциям личного кабинета.",
    "roles": ["студент", "куратор", "академический персонал"],
    "functions": functions
}

# === 9. Сохраняем ===
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ JSON сохранён в:", output_path)
