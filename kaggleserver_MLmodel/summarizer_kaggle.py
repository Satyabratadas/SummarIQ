import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = FastAPI()

model_name = "google-t5/t5-small"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

class Input(BaseModel):
    prompt: str

@app.post("/generate")
def generate(data: Input):
    inputs = tokenizer(
        data.prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(device)

    out = model.generate(
        inputs["input_ids"],
        num_beams=4,
        length_penalty=1.0,
        no_repeat_ngram_size=2,
        max_length=180,
        do_sample=False
    )

    return {"text": tokenizer.decode(out[0], skip_special_tokens=True)}
