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

functions_raw = []
current_func = None
url_pattern = re.compile(r"https?://[^\s]+")

# === 4. Извлечение по ключевым заголовкам ===
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

# === 5. Очистка и объединение по name ===
merged = defaultdict(lambda: {"description": "", "links": [], "keywords": [], "steps": []})
keyword_base = [
    "регистрация", "расписание", "оценки", "дисциплина", "портфолио", "заявка",
    "выписка", "анкета", "поддержка", "работа", "трудоустройство", "FX", "GPA", "пересдача"
]

for func in functions_raw:
    name = func["name"]
    desc = func["description"]

    # Очистка: рисунки и мусор
    desc = re.sub(r"\(?рис(унок)?\.?\s*\d+\)?", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"Рисунок\s*\d+\s*–.*(?:\n)?", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"\n?\s*[–-]\s*.*(?:форма|список|просмотр|создания|добавления|файлов|окно).*", "", desc, flags=re.IGNORECASE)
    desc = re.sub(rf"^{re.escape(name)}\s*\n*", "", desc).strip()

    # Вынести ссылки
    urls = url_pattern.findall(desc)
    for url in urls:
        func["links"].append({
            "url": url,
            "purpose": "см. подробнее",
            "type": "external"
        })
    desc = url_pattern.sub("", desc).strip()

    # Объединение
    if merged[name]["description"]:
        merged[name]["description"] += "\n\n" + desc
    else:
        merged[name]["description"] = desc
    merged[name]["links"].extend(func["links"])

# === 6. Сборка итоговой структуры ===
functions = []
for name, data_ in merged.items():
    found_keywords = list(set([
        word.lower() for word in keyword_base
        if re.search(rf"\b{word}\b", data_["description"], re.IGNORECASE)
    ]))
    steps = re.findall(r"\d\).+?(?=\n|$)", data_["description"])

    functions.append({
        "name": name,
        "description": data_["description"],
        "links": data_["links"],
        "keywords": found_keywords,
        "steps": steps if steps else []
    })

# === 7. Финальный JSON ===
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

# === 8. Сохраняем ===
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ JSON сохранён в:", output_path)
