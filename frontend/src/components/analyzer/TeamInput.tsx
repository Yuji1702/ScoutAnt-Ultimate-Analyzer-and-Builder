import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const AGENTS = [
  "Jett", "Sova", "Omen", "Cypher", 
  "Killjoy", "Raze", "Skye", "KAY/O"
];

interface TeamInputProps {
  teamName: string;
}

export default function TeamInput({ teamName }: TeamInputProps) {
  return (
    <Card className="w-full bg-gray-800/40 border-gray-700/50 backdrop-blur-sm shadow-xl">
      <CardHeader className="pb-4 border-b border-gray-700/30 mb-4">
        <CardTitle className="text-xl font-bold tracking-tight text-gray-100 flex items-center gap-2">
          {teamName}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {[1, 2, 3, 4, 5].map((playerNum) => (
          <div key={playerNum} className="grid grid-cols-1 md:grid-cols-[1fr_150px] gap-3 items-center group">
            <div className="relative">
              <Input 
                placeholder={`Player ${playerNum}`} 
                className="bg-gray-900/60 border-gray-700/60 text-gray-200 focus-visible:ring-blue-500/50 hover:border-gray-600 transition-colors h-10"
              />
            </div>
            
            <div className="relative">
              <select 
                className="h-10 w-full appearance-none rounded-lg border border-gray-700/60 bg-gray-900/60 px-3 py-1.5 pr-8 text-sm text-gray-200 outline-none transition-colors hover:border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                defaultValue=""
              >
                <option value="" disabled hidden>Select Agent</option>
                {AGENTS.map(agent => (
                  <option key={agent} value={agent} className="bg-gray-800 text-gray-100 py-1">
                    {agent}
                  </option>
                ))}
              </select>
              {/* Custom Chevron for select */}
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 group-hover:text-gray-400 transition-colors">
                <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3.13523 6.15803C3.3241 5.95657 3.64052 5.94637 3.84197 6.13523L7.5 9.56464L11.158 6.13523C11.3595 5.94637 11.6759 5.95657 11.8648 6.15803C12.0536 6.35949 12.0434 6.67591 11.842 6.86477L7.84197 10.6148C7.64964 10.7951 7.35036 10.7951 7.15803 10.6148L3.15803 6.86477C2.95657 6.67591 2.94637 6.35949 3.13523 6.15803Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
                </svg>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
