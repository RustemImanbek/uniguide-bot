# bot/bot_wrapper.py

from core.vectorizer import index_data
from core.search import find_best_answer
from core.generator import rewrite_answer
from config import PROCESSED_JSON

class Bot:
    def __init__(self):
        # Загружаем индексы и данные
        (
            self.index,
            self.texts,
            self.metadata,
            self.section_index,
            self.section_metadata,
            self.keyword_index,
            self.keywords_metadata
        ) = index_data()

    def get_best_answer(self, question: str, paraphrase: bool = True) -> str:
        raw_answer = find_best_answer(
            question,
            self.index,
            self.texts,
            self.metadata,
            self.section_index,
            self.section_metadata,
            self.keyword_index,
            self.keywords_metadata,
            debug = True
        )

        if isinstance(raw_answer, list):
            raw_answer = raw_answer[0] if raw_answer else "❌ Ничего не найдено."

        return rewrite_answer(question, raw_answer) if paraphrase else raw_answer