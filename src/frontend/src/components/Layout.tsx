import { Outlet } from 'react-router-dom';
import { useState } from 'react';
import Sidebar from './Sidebar';
import { Moon, Sun } from 'lucide-react';

export default function Layout() {
  const [dark, setDark] = useState(false);
  const toggle = () => {
    setDark(!dark);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className="flex h-full bg-slate-50 dark:bg-slate-950">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 py-4">
          <h1 className="text-lg font-semibold">NYC Taxi Analytics</h1>
          <button
            onClick={toggle}
            className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Toggle dark mode"
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
