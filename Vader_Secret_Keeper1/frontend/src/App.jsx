// frontend/src/App.jsx
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/chat";

export default function App() {
  const [sessionId, setSessionId] = useState("trial-01");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: "bot", text: "🌌 Vardarth: Speak 'begin' to start the trial." }
  ]);
  const [loading, setLoading] = useState(false);
  const [chapter, setChapter] = useState(0);
  const [unlocked, setUnlocked] = useState(false);
  const [secret, setSecret] = useState(null);
  const scrollRef = useRef();

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessageAsUser(text) {
    if (!text || loading) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const payload = { session_id: sessionId, message: text, mode: "story" };
      const res = await axios.post(API_URL, payload, { timeout: 15000 });

      const data = res.data;
      const botTextParts = [];
      if (data.reply) botTextParts.push(data.reply);
      if (data.question) botTextParts.push("\n\n" + (data.question || ""));
      const botText = botTextParts.join(" ");

      setMessages((m) => [...m, { role: "bot", text: botText }]);
      if (typeof data.chapter !== "undefined") setChapter(data.chapter);
      if (typeof data.unlocked !== "undefined") setUnlocked(Boolean(data.unlocked));
      if (data.secret) {
        setSecret(data.secret);
        setMessages((m) => [...m, { role: "bot", text: `🔐 SECRET: ${data.secret}` }]);
      }
    } catch (err) {
      console.error(err);
      let errMsg = "🚨 Network or server error. Check backend is running.";
      if (err.response && err.response.data) {
        errMsg = `Error: ${JSON.stringify(err.response.data)}`;
      }
      setMessages((m) => [...m, { role: "bot", text: errMsg }]);
    } finally {
      setLoading(false);
    }
  }

  const onSend = () => {
    if (!input.trim()) return;
    sendMessageAsUser(input.trim());
  };

  const generateNewSession = () => {
    const id = `sess-${Date.now().toString(36)}`;
    setSessionId(id);
    setMessages([{ role: "bot", text: "🌌 Vardarth: New session started. Say 'begin'." }]);
    setChapter(0);
    setUnlocked(false);
    setSecret(null);
  };

  return (
    <div className="chat-wrapper starwars-theme">
      {/* Background animation - optional spaceships */}
      <div className="starfield"></div>
      <div className="spaceship"></div>
      <div className="spaceship delay"></div>

      <header className="topbar neon-text">
        <div className="title">🛰️ Vader Secret Keeper</div>
        <div className="session-controls">
          <input
            className="session-input neon-box"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            title="Session ID"
          />
          <button onClick={generateNewSession} className="tiny-btn neon-btn">
            New
          </button>
        </div>
      </header>

      <main className="chat-panel">
        <div className="messages">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`bubble ${
                m.role === "user" ? "user neon-box" : "bot neon-box"
              }`}
            >
              {m.text}
            </div>
          ))}
          <div ref={scrollRef} />
        </div>

        <div className="status-row neon-text">
          <div>Chapter: {chapter} </div>
          <div>Unlocked: {unlocked ? "✔" : "✖"}</div>
          {secret && <div className="secret-indicator">🔐 Secret found</div>}
        </div>

        <div className="composer">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSend()}
            placeholder="Type your reply..."
            className="composer-input neon-box"
            disabled={loading}
          />
          <button onClick={onSend} className="send-btn neon-btn" disabled={loading}>
            {loading ? "..." : "Send"}
          </button>
        </div>
      </main>
    </div>
  );
}
