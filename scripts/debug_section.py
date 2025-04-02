import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import PROCESSED_JSON


def show_section_paragraphs(section_id="section_2"):
    with open(PROCESSED_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    for section in data["content"]:
        if section.get("id") == section_id:
            print(f"🔍 Найдено раздел: {section_id}")
            for para in section.get("paragraphs", []):
                print(f"\n🟩 {para.get('id')}")
                print(para.get("text"))
            return

    print("❌ Раздел не найден")

if __name__ == "__main__":
    show_section_paragraphs()
