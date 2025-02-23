"use client";
import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "./ui/card";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "./ui/select";
import Image from "next/image";
import { Progress } from "./ui/progress";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const CrimeForm = ({ onSubmit }) => {
  const [state, setState] = useState("");
  const [district, setDistrict] = useState("");
  const [years, setYears] = useState("");
  const [crimes, setCrimes] = useState("");
  const [predictYears, setPredictYears] = useState("");
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [availableYears, setAvailableYears] = useState([]);
  const [prevalentCrimes, setPrevalentCrimes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/states")
      .then((res) => res.json())
      .then((data) => setStates(data.states || []))
      .catch((err) => console.error("Error fetching states:", err));
  }, []);

  useEffect(() => {
    if (state) {
      fetch(`http://127.0.0.1:5000/districts?state=${state}`)
        .then((res) => res.json())
        .then((data) => setDistricts(data.districts || []))
        .catch((err) => console.error("Error fetching districts:", err));
    } else {
      setDistricts([]);
    }
  }, [state]);

  useEffect(() => {
    if (state || district) {
      fetch(`http://127.0.0.1:5000/years?state=${state}&district=${district}`)
        .then((res) => res.json())
        .then((data) => setAvailableYears(data.years || []))
        .catch((err) => console.error("Error fetching years:", err));

      fetch(`http://127.0.0.1:5000/prevalent-crimes?state=${state}&district=${district}`)
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data.prevalent_crimes)) {
            const transformedCrimes = data.prevalent_crimes.map(([crime, count]) => ({ crime, count }));
            setPrevalentCrimes(transformedCrimes);
          } else {
            setPrevalentCrimes([]);
          }
        })
        .catch((err) => {
          console.error("Error fetching prevalent crimes:", err);
          setPrevalentCrimes([]);
        });
    } else {
      setAvailableYears([]);
      setPrevalentCrimes([]);
    }
  }, [state, district]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setReport(null);
    try {
      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          state,
          district,
          years: years.split(",").map((y) => parseInt(y.trim())),
          crimes: crimes.split(",").map((c) => c.trim()),
          predict_years: parseInt(predictYears),
        }),
      });
      const data = await response.json();
      setReport(data);
    } catch (error) {
      console.error("Error running analysis:", error);
    }
    setLoading(false);
  };

  // Format predictions data for the chart
  const formatChartData = (predictions) => {
    return predictions.map((prediction) => ({
      year: prediction.year,
      predicted: prediction.predicted,
      confidenceInterval: prediction.confidence_interval,
    }));
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Crime Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label className="text-sm font-medium">State</Label>
              <Select onValueChange={setState}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a state" />
                </SelectTrigger>
                <SelectContent>
                  {states.map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">District</Label>
              <Select onValueChange={setDistrict}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a district" />
                </SelectTrigger>
                <SelectContent>
                  {districts.map((d) => (
                    <SelectItem key={d} value={d}>{d}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">Prevalent Crimes</Label>
              <Select onValueChange={setCrimes}>
                <SelectTrigger>
                  <SelectValue placeholder="Select crimes" />
                </SelectTrigger>
                <SelectContent>
                  {prevalentCrimes.map((crime) => (
                    <SelectItem key={crime.crime} value={crime.crime}>{crime.crime} ({crime.count} cases)</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">Prediction Years</Label>
              <Input
                type="number"
                value={predictYears}
                onChange={(e) => setPredictYears(e.target.value)}
                placeholder="e.g., 5"
                className="w-full"
              />
            </div>

            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Analyzing..." : "Run Analysis"}
            </Button>
          </form>

          {loading && <Progress className="mt-4" />}

          {report && (
            <div className="mt-8 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl font-bold">Analysis Report</CardTitle>
                  <CardDescription>Detailed crime analysis and predictions</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Historical Crime Statistics */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Historical Crime Statistics</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(report.historical_crime_statistics).map(([crime, count]) => (
                        <Card key={crime} className="p-4">
                          <p className="text-sm font-medium">{crime}</p>
                          <p className="text-2xl font-bold">{count}</p>
                          <p className="text-sm text-gray-500">cases</p>
                        </Card>
                      ))}
                    </div>
                  </div>

                  {/* Predictions */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Predictions</h3>
                    {Object.entries(report.predictions).map(([crime, predictions]) => (
                      <Card key={crime} className="p-4 mb-4">
                        <h4 className="text-md font-medium mb-2">{crime}</h4>
                        {/* Chart */}
                        <div className="h-64 mb-4">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={formatChartData(predictions)}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="year" />
                              <YAxis />
                              <Tooltip />
                              <Legend />
                              <Line type="monotone" dataKey="predicted" stroke="#8884d8" activeDot={{ r: 8 }} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                        {/* Table */}
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Year</TableHead>
                              <TableHead>Predicted</TableHead>
                              <TableHead>Confidence Interval</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {predictions.map((prediction, index) => (
                              <TableRow key={index}>
                                <TableCell>{prediction.year}</TableCell>
                                <TableCell>{prediction.predicted}</TableCell>
                                <TableCell>{prediction.confidence_interval}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </Card>
                    ))}
                  </div>

                  {/* Total Records Analyzed */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Total Records Analyzed</h3>
                    <p className="text-2xl font-bold">{report.total_records}</p>
                  </div>

                  {/* Crime Trend Plot */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Crime Trend Plot</h3>
                    <div className="border rounded-lg overflow-hidden shadow-sm max-w-lg mx-auto">
                      <Image
                        src={`http://127.0.0.1:5000/static/${report.plot_path.split('\\').pop()}`}
                        alt="Crime Trend Plot"
                        width={600}
                        height={400}
                        className="w-full h-auto"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CrimeForm;