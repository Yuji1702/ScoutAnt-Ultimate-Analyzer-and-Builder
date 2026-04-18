"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Activity } from 'lucide-react';

interface AnalysisBubbleProps {
  teamAWins: boolean;
  winProbability: number;
  bestAgent: string;
  insights: string[];
}

export default function AnalysisBubble({
  teamAWins,
  winProbability,
  bestAgent,
  insights
}: AnalysisBubbleProps) {
  const [isReady, setIsReady] = useState(false);
  const [internalProgress, setInternalProgress] = useState(0);

  // Simulate thinking and typing animation before showing results
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsReady(true);
      // Animate progress bar filling up after rendering
      setTimeout(() => setInternalProgress(winProbability), 100);
    }, 1500);
    
    return () => clearTimeout(timer);
  }, [winProbability]);

  return (
    <div className="w-full mt-2 mb-8 transition-colors duration-300">
      {!isReady ? (
        <div className="bg-white/80 dark:bg-gray-800/80 rounded-2xl p-6 w-full flex flex-col items-center justify-center gap-4 border border-gray-200 dark:border-gray-700/50 min-h-[300px] shadow-sm dark:shadow-none transition-colors duration-300">
          <div className="w-12 h-12 bg-blue-100 dark:bg-blue-600/20 text-blue-600 dark:text-blue-500 rounded-full flex items-center justify-center">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div className="flex gap-2 items-center text-gray-600 dark:text-gray-400 font-medium">
            <span>Generating strategic insights</span>
            <div className="flex space-x-1 ml-1">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
            </div>
          </div>
        </div>
      ) : (
        <div className="opacity-0 translate-y-2 animate-[fadeIn_0.5s_ease-out_forwards]">
          <div className="bg-white/90 dark:bg-gray-800/60 rounded-2xl border border-gray-200 dark:border-gray-700/50 shadow-xl dark:shadow-2xl backdrop-blur-md overflow-hidden transition-colors duration-300">
            <Card className="border-0 bg-transparent shadow-none w-full">
              
              <div className={`h-2 w-full transition-colors duration-500 ${teamAWins ? 'bg-blue-500' : 'bg-red-500'}`} />

              <CardHeader className="pb-4 border-b border-gray-100 dark:border-gray-700/30 pt-6 px-6">
                <CardTitle className="text-2xl font-bold tracking-tight flex items-center justify-between">
                  <span className="text-gray-900 dark:text-gray-100 flex items-center gap-2 transition-colors duration-300">
                    <Sparkles className="w-6 h-6 text-yellow-500" />
                    Match Analysis
                  </span>
                  <Badge variant={teamAWins ? "default" : "destructive"} className={`px-4 py-1.5 text-sm ${teamAWins ? 'bg-blue-600 hover:bg-blue-700 text-white' : ''}`}>
                    {teamAWins ? "Team A Advantage" : "Team B Advantage"}
                  </Badge>
                </CardTitle>
              </CardHeader>
              
              <CardContent className="pt-6 px-6 space-y-8">
                
                {/* Win Probability Section */}
                <div className="space-y-3 bg-gray-50 dark:bg-gray-900/50 p-5 rounded-xl border border-gray-100 dark:border-gray-700/50 transition-colors duration-300">
                  <div className="flex justify-between text-base font-semibold">
                    <span className="text-gray-700 dark:text-gray-300 transition-colors">Expected Win Probability</span>
                    <span className={`${teamAWins ? 'text-blue-600 dark:text-blue-400' : 'text-red-600 dark:text-red-400'} font-bold text-lg transition-colors`}>
                      {internalProgress}%
                    </span>
                  </div>
                  <Progress 
                    value={internalProgress} 
                    className="h-3 bg-gray-200 dark:bg-gray-800" 
                    indicatorClassName={teamAWins ? "bg-gradient-to-r from-blue-500 to-indigo-500 dark:from-blue-600 dark:to-indigo-400" : "bg-gradient-to-r from-red-500 to-orange-500 dark:from-red-600 dark:to-orange-400"}
                  />
                </div>

                {/* Best Agent Card */}
                <div className="bg-purple-50 dark:bg-purple-900/10 border border-purple-200 dark:border-purple-500/20 rounded-xl p-5 flex items-center justify-between transition-colors duration-300">
                  <div className="flex-col">
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium pb-2 transition-colors">Most Impactful Agent in Matchup</p>
                    <Badge variant="agent" className="text-base px-4 py-1.5 border-purple-300 dark:border-purple-500/30 bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 font-bold">
                      {bestAgent}
                    </Badge>
                  </div>
                </div>

                {/* Key Insights List */}
                <div className="space-y-4">
                  <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider transition-colors">Strategic Breakdown</h4>
                  <ul className="space-y-3">
                    {insights.map((insight, idx) => (
                      <li key={idx} className="flex gap-4 text-base text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-800/40 p-4 rounded-xl border border-gray-100 dark:border-gray-700/30 transition-colors duration-300">
                        <div className="mt-0.5">
                          <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center text-xs font-bold transition-colors">
                            {idx + 1}
                          </div>
                        </div>
                        <span className="leading-snug pt-0.5">{insight}</span>
                      </li>
                    ))}
                  </ul>
                </div>

              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
