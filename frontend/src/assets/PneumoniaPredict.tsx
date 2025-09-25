// src/components/PneumoniaPredict.tsx
import React, { useState } from "react";
import axios from "axios";
import "./PneumoniaPredict.css"; // Import the CSS file

interface PredictionResponse {
  prediction: string;
  confidence: number;
}

const PneumoniaPredict: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setPrediction(null);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await axios.post<PredictionResponse>(
        "http://localhost:8000/api/predict/", // Django API endpoint
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setPrediction(response.data);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || "Something went wrong.");
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
