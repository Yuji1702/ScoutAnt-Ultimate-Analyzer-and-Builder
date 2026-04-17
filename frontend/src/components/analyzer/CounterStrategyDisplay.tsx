"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Crosshair, Shield } from 'lucide-react';

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
                <Badge className="px-4 py-1.5 text-sm bg-red-600 hover:bg-red-700 text-white">
                  Strategy
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 px-6 space-y-8">
              
              <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-500/20 rounded-xl p-5 transition-colors duration-300">
                <p className="text-sm text-gray-600 dark:text-gray-400 font-medium pb-2 transition-colors">Recommended Counter Pick</p>
                <div className="flex items-center gap-3">
                  <div className="bg-red-100 dark:bg-red-500/20 rounded-full p-2">
                    <Shield className="w-5 h-5 text-red-600 dark:text-red-500" />
                  </div>
                  <span className="text-2xl font-bold text-red-700 dark:text-red-400">{data.agent}</span>
                </div>
              </div>

              <div className="space-y-4">
                 <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider transition-colors">
                    Tactical Reasoning
                 </h4>
                 <div className="bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-700/50 rounded-xl p-5 shadow-sm">
                   <p className="text-gray-800 dark:text-gray-200 leading-relaxed font-medium">
                     {data.reason || "The AI model has determined this agent provides the highest statistical advantage in this matchup based on historical performance data."}
                   </p>
                 </div>
              </div>

            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
