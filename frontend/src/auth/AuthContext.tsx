import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { login as loginRequest, register as registerRequest } from "../api/authApi";
import { registerUnauthorizedHandler } from "./sessionEvents";
import {
  clearAuthStorage,
  getStoredUser,
  getToken,
  setStoredUser,
  setToken,
} from "./tokenStorage";
import type { AuthUser } from "../types/auth";

type AuthContextValue = {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function readInitialAuth(): AuthUser | null {
  const token = getToken();
  const user = getStoredUser();
  if (!token || !user) {
    clearAuthStorage();
    return null;
  }
  return user;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(readInitialAuth);

  useEffect(() => {
    registerUnauthorizedHandler(() => {
      clearAuthStorage();
      setUser(null);
    });
    return () => registerUnauthorizedHandler(null);
  }, []);

  const persistAuth = useCallback((token: string, email: string, userId: string) => {
    setToken(token);
    const nextUser = { email, userId };
    setStoredUser(nextUser);
    setUser(nextUser);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await loginRequest({ email, password });
    persistAuth(response.token, response.email, response.userId);
  }, [persistAuth]);

  const register = useCallback(async (email: string, password: string) => {
    const response = await registerRequest({ email, password });
    persistAuth(response.token, response.email, response.userId);
  }, [persistAuth]);

  const logout = useCallback(() => {
    clearAuthStorage();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      login,
      register,
      logout,
    }),
    [user, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
