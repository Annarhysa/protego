"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const ReportPage = () => {
  const [crimeDetails, setCrimeDetails] = useState("");
  const [message, setMessage] = useState("");

  const handleReport = async () => {
    const res = await fetch("http://127.0.0.1:5000/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ crime: crimeDetails }),
    });
    const data = await res.json();
    setMessage(data.message);
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
        {message && <p className="mt-4 text-green-500">{message}</p>}
      </CardContent>
    </Card>
  );
};

export default ReportPage;