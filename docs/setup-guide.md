# Setup Guide

> **This file is read by the automated evaluation pipeline. Be precise and complete.**

## Prerequisites

Before you begin, ensure you have the following installed:

- [ ] Python 3.10+
- [ ] PostgreSQL or SQLite
- [ ] Modern Web Browser (Chrome, Firefox, Edge)
- [ ] An IBM Cloud account with watsonx.ai access
- [ ] IBM BOB

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description | Required |
|---|---|---|
| DATABASE_URL | Database connection string (e.g., SQLite or PostgreSQL)| Yes |
| WATSONX_API_KEY | IBM watsonx.ai API key for predictive risk analytics   | Yes |
| WATSONX_PROJECT_ID | IBM watsonx.ai project ID | Yes |
| PORT | Backend application running port (default: 8000) | No |

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/TeamCMPICA/supply-chain-optimizer.git
cd supply-chain-optimizer

# 2. Set up Python Virtual Environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Install backend dependencies
pip install -r requirements.txt

## Running the Application

# 1. Initialize Database Schema & Seed Data (if using local database)
sqlite3 optimizer.db < ../database/schema.sql
sqlite3 optimizer.db < ../database/sample_data.sql

# 2. Start the FastAPI backend server
python run.py

# 3. Launch the Frontend Interface
# Open supply-chain-optimizer/frontend/index.html directly in any modern browser

The application will be available at: http://localhost:8000

## Running Tests

# Execute backend module tests
pytest

## Quick Demo (Optional)

# Seed local database with sample shipment and cold-chain telemetry
sqlite3 backend/optimizer.db < database/sample_data.sql

# Serve frontend via simple Python HTTP server (alternative to direct file open)
cd frontend && python -m http.server 3000

## Troubleshooting

ModuleNotFoundError : Ensure your virtual environment is activated and rerun pip install -r requirements.txt inside the backend/ directory.
Database connection failed : Verify the DATABASE_URL path in backend/.env or re-apply schema.sql to re-initialize your database instance.
watsonx.ai 401 Unauthorized Error : Check that WATSONX_API_KEY and WATSONX_PROJECT_ID are correctly set in your backend/.env file.
CORS issue on Frontend API requests : Ensure the backend server (run.py) is running on http://localhost:8000 before opening index.html.

| Issue | Solution |
|---|---|
| [e.g., `ModuleNotFoundError`] | [e.g., Run `pip install -r requirements.txt` again] |
| [e.g., Database connection refused] | [e.g., Ensure PostgreSQL is running: `docker compose up db`] |
| [e.g., watsonx.ai 401 error] | [e.g., Check `WATSONX_API_KEY` in your `.env` file] |
