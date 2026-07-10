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
      // Convert plain text newlines to HTML for the editor
      const html = body.replace(/\n/g, "<br>");
      setContent(html);
    }
  }, [body]);

  const handleCopy = async () => {
    try {
      // Extract plain text from the editor HTML
      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = content;
      const plainText = `Subject: ${subject}\n\n${tempDiv.textContent || tempDiv.innerText}`;
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
