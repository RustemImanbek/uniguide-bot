from docx import Document
import json
import re
from datetime import date
import os
from collections import defaultdict

# === 1. Абсолютный путь к .docx ===
base = os.path.abspath(os.path.join(os.getcwd(), ".."))
input_path = os.path.join(base, "data", "NewRaw", "metod_otdel.docx")
output_dir = os.path.join(base, "data", "NewJson")
output_path = os.path.join(output_dir, "metodicheskiy_otdel.json")

# === 2. Загрузка документа ===
doc = Document(input_path)
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# === 3. Ключевые функции модуля ===
function_keywords = [
    "УМКД (Архив)", "УМКД преподавателей", "Структуры УМКД",
    "Интерактивный силлабус", "Каталоги", "Каталог дисциплин"
]
url_pattern = re.compile(r"https?://[^\s]+")
step_pattern = re.compile(r"(?:\d+\)|выбрать|открыть|нажать|перейти|ввести).+?(?=\n|$)", re.IGNORECASE)
keyword_base = [
    "УМКД", "архив", "файл", "каталог", "силлабус", "справочник",
    "дисциплина", "редактирование", "поиск", "просмотр", "сохранить", "добавить", "загрузка"
]

# === 4. Извлечение по ключевым заголовкам ===
functions_raw = []
current_func = None

for line in paragraphs:
    matched = False
    for keyword in function_keywords:
        if line.startswith(keyword):
            if current_func:
                functions_raw.append(current_func)
            current_func = {
                "name": keyword,
                "description": line,
                "links": []
            }
            matched = True
            break
    if not matched and current_func:
        current_func["description"] += "\n" + line

if current_func:
    functions_raw.append(current_func)

# === 5. Обработка и объединение по имени ===
merged = defaultdict(lambda: {"description": "", "links": [], "keywords": [], "steps": [], "summary": ""})

for func in functions_raw:
    name = func["name"]
    desc = func["description"]

    # Очистка
    desc = re.sub(r"\(?рис(унок)?\.?\s*\d+\)?", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"Рисунок\s*\d+\s*–.*(?:\n)?", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"\n?\s*[–-]\s*.*(?:форма|список|просмотр|создания|добавления|файлов|окно).*", "", desc, flags=re.IGNORECASE)
    desc = re.sub(rf"^{re.escape(name)}\s*\n*", "", desc).strip()

    # Ссылки
    urls = url_pattern.findall(desc)
    for url in urls:
        func["links"].append({
            "url": url,
            "purpose": "см. подробнее",
            "type": "external"
        })
    desc = url_pattern.sub("", desc).strip()

    # Сбор в агрегатор
    block = merged[name]
    block["description"] += ("\n\n" + desc).strip()
    block["links"].extend(func["links"])

# === 6. Сборка итоговой структуры ===
functions = []
for name, data in merged.items():
    # Summary: первые 1-2 строки
    first_lines = data["description"].split("\n")
    summary = first_lines[0]
    if len(first_lines) > 1 and len(summary) < 80:
        summary += " " + first_lines[1]

    # Steps
    steps = step_pattern.findall(data["description"])

    # Keywords
    found_keywords = list(set([
        word.lower() for word in keyword_base
        if re.search(rf"\b{word}\b", data["description"], re.IGNORECASE)
    ]))

    functions.append({
        "name": name,
        "summary": summary.strip(),
        "description": data["description"].strip(),
        "links": data["links"],
        "keywords": found_keywords,
        "steps": steps
    })

# === 7. Финальный JSON ===
result = {
    "metadata": {
        "file_name": "Методический отдел",
        "section_title": "Модуль Методический отдел",
        "source_type": "university_documentation",
        "last_updated": str(date.today()),
        "language": "ru",
        "document_version": "1.0",
        "doc_id": "metodicheskiy_otdel",
        "tags": ["методический отдел", "УМКД", "каталоги", "силлабус", "проверка"],
        "audience": "staff_only",
        "restricted": True
    },
    "section": "Модуль Методический отдел",
    "description": "Модуль предназначен для проверки УМКД, формирования отчетов, и работы со справочниками.",
    "roles": ["преподаватель", "сотрудник методического отдела"],
    "functions": functions
}

# === 8. Сохраняем результат ===
os.makedirs(output_dir, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ JSON сохранён в", output_path)
