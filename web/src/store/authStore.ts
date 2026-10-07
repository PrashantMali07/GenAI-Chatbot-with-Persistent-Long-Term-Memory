import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  userId: string | null;
  username: string | null;
  setAuth: (token: string, userId: string, username: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      userId: null,
      username: null,
      setAuth: (token, userId, username) => set({ token, userId, username }),
      logout: () => set({ token: null, userId: null, username: null }),
    }),
    {
      name: 'auth-storage', // saves to localStorage
    }
  )
);
