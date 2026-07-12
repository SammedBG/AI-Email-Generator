# AI Email Generator

An AI-powered web application that generates professional emails from a simple prompt. Users describe what they need (e.g. *"Write a follow-up email after an interview"*), pick a tone, select an AI model, and the app generates a complete email with a subject line and body using an LLM.

Built as part of the Full Stack AI Developer assignment, updated with advanced features.

### Live on : **https://ai-email-generator-ten-nu.vercel.app/**

---

## ✨ Features

**Core Features**
- **AI Email Generation**: Prompt-based email generation using Groq's active models, with a deterministic template fallback when offline or no API key is configured.
- **Tone Selector**: Supports Professional, Friendly, Formal, and Casual tones.
- **Design System**: A custom-built, modern light-theme UI using a single-column layout, optimized typography (Inter), and premium animations (shimmer loading skeletons, custom transitions). Fully responsive down to mobile.
- **Error Handling**: Comprehensive backend error catching with graceful offline mode, and visual red-banner errors on the frontend.

**Bonus Features Implemented**
- **Authentication (JWT Bearer Tokens)**: Register and log in. User sessions are managed using JWT tokens sent via `Authorization: Bearer` headers, ensuring reliable cross-origin authentication across all browsers. Routes and history are protected per-user.
- **Multiple AI Model Support**: Dropdown selector supporting **Llama 3.1 8B Instant** (priority model) and **Llama 3.3 70B Versatile**.
- **Rich Text Editor**: Integrated `react-quill` inside an "Edit Your Email" card. Allows users to format, add headers/lists, and refine the email before copying.
- **MongoDB Persistence**: Integrates with a MongoDB database to persist registered user accounts and prompt histories across restarts. **Graceful offline fallback**: if MongoDB is down, the backend automatically detects it and falls back to in-memory dictionaries so the app remains fully functional.
- **Email Subject Generation**: Auto-generates matching subject lines alongside the email body.
- **Copy-to-Clipboard**: Copy buttons for both the raw generated email and the rich-text formatted output.
- **Open in Email Client**: An "Open in Email" button that triggers a `mailto:` link, pre-filling the user's default email client with the generated subject and body.
- **Quick Example Chips**: Interactive example prompts to populate the composer instantly.


---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, Vanilla CSS (custom properties), Lucide Icons, React Quill |
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB (via `motor` asynchronous driver) with automatic fallback |
| **Authentication** | JWT (JSON Web Tokens), Bearer token authorization, `bcrypt` password hashing |
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
│   ├── tailwind.config.js   # Tailwind configuration
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
| POST | `/auth/register` | Create an account (returns JWT token in response body) |
| POST | `/auth/login` | Authenticate user (returns JWT token in response body) |
| POST | `/auth/logout` | Clear the session |
| GET | `/auth/me` | Fetch active user information (requires Bearer token) |

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
- **Bearer Token Auth**: JWT tokens are returned in the response body and sent via `Authorization: Bearer` headers. This approach was chosen because the frontend (Vercel) and backend (Render) are on separate domains — modern desktop browsers block cross-origin cookies, making Bearer tokens the reliable industry-standard solution.
- **Database Fallback Resilience**: Connection status is checked asynchronously at startup. If MongoDB is down, the server warns you but continues running by caching accounts and histories in-memory.
- **Structured LLM Parsing**: The prompt structure instructs the model to return `SUBJECT:` and `BODY:` demarcators. The backend parses this structure using regular expressions, falling back to heuristic subject-line generation if the LLM output is free-form.

---

## 🌐 Production Deployment Instructions

### 1. Database Setup (MongoDB Atlas)
1. Register a free account at [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas/register).
2. Create a free shared cluster (M0 tier).
3. Under **Database Access**, create a user with a secure password.
4. Under **Network Access**, whitelist `0.0.0.0/0` (access from anywhere) to allow Render's dynamic IPs to connect.
5. Click **Connect** -> **Connect your application** and copy the connection URI (e.g. `mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`).

### 2. Backend Deployment (Render)
1. Create a free account at [render.com](https://render.com/).
2. Click **New +** -> **Web Service** and connect your GitHub repository.
3. Configure settings:
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
4. In the **Environment Variables** tab, add:
   - `GROQ_API_KEY`: *(your actual live Groq key)*
   - `MONGODB_URL`: *(your Atlas connection URI from Step 1)*
   - `MONGODB_DB_NAME`: `ai_email_generator`
   - `JWT_SECRET`: *(a random string, e.g. `9f8e7d6c5b4a3b2c1d0e9f8a7b6c5d`)*
   - `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app` *(add the domain where you host your React app)*

### 3. Frontend Deployment (Vercel)
1. Register a free account at [vercel.com](https://vercel.com/).
2. Click **Add New** -> **Project** and import your repository.
3. In configure settings:
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
4. Expand **Environment Variables** and add:
   - `REACT_APP_API_URL`: `https://your-backend-domain.onrender.com` *(the public Render URL)*
5. Click **Deploy**.

---

## 📹 Demo

See attached screenshots for a walkthrough of the application.
### 🔐 1. Login:
Users can securely log in to access the application and start generating AI-powered emails.
<img width="610" height="410" alt="image" src="https://github.com/user-attachments/assets/b3d39f0a-5b92-482a-9428-d4bb92c6cbc7" />

---

### ✍️ 2. Enter Prompt
Users provide an email prompt, select the desired tone (Professional, Friendly, Formal, or Casual), and click **Generate Email**.
<img width="527" height="374" alt="image" src="https://github.com/user-attachments/assets/a3a7cfeb-7997-4cb2-8924-2c8f99931302" />

---

### 🤖 3. AI-Generated Email
The application generates a professional email along with a suitable subject line based on the user's prompt and selected tone.

<img width="501" height="379" alt="image" src="https://github.com/user-attachments/assets/dfcb9f68-0c4d-4335-93b0-5a53116def15" />

---

### ✏️ 4. Edit Generated Email
Users can review and edit the generated email content before copying or using it, allowing them to personalize the final message.

<img width="452" height="296" alt="image" src="https://github.com/user-attachments/assets/7264775e-b96e-4e02-aa71-84e6594b8ce1" />

---

### 🕒 5. Email History
All previously generated emails are stored in the history section, allowing users to revisit, edit, or reuse their past emails whenever needed.

<img width="438" height="164" alt="image" src="https://github.com/user-attachments/assets/b3a255aa-e838-43ac-8fc9-74598ef7d4b5" />

---

## 👤 Author

Sammed Ghattad
