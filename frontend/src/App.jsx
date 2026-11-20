import ReactMarkdown from "react-markdown";
import React from "react";
import "./App.css";
import { useRef, useState } from "react";
import {
  FileText,
  MessageSquare,
  Plus,
  Upload,
  Send,
  Trash2,
  PanelLeftClose,
  PanelLeftOpen,
  Bot,
  UserRound,
  Sparkles,
  LoaderCircle,
  AlertCircle,
  X,
  BookOpen,
  CheckCircle2,
} from "lucide-react";

const suggestions = [
  {
    title: "Summarize a document",
    prompt: "Can you summarize the main points of my document?",
  },
  {
    title: "Find key information",
    prompt: "What are the most important details in my document?",
  },
  {
    title: "Explain a concept",
    prompt: "Explain the main concepts in my document in simple terms.",
  },
];

function App() {
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const [documents, setDocuments] = useState([]);
  const [activeDocument, setActiveDocument] = useState("");
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [uploading, setUploading] = useState(false);
  const [sending, setSending] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  function clearChat() {
    setMessages([]);
    setQuestion("");
    setError("");
    setNotice("");
  }

  function selectDocument(document) {
  setActiveDocument(document);
  setError("");
  setNotice(`Selected document: ${document.filename}`);
}

  async function handleUpload(event) {
    const files = Array.from(event.target.files || []);
    event.target.value = "";

    if (!files.length) return;

    const nonPdf = files.find(
      (file) => !file.name.toLowerCase().endsWith(".pdf")
    );

    if (nonPdf) {
      setError("Please select PDF files only.");
      return;
    }

    setError("");
    setNotice("");
    setUploading(true);

    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
          "http://127.0.0.1:8000/documents/upload",
          {
            method: "POST",
            body: formData,
          }
        );

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(
            result.detail || `Failed to upload ${file.name}.`
          );
        }

        if (!result.document_id) {
  throw new Error(
    "Upload succeeded but the server did not return a document ID."
  );
}

const newDocument = {
  documentId: result.document_id,
  filename: result.filename || file.name,
  pages: result.pages_processed,
  chunks: result.chunks_created,
};

// Keep duplicate filenames as separate documents.
setDocuments((current) => [...current, newDocument]);

