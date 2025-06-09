
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch


MODEL_NAME = "t5-small"

print("Loading T5 model for title generation...")
try:
    # Check for GPU, fall back to CPU
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load the pre-trained T5 model and tokenizer
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, legacy=False)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME).to(DEVICE)
    model.eval()

    print(f"T5 Model loaded successfully on {DEVICE}.")
    MODEL_LOADED = True
except Exception as e:
    print(f"Error loading T5 model: {e}")
    MODEL_LOADED = False


def generate_titles(content: str, num_suggestions: int = 3) -> list[str]:

    if not MODEL_LOADED:
        raise RuntimeError("Title generation model is not loaded. Please check server logs.")


    prompt = f"summarize: {content}"


    inputs = tokenizer.encode(
        prompt,
        return_tensors="pt",
        max_length=512,
        truncation=True
    ).to(DEVICE)


    summary_ids = model.generate(
        inputs,
        max_length=60,  # Maximum length of the generated title
        min_length=8,  # Minimum length of the generated title
        length_penalty=2.0,  # Penalizes longer sequences to encourage conciseness
        num_beams=5,  # Number of beams for beam search. Must be > num_suggestions
        early_stopping=True,
        num_return_sequences=num_suggestions  # We want 3 titles
    )

    # Decode the generated token IDs back into text
    suggestions = [
        tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        for g in summary_ids
    ]

    return suggestions