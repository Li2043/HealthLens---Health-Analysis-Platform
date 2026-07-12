import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { AnalysisMode } from "../types/analysis";

const STORAGE_KEY = "healthlens_analysis_mode";

type AnalysisModeContextValue = {
  mode: AnalysisMode;
  setMode: (mode: AnalysisMode) => void;
  toggleMode: () => void;
};

const AnalysisModeContext = createContext<AnalysisModeContextValue | null>(null);

function readStoredMode(): AnalysisMode {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "mock") {
    return "mock";
  }
  return "ai";
}

export function AnalysisModeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<AnalysisMode>(readStoredMode);

  const setMode = useCallback((next: AnalysisMode) => {
    setModeState(next);
    localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const toggleMode = useCallback(() => {
    setMode(mode === "mock" ? "ai" : "mock");
  }, [mode, setMode]);

  const value = useMemo(
    () => ({
      mode,
      setMode,
      toggleMode,
    }),
    [mode, setMode, toggleMode],
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
