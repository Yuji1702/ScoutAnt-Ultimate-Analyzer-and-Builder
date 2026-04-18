"use client";

import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Menu } from 'lucide-react';
import MessageBubble from "./MessageBubble";

interface Message {
  id: string;
  content: string;
  isBot: boolean;
}

interface ChatInterfaceProps {
  onAnalysisData?: (data: any) => void;
  initialMessage?: string;
  onTypingStateChange?: (isTyping: boolean) => void;
}

export default function ChatInterface({ onAnalysisData, initialMessage, onTypingStateChange }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(
    initialMessage ? [{ id: '1', content: initialMessage, isBot: true }] : []
  );
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = inputValue.trim();
    const newUserMsg: Message = {
      id: Date.now().toString(),
      content: userMessage,
      isBot: false,
    };

    setMessages(prev => [...prev, newUserMsg]);
    setInputValue('');
    setIsTyping(true);
    if (onTypingStateChange) onTypingStateChange(true);
    if (onAnalysisData) onAnalysisData(null); // Reset analysis while fetching

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
      });
      
      if (response.status === 503) {
        throw new Error('AI_INITIALIZING');
      }
      
      if (!response.ok) {
        throw new Error('Failed to connect to backend AI server');
      }
      
      const data = await response.json();
      
      const newBotMsg: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        isBot: true,
      };
      setMessages(prev => [...prev, newBotMsg]);

      if (data.data && onAnalysisData) {
        onAnalysisData(data.data);
      }
    } catch (error: any) {
       console.error("Chat Error:", error);
       let errorMessage = "Sorry, I couldn't connect to the backend system. Please make sure the Python API is running on localhost:8000.";
       
       if (error.message === 'AI_INITIALIZING') {
         errorMessage = "The AI system is still warming up (loading ML models). This usually takes 30-40 seconds on the first run. Please wait a moment and try your request again.";
       } else if (error.name === 'AbortError') {
         errorMessage = "The request took too long. The backend might be overloaded. Please try again.";
       }


       setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        content: errorMessage,
        isBot: true,
      }]);
    } finally {
      setIsTyping(false);
      if (onTypingStateChange) onTypingStateChange(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background relative w-full transition-colors duration-300 overflow-hidden">
      {/* Mobile Header */}
      <header className="md:hidden h-14 border-b border-border flex items-center px-4 shrink-0 bg-background transition-colors">
        <button className="p-2 -ml-2 text-muted-foreground hover:text-foreground transition-colors">
          <Menu className="w-6 h-6" />
        </button>
        <h2 className="text-base font-semibold text-foreground ml-2 transition-colors">
          ScoutAnt AI
        </h2>
      </header>

      {/* Chat Area */}
      <div className="flex-1 w-full overflow-y-auto scrollbar-hide-default" ref={scrollRef}>
        <div className="flex flex-col pb-36 pt-8 min-h-max">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center pt-20 px-4">
              <div className="w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center mb-6 shadow-xl transition-colors">
                <span className="font-bold text-2xl">S</span>
              </div>
              <h1 className="text-3xl tracking-tight font-semibold text-foreground mb-2 transition-colors">How can I help you today?</h1>
            </div>
          )}
          
          {messages.map((msg) => (
            <MessageBubble key={msg.id} {...msg} />
          ))}
          {isTyping && (
            <div className="max-w-3xl mx-auto w-full px-4 py-8 flex items-center gap-4 text-muted-foreground transition-colors">
              <div className="h-8 w-8 rounded-full border border-border shadow-sm bg-primary text-primary-foreground shrink-0 flex items-center justify-center transition-colors">
                 <span className="font-bold">S</span>
              </div>
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-background via-background/90 to-transparent pt-10 pb-6 px-4 transition-colors">
        <div className="max-w-3xl mx-auto">
          <form 
            onSubmit={handleSubmit}
            className="flex items-end gap-2 bg-card focus-within:bg-background rounded-2xl px-3 py-3 border border-border shadow-lg relative transition-all"
          >
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message ScoutAnt..."
              className="w-full bg-transparent resize-none max-h-48 min-h-[44px] border-0 focus:border-0 outline-none focus:outline-none focus:ring-0 text-foreground placeholder:text-muted-foreground pt-2.5 px-2 font-medium transition-colors"
              rows={1}
              style={{ overflowY: 'hidden', boxShadow: 'none' }}
            />
              <button 
              type="submit" 
              disabled={!inputValue.trim() || isTyping}
              className={`p-2 rounded-xl shrink-0 transition-all duration-300 ${
                inputValue.trim() && !isTyping 
                  ? 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer shadow-md' 
                  : 'bg-muted text-muted-foreground cursor-not-allowed'
              }`}
            >
              <ArrowUp className="w-5 h-5 font-bold" />
              <span className="sr-only">Send message</span>
            </button>
          </form>
          <div className="text-center mt-3 h-5">
            <span className="text-xs text-muted-foreground font-medium transition-colors">
              ScoutAnt AI can make mistakes. Consider verifying match data.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
