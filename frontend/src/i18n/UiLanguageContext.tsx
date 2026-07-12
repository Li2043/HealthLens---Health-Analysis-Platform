import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { Language } from "../types/analysis";
import { getAppUi } from "./appUi";

const STORAGE_KEY = "healthlens_ui_language";

type UiLanguageContextValue = {
  language: Language;
  setLanguage: (language: Language) => void;
  ui: ReturnType<typeof getAppUi>;
};

const UiLanguageContext = createContext<UiLanguageContextValue | null>(null);

function readStoredLanguage(): Language {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "zh" ? "zh" : "en";
}

export function UiLanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(readStoredLanguage);

  const setLanguage = useCallback((next: Language) => {
    setLanguageState(next);
    localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const value = useMemo<UiLanguageContextValue>(
    () => ({
      language,
      setLanguage,
      ui: getAppUi(language),
    }),
    [language, setLanguage],
  );

  return (
    <UiLanguageContext.Provider value={value}>{children}</UiLanguageContext.Provider>
  );
}

export function useUiLanguage(): UiLanguageContextValue {
  const context = useContext(UiLanguageContext);
  if (!context) {
    throw new Error("useUiLanguage must be used within UiLanguageProvider");
  }
  return context;
}
