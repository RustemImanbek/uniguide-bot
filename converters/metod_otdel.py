from docx import Document
import json
import re
from datetime import date
import os
from collections import defaultdict

# === 1. Абсолютный путь к .docx ===
base = os.path.abspath(os.path.join(os.getcwd(), ".."))
input_path = os.path.join(base, "data", "NewRaw", "metod_otdel.docx")
doc = Document(input_path)

# === 2. Собираем все текстовые блоки ===
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# === 3. Ключевые функции модуля ===
function_keywords = [
    "УМКД (Архив)", "УМКД преподавателей", "Структуры УМКД",
    "Интерактивный силлабус", "Каталоги", "Каталог дисциплин"
]

functions_raw = []
current_func = None
url_pattern = re.compile(r"https?://[^\s]+")

# === 4. Извлечение функций ===
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

# === 5. Очистка и объединение по имени функции ===
merged = defaultdict(lambda: {"description": "", "links": [], "keywords": []})
keyword_base = [
    "УМКД", "архив", "файл", "каталог", "силлабус", "справочник",
    "дисциплина", "редактирование", "поиск", "просмотр", "сохранить", "добавить", "загрузка"
]

for func in functions_raw:
    name = func["name"]
    desc = func["description"]

    # Удалить упоминания рисунков
    desc = re.sub(r"\(?рис(унок)?\.?\s*\d+\)?", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"Рисунок\s*\d+\s*–.*(?:\n)?", "", desc, flags=re.IGNORECASE)
    # Удалить текстовые хвосты вроде "– форма создания дисциплины"
    desc = re.sub(r"\n?\s*[–-]\s*.*(?:форма|список|просмотр|создания|добавления|файлов).*\n?", "", desc, flags=re.IGNORECASE)
    # Удалить дубли заголовка
    desc = re.sub(rf"^{re.escape(name)}\s*\n*", "", desc).strip()

    # Найти и сохранить ссылки
    urls = url_pattern.findall(desc)
    for url in urls:
        func["links"].append({
            "url": url,
            "purpose": "см. подробнее",
            "type": "external"
        })
    desc = url_pattern.sub("", desc).strip()

    # Объединение описаний и ссылок
    if merged[name]["description"]:
        merged[name]["description"] += "\n\n" + desc
    else:
        merged[name]["description"] = desc

    merged[name]["links"].extend(func.get("links", []))

# === 6. Формируем итоговый список функций с keywords ===
functions = []
for name, data_ in merged.items():
    found_keywords = list(set([
        word.lower() for word in keyword_base
        if re.search(rf"\b{word}\b", data_["description"], re.IGNORECASE)
    ]))
    functions.append({
        "name": name,
        "description": data_["description"],
        "links": data_["links"],
        "keywords": found_keywords
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
output_dir = os.path.join(base, "data", "NewJson")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "metodicheskiy_otdel.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ JSON сохранён в", output_path)
