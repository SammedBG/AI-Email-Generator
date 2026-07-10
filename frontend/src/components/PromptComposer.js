import React from "react";
import { AlertCircle, Loader2, Sparkles } from "lucide-react";

export function PromptComposer({
  prompt,
  tone,
  model,
  loading,
  error,
  tones,
  models,
  examplePrompts,
  onPromptChange,
  onToneChange,
  onModelChange,
  onExampleSelect,
  onGenerate,
  onClear,
  onKeyDown,
}) {
  return (
    <div className="card">
      <div className="card__label">Compose</div>
      <div className="card__title">What email do you need?</div>

      <label className="prompt-label" htmlFor="prompt-input">
        Prompt
      </label>
      <textarea
        id="prompt-input"
        value={prompt}
        onChange={(e) => onPromptChange(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="e.g. Write a follow-up email after a job interview"
        className="prompt-textarea"
      />

      <div className="examples">
        {examplePrompts.map((example) => (
          <button
            key={example}
            onClick={() => onExampleSelect(example)}
            className="example-chip"
          >
            {example}
          </button>
        ))}
      </div>

      <div className="composer-row">
        <div className="composer-col">
          <label className="prompt-label">Tone</label>
          <div className="tone-group">
            {tones.map((item) => (
              <button
                key={item.name}
                onClick={() => onToneChange(item.name)}
                className={`tone-btn ${tone === item.name ? "tone-btn--active" : ""}`}
                title={item.description}
              >
                {item.name}
              </button>
            ))}
          </div>
        </div>

        <div className="composer-col">
          <label className="prompt-label" htmlFor="model-select">
            AI Model
          </label>
          <select
            id="model-select"
            value={model}
            onChange={(e) => onModelChange(e.target.value)}
            className="model-select"
          >
            {models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="actions">
        <button
          onClick={onGenerate}
          disabled={loading}
          className="btn btn--primary"
        >
          {loading ? (
            <>
              <Loader2 className="spin" size={16} />
              Generating…
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Generate Email
            </>
          )}
        </button>

        <button onClick={onClear} className="btn btn--secondary">
          Clear
        </button>
      </div>

      <p className="shortcut-hint">
        Press <kbd>Ctrl / ⌘ + Enter</kbd> to generate.
      </p>

      {error && (
        <div className="error-msg">
          <AlertCircle />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}