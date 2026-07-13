import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { AnalysisMode } from "../types/analysis";
import { readStoredMode, writeStoredMode } from "./analysisModeStorage";

type AnalysisModeContextValue = {
  mode: AnalysisMode;
  setMode: (mode: AnalysisMode) => void;
};

const AnalysisModeContext = createContext<AnalysisModeContextValue | null>(null);

export function AnalysisModeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<AnalysisMode>(readStoredMode);

  const setMode = useCallback((next: AnalysisMode) => {
    setModeState(next);
    writeStoredMode(next);
  }, []);

  const value = useMemo(
    () => ({
      mode,
      setMode,
    }),
    [mode, setMode],
  );

  return (
    <AnalysisModeContext.Provider value={value}>{children}</AnalysisModeContext.Provider>
  );
}

export function useAnalysisMode(): AnalysisModeContextValue {
  const context = useContext(AnalysisModeContext);
  if (!context) {
    throw new Error("useAnalysisMode must be used within AnalysisModeProvider");
  }
  return context;
}

export function isPaidAnalysisMode(mode: string): boolean {
  return mode === "openai" || mode === "deepseek" || mode === "ai";
}
