"use client";

import React, { useState, useEffect } from 'react';
import Sidebar from "@/components/Sidebar";
import DashboardContainer from "@/components/analyzer/DashboardContainer";

export default function Home() {
  // Using a key to reset the Dashboard state quickly without complex state management
  const [resetKey, setResetKey] = useState(0);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // Initialize theme by enforcing the dark class on default unless toggled
  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <div className="flex h-screen w-full bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-400 overflow-hidden font-sans transition-colors duration-300 ease-in-out">
      <Sidebar 
        onAction={() => setResetKey(prev => prev + 1)} 
        theme={theme} 
        toggleTheme={toggleTheme} 
      />
      <main className="flex-1 flex flex-col h-full overflow-hidden relative bg-gray-50 dark:bg-gray-900 transition-colors duration-300 ease-in-out">
        <DashboardContainer key={resetKey} />
      </main>
    </div>
  );
}
