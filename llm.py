import json
import os
import re
import time

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip()
_SKIP = ("whisper", "tts", "guard", "safeguard", "embed", "compound", "orpheus", "distil-whisper")
_PREFER = ("llama-4", "gpt-oss-120b", "qwen", "llama-3.3", "gpt-oss-20b", "llama-3.1", "llama")

SYSTEM_PROMPT = """You are an expert teacher who creates revision flashcards for students.
Rules:
- Use ONLY information present in the notes. Never invent facts.
- Each card tests ONE idea. Questions must be clear and self-contained.
- Answers must be short (1-3 sentences) and accurate.
- Mix question types: definitions, 'why/how', comparisons, and examples.
- Do not create duplicate or near-duplicate cards.
- Respond with VALID JSON ONLY, no markdown, no commentary, in exactly this format:
{"flashcards": [{"question": "...", "answer": "..."}]}"""


def build_prompt(notes: str, num_cards: int, difficulty: str) -> str:
    return (
        f"Create {num_cards} flashcards at {difficulty} difficulty from the notes below.\n"
        f"If the notes do not contain enough material, create fewer cards instead of making things up.\n\n"
        f"NOTES:\n\"\"\"\n{notes.strip()}\n\"\"\""
    )


def _get_client():
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")
    return Groq(api_key=api_key)


def list_chat_models(client) -> list:
    """Ask Groq which chat models are available right now, best first."""
    ids = [m.id for m in client.models.list().data]
    ids = [i for i in ids if not any(s in i.lower() for s in _SKIP)]
    ranked = []
    for pref in _PREFER:
        for i in ids:
            if pref in i.lower() and i not in ranked:
                ranked.append(i)
    return ranked + [i for i in ids if i not in ranked]


_cached_model = None


def pick_model(client, refresh: bool = False) -> str:
    global _cached_model
    if GROQ_MODEL:
        return GROQ_MODEL
    if _cached_model is None or refresh:
        models = list_chat_models(client)
        if not models:
            raise RuntimeError("No chat models are available for your Groq account.")
        _cached_model = models[0]
    return _cached_model


def _call_groq(prompt: str) -> str:
    client = _get_client()
    model = pick_model(client)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    try:
        response = client.chat.completions.create(
            model=model, messages=messages,
            response_format={"type": "json_object"}, temperature=0.3,
        )
    except Exception as e:
        msg = str(e).lower()
        if "model_not_found" in msg or "does not exist" in msg:
            # Chosen model disappeared -> re-discover and try once more
            model = pick_model(client, refresh=True)
            response = client.chat.completions.create(
                model=model, messages=messages,
                response_format={"type": "json_object"}, temperature=0.3,
            )
        elif "response_format" in msg or "json" in msg:
            # Some models don't support JSON mode -> the prompt already asks for JSON
            response = client.chat.completions.create(
                model=model, messages=messages, temperature=0.3,
            )
        else:
            raise
    return response.choices[0].message.content


def parse_flashcards(raw: str) -> pd.DataFrame:
    """Turn the LLM's JSON text into a clean DataFrame with Question/Answer columns."""
    text = raw.strip()
    # Remove ```json fences if the model added them anyway
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if not match:
            raise ValueError("The model did not return valid JSON. Try again.")
        data = json.loads(match.group(1))

    cards = data.get("flashcards", []) if isinstance(data, dict) else data
    rows = [
        {"Question": str(c.get("question", "")).strip(), "Answer": str(c.get("answer", "")).strip()}
        for c in cards
        if isinstance(c, dict)
    ]
    df = pd.DataFrame(rows, columns=["Question", "Answer"])
    df = df[(df["Question"] != "") & (df["Answer"] != "")]
    df = df.drop_duplicates(subset="Question").reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "No"
    if df.empty:
        raise ValueError("No flashcards could be created from these notes.")
    return df


def _is_temporary(err: Exception) -> bool:
    """True for overload / rate-limit errors that are worth retrying."""
    msg = str(err).lower()
    return any(k in msg for k in ("503", "429", "unavailable", "overloaded",
                                  "rate limit", "timeout", "connection"))


def _call_with_retry(prompt: str, tries: int = 4) -> str:
    """Retry temporary errors, waiting 2s, 4s, 8s ..."""
    for attempt in range(tries):
        try:
            return _call_groq(prompt)
        except Exception as e:
            if attempt == tries - 1 or not _is_temporary(e):
                raise
            time.sleep(2 ** (attempt + 1))


def generate_flashcards(notes: str, num_cards: int = 8, difficulty: str = "medium") -> pd.DataFrame:
    if not notes or len(notes.strip()) < 30:
        raise ValueError("Please paste some longer notes (at least a couple of sentences).")
    raw = _call_with_retry(build_prompt(notes, num_cards, difficulty))
    return parse_flashcards(raw)