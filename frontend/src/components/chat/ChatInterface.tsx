"use client";

import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Menu } from 'lucide-react';
import { ScrollArea } from "@/components/ui/scroll-area";
import MessageBubble from "./MessageBubble";

interface Message {
  id: string;
  content: string;
  isBot: boolean;
}

const INITIAL_MESSAGES: Message[] = [
  {
    id: '1',
    content: 'Welcome to ScoutAnt. How can I help you analyze your Valorant gameplay today?',
    isBot: true,
  }
];

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const newUserMsg: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      isBot: false,
    };

    setMessages(prev => [...prev, newUserMsg]);
    setInputValue('');
    setIsTyping(true);

    // Mock bot reply
    setTimeout(() => {
      const newBotMsg: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm analyzing the latest match stats based on your input. My advanced algorithms are connecting to the data pipeline. Please check back when integration is fully complete.",
        isBot: true,
      };
      setMessages(prev => [...prev, newBotMsg]);
      setIsTyping(false);
    }, 1200);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 relative w-full">
      {/* Mobile Header */}
      <header className="md:hidden h-14 border-b border-gray-800 flex items-center px-4 shrink-0 bg-gray-900">
        <button className="p-2 -ml-2 text-gray-400 hover:text-gray-100">
          <Menu className="w-6 h-6" />
        </button>
        <h2 className="text-base font-semibold text-gray-100 ml-2">
          ScoutAnt AI
        </h2>
      </header>

      {/* Chat Area */}
      <ScrollArea className="flex-1 w-full" ref={scrollRef}>
        <div className="flex flex-col pb-36 pt-8">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center pt-20 px-4">
              <div className="w-16 h-16 bg-white text-black rounded-full flex items-center justify-center mb-6 shadow-xl">
                <span className="font-bold text-2xl">S</span>
              </div>
              <h1 className="text-3xl tracking-tight font-semibold text-gray-100 mb-2">How can I help you today?</h1>
            </div>
          )}
          
          {messages.map((msg) => (
            <MessageBubble key={msg.id} {...msg} />
          ))}
          {isTyping && (
            <div className="max-w-3xl mx-auto w-full px-4 py-8 flex items-center gap-4 text-gray-400">
              <div className="h-8 w-8 rounded-full border border-gray-600 shadow-sm bg-white text-black shrink-0 flex items-center justify-center">
                 <span className="font-bold">S</span>
              </div>
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-gray-900 via-gray-900/90 to-transparent pt-10 pb-6 px-4">
        <div className="max-w-3xl mx-auto">
          <form 
            onSubmit={handleSubmit}
            className="flex items-end gap-2 bg-gray-800 focus-within:bg-gray-800 rounded-2xl px-3 py-3 border border-gray-700/50 shadow-lg relative transition-all"
          >
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message ScoutAnt..."
              className="w-full bg-transparent resize-none max-h-48 min-h-[44px] border-0 focus:ring-0 text-gray-100 placeholder:text-gray-500 pt-2.5 px-2 font-medium"
              rows={1}
              style={{ overflowY: 'hidden' }}
            />
            <button 
              type="submit" 
              disabled={!inputValue.trim() || isTyping}
              className={`p-2 rounded-xl shrink-0 transition-all ${
                inputValue.trim() && !isTyping 
                  ? 'bg-white text-black hover:bg-gray-200 cursor-pointer shadow-sm' 
                  : 'bg-gray-700 text-gray-500 cursor-default'
              }`}
            >
              <ArrowUp className="w-5 h-5 font-bold" />
              <span className="sr-only">Send message</span>
            </button>
          </form>
          <div className="text-center mt-3 h-5">
            <span className="text-xs text-gray-500 font-medium">
              ScoutAnt AI can make mistakes. Consider verifying match data.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
