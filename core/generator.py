from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from difflib import SequenceMatcher

_tokenizer = None
_model = None

def get_phi2():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        print("🔄 Загружается модель Phi-2 из ./models/phi2 ...")
        _tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", cache_dir="./models/phi2")
        _model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", cache_dir="./models/phi2")
        _model.to("cpu")
        print("✅ Модель загружена!")
    return _tokenizer, _model

def rewrite_answer(question: str, context: str) -> str:
    tokenizer, model = get_phi2()

    prompt = (
        f"Вопрос: {question}\n"
        f"Контекст: {context}\n"
        f"Ответ:"
    )

    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to("cpu")
        outputs = model.generate(
            **inputs,
            max_new_tokens=60,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            num_return_sequences=1
        )
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

        if "Ответ:" in generated:
            result = generated.split("Ответ:", 1)[1].strip()
        else:
            result = generated[len(prompt):].strip()

        similarity = SequenceMatcher(None, result, context).ratio()

        print("\n--- Отладка генерации ---")
        print("[PROMPT]:", prompt)
        print("[RAW]:", generated)
        print("[RESULT]:", result)
        print(f"[SIMILARITY]: {similarity:.2f}")
        print("------------------------\n")

        if similarity > 0.9:
            return f"Вы можете {context[0].lower() + context[1:]}"

        return result

    except Exception as e:
        return f"[Ошибка генерации с Phi-2: {e}]"
