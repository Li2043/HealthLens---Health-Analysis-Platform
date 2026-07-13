import type { AnalysisMode } from "../types/analysis";

export const STORAGE_KEY = "healthlens_analysis_mode";

const VALID_MODES = new Set<AnalysisMode>(["mock", "openai", "deepseek"]);

export function readStoredMode(storage: Storage = localStorage): AnalysisMode {
  const stored = storage.getItem(STORAGE_KEY);

  if (stored && VALID_MODES.has(stored as AnalysisMode)) {
    return stored as AnalysisMode;
  }

  if (stored === "ai") {
    storage.setItem(STORAGE_KEY, "deepseek");
    return "deepseek";
  }

  return "deepseek";
}

export function writeStoredMode(mode: AnalysisMode, storage: Storage = localStorage): void {
  storage.setItem(STORAGE_KEY, mode);
}
