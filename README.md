# PeopleGPT

PeopleGPT is an AI-powered talent search engine that helps recruiters find and screen candidates efficiently using natural language processing and LLMs.

## Features

- Natural language talent search
- Automated resume parsing and skill extraction
- Candidate ranking and scoring system
- AI-powered background checking and pre-screening
- Talent pool analytics and insights
- Personalized candidate outreach

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React
- LLM: Ollama
- Database: SQLite (development) / PostgreSQL (production)
- Vector Store: ChromaDB
- Analytics: PostHog

## Setup Instructions

1. Install Python 3.9+ and Node.js 16+

2. Install Ollama:
   ```bash
   # For Windows (using WSL):
   wsl --install
   curl https://ollama.ai/install.sh | sh
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DATABASE_URL=sqlite:///./peoplegpt.db
SECRET_KEY=your-secret-key
OLLAMA_BASE_URL=http://localhost:11434
```

## License

MIT 