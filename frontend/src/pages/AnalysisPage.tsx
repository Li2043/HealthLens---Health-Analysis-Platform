import { Link } from "react-router-dom";
import { useState } from "react";
import { isAxiosError } from "axios";
import { useAnalysisMode } from "../analysis/AnalysisModeContext";
import { submitAnalysis } from "../api/analysisApi";
import { AnalysisResultPanel } from "../components/AnalysisResultPanel";
import { useUiLanguage } from "../i18n/UiLanguageContext";
import type { AnalysisDetail } from "../types/analysis";

const SAMPLE_TEXT = {
  en: "My heart rate is 100 and I cannot sleep.",
  zh: "心率100，睡不着，心情低落。",
} as const;

function getErrorMessage(error: unknown, fallback: string, timeout: string): string {
  if (isAxiosError(error)) {
    const message = error.response?.data?.message;
    if (typeof message === "string" && message.length > 0) {
      return message;
    }
    if (error.code === "ECONNABORTED") {
      return timeout;
    }
  }
  return fallback;
}

export function AnalysisPage() {
  const { language, ui } = useUiLanguage();
  const { mode } = useAnalysisMode();
  const analysisUi = ui.analysis;

  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [savedAnalysis, setSavedAnalysis] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!text.trim()) {
      setError(analysisUi.emptyInput);
      return;
    }

    setLoading(true);
    setError(null);
    setSavedAnalysis(null);

    try {
      const data = await submitAnalysis({ text: text.trim(), language, mode });
      setSavedAnalysis(data);
    } catch (err) {
      setError(
        getErrorMessage(err, analysisUi.analysisFailed, analysisUi.timeout),
      );
    } finally {
      setLoading(false);
    }
  }

  function fillSample() {
    setText(SAMPLE_TEXT[language]);
    setError(null);
  }

  return (
    <section className="analysis-page">
      <h1>{analysisUi.pageTitle}</h1>
      <p className="page-intro">{analysisUi.pageIntro}</p>

      <form className="analysis-form" onSubmit={handleSubmit}>
        <div className="analysis-mode-row">
          <div>
            <span className="field-label">{analysisUi.analysisModeLabel}</span>
            <p className="analysis-mode-hint">
              {mode === "ai" ? analysisUi.modeAiHint : analysisUi.modeMockHint}
            </p>
          </div>
        </div>

        <label className="field-label" htmlFor="health-note">
          {analysisUi.healthNote}
        </label>
        <textarea
          id="health-note"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder={analysisUi.placeholder}
          rows={6}
          disabled={loading}
        />

        <div className="form-row">
          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={fillSample}
              disabled={loading}
            >
              {analysisUi.useSample}
            </button>
            <button type="submit" disabled={loading || !text.trim()}>
              {loading ? analysisUi.analysing : analysisUi.analyse}
            </button>
          </div>
        </div>
      </form>

      {error && (
        <p className="error-banner" role="alert">
          {error}
        </p>
      )}

      {loading && <p className="loading-banner">{analysisUi.loading}</p>}

      {savedAnalysis && (
        <>
          <p className="saved-banner">
            {analysisUi.saved}{" "}
            <Link to={`/history/${savedAnalysis.id}`}>{analysisUi.viewInHistory}</Link>
          </p>
          <AnalysisResultPanel result={savedAnalysis.result} />
        </>
      )}
    </section>
  );
}
