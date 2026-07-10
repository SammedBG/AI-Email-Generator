# AI Email Generator

An AI-powered web application that generates professional emails from a simple prompt. Users describe what they need (e.g. *"Write a follow-up email after an interview"*), pick a tone, select an AI model, and the app generates a complete email with a subject line and body using an LLM.

Built as part of the Full Stack AI Developer assignment, updated with advanced features.

---

## ✨ Features

**Core Features**
- **AI Email Generation**: Prompt-based email generation using Groq's active models, with a deterministic template fallback when offline or no API key is configured.
- **Tone Selector**: Supports Professional, Friendly, Formal, and Casual tones.
- **Design System**: A custom-built, modern light-theme UI using a single-column layout, optimized typography (Inter), and premium animations (shimmer loading skeletons, custom transitions). Fully responsive down to mobile.
- **Error Handling**: Comprehensive backend error catching with graceful offline mode, and visual red-banner errors on the frontend.

**Bonus Features Implemented**
- **Authentication (JWT & httpOnly Cookies)**: Register and log in. User sessions are securely stored using `httpOnly` cookies (avoiding `localStorage` for improved security). Routes and history lists are separated and protected per-user.
- **Multiple AI Model Support**: Dropdown selector supporting **Llama 3.1 8B Instant** (priority model) and **Llama 3.3 70B Versatile**.
- **Rich Text Editor**: Integrated `react-quill` inside an "Edit Your Email" card. Allows users to format, add headers/lists, and refine the email before copying.
- **MongoDB Persistence**: Integrates with a MongoDB database to persist registered user accounts and prompt histories across restarts. **Graceful offline fallback**: if MongoDB is down, the backend automatically detects it and falls back to in-memory dictionaries so the app remains fully functional.
- **Email Subject Generation**: Auto-generates matching subject lines alongside the email body.
- **Copy-to-Clipboard**: Copy buttons for both the raw generated email and the rich-text formatted output.
- **Quick Example Chips**: Interactive example prompts to populate the composer instantly.
- **Keyboard Shortcuts**: Generate emails using `Ctrl / ⌘ + Enter` inside the composer.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, Vanilla CSS (custom properties), Lucide Icons, React Quill |
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB (via `motor` asynchronous driver) with automatic fallback |
| **Authentication** | JWT (JSON Web Tokens), `httpOnly` secure session cookies, `bcrypt` password hashing |
| **Inference API** | Groq API — Llama 3.1 8B Instant (priority) & Llama 3.3 70B Versatile |

---

## 📂 Project Structure

```
ai-email-generator/
├── backend/
│   ├── main.py              # FastAPI app entrypoint
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py        # Environment, model settings, and JWT config
│   │   ├── database.py      # Async MongoDB setup (with connection checker)
│   │   ├── schemas.py       # Pydantic request/response & auth schemas
│   │   ├── server.py        # FastAPI app factory with CORS middleware configuration
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py      # Auth routes (register, login, logout, me)
│   │   │   └── email.py     # Email routes (models, generate, stream, history)
│   │   └── services/
│   │       ├── auth.py      # Direct bcrypt hashing, JWT validation
│   │       └── email_generation.py  # LLM completion & fallback template parsing
├── frontend/
│   ├── package.json         # Package configuration
│   ├── postcss.config.js    # PostCSS configs
│   ├── tailwind.config.js   # Tailwind configs (retained but unused)
│   ├── public/
│   │   └── index.html       # Inter font setup and mount point
│   ├── src/
│   │   ├── App.js           # Main state container and protected route shell
│   │   ├── index.js         # React renderer entry point
│   │   ├── index.css        # Vanilla CSS design system
│   │   └── components/
│   │       ├── AuthModal.js         # Register/login dialog
│   │       ├── EmailHeader.js       # App logo & logout controls
│   │       ├── PromptComposer.js    # Prompt textarea, model dropdown, tone row
│   │       ├── GeneratedEmailCard.js # Preview block & rich text container
│   │       ├── RichTextEditor.js    # Quill rich text box wrapper
│   │       └── PromptHistory.js     # User prompt history list
└── README.md                # Documentation file
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB (Optional — if running locally on `mongodb://localhost:27017` or Atlas. The app will gracefully fall back to in-memory mode if offline)
- A Groq API key ([console.groq.com](https://console.groq.com))

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd ai-email-generator
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
# Optional: set MONGODB_URL=mongodb://localhost:27017 or Atlas connection string
# Optional: set JWT_SECRET to a custom string

# Run the server
uvicorn main:app --reload
```
Backend will run at `http://localhost:8000`. You can visit `http://localhost:8000/docs` for the interactive Swagger API documentation.

### 3. Frontend Setup
```bash
cd ../frontend
npm install

# Create a .env file if changing the API URL:
# REACT_APP_API_URL=http://localhost:8000

npm start
```
Frontend will run at `http://localhost:3000`.

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create an account (returns JWT as httpOnly cookie) |
| POST | `/auth/login` | Authenticate user (returns JWT as httpOnly cookie) |
| POST | `/auth/logout` | Clear the session cookie |
| GET | `/auth/me` | Fetch active user information (requires cookie validation) |

### Email Generation
| Method | Endpoint | Description | Requires Auth? |
|---|---|---|---|
| GET | `/models` | List available Groq LLM models | No |
| POST | `/generate` | Generate email (returns subject + body) | **Yes** |
| POST | `/generate/stream` | Generate email via streaming (real-time plain text tokens) | **Yes** |
| GET | `/history` | Fetch the recent 20 prompt histories for the logged-in user | **Yes** |

---

## 🧠 Design Decisions

- **Direct Bcrypt Hashing**: Implemented hashing using the standard `bcrypt` module directly in Python. This bypasses the known `passlib` version check issue on Windows, resulting in a reliable runtime.
- **httpOnly Cookies**: Sessions are stored in secure browser cookies rather than `localStorage` to guard against Cross-Site Scripting (XSS) token theft.
- **Database Fallback Resilience**: Connection status is checked asynchronously at startup. If MongoDB is down, the server warns you but continues running by caching accounts and histories in-memory.
- **Structured LLM Parsing**: The prompt structure instructs the model to return `SUBJECT:` and `BODY:` demarcators. The backend parses this structure using regular expressions, falling back to heuristic subject-line generation if the LLM output is free-form.

---

## 👤 Author

Sammed Ghattad
