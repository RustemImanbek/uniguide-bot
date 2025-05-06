from docx import Document
import json
import re
from datetime import date
import os
from docx import Document

base = os.path.abspath(os.path.join(os.getcwd(), ".."))
path = os.path.join(base, "data", "raw", "main_page_converted.docx")
doc = Document(path)

# === 2. Собираем все текстовые блоки ===
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

# === 3. Находим начало нужного раздела ===
section_title = "Главная страница системы"
start_idx = next((i for i, text in enumerate(paragraphs) if text.startswith("2.4.") and section_title in text), None)
if start_idx is None:
    raise Exception("Раздел 2.4 не найден")

section_content = paragraphs[start_idx + 1:]

# === 4. Ключевые слова функций ===
function_keywords = [
    "новости", "новости МОН РК", "часто задаваемые вопросы", "документы",
    "сообщения", "личный профайл", "анкетирование глазами коллег",
    "онлайн тест", "заявка на тех.поддержку"
]

# === 5. Извлечение функций ===
functions = []
current_func = None
url_pattern = re.compile(r"https?://[^\s]+")

for line in section_content:
    line_l = line.lower()
    matched = False
    for keyword in function_keywords:
        if line_l.startswith(keyword):
            if current_func:
                functions.append(current_func)
            current_func = {
                "name": keyword.capitalize(),
                "description": line,
                "links": []
            }
            matched = True
            break
    if not matched and current_func:
        current_func["description"] += "\n" + line

if current_func:
    functions.append(current_func)

# === 6. Вынести ссылки ===
for func in functions:
    urls = url_pattern.findall(func["description"])
    if urls:
        for url in urls:
            purpose = "см. подробнее"
            if "test" in url:
                purpose = "пройти тест"
            elif "support" in url or "maintenance" in url:
                purpose = "подать заявку"
            func["links"].append({
                "url": url,
                "purpose": purpose,
                "type": "external"
            })
        func["description"] = url_pattern.sub("", func["description"]).strip()

# === 7. Дополнительные разделы (вручную) ===
additional_sections = [
    "Академическая политика",
    "Политика академической честности",
    "Правила проведения итогового контроля",
    "Горячая линия по дистанционному обучению",
    "Непрофильные дисциплины",
    "Регламент СЭР ФИНИШ",
    "Инструкция по итоговому контролю с ДОТ 2023–2024",
    "Положение о проверке документов на заимствования",
    "Правила пребывания и обучения",
    "Памятка – обязанности иностранного гражданина"
]

# === 8. Финальная структура ===
result = {
    "metadata": {
        "file_name": section_title,
        "section_title": section_title,
        "source_type": "university_documentation",
        "last_updated": str(date.today()),
        "language": "ru",
        "document_version": "1.0",
        "doc_id": "glavnaya_stranica_sistemy",
        "tags": ["главная", "вход", "меню", "функции", "faq", "поддержка"],
        "audience": "everyone",
        "restricted": False
    },
    "section": section_title,
    "access": {
        "description": "После авторизации пользователи попадают на главную страницу, доступ к функциям определяется ролевой политикой.",
        "role_based_access": True,
        "user_identification": {
            "display": ["ФИО", "логин", "ID"],
            "location": "правый верхний угол"
        }
    },
    "main_menu": {
        "location": "верхняя часть страницы",
        "type": "динамическое меню",
        "visible_modules": "зависят от роли пользователя"
    },
    "functions": functions,
    "additional_sections": additional_sections
}

# === 9. Сохраняем ===
with open("main_page_of_system.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ JSON сохранён в main_page_of_system.json")
