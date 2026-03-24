# expense-tracking-app

Full-stack starter workspace for a Flask + React expense tracking application.

## Project Structure
- `backend/`: Flask API for auth, transactions, categories, budgets, dashboard summary, and CSV export.
- `frontend/`: React (Vite) client for dashboard cards, transaction form, and recent transactions.
- `.github/copilot-instructions.md`: workspace-wide Copilot instructions.
- `.github/agents/`: custom agents for review, planning, and debugging workflows.
- `documents/`: requirements and planning references.

## Backend Setup (Flask)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Backend runs on `http://localhost:5000`.

## Frontend Setup (React)
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and calls the backend via `http://localhost:5000/api`.

## Notes
- This scaffold uses an in-memory store in backend for fast MVP setup.
- Replace auth placeholder hashing and token logic with secure production implementations.
- Add persistence (PostgreSQL/MySQL/SQLite) and migrations before production release.
