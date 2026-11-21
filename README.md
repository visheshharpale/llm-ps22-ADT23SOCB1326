# 🗂️ Flashcard Generator (PS22)

**Name:** Vishesh Harpale | **Roll No:** ADT23SOCB1326 | **Class:** LY AIA 6

## Problem Statement
Students need quick revision material. This app converts pasted study notes into
question-answer flashcards using an LLM and lets the student export them as a CSV file
(which can be imported into Anki, Quizlet, or Excel).

## How It Works
1. Paste notes into the web UI.
2. The app builds a prompt and sends it to an LLM (via the Groq API).
3. The LLM returns Q&A pairs as JSON.
4. The JSON is cleaned and loaded into a pandas DataFrame.
5. Flashcards are shown as cards and as a table, with a **Download CSV** button.

## Tech Stack
- Python 3
- Streamlit (UI)
- Groq API (LLM; the model is picked automatically from the models available on the account)
- pandas (DataFrame and CSV export)
- python-dotenv (loads the API key from `.env`)

## Project Structure
```
├── app.py             # Streamlit UI
├── llm.py             # Prompt, LLM call, JSON parsing, retry logic
├── test_samples.py    # Runs 5 sample inputs for testing
├── requirements.txt   # Dependencies
├── .env.example       # Template for the API key file
└── .gitignore
```

## How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/visheshharpale/llm-ps22-ADT23SOCB1326.git
   cd llm-ps22-ADT23SOCB1326
   ```

2. **(Optional) Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get a free Groq API key** at [console.groq.com](https://console.groq.com) → API Keys → Create API Key.

5. **Create a `.env` file** in the project folder (copy `.env.example`) and add your key:
   ```
   GROQ_API_KEY=your_key_here
   ```

6. **Run the app**
   ```bash
   streamlit run app.py
   ```
   Open http://localhost:8501 if the browser does not open automatically.

## Usage
1. Paste your notes (or click **Load sample notes**).
2. Choose the number of flashcards and the difficulty in the sidebar.
3. Click **Generate flashcards**.
4. Flip through the cards or view the table, then click **Download CSV**.

## Prompt Design
The system prompt tells the model to:
- use **only** the information in the notes (no invented facts),
- create one idea per card with short, accurate answers,
- mix question types (definitions, why/how, comparisons, examples),
- avoid duplicates,
- return **valid JSON only** in the form `{"flashcards": [{"question": "...", "answer": "..."}]}`.

## Error Handling
- Retries automatically (with waiting) on rate-limit or temporary server errors.
- If the chosen model is unavailable, it re-discovers an available model and tries again.
- Strips markdown fences and removes empty or duplicate cards when parsing JSON.
- Shows a friendly error message in the UI instead of crashing.

## Note on Security
The API key is stored only in a local `.env` file, which is excluded from Git through `.gitignore`.
