"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { UserCircle, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';

export default function PlayerProfileDisplay({ data }: { data: any }) {
  if (!data || !data.player) return null;

  const roleData = Object.entries(data.role_breakdown || {}).map(([name, value]) => ({
    name,
    value: Math.round((value as number) * 100)
  }));
  
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="w-full mt-2 mb-8 transition-colors duration-300">
      <div className="opacity-0 translate-y-2 animate-[fadeIn_0.5s_ease-out_forwards]">
        <div className="bg-white/90 dark:bg-gray-800/60 rounded-2xl border border-gray-200 dark:border-gray-700/50 shadow-xl dark:shadow-2xl backdrop-blur-md overflow-hidden transition-colors duration-300">
          <Card className="border-0 bg-transparent shadow-none w-full">
            <div className="h-2 w-full bg-blue-500" />
            <CardHeader className="pb-4 border-b border-gray-100 dark:border-gray-700/30 pt-6 px-6">
              <CardTitle className="text-2xl font-bold tracking-tight flex items-center justify-between">
                <span className="text-gray-900 dark:text-gray-100 flex items-center gap-2 transition-colors duration-300">
                  <UserCircle className="w-6 h-6 text-blue-500" />
                  Player Profile
                </span>
                <Badge className="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white">
                  {data.player}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 px-6 space-y-8">
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700/50 rounded-xl p-5 flex flex-col justify-center transition-colors duration-300">
                  <p className="text-sm text-gray-500 dark:text-gray-400 font-medium pb-1">Primary Role</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{data.main_role}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700/50 rounded-xl p-5 flex flex-col justify-center transition-colors duration-300">
                  <p className="text-sm text-gray-500 dark:text-gray-400 font-medium pb-1">Average ACS</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{data.average_stats?.acs?.toFixed(1) || 'N/A'}</p>
                </div>
              </div>

              {roleData.length > 0 && (
                <div className="space-y-4">
                  <h4 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider transition-colors flex items-center gap-2">
                      <Activity className="w-4 h-4" /> Role Dominance
                  </h4>
                  <div className="h-[250px] min-h-[250px] w-full pt-4 relative">
                     <ResponsiveContainer width="100%" height="100%" minHeight={250} minWidth={100}>
                         <PieChart>
                             <Pie
                                 data={roleData}
                                 cx="50%"
                                 cy="50%"
                                 innerRadius={60}
                                 outerRadius={90}
                                 paddingAngle={2}
                                 dataKey="value"
                                 stroke="none"
                             >
                                 {roleData.map((entry, index) => (
                                     <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                 ))}
                             </Pie>
                             <RechartsTooltip 
                                 contentStyle={{backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#f3f4f6'}}
                                 itemStyle={{color: '#fff'}}
                                 formatter={(value: number) => [`${value}%`, 'Play Rate']}
                             />
                             <Legend verticalAlign="bottom" height={36}/>
                         </PieChart>
                     </ResponsiveContainer>
                  </div>
                </div>
              )}

            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
