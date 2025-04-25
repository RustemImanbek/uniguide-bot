# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# FastAPI init
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Input schema
class Question(BaseModel):
    question: str

# Prompt system
system_prompt = """
Ты — интеллектуальный помощник пользователей системы UNIVER.
Отвечай только на русском языке. Отвечай кратко, чётко и по делу.
Используй только приведённый ниже контекст. Не выдумывай.
Обязательно используй термины, встречающиеся в вопросе.
"""

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=system_prompt + "\n\nКонтекст:\n{context}\n\nВопрос: {question}\nОтвет:"
)

# Инициализация компонентов цепочки
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local("/home/django/uniguide-bot/faiss_index", embedding, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_kwargs={"k": 2})
llm = Ollama(model="mistral:Q4_K_M", temperature=0)

llm_chain = LLMChain(llm=llm, prompt=prompt_template)
combine_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="context")
qa = RetrievalQA(combine_documents_chain=combine_chain, retriever=retriever)

# Маршрут обработки
@app.post("/ask")
async def ask_question(q: Question):
    try:
        result = qa.invoke({"query": q.question})
        return {"answer": result["result"]}
    except Exception as e:
        return {"error": str(e)}
