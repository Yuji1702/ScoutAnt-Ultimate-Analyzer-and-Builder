"use client";

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { MLTeamInsights } from '@/types/ml';

interface PlayerBarChartProps {
  team: MLTeamInsights;
  teamName: string;
  color: string;
  dataKey: 'predicted_rating' | 'predicted_acs';
}

export default function PlayerBarChart({ team, teamName, color, dataKey }: PlayerBarChartProps) {
  if (!team.players || team.players.length === 0) {
    return (
      <div className="w-full h-64 md:h-72 flex items-center justify-center text-gray-500 dark:text-gray-400 font-medium bg-gray-50/50 dark:bg-gray-800/20 rounded-xl border border-gray-100 dark:border-gray-800">
        Data not found for {teamName}
      </div>
    );
  }
  
  // Sort players by the chosen metric descending
  const sortedPlayers = [...team.players].sort((a, b) => b[dataKey] - a[dataKey]);
  
  const displayLabels = {
    'predicted_rating': 'Rating 2.0',
    'predicted_acs': 'Predicted ACS'
  };

  return (
    <div className="w-full min-h-[250px] h-64 md:h-72 select-none">
      <ResponsiveContainer width="100%" height="100%" minHeight={250}>
        <BarChart
          data={sortedPlayers}
          margin={{ top: 20, right: 30, left: -20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.15} stroke="currentColor" className="text-gray-400 dark:text-gray-600" />
          <XAxis 
             dataKey="name" 
             tick={{ fill: 'currentColor', fontSize: 12, className: 'text-gray-600 dark:text-gray-300' }} 
             axisLine={false}
             tickLine={false}
          />
          <YAxis 
             tick={{ fill: 'currentColor', fontSize: 12, className: 'text-gray-600 dark:text-gray-400' }}
             axisLine={false}
             tickLine={false}
          />
          <Tooltip 
             cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
             contentStyle={{ 
               backgroundColor: 'var(--tw-colors-gray-900, #111827)', 
               borderColor: 'var(--tw-colors-gray-800, #1f2937)',
               color: '#f3f4f6',
               borderRadius: '0.75rem',
               boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
             }}
          />
          <Legend />
          <Bar dataKey={dataKey} name={displayLabels[dataKey]} fill={color} radius={[4, 4, 0, 0]}>
            {sortedPlayers.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={color} fillOpacity={0.8 + (0.2 * (1 - index/sortedPlayers.length))} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
