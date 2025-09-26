import React, { useState, useContext } from "react";
import axios from "axios";
import AuthContext from "../Auth/AuthContext";

const PneumoniaPredict = () => {
  const [file, setFile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { authTokens } = useContext(AuthContext);

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
    
    // Check if authTokens exist
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
            Authorization: `Bearer ${authTokens.access}`, // ✅ Correct: Add Authorization header
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
  return (
    <div className="predictor-container">
      <h2 className="predictor-title">Pneumonia Predictor</h2>
      <form onSubmit={handleSubmit} className="predictor-form">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="predictor-input"
        />
        <button type="submit" className="predictor-button">
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>

      {error && <p className="predictor-error">{error}</p>}

      {prediction && (
        <div className="predictor-result">
          <p>
            <strong>Prediction:</strong> {prediction.prediction}
          </p>
          <p>
            <strong>Confidence:</strong>{" "}
            {(prediction.confidence * 100).toFixed(2)}%
          </p>
        </div>
      )}
    </div>
  );
};

export default PneumoniaPredict;