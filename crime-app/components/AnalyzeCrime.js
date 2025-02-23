"use client"; // Mark as a Client Component
import { useState } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";

const AnalyzeCrime = () => {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    const params = {
      state: "California",
      district: "Los Angeles",
      years: [2019, 2020, 2021],
      crimes: ["murder", "robbery"],
      predict_years: 5,
    };

    try {
      const res = await axios.post("http://127.0.0.1:5000/analyze", params);
      setAnalysisResult(res.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "An error occurred.");
      setAnalysisResult(null);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Crime Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <Button onClick={handleAnalyze}>Run Analysis</Button>

        {error && <p className="text-red-500">{error}</p>}

        {analysisResult && (
          <div className="mt-4">
            <h2 className="text-xl font-bold">Analysis Results:</h2>
            <pre className="bg-gray-100 p-4 rounded">
              {JSON.stringify(analysisResult, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AnalyzeCrime;