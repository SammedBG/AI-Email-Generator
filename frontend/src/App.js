import React, { useEffect, useState, useCallback } from "react";
import { Analytics } from "@vercel/analytics/react";
import { EmailHeader } from "./components/EmailHeader";
import { PromptComposer } from "./components/PromptComposer";
import { GeneratedEmailCard } from "./components/GeneratedEmailCard";
import { PromptHistory } from "./components/PromptHistory";
import { AuthModal } from "./components/AuthModal";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const TONES = [
  { name: "Professional", description: "Clear, polished, and business-ready." },
  { name: "Friendly", description: "Warm and approachable without sounding sloppy." },
  { name: "Formal", description: "Respectful, traditional, and highly structured." },
  { name: "Casual", description: "Relaxed and conversational for familiar recipients." },
];

const EXAMPLE_PROMPTS = [
  "Write a follow-up email after an interview",
  "Generate a leave request email",
  "Write a cold outreach email for a SaaS product",
];

const DEFAULT_MODELS = [
  { id: "llama-3.1-8b-instant", name: "Llama 3.1 8B Instant", description: "" },
];

/* Helper to build headers with Authorization Bearer token */
function authHeaders(extraHeaders = {}) {
  const token = localStorage.getItem("auth_token");
  const headers = { ...extraHeaders };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

function App() {
  const [user, setUser] = useState(null);
  const [authChecking, setAuthChecking] = useState(true);

  const [prompt, setPrompt] = useState("");
  const [tone, setTone] = useState("Professional");
  const [model, setModel] = useState("llama-3.1-8b-instant");
  const [models, setModels] = useState(DEFAULT_MODELS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  // Check if user is already authenticated via stored token
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("auth_token");
      if (!token) {
        setAuthChecking(false);
        return;
      }
      try {
        const res = await fetch(`${API_URL}/auth/me`, {
          headers: authHeaders(),
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          setUser(data.username);
        } else {
          // Token expired or invalid — clear it
          localStorage.removeItem("auth_token");
        }
      } catch (_err) {
        /* not authenticated */
      } finally {
        setAuthChecking(false);
      }
    };
    checkAuth();
  }, []);

  // Fetch available models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await fetch(`${API_URL}/models`);
        if (res.ok) {
          const data = await res.json();
          if (data.models && data.models.length > 0) {
            setModels(data.models);
            setModel(data.models[0].id);
          }
        }
      } catch (_err) {
        /* use defaults */
      }
    };
    fetchModels();
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/history`, {
        headers: authHeaders(),
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data.history || []);
      }
    } catch (_err) {
      /* history load failed */
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  // Load history when user logs in
  useEffect(() => {
    if (user) {
      loadHistory();
    } else {
      setHistory([]);
      setHistoryLoading(false);
    }
  }, [user, loadHistory]);

  /* Called by AuthModal on successful login/register */
  const handleAuth = (username, token) => {
    if (token) {
      localStorage.setItem("auth_token", token);
    }
    setUser(username);
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt describing the email you need.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: authHeaders({ "Content-Type": "application/json" }),
        credentials: "include",
        body: JSON.stringify({ prompt, tone, model }),
      });

      const data = await res.json();

      if (!res.ok) {
        if (res.status === 401) {
          setError("Not authenticated — please log in");
          localStorage.removeItem("auth_token");
          setUser(null);
          return;
        }
        setError(data.detail || "Something went wrong while generating the email.");
        return;
      }

      setResult(data);
      loadHistory();
    } catch (_err) {
      setError("Cannot connect to the server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result) return;

    try {
      const fullText = `Subject: ${result.subject}\n\n${result.body}`;
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (_err) {
      /* clipboard API not available */
    }
  };


  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        headers: authHeaders(),
        credentials: "include",
      });
    } catch (_err) {
      /* ignore */
    }
    localStorage.removeItem("auth_token");
    setUser(null);
    setResult(null);
    setHistory([]);
  };

  const reuseHistoryItem = (item) => {
    setPrompt(item.prompt);
    setTone(item.tone);
    setResult(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Show nothing while checking auth
  if (authChecking) {
    return (
      <div className="app-container" style={{ textAlign: "center", paddingTop: "120px" }}>
        <p style={{ color: "#64748b" }}>Loading…</p>
        <Analytics />
      </div>
    );
  }

  // Show auth modal if not logged in
  if (!user) {
    return (
      <div className="app-container">
        <AuthModal onAuth={handleAuth} />
        <Analytics />
      </div>
    );
  }

  return (
    <div className="app-container">
      <EmailHeader user={user} onLogout={handleLogout} />

      <PromptComposer
        prompt={prompt}
        tone={tone}
        model={model}
        loading={loading}
        error={error}
        tones={TONES}
        models={models}
        examplePrompts={EXAMPLE_PROMPTS}
        onPromptChange={setPrompt}
        onToneChange={setTone}
        onModelChange={setModel}
        onExampleSelect={setPrompt}
        onGenerate={handleGenerate}
        onClear={() => {
          setPrompt("");
          setError("");
          setResult(null);
        }}
      />

      <GeneratedEmailCard
        result={result}
        loading={loading}
        copied={copied}
        onCopy={handleCopy}
      />

      <PromptHistory
        history={history}
        loading={historyLoading}
        onReuse={reuseHistoryItem}
      />

      <footer className="app-footer">
        Built with FastAPI, React, and Groq AI.
      </footer>
      <Analytics />
    </div>
  );
}

export default App;
