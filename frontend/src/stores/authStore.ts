import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  nativeLanguage: string;
  isPremium: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  targetLanguage: string;

  // Actions
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  setTargetLanguage: (language: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      targetLanguage: 'en',

      setAuth: (user, token) =>
        set({
          user,
          token,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        }),

      setTargetLanguage: (language) =>
        set({ targetLanguage: language }),
    }),
    {
      name: 'muse-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        targetLanguage: state.targetLanguage,
      }),
    }
  )
);
