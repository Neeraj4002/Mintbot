interface ChatMessageProps {
  role: "user" | "assistant"
  content: string
  avatar: string
}

export function ChatMessage({ role, content, avatar }: ChatMessageProps) {
  const isUser = role === "user"

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[80%] ${isUser ? "flex-row-reverse" : ""}`}>
        <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0 mx-2">
          <img src={avatar || "/placeholder.svg"} alt={role} className="w-full h-full object-cover" />
        </div>
        <div className={`p-3 rounded-lg ${isUser ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
      </div>
    </div>
  )
}
