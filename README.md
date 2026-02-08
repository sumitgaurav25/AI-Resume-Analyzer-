AI Resume Analyzer

A Streamlit app that analyzes your resume with AI, lets you chat with an agent for follow-up questions, export the report, and compare your resume against a job description—all powered by [Open Router](https://openrouter.ai/).

---

## Features

- **Resume upload** – Upload your resume as **PDF** or **TXT**.
- **Optional job role** – Enter the role you’re targeting so feedback is tailored (e.g. “Data Scientist”, “Product Manager”).
- **AI analysis** – Get structured feedback on:
  - Content clarity and impact  
  - Skills presentation  
  - Experience descriptions  
  - A score out of 100 and concrete improvement suggestions  
- **Chat with the agent** – After the analysis, ask follow-up questions in a chat. The agent has full context (resume + analysis) and can answer things like “How do I improve the skills section?” or “Rewrite my experience for a data scientist role.”
- **Export** – Download the analysis (and chat transcript) as **TXT** or **PDF**.
- **Job description matching** – Paste a full job description and get:
  - A **match score** (0–100) with a short justification  
  - **Missing keywords/skills** from the JD  
  - **Tailored suggestions** (3–5 concrete changes) to align your resume with the role  

---

## Tech stack

- **Streamlit** – Web UI  
- **Open Router** – AI API (OpenAI-compatible; used with `openai/gpt-4o-mini` or any model you set)  
- **PyPDF2** – PDF text extraction  
- **fpdf2** – PDF export for reports  
- **python-dotenv** – Load `.env` for API keys  

---

## Prerequisites

- **Python 3.13+**
- **UV** (recommended) or pip for dependency management  
- An **Open Router** API key from [openrouter.ai](https://openrouter.ai/)  

---

## Installation

1. **Clone the repo** (or navigate to this folder):

   ```bash
   git clone <your-repo-url>
   cd project2
   ```

2. **Install dependencies** (with UV):

   ```bash
   uv sync
   ```

   Or with pip:

   ```bash
   pip install -e .
   ```

3. **Environment variables** – Create a `.env` file in the project root:

   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

   Optional (defaults to `openai/gpt-4o-mini` if not set):

   ```env
   OPENROUTER_MODEL=openai/gpt-4o-mini
   ```

   Get your API key from [Open Router](https://openrouter.ai/keys).

---

## How to run

From the project root:

```bash
uv run streamlit run main.py
```

Or with pip:

```bash
streamlit run main.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

---

## Usage flow

1. **Upload** your resume (PDF or TXT) and optionally enter a job role.  
2. Click **Analyze Resume** and wait for the AI analysis and score.  
3. Use **Download as TXT** or **Download as PDF** to save the report (and chat transcript).  
4. (Optional) Paste a **job description** and click **Match resume with job description** to get a match score and tailored suggestions.  
5. Use the **chat** at the bottom to ask follow-up questions about your resume or the analysis.  

---

## Project structure

```
project2/
├── main.py          # Streamlit app (upload, analysis, chat, export, job match)
├── pyproject.toml   # Dependencies and project metadata
├── .env             # Your OPENROUTER_API_KEY (not committed)
├── README.md        # This file
└── ...
```

---

## License

Use this project as you like; adjust license and attribution to match your repo.
