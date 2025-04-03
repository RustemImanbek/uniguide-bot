from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_ID = "cointegrated/rut5-base-instruct-russian"
CACHE_DIR = "./models/rut5"

print(f"📦 Скачивается модель {MODEL_ID} в {CACHE_DIR}...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)

print("✅ Модель успешно скачана и сохранена локально!")
