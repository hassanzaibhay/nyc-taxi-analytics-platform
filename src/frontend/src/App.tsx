import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import ZoneAnalytics from './pages/ZoneAnalytics';
import FareInsights from './pages/FareInsights';
import LiveMonitor from './pages/LiveMonitor';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Overview />} />
        <Route path="/zones" element={<ZoneAnalytics />} />
        <Route path="/fares" element={<FareInsights />} />
        <Route path="/live" element={<LiveMonitor />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
