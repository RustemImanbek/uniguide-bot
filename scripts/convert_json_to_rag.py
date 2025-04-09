import os
import json

# INPUT_DIR = "../data/JSON"
# OUTPUT_DIR = "../data/rag_docs"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_DIR = os.path.join(BASE_DIR, "data", "JSON")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "rag_docs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def json_to_md(module):
    lines = [
        f"# 📘 Модуль: {module.get('title', 'Без названия')}",
        f"**ID**: {module.get('id', '-')}",
        f"**Доступно для**: {', '.join(module.get('available_roles', []))}",
        "",
        "## 📝 Описание",
        module.get("description", "–"),
        "",
    ]

    steps = module.get("steps", [])
    if steps:
        lines.append("## 🩜 Шаги")
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    ui_notes = module.get("ui_notes", [])
    if ui_notes:
        lines.append("## 💡 Подсказки интерфейса")
        for note in ui_notes:
            lines.append(f"– {note}")
        lines.append("")

    notes = module.get("notes", [])
    if notes:
        lines.append("## 📌 Примечания")
        for note in notes:
            lines.append(f"– {note}")
        lines.append("")

    access = module.get("access_control")
    if access:
        lines.append("**Права доступа**: " + access)
        lines.append("")

    keywords = module.get("keywords")
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

        # Один модуль, или список модулей
        if "modules" in data:
            modules = data["modules"]
        elif "content" in data:
            modules = data["content"]
        else:
            modules = [data]

        for module in modules:
            file_id = module.get("id", os.path.splitext(filename)[0])
            out_file = os.path.join(OUTPUT_DIR, f"{file_id}.md")
            with open(out_file, "w", encoding="utf-8") as out:
                out.write(json_to_md(module))

print(f"✅ Преобразование завершено. Файлы в папке: {OUTPUT_DIR}")
