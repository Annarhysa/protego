"use client";
import CrimeForm from "../../../components/CrimeForm";

const AnalyzePage = () => {
  const handleAnalyze = async (params) => {
    const res = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    const data = await res.json();
    console.log(data); // Display or process the analysis results
  };

  return (
    <div className="container mx-auto p-4">
      <CrimeForm onSubmit={handleAnalyze} />
    </div>
  );
};

export default AnalyzePage;