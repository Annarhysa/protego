"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { API_URL } from "@/config/constants";
import  Turnstile from "react-turnstile";

const ReportPage = () => {
  const [crimeDetails, setCrimeDetails] = useState("");
  const [location, setLocation] = useState("");
  const [attackType, setAttackType] = useState("");
  const [message, setMessage] = useState("");
  const [detectedCrimes, setDetectedCrimes] = useState([]);
  const [recommendations, setRecommendations] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isVerified, setIsVerified] = useState(false);

  const handleReport = async () => {
    const res = await fetch(`${API_URL}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crime: crimeDetails,
        location: location,
        attack_type: attackType,
      }),
    });
    const data = await res.json();
    setMessage(data.message);
    setDetectedCrimes(data.detected_crimes || []);
    setRecommendations(data.recommendations);
    setIsSubmitted(true);
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

        <div className="mb-4">
          <Turnstile
            sitekey={process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY}
            onSuccess={() => setIsVerified(true)}
            onError={() => setIsVerified(false)}
            options={{ theme: "light" }}
          />
        </div>

        {/* 🔒 Disabled until Turnstile passes */}
        <Button className="mt-3" onClick={handleReport} disabled={!isVerified}>
          Report Crime
        </Button>

        {isSubmitted && (
          <div className="mt-6 border-t pt-4">
            <p className="text-green-500 mb-4">{message}</p>

            {detectedCrimes.length > 0 && (
              <div className="mb-4">
                <h3 className="font-semibold mb-2">Detected Crimes:</h3>
                <ul className="list-disc pl-5">
                  {detectedCrimes.map((crime, index) => (
                    <li key={index} className="text-gray-700">{crime}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {recommendations && recommendations !== "No specific recommendations available." && (
              <div>
                <h3 className="font-semibold mb-2">Recommendations:</h3>
                <p className="text-gray-700">{recommendations}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ReportPage;