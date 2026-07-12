import { useRef } from "react";
import { useAnalysisMode } from "../analysis/AnalysisModeContext";
import { useUiLanguage } from "../i18n/UiLanguageContext";

export function AnalysisModeToggle() {
  const { mode, setMode } = useAnalysisMode();
  const { ui } = useUiLanguage();
  const dialogRef = useRef<HTMLDialogElement>(null);
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

  function handleToggle() {
    if (mode === "ai") {
      openConfirmDialog();
      return;
    }
    setMode("ai");
  }

  function confirmMockMode() {
    setMode("mock");
    closeConfirmDialog();
  }

  return (
    <>
      <button
        type="button"
        className={`pill-toggle analysis-mode-toggle ${mode}`}
        role="switch"
        aria-checked={mode === "ai"}
        aria-label={analysisUi.analysisModeLabel}
        onClick={handleToggle}
      >
        <span className="pill-toggle-slider" aria-hidden="true" />
        <span className={`pill-toggle-option ${mode === "ai" ? "active" : ""}`}>
          {analysisUi.modeAi}
        </span>
        <span className={`pill-toggle-option ${mode === "mock" ? "active" : ""}`}>
          {analysisUi.modeMock}
        </span>
      </button>

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
