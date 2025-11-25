import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  Home,
  BookOpen,
  MessageCircle,
  BookMarked,
  Mic,
  User,
  Flame,
  Trophy
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { useLearningStore } from '../stores/learningStore';
import { cn } from '../lib/utils';

const navItems = [
  { path: '/dashboard', icon: Home, label: '홈' },
  { path: '/lessons', icon: BookOpen, label: '레슨' },
  { path: '/conversation', icon: MessageCircle, label: '대화' },
  { path: '/vocabulary', icon: BookMarked, label: '단어장' },
  { path: '/pronunciation', icon: Mic, label: '발음' },
];

export function Layout() {
  const location = useLocation();
  const { user } = useAuthStore();
  const { streak, totalXp } = useLearningStore();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto h-full px-4 flex items-center justify-between">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
            <span className="font-bold text-xl text-gray-900">MUSE Language</span>
          </Link>

          {/* Stats */}
          <div className="flex items-center gap-6">
            {/* Streak */}
            <div className="flex items-center gap-1.5">
              <Flame className={cn(
                "w-5 h-5",
                streak.current > 0 ? "text-orange-500" : "text-gray-400"
              )} />
              <span className="font-semibold text-gray-700">{streak.current}</span>
            </div>

            {/* XP */}
            <div className="flex items-center gap-1.5">
              <Trophy className="w-5 h-5 text-yellow-500" />
              <span className="font-semibold text-gray-700">{totalXp} XP</span>
            </div>

            {/* Profile */}
            <Link
              to="/profile"
              className="flex items-center gap-2 hover:bg-gray-100 rounded-full p-1.5 transition-colors"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.name?.charAt(0) || 'U'}
                </span>
              </div>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-16 pb-20 md:pb-0 md:pl-64">
        <div className="max-w-5xl mx-auto p-6">
          <Outlet />
        </div>
      </main>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-200 flex-col">
        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={cn(
                      "flex items-center gap-3 px-4 py-3 rounded-xl transition-all",
                      isActive
                        ? "bg-blue-50 text-blue-600 font-medium"
                        : "text-gray-600 hover:bg-gray-100"
                    )}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Language Selector */}
        <div className="p-4 border-t border-gray-200">
          <LanguageSelector />
        </div>
      </aside>

      {/* Mobile Bottom Nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-white border-t border-gray-200">
        <ul className="flex h-full">
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <li key={item.path} className="flex-1">
                <Link
                  to={item.path}
                  className={cn(
                    "flex flex-col items-center justify-center h-full gap-0.5 transition-colors",
                    isActive ? "text-blue-600" : "text-gray-500"
                  )}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="text-xs">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}

function LanguageSelector() {
  const { targetLanguage, setTargetLanguage } = useAuthStore();

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'zh', name: '中文', flag: '🇨🇳' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
  ];

  const current = languages.find(l => l.code === targetLanguage) || languages[0];

  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
        학습 언어
      </label>
      <select
        value={targetLanguage}
        onChange={(e) => setTargetLanguage(e.target.value)}
        className="w-full px-3 py-2 bg-gray-100 border-0 rounded-lg text-sm font-medium focus:ring-2 focus:ring-blue-500"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}
