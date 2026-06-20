import { useContext, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import AuthContext from "../Auth/AuthContext";
import { API_BASE_URL } from "../../config/api";

function RAGChat() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const { logoutUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleAsk = async () => {
    if (!query.trim()) return;

    setError("");
    try {
      const res = await fetch(
        `${API_BASE_URL}/api/rag-query/?query=${encodeURIComponent(query)}`,
        {
          headers: {
            "Idempotency-Key": crypto.randomUUID(),
          },
        }
      );
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Failed to get an answer.");
        return;
      }

      setAnswer(data.answer || "");
      setQuery("");
    } catch (err) {
      console.error(err);
      setError("Could not reach the server. Is the backend running?");
    }
  };

  const handlePredictNavigate = () => {
    navigate("/predict");
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 overflow-hidden flex flex-col">
      <motion.div
        className="absolute -top-10 -left-10 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-2xl opacity-60"
        animate={{ y: [0, 30, 0], x: [0, 20, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute -bottom-20 right-0 w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-2xl opacity-60"
        animate={{ y: [0, -40, 0], x: [0, -30, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute top-20 right-20 w-60 h-60 bg-purple-200 rounded-full mix-blend-multiply filter blur-2xl opacity-50"
        animate={{ y: [0, 25, 0], x: [0, -15, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />

      <button
        onClick={handlePredictNavigate}
        className="fixed top-4 left-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 z-50"
      >
        Predict
      </button>

      <button
        onClick={logoutUser}
        className="fixed top-4 right-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 z-50"
      >
        Logout
      </button>

      <div className="flex-1 p-6 overflow-auto mt-16">
        {error && (
          <p className="mb-4 text-red-600 text-sm font-medium">{error}</p>
        )}
        {answer && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="p-4 bg-white rounded-lg shadow-md border border-gray-200"
          >
            <strong>Answer:</strong>
            <pre className="whitespace-pre-wrap">{answer}</pre>
          </motion.div>
        )}
      </div>

      <div className="w-full p-4 bg-white border-t border-gray-200 flex items-center">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Type your question..."
          className="flex-1 border p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          onClick={handleAsk}
          className="ml-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 shadow-md"
        >
          Ask
        </button>
      </div>
    </div>
  );
}

export default RAGChat;
