import { Link } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";
import { isAxiosError } from "axios";
import { useAnalysisMode } from "../analysis/AnalysisModeContext";
import { fetchAnalysisQuota, submitAnalysis } from "../api/analysisApi";
import { AnalysisModeToggle } from "../components/AnalysisModeToggle";
import { AnalysisResultPanel } from "../components/AnalysisResultPanel";
import { useUiLanguage } from "../i18n/UiLanguageContext";
import type { AnalysisDetail, AnalysisQuota } from "../types/analysis";

const OPENAI_REGION_HELP_URL =
  "https://help.openai.com/en/articles/8660928-openai-api-supported-countries-and-territories";

const SAMPLE_TEXT = {
  en: "My heart rate is 100 and I cannot sleep.",
  zh: "心率100，睡不着，心情低落。",
} as const;

function getErrorMessage(
  error: unknown,
  fallback: string,
  timeout: string,
  dailyLimitExceeded: string,
): string {
  if (isAxiosError(error)) {
    const message = error.response?.data?.message;
    if (typeof message === "string" && message.length > 0) {
      return message;
    }
    if (error.response?.status === 429) {
      return dailyLimitExceeded;
    }
    if (error.code === "ECONNABORTED") {
      return timeout;
    }
  }
  return fallback;
}

function formatDailyQuotaFooter(
  template: string,
  quota: AnalysisQuota,
): string {
  return template
    .replaceAll("{used}", String(quota.usedToday))
    .replaceAll("{limit}", String(quota.dailyLimit));
}

export function AnalysisPage() {
  const { language, ui } = useUiLanguage();
  const { mode } = useAnalysisMode();
  const analysisUi = ui.analysis;

  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [savedAnalysis, setSavedAnalysis] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [quota, setQuota] = useState<AnalysisQuota | null>(null);

  const loadQuota = useCallback(async () => {
    try {
      const data = await fetchAnalysisQuota();
      setQuota(data);
    } catch {
      setQuota({ dailyLimit: 10, usedToday: 0, remainingToday: 10 });
    }
  }, []);

  useEffect(() => {
    void loadQuota();
  }, [loadQuota]);

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
      await loadQuota();
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          analysisUi.analysisFailed,
          analysisUi.timeout,
          analysisUi.dailyLimitExceeded,
        ),
      );
      if (isAxiosError(err) && err.response?.status === 429) {
        await loadQuota();
      }
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
      <p className="openai-region-notice">
        <span>{analysisUi.openaiRegionNotice}</span>
        <a
          href={OPENAI_REGION_HELP_URL}
          className="info-icon-link"
          target="_blank"
          rel="noopener noreferrer"
          title={analysisUi.openaiRegionLinkLabel}
          aria-label={analysisUi.openaiRegionLinkLabel}
        >
          i
        </a>
      </p>

      <div className="analysis-page-header">
        <h1>{analysisUi.pageTitle}</h1>
        <AnalysisModeToggle />
      </div>

      <p className="page-intro">{analysisUi.pageIntro}</p>
      <p className="analysis-mode-hint">
        {mode === "mock"
          ? analysisUi.modeMockHint
          : mode === "openai"
            ? analysisUi.modeOpenAiHint
            : analysisUi.modeDeepSeekHint}
      </p>

      <form className="analysis-form" onSubmit={handleSubmit}>
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

      {quota && (
        <p className="analysis-quota-footer">
          {formatDailyQuotaFooter(analysisUi.dailyQuotaFooter, quota)}
        </p>
      )}
    </section>
  );
}
