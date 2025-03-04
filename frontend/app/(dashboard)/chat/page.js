"use client";
import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { API_URL } from "@/config/constants";

const ChatPage = () => {
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const chatRef = useRef(null);

    const handleSubmit = async () => {
        if (!query.trim() || loading) return;

        // Add user message to chat
        const newMessages = [...messages, { sender: "user", text: query }];
        setMessages(newMessages);
        setQuery("");
        setLoading(true);

        try {
            const res = await fetch(`${API_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query }),
            });

            const data = await res.text();
            setMessages([...newMessages, { sender: "bot", text: data }]);
        } catch (error) {
            setMessages([...newMessages, { sender: "bot", text: "Error fetching response. Please try again." }]);
        } finally {
            setLoading(false);
        }
    };

    // Auto-scroll to latest message
    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    }, [messages, loading]);

    return (
        <div className="p-5 max-w-xl mx-auto flex flex-col h-screen">
            {/* Title */}
            <h1 className="text-2xl font-bold text-center mb-4">Recommendation Engine</h1>

            <Card className="flex-grow overflow-hidden">
                <CardContent className="h-full flex flex-col">
                    {/* Chat Window */}
                    <div ref={chatRef} className="flex-1 overflow-y-auto space-y-4 p-4 bg-gray-100 rounded-lg flex flex-col items-center justify-center">
                        {messages.length === 0 ? (
                            <p className="text-gray-500 text-center text-sm">
                                👋 Hello! Type a message below to start chatting.
                            </p>
                        ) : (
                            messages.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`p-3 rounded-lg max-w-xs ${
                                        msg.sender === "user"
                                            ? "bg-blue-500 text-white self-end"
                                            : "bg-gray-300 text-black self-start"
                                    }`}
                                >
                                    {msg.text}
                                </div>
                            ))
                        )}
                        {loading && (
                            <div className="p-3 bg-gray-300 text-black self-start rounded-lg max-w-xs">
                                Typing...
                            </div>
                        )}
                    </div>

                    {/* Input & Send Button */}
                    <div className="flex items-center gap-2 mt-4">
                        <Input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Type your message..."
                            className="flex-1"
                            disabled={loading}
                        />
                        <Button onClick={handleSubmit} className="w-24" disabled={loading}>
                            {loading ? "..." : "Send"}
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default ChatPage;
