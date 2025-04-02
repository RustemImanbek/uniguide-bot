# config.py
from pathlib import Path

# 📁 Пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
JSON_DIR = DATA_DIR / "JSON"
GEN_DIR = DATA_DIR / "generated"

# 📄 Основные файлы
PROCESSED_JSON = JSON_DIR / "Processed_Main_Page.json"
GENERATED_QUESTIONS = GEN_DIR / "generated_complex_questions.json"
BOT_ANSWERS = GEN_DIR / "bot_answers_complex_questions.json"

# 🤖 Модель генерации
GENERATION_MODEL = "cointegrated/rut5-base-paraphraser"
MAX_GEN_LENGTH = 128
