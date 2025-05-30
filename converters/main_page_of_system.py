from docx import Document
import json
import re
from datetime import date
import os

# === Настройки и паттерны ===
function_keywords = [
    "новости", "новости мон рк", "часто задаваемые вопросы", "документы",
    "сообщения", "личный профайл", "анкетирование глазами коллег",
    "онлайн тест", "заявка на тех.поддержку"
]

url_pattern = re.compile(r"https?://[^\s]+")
step_patterns = [r"нажмите", r"выберите", r"перейдите", r"откройте", r"введите", r"загрузите", r"отправьте", r"щелкните"]

tag_keywords = {
    "тест": "оценка",
    "анкета": "опрос",
    "профайл": "профиль",
    "поддержк": "техподдержка",
    "новост": "новости",
    "вопрос": "faq",
    "заявка": "запрос",
    "редактир": "изменения"
}

# === Функции обработки ===
def normalize_id(text):
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def extract_steps(text):
    return [line.strip() for line in text.splitlines() if any(re.search(p, line.lower()) for p in step_patterns)]

def extract_tags(text):
    tags = set()
    for k, v in tag_keywords.items():
        if k in text.lower():
            tags.add(v)
    return list(tags)

def extract_links(text):
    urls = url_pattern.findall(text)
    links = []
    for url in urls:
        purpose = "ссылка"
        if "test" in url:
            purpose = "пройти тест"
        elif "support" in url or "maintenance" in url:
            purpose = "подать заявку"
        links.append({
            "url": url,
            "type": "external",
            "description": purpose
        })
    return links, url_pattern.sub("", text).strip()

def process_docx(input_path, output_path, module_id="main_page", module_title="Главная страница системы"):
    doc = Document(input_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # Найдём нужный раздел
    section_title = module_title
    start_idx = next((i for i, text in enumerate(paragraphs) if text.startswith("2.4.") and section_title in text), None)
    if start_idx is None:
        raise Exception("Раздел 2.4 не найден")
    section_content = paragraphs[start_idx + 1:]

    functions = {}
    current_func = None

    for line in section_content:
        line_l = line.lower()
        matched = False
        for keyword in function_keywords:
            if line_l.startswith(keyword):
                if current_func:
                    fid = current_func["function_id"]
                    functions.setdefault(fid, current_func)
                fid = normalize_id(keyword)
                current_func = {
                    "function_id": fid,
                    "title": keyword.capitalize(),
                    "description": line,
                    "steps": [],
                    "entities": [],
                    "tags": [],
                    "links": []
                }
                matched = True
                break
        if not matched and current_func:
            current_func["description"] += "\n" + line

    if current_func:
        fid = current_func["function_id"]
        functions.setdefault(fid, current_func)

    # Постобработка: шаги, теги, ссылки
    for func in functions.values():
        func["steps"] = extract_steps(func["description"])
        func["tags"] = extract_tags(func["description"])
        links, clean_text = extract_links(func["description"])
        func["links"] = links
        func["description"] = clean_text

    # Статичные блоки
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

    # Финальный JSON
    result = {
        "module_id": module_id,
        "module_title": module_title,
        "description": "Главная страница отображается после авторизации и предоставляет доступ к функциональности системы в зависимости от роли пользователя.",
        "roles": ["студент", "преподаватель", "администратор", "сотрудник методотдела"],
        "functions": list(functions.values()),
        "relations": {
            "depends_on": ["роль пользователя", "авторизация"],
            "used_by": ["все модули"]
        },
        "source_doc": os.path.basename(input_path),
        "lang": "ru",
        "metadata": {
            "file_name": os.path.basename(input_path),
            "section_title": section_title,
            "source_type": "university_documentation",
            "last_updated": str(date.today()),
            "language": "ru",
            "document_version": "1.0",
            "doc_id": normalize_id(section_title),
            "tags": ["главная", "вход", "меню", "функции", "faq", "поддержка"],
            "audience": "everyone",
            "restricted": False
        },
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
        "additional_sections": additional_sections
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("✅ JSON сохранён в:", output_path)


# ▶ Пример запуска
if __name__ == "__main__":
    base = os.path.abspath(os.path.join(os.getcwd(), ".."))
    input_path = os.path.join(base, "data", "NewRaw", "main_page_converted.docx")
    output_path = os.path.join(base, "data", "NewJson", "main_page_clean.json")
    process_docx(input_path, output_path)
