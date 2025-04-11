from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from scripts.rag_ask import get_answer  # Импорт функции с логикой RAG

app = FastAPI()

# Разрешим CORS (если нужно подключаться из C# клиента)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель входящего запроса
class Question(BaseModel):
    question: str

# Обработка запроса к боту через RAG
@app.post("/ask")
async def ask_bot(data: Question):
    print(f"\U0001F4AC Запрос от клиента: {data.question}")
    answer = get_answer(data.question)
    return {"answer": answer}

# Простой пинг для проверки
@app.get("/")
async def root():
    return {"message": "Бот API работает!"}
