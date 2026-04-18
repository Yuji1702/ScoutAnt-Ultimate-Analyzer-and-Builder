"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Crosshair, Shield, Zap, Info } from 'lucide-react';
import WinRateComparisonChart from './charts/WinRateComparisonChart';

export default function CounterStrategyDisplay({ data }: { data: any }) {
  if (!data || !data.agent) return null;

  return (
    <div className="w-full mt-2 mb-8 transition-colors duration-300">
      <div className="opacity-0 translate-y-2 animate-[fadeIn_0.5s_ease-out_forwards]">
        <div className="bg-white/90 dark:bg-gray-800/60 rounded-2xl border border-gray-200 dark:border-gray-700/50 shadow-xl dark:shadow-2xl backdrop-blur-md overflow-hidden transition-colors duration-300">
          <Card className="border-0 bg-transparent shadow-none w-full">
            <div className="h-2 w-full bg-red-500" />
            <CardHeader className="pb-4 border-b border-gray-100 dark:border-gray-700/30 pt-6 px-6">
              <CardTitle className="text-2xl font-bold tracking-tight flex items-center justify-between">
                <span className="text-gray-900 dark:text-gray-100 flex items-center gap-2 transition-colors duration-300">
                  <Crosshair className="w-6 h-6 text-red-500" />
                  Counter Strategy
                </span>
                <Badge className="px-4 py-1.5 text-sm bg-red-600 hover:bg-red-700 text-white shadow-md">
                   {data.map} Analysis
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 px-6 space-y-8">
              
              {/* PRIMARY RECOMMENDATION */}
              <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-500/20 rounded-xl p-5 transition-colors duration-300 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-bold uppercase tracking-wider flex items-center gap-2">
                        <Shield className="w-4 h-4" /> Pick to Counter
                    </p>
                    <Badge variant="outline" className="border-red-400 text-red-600 dark:text-red-400 font-black">
                        {data.win_rate_vs}% Win Probability
                    </Badge>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-3xl font-black text-red-700 dark:text-red-400 drop-shadow-sm">{data.agent}</span>
                  <span className="text-gray-400 text-sm italic">vs</span>
                  <span className="text-xl font-bold text-gray-500 dark:text-gray-500 line-through opacity-50">{data.target_agent}</span>
                </div>
              </div>

              {/* VISUALIZATION: WIN RATE COMPARISON */}
              <div className="space-y-4">
                 <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-500" /> Matchup Advantage
                 </h4>
                 <WinRateComparisonChart 
                    agentA={data.agent} 
                    agentB={data.target_agent} 
                    winRateA={data.win_rate_vs || 55} 
                 />
              </div>

              {/* TACTICAL ROADMAP */}
              <div className="space-y-4">
                 <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <Info className="w-4 h-4 text-blue-500" /> Strategic Steps
                 </h4>
                 <div className="space-y-3">
                    {data.strategic_steps?.map((step: string, idx: number) => (
                      <div key={idx} className="flex gap-4 items-start bg-gray-50 dark:bg-gray-900/50 p-4 rounded-xl border border-gray-100 dark:border-gray-800 transition-all hover:bg-white dark:hover:bg-gray-800">
                        <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-xs shrink-0">
                          {idx + 1}
                        </div>
                        <p className="text-sm text-gray-700 dark:text-gray-300 font-medium">{step}</p>
                      </div>
                    ))}
                 </div>
              </div>

            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

