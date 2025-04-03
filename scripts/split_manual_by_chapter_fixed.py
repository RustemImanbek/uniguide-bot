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

def split_into_chapters(text):
    # Более универсальный шаблон: заголовок с номером и текстом
    pattern = re.compile(r"(\n|^)(\d{1,2}(?:\.\d{1,2})*)([^\n]+)(.*?)(?=\n\d{1,2}(?:\.\d{1,2})+|\Z)", re.DOTALL)
    matches = pattern.findall(text)
    chapters = []
    for i, (_, number, title_text, body) in enumerate(matches):
        title = f"{number} {title_text.strip()}"
        body_lines = body.strip().split("\n")
        paragraphs = [p.strip() for p in body_lines if len(p.strip()) > 30]

        if not paragraphs:
            continue

        chapters.append({
            "id": f"chapter_{i+1}",
            "title": title,
            "number": number,
            "paragraphs": [{"id": f"chapter_{i+1}.{j+1}", "text": p} for j, p in enumerate(paragraphs)],
            "keywords": []
        })
    return chapters

def save_chapters_to_files(chapters, original_pdf_name, output_dir="data/JSON"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    saved_paths = []

    for chapter in chapters:
        filename = f"Processed_{chapter['number'].replace('.', '_')}_{chapter['title'][:40].strip().replace(' ', '_')}.json"
        output_path = Path(output_dir) / filename

        json_data = {
            "metadata": {
                "file_name": original_pdf_name,
                "chapter_number": chapter["number"],
                "source_type": "pdf_manual",
                "last_updated": "2025-04-03"
            },
            "content": [chapter]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        saved_paths.append(str(output_path))
    
    return saved_paths

def process_pdf_to_chapters(pdf_path):
    original_pdf_name = Path(pdf_path).name
    text = extract_clean_text(pdf_path)
    chapters = split_into_chapters(text)
    return save_chapters_to_files(chapters, original_pdf_name)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("❌ Укажите путь к PDF-файлу как аргумент.")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    saved_files = process_pdf_to_chapters(pdf_path)

    if not saved_files:
        print("⚠️ Главы не найдены. Проверь формат PDF или регулярку.")
        sys.exit(0)

    print(f"[✔] Разделено и сохранено {len(saved_files)} глав в {Path(saved_files[0]).parent}")
