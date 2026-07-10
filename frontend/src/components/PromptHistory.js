import React from "react";
import { ChevronRight } from "lucide-react";

export function PromptHistory({ history, loading, onReuse }) {
  const formatTime = (value) => {
    if (!value) return "Just now";

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "Recently";

    return new Intl.DateTimeFormat(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    }).format(date);
  };

  return (
    <div className="card">
      <div className="card__label">History</div>
      <div className="card__title">Recent Prompts</div>

      {loading ? (
        <div className="skeleton">
          <div className="skeleton__line skeleton__line--short" />
          <div className="skeleton__line skeleton__line--short" style={{ marginTop: 10 }} />
          <div className="skeleton__line skeleton__line--short" style={{ marginTop: 10 }} />
        </div>
      ) : history.length === 0 ? (
        <div className="history-empty">
          No generations yet. Your prompt history will appear here.
        </div>
      ) : (
        <ul className="history-list">
          {history.slice(0, 5).map((item, index) => (
            <li key={`${item.created_at}-${index}`}>
              <button className="history-item" onClick={() => onReuse(item)}>
                <div className="history-item__top">
                  <span className="history-item__subject">{item.subject}</span>
                  <span className="history-item__tone">{item.tone}</span>
                </div>
                <p className="history-item__prompt">{item.prompt}</p>
                <div className="history-item__footer">
                  <span>{formatTime(item.created_at)}</span>
                  <span className="history-item__reuse">
                    Reuse <ChevronRight />
                  </span>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}