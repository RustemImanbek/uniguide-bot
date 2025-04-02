# scripts/postprocess_converted.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import re
from pathlib import Path
from config import JSON_DIR

INPUT_FILE = JSON_DIR / "Converted_Main_Page.json"
OUTPUT_FILE = JSON_DIR / "Converted_Main_Page_Processed.json"


def split_to_sections(flat_paragraphs):
    sections = []
    current = {"id": None, "title": None, "keywords": [], "paragraphs": []}
    section_counter = 1
    para_counter = 1

    for para in flat_paragraphs:
        text = para["text"]

        # Если встречается подзаголовок типа "Новости.", "Документы.", и т.п.
        if re.match(r"^[А-Яа-яЁё\w\s]{3,}\.$", text.strip()):
            # Завершаем текущий раздел
            if current["paragraphs"]:
                sections.append(current)
                section_counter += 1
                para_counter = 1
            # Начинаем новый
            current = {
                "id": f"section_{section_counter}",
                "title": text.strip(". "),
                "keywords": [],
                "paragraphs": []
            }
        else:
            current["paragraphs"].append({
                "id": f"section_{section_counter}.{para_counter}",
                "text": text.strip()
            })
            para_counter += 1

    if current["paragraphs"]:
        sections.append(current)

    return sections


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat_paragraphs = data["content"][0]["paragraphs"]
    sections = split_to_sections(flat_paragraphs)

    result = {
        "metadata": {
            "file_name": "Converted_Main_Page_Processed",
            "source_type": "postprocessed",
            "last_updated": "2025-03-27"
        },
        "content": sections
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"✅ Постобработка завершена. Сохранено в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
