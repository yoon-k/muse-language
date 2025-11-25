import { Link } from 'react-router-dom';
import {
  Flame,
  Trophy,
  Target,
  BookOpen,
  MessageCircle,
  Mic,
  ChevronRight,
  Clock,
  TrendingUp,
  Zap
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useLearningStore } from '../stores/learningStore';
import { useAuthStore } from '../stores/authStore';
import { cn } from '../lib/utils';

export function DashboardPage() {
  const { user, targetLanguage } = useAuthStore();
  const { streak, totalXp, dailyProgress, currentLevel, levelProgress } = useLearningStore();

  const languageNames: Record<string, string> = {
    en: 'English',
    ja: '日本語',
    zh: '中文',
    es: 'Español',
    fr: 'Français',
  };

  const quickActions = [
    {
      title: 'AI 대화',
      description: '튜터와 대화 연습',
      icon: MessageCircle,
      path: '/conversation',
      color: 'bg-blue-500',
    },
    {
      title: '레슨',
      description: '오늘의 레슨 시작',
      icon: BookOpen,
      path: '/lessons',
      color: 'bg-green-500',
    },
    {
      title: '발음 연습',
      description: '발음 평가 받기',
      icon: Mic,
      path: '/pronunciation',
      color: 'bg-purple-500',
    },
  ];

  const dailyChallenges = [
    { id: 1, title: '레슨 1개 완료', target: 1, current: 1, xp: 20, done: true },
    { id: 2, title: '단어 10개 복습', target: 10, current: 7, xp: 15, done: false },
    { id: 3, title: 'AI와 3회 대화', target: 3, current: 1, xp: 15, done: false },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          안녕하세요, {user?.name || 'Learner'}님! 👋
        </h1>
        <p className="text-gray-600 mt-1">
          오늘도 {languageNames[targetLanguage]} 학습을 시작해볼까요?
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={Flame}
          label="스트릭"
          value={`${streak.current}일`}
          color="text-orange-500"
          bgColor="bg-orange-50"
        />
        <StatCard
          icon={Trophy}
          label="총 XP"
          value={totalXp.toLocaleString()}
          color="text-yellow-500"
          bgColor="bg-yellow-50"
        />
        <StatCard
          icon={Zap}
          label="오늘 XP"
          value={dailyProgress.xpEarned.toString()}
          color="text-blue-500"
          bgColor="bg-blue-50"
        />
        <StatCard
          icon={Clock}
          label="오늘 학습"
          value={`${dailyProgress.studyMinutes}분`}
          color="text-green-500"
          bgColor="bg-green-50"
        />
      </div>

      {/* Level Progress */}
      <div className="bg-white rounded-2xl p-5 border border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div>
            <span className="text-sm text-gray-500">현재 레벨</span>
            <h3 className="text-xl font-bold text-gray-900">{currentLevel}</h3>
          </div>
          <div className="text-right">
            <span className="text-sm text-gray-500">다음 레벨까지</span>
            <p className="text-lg font-semibold text-gray-700">
              {(100 - levelProgress).toFixed(0)}% 남음
            </p>
          </div>
        </div>
        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${levelProgress}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-3">빠른 시작</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <Link
              key={action.path}
              to={action.path}
              className="bg-white rounded-2xl p-5 border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all group"
            >
              <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center mb-3', action.color)}>
                <action.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                {action.title}
              </h3>
              <p className="text-sm text-gray-500 mt-1">{action.description}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* Daily Challenges */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">오늘의 목표</h2>
          <span className="text-sm text-gray-500">
            {dailyChallenges.filter((c) => c.done).length}/{dailyChallenges.length} 완료
          </span>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 divide-y divide-gray-100">
          {dailyChallenges.map((challenge) => (
            <div
              key={challenge.id}
              className={cn(
                'p-4 flex items-center gap-4',
                challenge.done && 'bg-green-50'
              )}
            >
              <div
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center',
                  challenge.done ? 'bg-green-500' : 'bg-gray-100'
                )}
              >
                {challenge.done ? (
                  <span className="text-white">✓</span>
                ) : (
                  <Target className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <div className="flex-1">
                <p className={cn(
                  'font-medium',
                  challenge.done ? 'text-green-700' : 'text-gray-900'
                )}>
                  {challenge.title}
                </p>
                {!challenge.done && (
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${(challenge.current / challenge.target) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">
                      {challenge.current}/{challenge.target}
                    </span>
                  </div>
                )}
              </div>
              <div className="text-right">
                <span className={cn(
                  'text-sm font-medium',
                  challenge.done ? 'text-green-600' : 'text-gray-500'
                )}>
                  +{challenge.xp} XP
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Continue Learning */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">이어서 학습</h2>
          <Link to="/lessons" className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
            전체 보기 <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
              <BookOpen className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Past Simple Tense</h3>
              <p className="text-sm text-gray-500 mt-1">
                과거 시제로 경험 이야기하기
              </p>
              <div className="flex items-center gap-2 mt-2">
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full w-2/3" />
                </div>
                <span className="text-xs text-gray-500">66%</span>
              </div>
            </div>
            <Link
              to="/lessons/lesson_005"
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-xl hover:bg-blue-700 transition-colors"
            >
              계속하기
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
  bgColor,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  color: string;
  bgColor: string;
}) {
  return (
    <div className="bg-white rounded-2xl p-4 border border-gray-200">
      <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center mb-2', bgColor)}>
        <Icon className={cn('w-5 h-5', color)} />
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
}
