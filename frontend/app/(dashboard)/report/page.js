"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { API_URL } from "@/config/constants";

const ReportPage = () => {
  const [crimeDetails, setCrimeDetails] = useState("");
  const [location, setLocation] = useState("");
  const [attackType, setAttackType] = useState("");
  const [message, setMessage] = useState("");

  const handleReport = async () => {
    const res = await fetch(`${API_URL}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        crime: crimeDetails,
        location: location,
        attack_type: attackType
      }),
    });
    const data = await res.json();
    setMessage(data.message);
  };

  return (
    <Card>
      <CardHeader>
      <CardTitle className="text-2xl font-bold">Report a crime</CardTitle>
      </CardHeader>
      <CardContent>
        <Input
          type="text"
          value={crimeDetails}
          onChange={(e) => setCrimeDetails(e.target.value)}
          placeholder="Enter crime details"
          className="mb-4"
        />
        <Input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Enter location"
          className="mb-4"
        />
        <Input
          type="text"
          value={attackType}
          onChange={(e) => setAttackType(e.target.value)}
          placeholder="Enter type of attack"
          className="mb-4"
        />
        <Button className="mt-3" onClick={handleReport}>Report Crime</Button>
        {message && <p className="mt-4 text-green-500">{message}</p>}
      </CardContent>
    </Card>
  );
};

export default ReportPage;