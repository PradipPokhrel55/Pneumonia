import React, { useState, useContext } from "react";
import axios from "axios";
import AuthContext from "../Auth/AuthContext";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom"; 

const PneumoniaPredict = () => {
  const [file, setFile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { authTokens, logoutUser } = useContext(AuthContext);
  const navigate = useNavigate(); 

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setPrediction(null);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    if (!authTokens || !authTokens.access) {
      setError("Authentication failed. Please log in again.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await axios.post(
        "http://localhost:8000/api/predict/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${authTokens.access}`,
          },
        }
      );

      setPrediction(response.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Something went wrong.");
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  const handleNavigateChat = () => {
    navigate("/chat"); 
  };

  return (
    <div className="relative min-h-screen flex items-end justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 overflow-hidden">
      {/* 🔹 Chat button (fixed top-left) */}
      <button
        onClick={handleNavigateChat}
        className="fixed top-4 left-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 z-50"
      >
        Chat
      </button>

      {/* 🔹 Logout button (fixed top-right) */}
      <button
        onClick={logoutUser}
        className="fixed top-4 right-4 bg-red-500 hover:bg-red-600 text-white text-sm font-semibold py-1 px-3 rounded-md shadow-md transition z-50"
      >
        Logout
      </button>

      {/* 🔹 Animated background bubbles */}
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

      {/* 🔹 Predictor UI (bottom-centered) */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative max-w-md w-full mx-auto mb-10 p-6 bg-white shadow-2xl rounded-2xl border border-gray-200 z-10"
      >
        <h2 className="text-2xl font-bold text-center text-blue-600 mb-6">
          Pneumonia Predictor
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="w-full p-2 border border-gray-300 rounded-lg text-sm cursor-pointer file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Predicting..." : "Predict"}
          </button>
        </form>

        {error && (
          <p className="mt-4 text-red-600 text-sm font-medium text-center">
            {error}
          </p>
        )}

        {prediction && (
          <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-gray-800">
              <strong>Prediction:</strong> {prediction.prediction}
            </p>
            <p className="text-gray-800">
              <strong>Confidence:</strong>{" "}
              {(prediction.confidence * 100).toFixed(2)}%
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default PneumoniaPredict;
