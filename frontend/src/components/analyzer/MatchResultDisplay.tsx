"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { MLMatchQueryResponse } from '@/types/ml';
import TeamRadarChart from './charts/TeamRadarChart';
import PlayerBarChart from './charts/PlayerBarChart';
import { Sparkles, Map, Swords, BrainCircuit, Users, TrendingUp } from 'lucide-react';

interface MatchResultDisplayProps {
  data: MLMatchQueryResponse;
}

export default function MatchResultDisplay({ data }: MatchResultDisplayProps) {
  const teamAWins = data.team_a_win_probability > data.team_b_win_probability;

  return (
    <div className="space-y-6 w-full animate-[fadeIn_0.5s_ease-out_forwards]">
      
      {/* HEADER CARD */}
      <Card className="bg-white/90 dark:bg-gray-900/60 shadow-xl dark:shadow-2xl border-gray-200 dark:border-gray-800/50 backdrop-blur-md overflow-hidden transition-all duration-300 hover:shadow-blue-900/5 hover:border-blue-500/20">
        <div className={`h-1.5 w-full bg-gradient-to-r ${teamAWins ? 'from-blue-500 to-blue-400' : 'from-red-500 to-red-400'}`} />
        <CardHeader className="pb-4">
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-2xl font-black tracking-tight flex items-center gap-2">
                <Map className="w-5 h-5 text-gray-500" />
                {data.map} Matchup Analysis
              </CardTitle>
              <CardDescription className="mt-1 flex items-center gap-2">
                <Badge variant="outline" className={`${
                  data.confidence === 'High' ? 'text-green-600 border-green-600/30 bg-green-50' : 
                  data.confidence === 'Medium' ? 'text-yellow-600 border-yellow-600/30 bg-yellow-50' : 
                  'text-red-600 border-red-600/30 bg-red-50'
                } dark:bg-transparent`}>
                  {data.confidence} Confidence
                </Badge>
                <span className="text-xs text-gray-400 italic">{data.note}</span>
              </CardDescription>
            </div>
            <Badge variant={teamAWins ? "default" : "destructive"} className={`px-4 py-1.5 text-base shadow-lg ${teamAWins ? 'bg-blue-600 hover:bg-blue-700' : 'bg-red-600 hover:bg-red-700'}`}>
              Team {teamAWins ? "A" : "B"} Favored
            </Badge>
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-2 bg-gray-50 dark:bg-gray-800/50 p-5 rounded-2xl border border-gray-100 dark:border-gray-700/50">
            <div className="flex justify-between items-end mb-2">
              <div className="flex flex-col">
                <span className="text-sm font-bold text-blue-600 dark:text-blue-400">Team A</span>
                <span className="text-2xl font-black text-gray-900 dark:text-white">{(data.team_a_win_probability * 100).toFixed(1)}%</span>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-sm font-bold text-red-600 dark:text-red-400">Team B</span>
                <span className="text-2xl font-black text-gray-900 dark:text-white">{(data.team_b_win_probability * 100).toFixed(1)}%</span>
              </div>
            </div>
            <div className="h-4 w-full bg-red-500 rounded-full overflow-hidden flex relative">
              <div 
                className="h-full bg-blue-500 transition-all duration-1000 ease-out z-10"
                style={{ width: `${data.team_a_win_probability * 100}%` }}
              />
              {/* Optional marker at 50% */}
              <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-white/50 z-20" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* TEAM ROSTERS SECTION */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
         {/* Team A Roster */}
         <Card className="bg-white/90 dark:bg-gray-900/60 shadow-lg border-blue-200 dark:border-blue-900/30 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-16 bg-blue-500/10 blur-[100px] rounded-full pointer-events-none" />
            <CardHeader className="pb-3 border-b border-blue-100 dark:border-blue-900/50">
               <CardTitle className="text-lg flex items-center gap-2 text-blue-700 dark:text-blue-400">
                  <Users className="w-5 h-5" /> Team A Selected Roster
               </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3 relative z-10">
               {data.team_a.players.map((p, idx) => (
                 <div key={idx} className="flex flex-col bg-gray-50/80 dark:bg-gray-800/60 p-3 rounded-xl border border-gray-200 dark:border-gray-700/50 shadow-sm transition-all hover:border-blue-300 dark:hover:border-blue-500/50 hover:bg-white dark:hover:bg-gray-800">
                    <div className="flex justify-between items-center mb-2">
                       <span className="font-bold text-gray-900 dark:text-gray-100 text-base">{p.name}</span>
                       <Badge variant="outline" className="bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 border-blue-200 dark:border-blue-800 shadow-sm">
                          {p.agent}
                       </Badge>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                       <div className="bg-white dark:bg-gray-900 rounded p-1.5 text-center border border-gray-100 dark:border-gray-800">
                          <span className="block text-gray-500 dark:text-gray-500 uppercase font-bold text-[10px]">Proj. Rating</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200">{p.predicted_rating.toFixed(2)}</span>
                       </div>
                       <div className="bg-white dark:bg-gray-900 rounded p-1.5 text-center border border-gray-100 dark:border-gray-800">
                          <span className="block text-gray-500 dark:text-gray-500 uppercase font-bold text-[10px]">Proj. ACS</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200">{p.predicted_acs.toFixed(0)}</span>
                       </div>
                       <div className="bg-white dark:bg-gray-900 rounded p-1.5 text-center border border-gray-100 dark:border-gray-800">
                          <span className="block text-gray-500 dark:text-gray-500 uppercase font-bold text-[10px]">Best Role</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200 truncate" title={p.best_role}>{p.best_role}</span>
                       </div>
                    </div>
                 </div>
               ))}
            </CardContent>
         </Card>

         {/* Team B Roster */}
         <Card className="bg-white/90 dark:bg-gray-900/60 shadow-lg border-red-200 dark:border-red-900/30 overflow-hidden relative">
            <div className="absolute top-0 left-0 p-16 bg-red-500/10 blur-[100px] rounded-full pointer-events-none" />
            <CardHeader className="pb-3 border-b border-red-100 dark:border-red-900/50">
               <CardTitle className="text-lg flex items-center gap-2 text-red-700 dark:text-red-400">
                  <Users className="w-5 h-5" /> Team B Selected Roster
               </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3 relative z-10">
               {data.team_b.players.map((p, idx) => (
                 <div key={idx} className="flex flex-col bg-gray-50/80 dark:bg-gray-800/60 p-3 rounded-xl border border-gray-200 dark:border-gray-700/50 shadow-sm transition-all hover:border-red-300 dark:hover:border-red-500/50 hover:bg-white dark:hover:bg-gray-800">
                    <div className="flex justify-between items-center mb-2">
                       <span className="font-bold text-gray-900 dark:text-gray-100 text-base">{p.name}</span>
                       <Badge variant="outline" className="bg-red-50 text-red-700 dark:bg-red-900/40 dark:text-red-300 border-red-200 dark:border-red-800 shadow-sm">
                          {p.agent}
                       </Badge>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                       <div className="bg-white dark:bg-gray-900 rounded p-1.5 text-center border border-gray-100 dark:border-gray-800">
                          <span className="block text-gray-500 dark:text-gray-500 uppercase font-bold text-[10px]">Proj. Rating</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200">{p.predicted_rating.toFixed(2)}</span>
                       </div>
                       <div className="bg-white dark:bg-gray-900 rounded p-1.5 text-center border border-gray-100 dark:border-gray-800">
                          <span className="block text-gray-500 dark:text-gray-500 uppercase font-bold text-[10px]">Proj. ACS</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200">{p.predicted_acs.toFixed(0)}</span>
                       </div>
                       <div className="bg-white dark:bg-gray-900 rounded p-1.5 text-center border border-gray-100 dark:border-gray-800">
                          <span className="block text-gray-500 dark:text-gray-500 uppercase font-bold text-[10px]">Best Role</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200 truncate" title={p.best_role}>{p.best_role}</span>
                       </div>
                    </div>
                 </div>
               ))}
            </CardContent>
         </Card>
      </div>

      {/* CHARTS GRID */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        
        {/* Radar Chart */}
        <Card className="bg-white/90 dark:bg-gray-900/60 shadow-lg border-gray-200 dark:border-gray-800/50">
          <CardHeader className="pb-0">
            <CardTitle className="text-lg flex items-center gap-2 text-gray-800 dark:text-gray-200">
              <Swords className="w-5 h-5 text-purple-500" />
              Team Composition Matchup
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
             <TeamRadarChart teamA={data.team_a} teamB={data.team_b} />
          </CardContent>
        </Card>

        {/* Players ACS Chart */}
        <Card className="bg-white/90 dark:bg-gray-900/60 shadow-lg border-gray-200 dark:border-gray-800/50">
          <CardHeader className="pb-0">
            <CardTitle className="text-lg flex items-center gap-2 text-gray-800 dark:text-gray-200">
              <TrendingUp className="w-5 h-5 text-green-500" />
              Top Fragger Predictions (ACS)
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
             <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-xs font-bold text-blue-500 uppercase tracking-wider mb-2 block text-center">Team A</span>
                  <PlayerBarChart team={data.team_a} teamName="Team A" color="#3b82f6" dataKey="predicted_acs" />
                </div>
                <div>
                  <span className="text-xs font-bold text-red-500 uppercase tracking-wider mb-2 block text-center">Team B</span>
                  <PlayerBarChart team={data.team_b} teamName="Team B" color="#ef4444" dataKey="predicted_acs" />
                </div>
             </div>
          </CardContent>
        </Card>
      </div>

      {/* STRATEGIC INSIGHTS */}
      <Card className="bg-white/90 dark:bg-gray-900/60 shadow-lg border-gray-200 dark:border-gray-800/50 overflow-hidden relative">
        <div className="absolute top-0 right-0 p-16 bg-blue-500/5 blur-[100px] rounded-full pointer-events-none" />
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2 text-gray-800 dark:text-gray-200">
            <BrainCircuit className="w-6 h-6 text-yellow-500" />
            AI Strategic Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
            
            {/* Reasoning */}
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Model Reasoning</h4>
              <ul className="space-y-3">
                {data.model_reasoning.map((reason, idx) => (
                  <li key={idx} className="flex gap-3 text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800/40 p-3 rounded-xl border border-gray-100 dark:border-gray-700/30">
                    <Sparkles className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Tactical Insights */}
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Tactical Insights</h4>
              <ul className="space-y-3">
                {data.insights.map((insight, idx) => (
                  <li key={idx} className="flex gap-3 text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800/40 p-3 rounded-xl border border-gray-100 dark:border-gray-700/30">
                    <Users className="w-4 h-4 text-purple-500 shrink-0 mt-0.5" />
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>

          </div>
        </CardContent>
      </Card>

    </div>
  );
}
