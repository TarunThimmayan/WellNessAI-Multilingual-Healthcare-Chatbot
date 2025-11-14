'use client';

const AUTH_TOKEN_KEY = 'health_companion_auth';
const AUTH_USER_KEY = 'health_companion_user';

export interface AuthUser {
  email: string;
  fullName: string;
  createdAt: string;
}

export function setAuth(user: AuthUser): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(AUTH_TOKEN_KEY, 'authenticated');
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
}

export function clearAuth(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(AUTH_TOKEN_KEY) === 'authenticated';
}

export function getAuthUser(): AuthUser | null {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(AUTH_USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr) as AuthUser;
  } catch {
    return null;
  }
}

