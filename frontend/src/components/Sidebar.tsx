import React from 'react';
import { Settings, Zap, History, Plus, Sun, Moon } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface SidebarProps {
  onAction?: () => void;
  theme?: 'dark' | 'light';
  toggleTheme?: () => void;
}

export default function Sidebar({ onAction, theme, toggleTheme }: SidebarProps) {
  return (
    <aside className="w-[260px] h-full bg-gray-50 border-r border-gray-200 dark:bg-gray-800 dark:border-gray-700/50 flex-col hidden md:flex p-3 transition-colors duration-300">

      {/* Header Area */}
      <div className="flex items-center justify-between mb-4 mt-2 px-2">
        <button onClick={onAction} className="flex flex-1 items-center gap-2 group hover:bg-gray-200 dark:hover:bg-gray-700 p-2 rounded-lg transition-colors text-gray-700 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100">
          <div className="bg-blue-600 dark:bg-white text-white dark:text-black rounded-full p-1 shadow-sm">
            <Zap className="w-4 h-4 fill-current" />
          </div>
          <span className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">ScoutAnt AI</span>
        </button>

        {/* Theme Toggle Button */}
        {toggleTheme && (
          <button
            onClick={toggleTheme}
            className="p-2 ml-1 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors shrink-0"
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        )}
      </div>

      <div className="mb-4">
        <button onClick={onAction} className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground py-2.5 px-3 rounded-lg transition-all text-sm font-semibold shadow-md">
          <Plus className="w-4 h-4" />
          New Analysis
        </button>
      </div>

      {/* History Links */}
      <nav className="flex-1 overflow-y-auto scrollbar-hide-default space-y-1 mt-4">
        <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-500 mb-2 px-3 tracking-wider uppercase">Recent History</h2>

        <button onClick={onAction} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700/60 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors group">
          <History className="w-4 h-4 opacity-50 shrink-0 group-hover:opacity-100 transition-opacity" />
          <span className="text-sm font-medium truncate group-hover:text-gray-900 dark:group-hover:text-gray-200">Ascent comp analysis</span>
        </button>
        <button onClick={onAction} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700/60 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors group">
          <History className="w-4 h-4 opacity-50 shrink-0 group-hover:opacity-100 transition-opacity" />
          <span className="text-sm font-medium truncate group-hover:text-gray-900 dark:group-hover:text-gray-200">Jett Entry Pathing</span>
        </button>
        <button onClick={onAction} className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700/60 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors group">
          <History className="w-4 h-4 opacity-50 shrink-0 group-hover:opacity-100 transition-opacity" />
          <span className="text-sm font-medium truncate group-hover:text-gray-900 dark:group-hover:text-gray-200">Viper lineups</span>
        </button>
      </nav>

      {/* User Profile */}
      <div className="pt-2 border-t border-gray-200 dark:border-gray-700/50 mt-2">
        <div className="flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700/50 cursor-pointer transition-colors group">
          <Avatar className="h-8 w-8 border border-gray-300 dark:border-gray-600 group-hover:border-gray-400 dark:group-hover:border-gray-500 transition-colors">
            <AvatarImage src="https://github.com/shadcn.png" />
            <AvatarFallback className="bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200">UN</AvatarFallback>
          </Avatar>
          <div className="flex flex-col flex-1 overflow-hidden">
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">Login</span>
            <span className="text-xs text-gray-500 dark:text-gray-500 truncate"></span>
          </div>
          <Settings className="w-4 h-4 text-gray-500 dark:text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>
    </aside >
  );
}
