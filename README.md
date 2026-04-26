# FinLit AI Service

The **FinLit AI Service** is a high-performance backend microservice built with FastAPI, designed to power the AI-driven financial literacy capabilities of the FinLit platform. It leverages the Groq LPU™ Inference Engine to provide lightning-fast financial advice and insights.

## 🚀 Features

- **Blazing Fast AI**: Powered by Groq for near-instant responses.
- **RESTful API**: Clean and documentation-friendly endpoints using FastAPI.
- **Scalable Architecture**: Modular structure designed for growth.
- **Asynchronous Execution**: Fully utilizes Python's `asyncio` for high concurrency.
- **Contextual Intelligence**: Analyzes user financial profiles and transactions for personalized advice.
- **Session Management**: Supports multiple persistent chat sessions with history tracking.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **LLM Engine**: [Groq](https://groq.com/)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **Language**: Python 3.10+

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd finlit-ai-service
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Create a `.env` file in the root directory and add your credentials:
   ```env
   GROQ_API_KEY=your_api_key_here
   GROQ_MODEL=llama3-70b-8192  # or your preferred model
   ```

## 🏃 Running the Application

Start the development server with hot-reload:

```bash
uvicorn app.main:app --reload
```

The service will be available at `http://127.0.0.1:8000`.

## 📖 API Documentation

Once the server is running, you can access the interactive API docs:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 📡 API Endpoints

### Chat Assistant
`POST /api/chat/`

**Request Body:**
```json
{
  "message": "How can I start investing with $100?"
}
```

**Response:**
```json
{
  "response": "Starting with $100 is a great first step! You can consider..."
}
```

## 📂 Project Structure

```text
finlit-ai-service/
├── app/
│   ├── api/            # Route handlers
│   ├── core/           # Configuration and security
│   ├── schemas/        # Pydantic models (Request/Response)
│   ├── services/       # Business logic & LLM integration
│   └── main.py         # App entry point
├── .env                # Environment variables (Internal only)
├── .gitignore          # Git ignore rules
└── requirements.txt    # Project dependencies
```

---
Built with ❤️ by the FinLit AI Team.
