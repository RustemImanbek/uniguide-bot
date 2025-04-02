# scripts/convert_docx.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from docx import Document
from pathlib import Path
import json
import re
from config import RAW_DIR, JSON_DIR


def extract_paragraphs(docx_path):
    doc = Document(docx_path)
    raw_paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return raw_paragraphs


def split_sections(paragraphs):
    sections = []
    current = {"id": None, "title": None, "paragraphs": []}
    section_counter = 1
    para_counter = 1

    for p in paragraphs:
        # Простейшее правило: если абзац начинается с цифры и точки — это заголовок
        if re.match(r"^\d+(\.\d+)?[)\.]?", p):
            if current["title"]:
                sections.append(current)
                section_counter += 1
                para_counter = 1
                current = {"id": f"section_{section_counter}", "title": p, "paragraphs": []}
            else:
                current["id"] = f"section_{section_counter}"
                current["title"] = p
        else:
            current["paragraphs"].append({
                "id": f"section_{section_counter}.{para_counter}",
                "text": p
            })
            para_counter += 1

    if current["title"]:
        sections.append(current)

    return sections


def build_json_structure(sections):
    return {
        "metadata": {
            "file_name": "Главная страница системы (из docx)",
            "source_type": "auto_generated",
            "last_updated": "2025-03-27"
        },
        "content": sections
    }


def convert():
    docx_file = RAW_DIR / "Главная страница системы.docx"
    output_file = JSON_DIR / "Converted_Main_Page.json"

    paras = extract_paragraphs(docx_file)
    sections = split_sections(paras)
    result = build_json_structure(sections)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"✅ Сконвертировано: {output_file}")


if __name__ == "__main__":
    convert()
