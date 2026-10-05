import { Mic, Send } from "lucide-react";
import React, { useState } from "react";

export function ChatInput({ onSendMessage }: { onSendMessage: (msg: string) => void }) {
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage("");
    }
  };

  const handleMicClick = () => {
    setIsRecording(!isRecording);
    // TODO: Implement Web Speech API / Whisper transcription here
    if (!isRecording) {
      console.log("Started recording voice...");
    } else {
      console.log("Stopped recording voice.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2 p-4 bg-background border-t">
      <button
        type="button"
        onClick={handleMicClick}
        className={`p-3 rounded-full transition-colors ${
          isRecording ? "bg-red-500 text-white animate-pulse" : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
        }`}
        title="Use Voice Input"
      >
        <Mic size={20} />
      </button>
      
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
        className="flex-1 p-3 rounded-lg border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />
      
      <button
        type="submit"
        disabled={!message.trim()}
        className="p-3 rounded-lg bg-primary text-primary-foreground disabled:opacity-50 hover:bg-primary/90 transition-colors"
      >
        <Send size={20} />
      </button>
    </form>
  );
}
