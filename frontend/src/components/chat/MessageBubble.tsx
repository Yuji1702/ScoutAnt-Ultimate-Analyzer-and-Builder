import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Zap, User } from 'lucide-react';

interface MessageBubbleProps {
  content: string;
  isBot: boolean;
}

export default function MessageBubble({ content, isBot }: MessageBubbleProps) {
  return (
    <div className={`group w-full transition-colors duration-300`}>
      <div className={`max-w-3xl mx-auto flex gap-4 px-4 py-6 md:px-6`}>
        <div className="shrink-0 mt-0.5">
          {isBot ? (
            <Avatar className="h-8 w-8 rounded-full border border-gray-200 dark:border-gray-600 shadow-sm bg-blue-600 dark:bg-white text-white dark:text-black">
              <div className="w-full h-full flex items-center justify-center">
                <Zap className="w-5 h-5 fill-current" />
              </div>
            </Avatar>
          ) : (
            <Avatar className="h-8 w-8 rounded-full border border-gray-200 dark:border-gray-600 bg-gray-100 dark:bg-gray-700">
              <div className="w-full h-full flex items-center justify-center text-gray-800 dark:text-gray-300">
                <User className="w-5 h-5" />
              </div>
            </Avatar>
          )}
        </div>

        <div className="flex-1 space-y-2 overflow-hidden">
          <div className="font-semibold text-sm text-gray-900 dark:text-gray-100 transition-colors">
            {isBot ? 'ScoutAnt' : 'You'}
          </div>
          <div className={`text-base leading-relaxed whitespace-pre-wrap flex flex-col gap-3 transition-colors ${isBot ? 'text-gray-700 dark:text-gray-300 font-light' : 'text-gray-800 dark:text-gray-200'}`}>
            {content}
          </div>
        </div>
      </div>
    </div>
  );
}
