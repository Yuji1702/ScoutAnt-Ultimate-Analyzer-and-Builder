"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { User, Crosshair } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell } from 'recharts';

export default function AgentOptimizationDisplay({ data }: { data: any }) {
  if (!data || !data.suggestions) return null;

  const chartData = data.suggestions.slice(0, 5).map((s: any) => ({
    name: s.agent,
    rating: s.predicted_rating,
    role: s.best_role
  }));

  // Find max rating for domain
  const maxRating = Math.max(...chartData.map((d: any) => d.rating));
  const minRating = Math.min(...chartData.map((d: any) => d.rating));

  return (
    <div className="w-full mt-2 mb-8 transition-colors duration-300">
      <div className="opacity-0 translate-y-2 animate-[fadeIn_0.5s_ease-out_forwards]">
        <div className="bg-white/90 dark:bg-gray-800/60 rounded-2xl border border-gray-200 dark:border-gray-700/50 shadow-xl dark:shadow-2xl backdrop-blur-md overflow-hidden transition-colors duration-300">
          <Card className="border-0 bg-transparent shadow-none w-full">
            <div className="h-2 w-full bg-indigo-500" />
            <CardHeader className="pb-4 border-b border-gray-100 dark:border-gray-700/30 pt-6 px-6">
              <CardTitle className="text-2xl font-bold tracking-tight flex items-center justify-between">
                <span className="text-gray-900 dark:text-gray-100 flex items-center gap-2 transition-colors duration-300">
                  <User className="w-6 h-6 text-indigo-500" />
                  Agent Optimization
                </span>
                <Badge className="px-4 py-1.5 text-sm bg-indigo-600 hover:bg-indigo-700 text-white">
                  For {data.player}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 px-6 space-y-8">
              
              <div className="bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-200 dark:border-indigo-500/20 rounded-xl p-5 flex items-center justify-between transition-colors duration-300">
                <div className="flex-col">
                  <p className="text-sm text-gray-600 dark:text-gray-400 font-medium pb-2 transition-colors">Top Recommended Agent on {data.map}</p>
                  <div className="flex gap-2 items-center">
                    <Badge variant="default" className="text-base px-4 py-1.5 bg-indigo-100 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-400 font-bold border-indigo-300 dark:border-indigo-500/30">
                      {data.suggestions[0].agent}
                    </Badge>
                    <span className="text-gray-500 dark:text-gray-500 text-sm font-semibold">({data.suggestions[0].best_role})</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400 font-medium pb-1 transition-colors">Prog. Rating</p>
                  <p className="text-2xl font-black text-gray-800 dark:text-gray-100">{data.suggestions[0].predicted_rating.toFixed(2)}</p>
                </div>
              </div>

              <div className="space-y-4">
                 <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider transition-colors flex items-center gap-2">
                    <Crosshair className="w-4 h-4" /> Agent Performance Curve
                 </h4>
                 <div className="h-[250px] min-h-[250px] w-full pt-4 relative">
                    <ResponsiveContainer width="100%" height="100%" minHeight={250} minWidth={100}>
                      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                        <XAxis dataKey="name" tick={{fill: '#888', fontSize: 13}} axisLine={false} tickLine={false} />
                        <YAxis domain={[Math.max(0, minRating - 0.2), maxRating + 0.1]} tick={{fill: '#888', fontSize: 13}} axisLine={false} tickLine={false} />
                        <RechartsTooltip 
                           cursor={{fill: 'transparent'}}
                           contentStyle={{backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#f3f4f6'}}
                           itemStyle={{color: '#818cf8'}}
                        />
                        <Bar dataKey="rating" radius={[4, 4, 0, 0]}>
                           {chartData.map((entry: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={index === 0 ? '#6366f1' : '#94a3b8'} />
                           ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                 </div>
              </div>

            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
