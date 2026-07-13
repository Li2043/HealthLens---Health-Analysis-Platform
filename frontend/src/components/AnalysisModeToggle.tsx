import { useRef } from "react";
import {
  isPaidAnalysisMode,
  useAnalysisMode,
} from "../analysis/AnalysisModeContext";
import type { AnalysisMode } from "../types/analysis";
import { useUiLanguage } from "../i18n/UiLanguageContext";

const MODES: AnalysisMode[] = ["mock", "openai", "deepseek"];

export function AnalysisModeToggle() {
  const { mode, setMode } = useAnalysisMode();
  const { ui } = useUiLanguage();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const pendingModeRef = useRef<AnalysisMode>("mock");
  const analysisUi = ui.analysis;

  function openConfirmDialog() {
    const dialog = dialogRef.current;
    if (!dialog) {
      return;
    }
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
      return;
    }
    dialog.setAttribute("open", "");
  }

  function closeConfirmDialog() {
    dialogRef.current?.close();
  }

  function modeLabel(selected: AnalysisMode): string {
    if (selected === "mock") {
      return analysisUi.modeMock;
    }
    if (selected === "openai") {
      return analysisUi.modeOpenAi;
    }
    return analysisUi.modeDeepSeek;
  }

  function handleSelectChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const nextMode = event.target.value as AnalysisMode;
    if (nextMode === mode) {
      return;
    }
    if (nextMode === "mock" && isPaidAnalysisMode(mode)) {
      pendingModeRef.current = nextMode;
      openConfirmDialog();
      return;
    }
    setMode(nextMode);
  }

  function confirmMockMode() {
    setMode(pendingModeRef.current);
    closeConfirmDialog();
  }

  return (
    <>
      <label className="analysis-mode-select-label">
        <span className="analysis-mode-select-text">{analysisUi.analysisModeLabel}</span>
        <select
          className="analysis-mode-select"
          value={mode}
          aria-label={analysisUi.analysisModeLabel}
          onChange={handleSelectChange}
        >
          {MODES.map((option) => (
            <option key={option} value={option}>
              {modeLabel(option)}
            </option>
          ))}
        </select>
      </label>

      <dialog
        ref={dialogRef}
        className="mode-confirm-dialog"
        onCancel={closeConfirmDialog}
      >
        <h2>{analysisUi.modeMockConfirmTitle}</h2>
        <p>{analysisUi.modeMockConfirmMessage}</p>
        <div className="mode-confirm-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={closeConfirmDialog}
          >
            {analysisUi.modeMockConfirmCancel}
          </button>
          <button type="button" onClick={confirmMockMode}>
            {analysisUi.modeMockConfirmOk}
          </button>
        </div>
      </dialog>
    </>
  );
}
