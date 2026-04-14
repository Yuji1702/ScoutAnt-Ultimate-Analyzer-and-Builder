"use client";

import React, { useState, useRef, useEffect } from 'react';
import AnalysisBubble from "./AnalysisBubble";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowUp, TrendingUp, Monitor } from 'lucide-react';

import { MLMatchQueryResponse } from '@/types/ml';
import MatchResultDisplay from './MatchResultDisplay';

// Mock Analysis Data representing the true ML schema
const MOCK_RESULTS: MLMatchQueryResponse[] = [
  {
    map: "Pearl",
    team_a_win_probability: 0.62,
    team_b_win_probability: 0.38,
    confidence: "Medium",
    model_reasoning: [
      "Team A has higher average rating based on historical performance.",
      "Team A shows stronger combat score (ACS)."
    ],
    team_a: {
      players: [
        { name: "TenZ", agent: "Jett", predicted_rating: 1.28, predicted_acs: 265.0, best_role: "Duelist", worst_role: "Sentinel", flexibility_score: 3 },
        { name: "Zellsis", agent: "KAY/O", predicted_rating: 1.12, predicted_acs: 230.0, best_role: "Initiator", worst_role: "Controller", flexibility_score: 4 },
        { name: "johnqt", agent: "Cypher", predicted_rating: 1.05, predicted_acs: 210.0, best_role: "Sentinel", worst_role: "Duelist", flexibility_score: 5 },
        { name: "Sacy", agent: "Sova", predicted_rating: 1.18, predicted_acs: 240.0, best_role: "Initiator", worst_role: "Duelist", flexibility_score: 4 },
        { name: "Oxy", agent: "Omen", predicted_rating: 1.12, predicted_acs: 257.5, best_role: "Controller", worst_role: "Sentinel", flexibility_score: 3 }
      ],
      summary: {
        avg_rating: 1.15,
        avg_acs: 240.5,
        role_distribution: { duelist: 1, controller: 1, initiator: 2, sentinel: 1 }
      }
    },
    team_b: {
      players: [
        { name: "Demon1", agent: "Jett", predicted_rating: 1.30, predicted_acs: 270.0, best_role: "Duelist", worst_role: "Initiator", flexibility_score: 3 },
        { name: "Ethan", agent: "Skye", predicted_rating: 1.10, predicted_acs: 215.0, best_role: "Initiator", worst_role: "Duelist", flexibility_score: 4 },
        { name: "jawgemo", agent: "Raze", predicted_rating: 1.05, predicted_acs: 235.0, best_role: "Duelist", worst_role: "Controller", flexibility_score: 4 },
        { name: "Boostio", agent: "Killjoy", predicted_rating: 1.02, predicted_acs: 200.0, best_role: "Sentinel", worst_role: "Duelist", flexibility_score: 5 },
        { name: "C0M", agent: "Sova", predicted_rating: 1.08, predicted_acs: 215.0, best_role: "Initiator", worst_role: "Duelist", flexibility_score: 4 }
      ],
      summary: {
        avg_rating: 1.11,
        avg_acs: 227.0,
        role_distribution: { duelist: 2, controller: 0, initiator: 2, sentinel: 1 }
      }
    },
    insights: [
      "Team B lacks a controller (smokes).",
      "TenZ is on their most comfortable role (Duelist).",
      "jawgemo is playing their worst role (Duelist). Switch them to Initiator for better performance."
    ],
    note: "Predictions are probabilistic and not guaranteed outcomes."
  }
];

interface ChatMessage {
  id: string;
  isUser: boolean;
  content: string;
}

