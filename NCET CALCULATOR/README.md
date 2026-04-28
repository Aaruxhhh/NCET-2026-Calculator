# NCET 2026 Score Calculator

A premium glassmorphism web app to calculate your NCET 2026 score by uploading response-sheet PDFs.

**Built by [u/ruxh_alt](https://www.reddit.com/user/ruxh_alt)**

---

## Features

- **PDF Upload** — Drag-and-drop up to 7 response-sheet PDFs
- **Regex Parsing** — Automatically extracts Question IDs and Candidate Answers
- **Instant Scoring** — +4 correct · −1 incorrect · 0 unattempted
- **Interactive Table** — Edit any answer via dropdown; score recalculates instantly
- **Search** — Filter questions by ID
- **Liquid Glass UI** — Monochrome black & white glassmorphism design

---

## How to Run Locally

### 1. Install Python dependencies

```bash
cd "NCET CALCULATOR"
pip install -r requirements.txt
```

### 2. (Optional) Add the real answer key

Open `app.py` and replace the `OFFICIAL_ANSWER_KEY` dictionary with the real NCET 2026 answer key:

```python
OFFICIAL_ANSWER_KEY = {
    "12442": "2",
    "12443": "3",
    # ... add all questions
}
```

### 3. Run the server

```bash
python app.py
```

### 4. Open in your browser

Navigate to **http://localhost:5000**

---

## Project Structure

```
NCET CALCULATOR/
├── app.py               # Flask backend (PDF parsing, scoring API)
├── templates/
│   └── index.html       # Frontend (HTML + CSS + JS, all-in-one)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## Tech Stack

| Layer    | Technology                  |
|----------|-----------------------------|
| Backend  | Python · Flask              |
| PDF      | pdfplumber                  |
| Frontend | Vanilla HTML · CSS · JS     |
| Design   | Glassmorphism (monochrome)  |
