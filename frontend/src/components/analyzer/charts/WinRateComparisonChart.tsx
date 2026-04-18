"use client";

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';

interface WinRateComparisonChartProps {
  agentA: string;
  agentB: string;
  winRateA: number; // Win rate of A vs B
}

export default function WinRateComparisonChart({ agentA, agentB, winRateA }: WinRateComparisonChartProps) {
  const winRateB = 100 - winRateA;
  
  const data = [
    { name: agentA, value: winRateA, color: '#3b82f6' },
    { name: agentB, value: winRateB, color: '#ef4444' }
  ];

  return (
    <div className="h-[200px] w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} strokeOpacity={0.1} />
          <XAxis type="number" domain={[0, 100]} hide />
          <YAxis 
            dataKey="name" 
            type="category" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 'bold' }}
            width={70}
          />
          <Tooltip 
            cursor={{ fill: 'transparent' }}
            contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
            formatter={(value: number) => [`${value}%`, 'Win Rate']}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={32}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
            <LabelList 
                dataKey="value" 
                position="right" 
                formatter={(val: number) => `${val}%`}
                style={{ fill: '#9ca3af', fontSize: 11, fontWeight: 'bold' }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