// Automatically select the newly uploaded PDF.
setActiveDocument(newDocument);
      }

      setNotice("Your document has been uploaded successfully.");
    } catch (uploadError) {
      setError(
        uploadError.message ||
          "Unable to upload the document. Check that the backend is running."
      );
    } finally {
      setUploading(false);
    }
  }

  async function handleSend(customQuestion) {
    const text = (customQuestion ?? question).trim();

    if (!text || sending) return;

    if (!activeDocument) {
      setError("Please upload and select a PDF before asking a question.");
      return;
    }

    setError("");
    setNotice("");
    setQuestion("");

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };

    setMessages((current) => [...current, userMessage]);
    setSending(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: text,
          document_id: activeDocument.documentId,
        }),
      });

      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          result.detail || "Unable to generate an answer."
        );
      }

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: result.answer,
          sources: result.sources || [],
        },
      ]);
    } catch (chatError) {
      setError(
        chatError.message ||
          "Unable to reach the server. Check that the backend is running."
      );
    } finally {
      setSending(false);

      requestAnimationFrame(() => {
        chatEndRef.current?.scrollIntoView({
          behavior: "smooth",
        });
      });
    }
  }

  return (
    <div className="app-shell">
      <aside
        className={`sidebar ${
          sidebarOpen ? "" : "sidebar-collapsed"
        }`}
      >
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-icon">
              <BookOpen size={21} strokeWidth={2.2} />
            </div>

            {sidebarOpen && (
              <div className="brand-copy">
                <span className="brand-name">DocuChat</span>
                <span className="brand-caption">
                  YOUR DOCUMENT ASSISTANT
                </span>
              </div>
            )}
          </div>

          <button
            className="icon-button sidebar-toggle"
            onClick={() => setSidebarOpen((current) => !current)}
            aria-label={
              sidebarOpen ? "Collapse sidebar" : "Expand sidebar"
            }
            title={
              sidebarOpen ? "Collapse sidebar" : "Expand sidebar"
            }
          >
            {sidebarOpen ? (
              <PanelLeftClose size={19} />
            ) : (
              <PanelLeftOpen size={19} />
            )}
          </button>
        </div>

        <button
          className="new-chat-button"
          onClick={clearChat}
          title="Start a new conversation"
        >
          <Plus size={19} />
          {sidebarOpen && <span>New conversation</span>}
        </button>

        <div className="sidebar-section">
          {sidebarOpen && (
            <div className="section-heading">
              <span>WORKSPACE</span>
            </div>
          )}

          <div className="navigation-item active">
            <MessageSquare size={18} />
            {sidebarOpen && <span>Document chat</span>}
          </div>
        </div>

        <div className="documents-section">
          <div className="documents-heading">
            {sidebarOpen && <span>Your documents</span>}

            <button
              className="icon-button small-icon"
              onClick={openFilePicker}
              title="Upload PDF"
              aria-label="Upload PDF"
            >
              <Plus size={17} />
            </button>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            multiple
            hidden
            onChange={handleUpload}
          />

          {uploading && (
            <div className="upload-status">
              <LoaderCircle size={15} className="spin" />
              {sidebarOpen && <span>Uploading PDF...</span>}
            </div>
          )}

          {documents.length === 0 &&
            !uploading &&
            sidebarOpen && (
              <div className="empty-documents">
                <FileText size={23} />
                <p>No documents yet</p>
                <span>Upload a PDF to get started.</span>
              </div>
            )}

          <div className="document-list">
            {documents.map((document) => {
              const isSelected =
                    activeDocument?.documentId === document.documentId;

              return (
                <button
                  type="button"
                  className={`document-item ${
                    isSelected ? "active-document" : ""
                  }`}
                  key={document.documentId}
                  title={`Select ${document.filename}`}
                  onClick={() => selectDocument(document)}

                  aria-pressed={isSelected}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    cursor: "pointer",
                    border: isSelected
                      ? "1px solid var(--accent-color, #8b5cf6)"
                      : undefined,
                  }}
                >
                  <div className="document-icon">
                    <FileText size={17} />
                  </div>

                  {sidebarOpen && (
                    <div className="document-details">
                      <span className="document-name">
                        {document.filename}
                      </span>

                      <span className="document-meta">
                        {document.pages}{" "}
                        {document.pages === 1 ? "page" : "pages"}
                        {document.chunks != null &&
                          ` · ${document.chunks} chunks`}
                      </span>
                    </div>
                  )}

                  {sidebarOpen &&
                    (isSelected ? (
                      <CheckCircle2
                        size={15}
                        className="document-check"
                        aria-label="Selected document"
                      />
                    ) : (
                      <FileText
                        size={15}
                        aria-label="Uploaded document"
                      />
                    ))}
                </button>
              );
            })}
          </div>

          {sidebarOpen && (
            <button
              className="upload-document-button"
              onClick={openFilePicker}
              disabled={uploading}
            >
              <Upload size={16} />
              Add PDF documents
            </button>
          )}

          {sidebarOpen && activeDocument && (
            <div
              style={{
                marginTop: "12px",
                padding: "10px",
                fontSize: "12px",
                overflowWrap: "anywhere",
                borderRadius: "8px",
                background: "rgba(139, 92, 246, 0.08)",
              }}
            >
              <strong>Searching in:</strong>
              <br />
              {activeDocument?.filename}
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          <div className="profile-avatar">B</div>

          {sidebarOpen && (
            <div className="profile-details">
              <span className="profile-name">My Workspace</span>
              <span className="profile-plan">
                AI document assistant
              </span>
            </div>
          )}
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Workspace</span>
            <span className="breadcrumb-divider">/</span>
            <strong>Document chat</strong>
          </div>

          <div className="topbar-actions">
            <div className="connection-status">
              <span className="status-dot" />
              Local workspace
            </div>

            <button
              className="icon-button clear-chat-button"
              onClick={clearChat}
              disabled={messages.length === 0}
              title="Clear conversation"
              aria-label="Clear conversation"
            >
              <Trash2 size={17} />
            </button>
          </div>
        </header>

        <section className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-icon">
                <Sparkles size={25} />
              </div>

              <div className="welcome-eyebrow">
                YOUR AI-POWERED WORKSPACE
              </div>

              <h1>
                Your documents.
                <br />
                <span>Your answers.</span>
              </h1>

              <p className="welcome-description">
                Upload your PDFs and ask questions in plain English.
                Get document-grounded answers with references to the
                original pages.
              </p>

              <button
                className="welcome-upload-button"
                onClick={openFilePicker}
                disabled={uploading}
              >
                <Upload size={18} />
                Upload your first PDF
              </button>

              <div className="privacy-note">
                <FileText size={14} />
                Your files are processed by your local backend.
              </div>

              {activeDocument && (
                <div className="privacy-note">
                  <CheckCircle2 size={14} />
                  Selected PDF: {activeDocument?.filename}
                </div>
              )}

              <div className="suggestions-heading">
                TRY ASKING
              </div>

              <div className="suggestion-grid">
                {suggestions.map((suggestion) => (
                  <button
                    className="suggestion-card"
                    key={suggestion.title}
                    onClick={() =>
                      handleSend(suggestion.prompt)
                    }
                    disabled={sending}
                  >
                    <span>{suggestion.title}</span>
                    <p>{suggestion.prompt}</p>
                    <span className="suggestion-arrow">↗</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="conversation">
              <div className="conversation-heading">
                <div>
                  <span className="conversation-label">
                    CONVERSATION
                  </span>
                  <h2>Ask your documents</h2>

                  {activeDocument && (
                    <p
                      style={{
                        fontSize: "12px",
                        overflowWrap: "anywhere",
                      }}
                    >
                      Searching in: {activeDocument?.filename}
                    </p>
                  )}
                </div>

                <span className="message-count">
                  {messages.length}{" "}
                  {messages.length === 1 ? "message" : "messages"}
                </span>
              </div>

              {messages.map((message) => (
                <article
                  className={`message message-${message.role}`}
                  key={message.id}
                >
                  <div
                    className={`message-avatar avatar-${message.role}`}
                  >
                    {message.role === "assistant" ? (
                      <Bot size={19} />
                    ) : (
                      <UserRound size={19} />
                    )}
                  </div>

                  <div className="message-body">
                    <div className="message-author">
                      {message.role === "assistant"
                        ? "DocuChat AI"
                        : "You"}
                    </div>

                    <div className="message-content">
                      {message.role === "assistant" ? (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      ) : (
                        message.content
                      )}
                    </div>

                    {message.sources?.length > 0 && (
                      <div className="sources-panel">
                        <div className="sources-heading">
                          <BookOpen size={15} />
                          Sources used
                        </div>

                        <div className="source-list">
                          {message.sources.map(
                            (source, index) => (
                              <div
                                className="source-chip"
                                key={`${source.source}-${source.page_number}-${index}`}
                              >
                                <FileText size={14} />
                                <span>{source.source}</span>
                                <span className="source-page">
                                  Page {source.page_number}
                                </span>
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </article>
              ))}

              {sending && (
                <article className="message message-assistant">
                  <div className="message-avatar avatar-assistant">
                    <Bot size={19} />
                  </div>

                  <div className="message-body">
                    <div className="message-author">
                      DocuChat AI
                    </div>

                    <div className="typing-indicator">
                      <LoaderCircle
                        size={16}
                        className="spin"
                      />
                      Searching the selected document...
                    </div>
                  </div>
                </article>
              )}

              <div ref={chatEndRef} />
            </div>
          )}

          {error && (
            <div
              className="feedback-banner error-banner"
              role="alert"
            >
              <AlertCircle size={17} />
              <span>{error}</span>

              <button
                className="feedback-close"
                onClick={() => setError("")}
                aria-label="Dismiss error"
              >
                <X size={16} />
              </button>
            </div>
          )}

          {notice && (
            <div
              className="feedback-banner success-banner"
              role="status"
            >
              <CheckCircle2 size={17} />
              <span>{notice}</span>

              <button
                className="feedback-close"
                onClick={() => setNotice("")}
                aria-label="Dismiss message"
              >
                <X size={16} />
              </button>
            </div>
          )}

          <div className="composer-area">
            <form
              className="composer"
              onSubmit={(event) => {
                event.preventDefault();
                handleSend();
              }}
            >
              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey &&
                    !event.nativeEvent.isComposing
                  ) {
                    event.preventDefault();
                    handleSend();
                  }
                }}
                placeholder={
                  activeDocument
                    ? `Ask about ${activeDocument?.filename}...`
                    : "Upload and select a PDF to start chatting..."
                }
                rows={1}
                maxLength={2000}
                aria-label="Ask a question about your documents"
              />

              <div className="composer-bottom">
                <div className="composer-hint">
                  <Sparkles size={14} />
                  Answers grounded in your selected document
                </div>

                <div className="composer-actions">
                  <span className="character-count">
                    {question.length}/2000
                  </span>

                  <button
                    type="submit"
                    className="send-button"
                    disabled={
                      !question.trim() ||
                      sending ||
                      !activeDocument
                    }
                    aria-label="Send question"
                    title="Send question"
                  >
                    {sending ? (
                      <LoaderCircle
                        size={18}
                        className="spin"
                      />
                    ) : (
                      <Send size={18} />
                    )}
                  </button>
                </div>
              </div>
            </form>

            <p className="disclaimer">
              AI-generated answers may be inaccurate. Verify
              important details against the cited pages.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;