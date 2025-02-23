"use client"; // Mark as a Client Component
import { useState } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Input } from "./ui/input";

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
      const res = await axios.get(`http://127.0.0.1:5000/query?input=${query}`);
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
        <CardTitle>Query Crime</CardTitle>
      </CardHeader>
      <CardContent>
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about a crime"
          className="mb-4"
        />
        <Button onClick={handleQuery}>Ask</Button>

        {error && <p className="text-red-500">{error}</p>}

        {response && (
          <div className="mt-4">
            <h2 className="text-xl font-bold">Response:</h2>
            <p>{response}</p>
          </div>
        )}

        {similarCrimes.length > 0 && (
          <div className="mt-4">
            <h2 className="text-xl font-bold">Similar Crimes:</h2>
            <ul>
              {similarCrimes.map((crime, index) => (
                <li key={index} className="mt-2">
                  <strong>{crime.crime}</strong>: {crime.description}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default QueryCrime;