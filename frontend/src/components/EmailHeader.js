import React from "react";
import { Mail, LogOut, User } from "lucide-react";

export function EmailHeader({ user, onLogout }) {
  return (
    <header className="app-header">
      <div className="app-header__top-bar">
        <div className="app-header__badge">
          <Mail />
          AI Email Generator
        </div>
        {user && (
          <div className="app-header__user">
            <span className="app-header__username">
              <User size={14} />
              {user}
            </span>
            <button onClick={onLogout} className="btn btn--secondary btn--sm">
              <LogOut size={14} />
              Logout
            </button>
          </div>
        )}
      </div>
      <h1 className="app-header__title">Generate polished emails in seconds</h1>
      <p className="app-header__subtitle">
        Describe what you need, pick a tone and model, and get a ready-to-send email.
      </p>
    </header>
  );
}