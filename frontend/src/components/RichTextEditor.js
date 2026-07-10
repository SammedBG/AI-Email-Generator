import React, { useState, useEffect } from "react";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import { Check, Copy } from "lucide-react";

const QUILL_MODULES = {
  toolbar: [
    [{ header: [1, 2, 3, false] }],
    ["bold", "italic", "underline"],
    [{ list: "ordered" }, { list: "bullet" }],
    ["link"],
    ["clean"],
  ],
};

export function RichTextEditor({ body, subject }) {
  const [content, setContent] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (body) {
      // Split by double newlines to find paragraphs
      const paragraphs = body.split(/\n\n+/);
      const html = paragraphs
        .map((p) => {
          // Replace single newlines within a paragraph with <br>
          const line = p.replace(/\n/g, "<br>");
          return `<p>${line}</p>`;
        })
        .join("");
      setContent(html);
    }
  }, [body]);

  const handleCopy = async () => {
    try {
      let html = content;

      // Convert block tag boundaries and line breaks to newlines
      html = html.replace(/<\/p>/gi, "\n\n");
      html = html.replace(/<\/div>/gi, "\n");
      html = html.replace(/<\/li>/gi, "\n");
      html = html.replace(/<br\s*\/?>/gi, "\n");
      html = html.replace(/<\/h[1-6]>/gi, "\n\n");

      // Strip all remaining HTML tags
      let text = html.replace(/<[^>]+>/g, "");

      // Use a textarea to decode HTML entities (like &nbsp; or &amp;) without collapsing newlines
      const txt = document.createElement("textarea");
      txt.innerHTML = text;
      let decodedText = txt.value;

      // Normalize consecutive newlines and trim whitespace
      decodedText = decodedText.replace(/\n{3,}/g, "\n\n").trim();

      const plainText = `Subject: ${subject}\n\n${decodedText}`;
      await navigator.clipboard.writeText(plainText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (_err) {
      /* clipboard not available */
    }
  };

  if (!body) return null;

  return (
    <div className="card">
      <div className="output-header">
        <div>
          <div className="card__label">Editor</div>
          <div className="card__title">Edit Your Email</div>
        </div>
        <button onClick={handleCopy} className="btn btn--copy">
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? "Copied!" : "Copy edited"}
        </button>
      </div>
      <p className="editor-hint">
        Edit the generated email below. Formatting will be preserved when you copy.
      </p>
      <div className="editor-wrapper">
        <ReactQuill
          theme="snow"
          value={content}
          onChange={setContent}
          modules={QUILL_MODULES}
          placeholder="Your email content will appear here..."
        />
      </div>
    </div>
  );
}
