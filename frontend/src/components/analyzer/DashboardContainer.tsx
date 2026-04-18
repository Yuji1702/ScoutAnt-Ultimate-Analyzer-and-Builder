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

import ChatInterface from '../chat/ChatInterface';
import AgentOptimizationDisplay from './AgentOptimizationDisplay';
import TeamOptimizationDisplay from './TeamOptimizationDisplay';
import PlayerProfileDisplay from './PlayerProfileDisplay';
import CounterStrategyDisplay from './CounterStrategyDisplay';

export default function DashboardContainer() {
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  return (
    <div className="flex flex-col lg:flex-row h-full w-full bg-background border-t border-border lg:border-none relative transition-colors duration-300">
      
      {/* LEFT PANEL: CHAT INTERFACE */}
      <div className="w-full lg:w-[40%] xl:w-[35%] h-[50vh] lg:h-full flex flex-col relative z-20 border-b lg:border-b-0 lg:border-r border-border bg-card shadow-lg dark:shadow-2xl shrink-0 transition-colors duration-300">
        <ChatInterface 
          onAnalysisData={setAnalysisData}
          onTypingStateChange={setIsAnalyzing}
          initialMessage="Describe the matchup, player, or team here, and I'll generate the analysis on the right."
        />
      </div>

      {/* RIGHT PANEL: DASHBOARD RESULTS */}
      <div className="flex-1 h-[50vh] lg:h-full bg-muted/30 flex flex-col relative z-0 transition-colors duration-300">
        {/* Background gradient subtle */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/5 pointer-events-none transition-colors duration-300"></div>

        <ScrollArea className="flex-1 w-full px-4 lg:px-8 py-8 h-full min-h-[500px]">
          <div className="max-w-3xl mx-auto pb-12">
            
            {/* NO ANALYSIS STATE */}
            {!isAnalyzing && !analysisData && (
              <div className="h-full min-h-[50vh] flex flex-col items-center justify-center text-center opacity-40 transition-opacity">
                <TrendingUp className="w-24 h-24 text-muted-foreground mb-6 transition-colors" />
                <h2 className="text-2xl font-bold text-foreground mb-2 transition-colors">Analysis Dashboard</h2>
                <p className="text-muted-foreground max-w-sm transition-colors">
                  Waiting for your latest request. Results will appear here once processed.
                </p>
              </div>
            )}

            {/* AI DASHBOARD RESPONSE */}
            {(isAnalyzing || analysisData) && (
              <div className="w-full h-full flex flex-col justify-start">
               {isAnalyzing && !analysisData ? (
                  <div className="h-[400px] flex items-center justify-center">
                     <div className="flex gap-2 items-center text-muted-foreground font-medium">
                        <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        <span>Querying ML model...</span>
                     </div>
                  </div>
               ) : analysisData ? (
                 analysisData.type === 'match_prediction' ? (
                   <MatchResultDisplay data={analysisData.analysis} />
                 ) : analysisData.type === 'agent_optimization' ? (
                   <AgentOptimizationDisplay data={analysisData.analysis} />
                 ) : analysisData.type === 'team_optimization' ? (
                   <TeamOptimizationDisplay data={analysisData.analysis} />
                 ) : analysisData.type === 'player_profile' ? (
                   <PlayerProfileDisplay data={analysisData.analysis} />
                 ) : analysisData.type === 'counter' ? (
                   <CounterStrategyDisplay data={analysisData.analysis} />
                 ) : null
               ) : null}
              </div>
            )}

          </div>
        </ScrollArea>
      </div>
      
    </div>
  );
}
