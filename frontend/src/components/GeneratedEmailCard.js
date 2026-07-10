import React from "react";
import { Check, Copy } from "lucide-react";
import { RichTextEditor } from "./RichTextEditor";

export function GeneratedEmailCard({ result, loading, copied, onCopy }) {
  return (
    <>
      <div className="card">
        <div className="output-header">
          <div>
            <div className="card__label">Output</div>
            <div className="card__title">Generated Email</div>
          </div>
          {result && (
            <button onClick={onCopy} className="btn btn--copy">
              {copied ? <Check size={14} /> : <Copy size={14} />}
              {copied ? "Copied!" : "Copy"}
            </button>
          )}
        </div>

        {!result && !loading && (
          <div className="output-empty">
            Your generated email will appear here. Try an example prompt to get started.
          </div>
        )}

        {loading && (
          <div className="skeleton">
            <div className="skeleton__line skeleton__line--short" />
            <div className="skeleton__line skeleton__line--tall" />
          </div>
        )}

        {result && !loading && (
          <div className="email-result">
            <div className="email-result__subject">
              <div className="email-result__subject-label">
                Subject
                <span className="email-result__provider">
                  {result.provider || "mock"}
                </span>
                <span className="email-result__model-tag">
                  {result.model || "default"}
                </span>
              </div>
              <div className="email-result__subject-text">{result.subject}</div>
            </div>
            <div className="email-result__body">
              <div className="email-result__body-label">Body</div>
              <div className="email-result__body-text">{result.body}</div>
            </div>
          </div>
        )}
      </div>

      {result && !loading && (
        <RichTextEditor body={result.body} subject={result.subject} />
      )}
    </>
  );
}