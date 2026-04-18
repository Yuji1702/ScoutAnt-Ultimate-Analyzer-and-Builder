"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, LayoutList, TrendingUp } from 'lucide-react';

export default function TeamOptimizationDisplay({ data }: { data: any }) {
  if (!data || !data.compositions || data.compositions.length === 0) return null;

  const topComp = data.compositions[0];

  return (
    <div className="w-full mt-2 mb-8 transition-colors duration-300">
      <div className="opacity-0 translate-y-2 animate-[fadeIn_0.5s_ease-out_forwards]">
        <div className="bg-white/90 dark:bg-gray-800/60 rounded-2xl border border-gray-200 dark:border-gray-700/50 shadow-xl dark:shadow-2xl backdrop-blur-md overflow-hidden transition-colors duration-300">
          <Card className="border-0 bg-transparent shadow-none w-full">
            <div className="h-2 w-full bg-emerald-500" />
            <CardHeader className="pb-4 border-b border-gray-100 dark:border-gray-700/30 pt-6 px-6">
              <CardTitle className="text-2xl font-bold tracking-tight flex items-center justify-between">
                <span className="text-gray-900 dark:text-gray-100 flex items-center gap-2 transition-colors duration-300">
                  <Users className="w-6 h-6 text-emerald-500" />
                  Team Optimization
                </span>
                <Badge className="px-4 py-1.5 text-sm bg-emerald-600 hover:bg-emerald-700 text-white">
                  {data.map}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 px-6 space-y-8">
              
              <div className="bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl p-5 flex items-center justify-between transition-colors duration-300">
                <div className="flex-col">
                  <p className="text-sm text-gray-600 dark:text-gray-400 font-medium pb-2 transition-colors">Best Predicted Roster Strategy</p>
                  <p className="text-gray-800 dark:text-gray-200 font-medium text-sm">
                    Maximizes aggregate predicted combat score across assigned roles.
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400 font-medium pb-1 transition-colors">Total Rating</p>
                  <p className="text-2xl font-black text-gray-800 dark:text-gray-100">{topComp.total_rating.toFixed(2)}</p>
                </div>
              </div>

              <div className="space-y-4">
                 <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider transition-colors flex items-center gap-2">
                    <LayoutList className="w-4 h-4" /> Roster Composition
                 </h4>
                 
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                   {topComp.players.map((p: [string, string], idx: number) => (
                     <div key={idx} className="flex flex-row items-center justify-between bg-gray-50 dark:bg-gray-800/40 border border-gray-100 dark:border-gray-700/50 rounded-xl p-4 shadow-sm transition-colors duration-300">
                        <div className="flex items-center gap-3">
                           <div className="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-bold flex items-center justify-center text-sm border border-emerald-200 dark:border-emerald-500/30">
                              {p[0].charAt(0).toUpperCase()}
                           </div>
                           <span className="font-bold text-gray-900 dark:text-gray-100">{p[0]}</span>
                        </div>
                        <Badge variant="outline" className="text-emerald-700 dark:text-emerald-400 font-bold border-emerald-300 dark:border-emerald-700/50 bg-emerald-50 dark:bg-emerald-900/10 px-3 py-1">
                           {p[1]}
                        </Badge>
                     </div>
                   ))}
                 </div>
              </div>

              <div className="space-y-4">
                 <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider transition-colors pt-4 border-t border-gray-100 dark:border-gray-700/30 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-500" /> Strategic Roadmap
                 </h4>
                 <div className="space-y-3">
                    {data.strategic_roadmap?.map((step: string, idx: number) => (
                      <div key={idx} className="flex gap-4 items-start bg-gray-50 dark:bg-gray-900/40 p-4 rounded-xl border border-gray-100 dark:border-gray-800 transition-all hover:bg-white dark:hover:bg-gray-800">
                        <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400 flex items-center justify-center font-bold text-xs shrink-0">
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

