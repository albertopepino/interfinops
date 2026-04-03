import { create } from 'zustand';
import type { User, Role } from '@/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  role: Role | null;
  assignedSites: string[];
  setUser: (user: User) => void;
  clearUser: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  role: null,
  assignedSites: [],

  setUser: (user: User) =>
    set({
      user,
      isAuthenticated: true,
      role: user.role,
      assignedSites: user.assigned_site_ids ?? [],
    }),

  clearUser: () =>
    set({
      user: null,
      isAuthenticated: false,
      role: null,
      assignedSites: [],
    }),
}));
