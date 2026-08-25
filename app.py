"""
Compatibility helper.
This project now runs as:
- FastAPI backend: backend/main.py
- React frontend: frontend/
"""

from __future__ import annotations


def main() -> None:
    print("This project no longer uses Streamlit app.py.")
    print("Run backend:  py -3.11 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
    print("Run frontend: cd frontend && npm run dev")
    print("Open UI at:   http://localhost:5173")


if __name__ == "__main__":
    main()
