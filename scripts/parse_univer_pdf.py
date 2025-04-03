import re
import json
from pathlib import Path
from PyPDF2 import PdfReader

def extract_clean_text(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    full_text = full_text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    full_text = re.sub(r"\s{2,}", " ", full_text)
    full_text = re.sub(r"\n{2,}", "\n", full_text)
    return full_text

def split_into_sections(text):
    pattern = re.compile(r"\n(?=\d{1,2}(?:\.\d{1,2})?\s+)")
    sections = pattern.split(text)
    return sections

def build_json(sections):
    content = []
    for i, section in enumerate(sections):
        lines = section.strip().split("\n")
        if not lines:
            continue

        title_line = lines[0].strip()
        body = "\n".join(lines[1:]).strip()

        if not body or len(body) < 30:
            continue

        section_id = f"section_{i+1}"
        paragraphs = [
            {"id": f"{section_id}.{j+1}", "text": p.strip()}
            for j, p in enumerate(re.split(r"\n{1,}", body)) if len(p.strip()) > 30
        ]

        if not paragraphs:
            continue

        content.append({
            "id": section_id,
            "title": title_line,
            "keywords": [],
            "paragraphs": paragraphs
        })
    return content

def convert_pdf_to_json(pdf_path: str, output_folder="data/JSON"):
    text = extract_clean_text(pdf_path)
    sections = split_into_sections(text)
    content = build_json(sections)

    result = {
        "metadata": {
            "file_name": Path(pdf_path).name,
            "source_type": "pdf_manual",
            "last_updated": "2025-04-03"
        },
        "content": content
    }

    Path(output_folder).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_folder) / ("Parsed_" + Path(pdf_path).stem + ".json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[✔] JSON успешно сохранён: {output_path}")
    return output_path

# Пример запуска
if __name__ == "__main__":
    convert_pdf_to_json("Общая Руководство пользователей УНИВЕР (1).pdf")
