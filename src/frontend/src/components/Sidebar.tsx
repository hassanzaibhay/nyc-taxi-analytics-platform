import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MapPin, DollarSign, Activity } from 'lucide-react';

const links = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/zones', label: 'Zone Analytics', icon: MapPin },
  { to: '/fares', label: 'Fare Insights', icon: DollarSign },
  { to: '/live', label: 'Live Monitor', icon: Activity },
];

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <div className="mb-8 px-2 text-sm font-semibold uppercase tracking-wider text-slate-500">
        Taxi Platform
      </div>
      <nav className="space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                isActive
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
