# main.py

import argparse
from bot.bot_wrapper import Bot
from core.vectorizer import index_data

bot = Bot()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["ask", "index"])
    parser.add_argument("--query", type=str, help="Вопрос пользователя")
    args = parser.parse_args()

    if args.command == "index":
        index_data()

    elif args.command == "ask":
        if args.query:
            answer = bot.get_best_answer(args.query, paraphrase=False)


            print("🤖 Ответ:", answer)
        else:
            print("❌ Пожалуйста, укажите вопрос через --query")
