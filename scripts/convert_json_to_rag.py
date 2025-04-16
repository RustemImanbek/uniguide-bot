import os
import json
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_DIR = os.path.join(BASE_DIR, "data", "JSON")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "rag_docs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_keywords(text):
    words = re.findall(r'\b[а-яА-Яa-zA-Z]{4,}\b', text)
    return list(sorted(set(words[:8])))

def json_to_md(module):
    title = module.get("title", "Без названия")
    module_id = module.get("id", "-")
    available_roles = ", ".join(module.get("available_roles", []))
    description = module.get("description", "–")
    steps = module.get("steps", [])
    ui_notes = module.get("ui_notes", [])
    notes = module.get("notes", [])
    access = module.get("access_control")
    keywords = module.get("keywords")

    # Генерация ключевых слов, если они отсутствуют
    if not keywords:
        base_text = " ".join([title, description] + steps + notes + ui_notes)
        keywords = extract_keywords(base_text)

    lines = [
        f"# 📘 Модуль: {title}",
        f"**ID**: {module_id}",
        f"**Доступно для**: {available_roles}",
        "",
        "## 📝 Описание",
        description,
        ""
    ]

    if steps:
        lines.append("## 🩜 Шаги")
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    if ui_notes:
        lines.append("## 💡 Подсказки интерфейса")
        for note in ui_notes:
            lines.append(f"– {note}")
        lines.append("")

    if notes:
        lines.append("## 📌 Примечания")
        for note in notes:
            lines.append(f"– {note}")
        lines.append("")

    if access:
        lines.append("**Права доступа**: " + access)
        lines.append("")

    if keywords:
        lines.append("**Ключевые слова**: " + ", ".join(keywords))
        lines.append("")

    return "\n".join(lines)

# Обработка всех JSON-файлов
for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️ Ошибка JSON в файле {filename}: {e}")
            continue

        # Один модуль или список модулей
        if "modules" in data:
            modules = data["modules"]
        elif "content" in data:
            modules = data["content"]
        else:
            modules = [data]

        for module in modules:
            if not isinstance(module, dict):
                continue
            file_id = module.get("id", os.path.splitext(filename)[0])
            out_file = os.path.join(OUTPUT_DIR, f"{file_id}.md")
            with open(out_file, "w", encoding="utf-8") as out:
                out.write(json_to_md(module))

print(f"✅ Преобразование завершено. Файлы в папке: {OUTPUT_DIR}")