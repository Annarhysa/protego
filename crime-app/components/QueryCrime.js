"use client"; // Mark as a Client Component
import { useState } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "./ui/card";
import { Input } from "./ui/input";
import { API_URL } from "@/config/constants";

const QueryCrime = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [similarCrimes, setSimilarCrimes] = useState([]);
  const [error, setError] = useState("");

  const handleQuery = async () => {
    if (!query) {
      setError("Please enter a query.");
      return;
    }

    try {
      const res = await axios.get(`${API_URL}/query?input=${query}`);
      setResponse(res.data.response);
      setSimilarCrimes(res.data.similar_crimes || []);
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "An error occurred.");
      setResponse("");
      setSimilarCrimes([]);
    }
  };

  return (
    <Card>
      <CardHeader>
      <CardTitle className="text-2xl font-bold">Query Crime</CardTitle>
        <CardDescription>Ask about a crime and get detailed information.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex space-x-4">
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about a crime"
            className="flex-1"
          />
          <Button onClick={handleQuery}>Ask</Button>
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        {response && (
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Response</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">{response}</p>
            </CardContent>
          </Card>
        )}

        {similarCrimes.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Similar Crimes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {similarCrimes.map((crime, index) => (
                  <Card key={index} className="p-4">
                    <h3 className="font-semibold text-lg">{crime.crime}</h3>
                    <p className="text-gray-700">{crime.description}</p>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  );
};

export default QueryCrime;