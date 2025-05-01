"use client"

import React from "react";
import { useRouter } from "next/navigation";
import { useState, useRef, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatMessage } from "@/components/chat-message"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Phone, ImageIcon, Send } from "lucide-react"
import { characters } from "@/data/characters"

// Function to format text by replacing *word* with <b>word</b>
const formatResponse = (text: string) => {
  return text.replace(/\*(.*?)\*/g, "<b>$1</b>");
};

export default function ChatPage({ params }: { params: Promise<{ id: string }> }) {
  // Unwrap the promise using React.use()
  const resolvedParams = React.use(params);  
  const router = useRouter();

  const character = characters.find((c) => c.id === resolvedParams.id) || characters[0]

  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([])
  const [input, setInput] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Add initial message from character
    setMessages([{ role: "assistant", content: character.greeting }])
  }, [character.id])

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: input }])
    const userInput = input
    setInput("")

    try {
      const res = await fetch("http://localhost:8000/chat_api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: resolvedParams.id,
          user_input: userInput,
          character: resolvedParams.id
        }),
      })

      if (!res.ok) {
        throw new Error("Network response was not ok")
      }

      const data = await res.json()
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }])
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: " + err.message },
      ])
    }
  }

  const handleCallClick = () => {
    // Use the unwrapped params value
    router.push(`/call/${resolvedParams.id}`);
  };

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <header className="flex items-center p-4 border-b">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full overflow-hidden">
              <img
                src={character.avatar || "/placeholder.svg"}
                alt={character.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h2 className="font-semibold">{character.name}</h2>
              <p className="text-xs text-gray-500">{character.creator}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" className="ml-auto" onClick={handleCallClick}>
            <Phone className="h-5 w-5" />
          </Button>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              role={message.role}
              content={
                message.role === "assistant"
                  ? formatResponse(message.content)
                  : message.content
              }
              avatar={message.role === "assistant" ? character.avatar : "/placeholder-user.jpg?height=40&width=40"}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>

        <footer className="p-4 border-t">
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <Button type="button" variant="ghost" size="icon">
              <ImageIcon className="h-5 w-5" />
            </Button>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Message ${character.name}...`}
              className="flex-1"
            />
            <Button type="submit" size="icon" disabled={!input.trim()}>
              <Send className="h-5 w-5" />
            </Button>
          </form>
          <p className="text-xs text-center text-gray-400 mt-2">
            This is AI, and not a real person. Treat everything it says as fiction
          </p>
        </footer>
      </div>
    </div>
  );
}
