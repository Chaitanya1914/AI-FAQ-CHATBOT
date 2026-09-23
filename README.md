# 🤖 AI-Powered FAQ Chatbot

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📌 Overview
An intelligent, AI-powered FAQ chatbot designed for customer support. This project leverages Natural Language Processing (NLP) to understand user queries rather than relying on brittle keyword matching. By utilizing semantic search powered by Sentence Transformers, the chatbot can accurately map diverse user questions to the most relevant predefined FAQs, providing instant, highly accurate answers.

## ✨ Features
- **🧠 Semantic Search:** Uses Sentence Transformers to understand the meaning behind queries.
- **💬 Real-time Chat Interface:** Smooth and responsive API for instant communication.
- **📊 Admin Dashboard:** Analyze bot performance and view metrics.
- **📝 Conversation Logging & Feedback:** All interactions are logged with optional user feedback to continuously improve responses.
- **🔧 FAQ Management (CRUD):** Easily add, update, delete, or categorize FAQs via a RESTful API.
- **🎯 Confidence-based Routing:** Automatically detects when a query is off-topic or unmatched and gracefully falls back to default responses.
- **📱 Responsive Design:** Built to integrate easily with mobile or web frontends.

## 🏗️ Architecture
The application follows a clean, layered architecture:
- **API Layer (Routers):** Handles HTTP requests using FastAPI.
- **Service Layer:** Contains core business logic (`ChatService`, `FAQService`).
- **NLP Engine:** Preprocesses text and performs semantic similarity search using Sentence Transformers.
- **Database Layer:** Manages persistent storage using SQLAlchemy & SQLite.

## 💻 Tech Stack

| Component | Technology |
| --- | --- |
| **Backend** | FastAPI, Python 3.10+ |
| **NLP** | `sentence-transformers`, NLTK |
| **Database** | SQLite + SQLAlchemy |
| **Frontend** | HTML5, CSS3, JavaScript (Dashboard/UI) |
| **Testing** | pytest |

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/faq-chatbot.git
   cd faq-chatbot
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   python -m app.main
   ```

5. **Access the application**
   - Chat Interface: [http://localhost:8000](http://localhost:8000)
   - Admin Dashboard: [http://localhost:8000/admin](http://localhost:8000/admin)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📖 API Documentation
FastAPI automatically generates interactive documentation. Once the server is running, visit `/docs` (Swagger UI) or `/redoc` (ReDoc) to explore endpoints.

**Main Endpoints:**
- `POST /api/chat` — Send a message to the chatbot
- `GET /api/faq` — List all FAQs (with optional category filtering)
- `POST /api/faq` — Add a new FAQ
- `GET /api/logs` — View paginated conversation logs
- `GET /api/logs/stats` — Get high-level bot usage statistics

## ⚙️ How It Works
1. **Embedding Generation:** Predefined FAQ questions are processed and encoded into dense mathematical vectors using sentence-transformers.
2. **Query Processing:** When a user asks a question, the input is preprocessed and encoded in the same vector space.
3. **Semantic Matching:** Cosine similarity is calculated between the user query vector and all FAQ vectors to find the best match.
4. **Confidence Threshold:** If the highest similarity score exceeds a defined threshold, the corresponding FAQ answer is returned. Otherwise, a graceful fallback response is provided.
5. **Continuous Learning:** All interactions and confidence scores are logged to the database for further analysis and improvement.

## 📁 Project Structure
```text
.
├── app
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── nlp
│   │   ├── engine.py
│   │   └── preprocessor.py
│   ├── services
│   │   ├── chat_service.py
│   │   └── faq_service.py
│   ├── routers
│   │   ├── chat.py
│   │   ├── faq.py
│   │   └── logs.py
│   └── templates
│       ├── index.html
│       └── admin.html
├── data
│   └── faq_seed.json
├── tests
│   ├── conftest.py
│   ├── test_nlp_engine.py
│   ├── test_chat.py
│   └── test_faq.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔐 Environment Variables (Optional)

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./chatbot.db` | Database connection string |
| `MODEL_NAME` | `all-MiniLM-L6-v2` | Sentence Transformer model name |
| `SIMILARITY_THRESHOLD` | `0.65` | Minimum confidence to return a match |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `ENV` | `development` | Set to `production` to disable hot-reload |

## 🧪 Running Tests
The project includes a robust test suite covering unit tests for the NLP engine and integration tests for the API.
```bash
pytest tests/ -v
```

## 🔮 Future Improvements
- Multi-language support using cross-lingual embeddings
- Integration with LLMs for generative responses
- WebSocket support for real-time chat
- User authentication for admin dashboard
- Export conversation logs to CSV

## 📄 License
MIT License

## ✍️ Author
Your Name
