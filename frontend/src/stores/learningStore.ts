import { create } from 'zustand';

interface DailyProgress {
  studyMinutes: number;
  lessonsCompleted: number;
  wordsReviewed: number;
  xpEarned: number;
  dailyGoalProgress: number;
}

interface Streak {
  current: number;
  longest: number;
  isTodayComplete: boolean;
}

interface LearningState {
  // Progress
  currentLevel: string;
  levelProgress: number;
  totalXp: number;
  streak: Streak;
  dailyProgress: DailyProgress;

  // Session
  activeSessionId: string | null;
  sessionMessages: Message[];

  // Actions
  setProgress: (progress: Partial<LearningState>) => void;
  addXp: (amount: number) => void;
  startSession: (sessionId: string) => void;
  endSession: () => void;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  corrections?: Correction[];
  vocabulary?: VocabularyItem[];
  timestamp: Date;
}

interface Correction {
  original: string;
  corrected: string;
  explanation: string;
}

interface VocabularyItem {
  word: string;
  definition: string;
  example: string;
}

export const useLearningStore = create<LearningState>((set) => ({
  currentLevel: 'A1',
  levelProgress: 0,
  totalXp: 0,
  streak: {
    current: 0,
    longest: 0,
    isTodayComplete: false,
  },
  dailyProgress: {
    studyMinutes: 0,
    lessonsCompleted: 0,
    wordsReviewed: 0,
    xpEarned: 0,
    dailyGoalProgress: 0,
  },

  activeSessionId: null,
  sessionMessages: [],

  setProgress: (progress) =>
    set((state) => ({ ...state, ...progress })),

  addXp: (amount) =>
    set((state) => ({
      totalXp: state.totalXp + amount,
      dailyProgress: {
        ...state.dailyProgress,
        xpEarned: state.dailyProgress.xpEarned + amount,
      },
    })),

  startSession: (sessionId) =>
    set({ activeSessionId: sessionId, sessionMessages: [] }),

  endSession: () =>
    set({ activeSessionId: null }),

  addMessage: (message) =>
    set((state) => ({
      sessionMessages: [...state.sessionMessages, message],
    })),

  clearMessages: () =>
    set({ sessionMessages: [] }),
}));
