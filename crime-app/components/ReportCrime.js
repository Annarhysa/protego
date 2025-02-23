"use client"; // Mark as a Client Component
import { useState } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Input } from "./ui/input";

const ReportCrime = () => {
  const [crimeDetails, setCrimeDetails] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleReport = async () => {
    if (!crimeDetails) {
      setError("Please provide crime details.");
      return;
    }

    try {
      const res = await axios.post("http://127.0.0.1:5000/report", {
        crime: crimeDetails,
      });
      setMessage(res.data.message);
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "An error occurred.");
      setMessage("");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Report a Crime</CardTitle>
      </CardHeader>
      <CardContent>
        <Input
          type="text"
          value={crimeDetails}
          onChange={(e) => setCrimeDetails(e.target.value)}
          placeholder="Enter crime details"
          className="mb-4"
        />
        <Button onClick={handleReport}>Report Crime</Button>

        {error && <p className="text-red-500">{error}</p>}
        {message && <p className="text-green-500">{message}</p>}
      </CardContent>
    </Card>
  );
};

export default ReportCrime;