export default function DashboardContainer() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [latestAnalysis, setLatestAnalysis] = useState<MLMatchQueryResponse | null>(null);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      const scrollElement = scrollRef.current;
      scrollElement.scrollTop = scrollElement.scrollHeight;
    }
  }, [messages, analyzing]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || analyzing) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      isUser: true,
      content: inputValue.trim()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setAnalyzing(true);
    setLatestAnalysis(null);
    
    // Simulate AI thinking and API delay
    setTimeout(() => {
      const randomResult = MOCK_RESULTS[Math.floor(Math.random() * MOCK_RESULTS.length)];
      setLatestAnalysis(randomResult);
      
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        isUser: false,
        content: "I've completed the analysis! You can view the full strategic breakdown on the dashboard to the right."
      };
      setMessages(prev => [...prev, botMessage]);
      setAnalyzing(false);
    }, 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-full w-full bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 lg:border-none relative transition-colors duration-300">
      
      {/* LEFT PANEL: CHAT INTERFACE */}
      <div className="w-full lg:w-[40%] xl:w-[35%] h-[50vh] lg:h-full flex flex-col relative z-20 border-b lg:border-b-0 lg:border-r border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/80 shadow-lg dark:shadow-2xl shrink-0 transition-colors duration-300">
        <ScrollArea className="flex-1 w-full" ref={scrollRef}>
          <div className="p-4 lg:p-6 pb-32">
            
            {/* EMPTY CHAT STATE */}
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center text-center opacity-70 mt-10 transition-opacity">
                <div className="w-16 h-16 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-500 rounded-2xl flex items-center justify-center mb-4 shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
                  <Monitor className="w-8 h-8" />
                </div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-gray-200 mb-2 transition-colors">ScoutAnt Assistant</h1>
                <p className="text-gray-500 dark:text-gray-400 text-sm max-w-[250px] transition-colors">
                  Describe the matchup here, and I'll generate the analysis on the right.
                </p>
              </div>
            )}

            {/* CHAT HISTORY */}
            <div className="space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex w-full ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                  {msg.isUser ? (
                    <div className="bg-blue-600 text-white rounded-2xl rounded-br-none px-4 py-3 max-w-[85%] border border-blue-500/50 shadow-sm text-sm font-medium transition-colors">
                      {msg.content}
                    </div>
                  ) : (
                    <div className="bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-2xl rounded-bl-none px-4 py-3 max-w-[85%] border border-gray-200 dark:border-gray-700 shadow-sm text-sm transition-colors">
                      {msg.content}
                    </div>
                  )}
                </div>
              ))}
              
              {/* TYPING INDICATOR */}
              {analyzing && (
                <div className="flex w-full justify-start mt-2">
                  <div className="bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-2xl rounded-bl-none px-5 py-4 w-16 border border-gray-200 dark:border-gray-700 shadow-sm flex items-center justify-center h-10 transition-colors">
                    <div className="flex space-x-1">
                      <div className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </ScrollArea>

        {/* BOTTOM INPUT AREA */}
        <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-gray-50 via-gray-50/95 dark:from-gray-900 dark:via-gray-900/95 to-transparent pt-8 pb-4 px-4 z-20">
          <form 
            onSubmit={handleSubmit}
            className="flex items-end gap-2 bg-white dark:bg-gray-800 focus-within:bg-gray-50 dark:focus-within:bg-gray-700/80 rounded-2xl px-3 py-2 border border-gray-200 dark:border-gray-700 shadow-xl relative transition-all"
          >
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask for an analysis..."
              className="w-full bg-transparent resize-none max-h-32 min-h-[40px] border-0 focus:ring-0 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 pt-2 px-2 text-sm outline-none transition-colors"
              rows={1}
              style={{ overflowY: 'hidden' }}
            />
            <button 
              type="submit" 
              disabled={!inputValue.trim() || analyzing}
              className={`p-2.5 rounded-xl shrink-0 transition-all ${
                inputValue.trim() && !analyzing 
                  ? 'bg-blue-600 text-white hover:bg-blue-500 cursor-pointer shadow-md' 
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
              }`}
            >
              <ArrowUp className="w-4 h-4 font-bold" />
              <span className="sr-only">Analyze Match</span>
            </button>
          </form>
        </div>
      </div>

      {/* RIGHT PANEL: DASHBOARD RESULTS */}
      <div className="flex-1 h-[50vh] lg:h-full bg-gray-100/50 dark:bg-gray-950/50 flex flex-col relative z-0 transition-colors duration-300">
        {/* Background gradient subtle */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-100/20 via-transparent to-purple-100/20 dark:from-blue-900/5 dark:to-purple-900/5 pointer-events-none transition-colors duration-300"></div>

        <ScrollArea className="flex-1 w-full px-4 lg:px-8 py-8 h-full min-h-[500px]">
          <div className="max-w-3xl mx-auto pb-12">
            
            {/* NO ANALYSIS STATE */}
            {!analyzing && !latestAnalysis && (
              <div className="h-full min-h-[50vh] flex flex-col items-center justify-center text-center opacity-40 transition-opacity">
                <TrendingUp className="w-24 h-24 text-gray-400 dark:text-gray-700 mb-6 transition-colors" />
                <h2 className="text-2xl font-bold text-gray-500 dark:text-gray-500 mb-2 transition-colors">Analysis Dashboard</h2>
                <p className="text-gray-500 dark:text-gray-600 max-w-sm transition-colors">
                  Waiting for your latest request. Results will appear here once processed.
                </p>
              </div>
            )}

            {/* AI DASHBOARD RESPONSE */}
            {(analyzing || latestAnalysis) && (
              <div className="w-full h-full flex flex-col justify-start">
               {analyzing && !latestAnalysis ? (
                  <div className="h-[400px] flex items-center justify-center">
                     <div className="flex gap-2 items-center text-gray-600 dark:text-gray-400 font-medium">
                        <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                        <span>Querying ML model...</span>
                     </div>
                  </div>
               ) : latestAnalysis ? (
                 <MatchResultDisplay data={latestAnalysis} />
               ) : null}
              </div>
            )}

          </div>
        </ScrollArea>
      </div>
      
    </div>
  );
}
