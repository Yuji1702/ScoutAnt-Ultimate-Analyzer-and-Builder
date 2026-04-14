"use client";

import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { MLTeamInsights } from '@/types/ml';

interface TeamRadarChartProps {
  teamA: MLTeamInsights;
  teamB: MLTeamInsights;
}

export default function TeamRadarChart({ teamA, teamB }: TeamRadarChartProps) {
  // Synthesize 5 dimensions for the radar chart based on the ML data
  
  const calcFlexibility = (team: MLTeamInsights) => {
    if (!team.players || team.players.length === 0) return 60;
    return (team.players.reduce((acc, p) => acc + p.flexibility_score, 0) / team.players.length) / 5 * 100;
  };
  
  const data = [
    {
      subject: 'Firepower (ACS)',
      A: Math.min((teamA.summary.avg_acs / 300) * 100, 100),
      B: Math.min((teamB.summary.avg_acs / 300) * 100, 100),
      fullMark: 100,
    },
    {
      subject: 'Impact (Rating)',
      A: Math.min((teamA.summary.avg_rating / 1.5) * 100, 100),
      B: Math.min((teamB.summary.avg_rating / 1.5) * 100, 100),
      fullMark: 100,
    },
    {
      subject: 'Flexibility',
      A: calcFlexibility(teamA),
      B: calcFlexibility(teamB),
      fullMark: 100,
    },
    {
      subject: 'Aggression',
      A: ((teamA.summary.role_distribution.duelist || 0) * 20) + ((teamA.summary.role_distribution.initiator || 0) * 10) + 20,
      B: ((teamB.summary.role_distribution.duelist || 0) * 20) + ((teamB.summary.role_distribution.initiator || 0) * 10) + 20,
      fullMark: 100,
    },
    {
      subject: 'Defense/Control',
      A: ((teamA.summary.role_distribution.sentinel || 0) * 25) + ((teamA.summary.role_distribution.controller || 0) * 25) + 10,
      B: ((teamB.summary.role_distribution.sentinel || 0) * 25) + ((teamB.summary.role_distribution.controller || 0) * 25) + 10,
      fullMark: 100,
    },
  ];

  return (
    <div className="w-full min-h-[250px] h-64 md:h-80 select-none">
      <ResponsiveContainer width="100%" height="100%" minHeight={250}>
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid strokeOpacity={0.2} stroke="currentColor" className="text-gray-400 dark:text-gray-500" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: 'currentColor', fontSize: 12, className: 'text-gray-600 dark:text-gray-300' }}
          />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          
          <Tooltip 
             contentStyle={{ 
               backgroundColor: 'var(--tw-colors-gray-900, #111827)', 
               borderColor: 'var(--tw-colors-gray-800, #1f2937)',
               color: '#f3f4f6',
               borderRadius: '0.75rem',
               boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
             }}
             itemStyle={{ color: '#e5e7eb' }}
          />
          
          <Radar name="Team A" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} strokeWidth={2} />
          <Radar name="Team B" dataKey="B" stroke="#ef4444" fill="#ef4444" fillOpacity={0.4} strokeWidth={2} />
          
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
