import { isAxiosError } from "axios";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { clearAnalyses, listAnalyses } from "../api/analysisApi";
import { useUiLanguage } from "../i18n/UiLanguageContext";
import type { AnalysisSummary } from "../types/analysis";

function getErrorMessage(error: unknown, fallback: string): string | null {
  if (isAxiosError(error)) {
    if (error.response?.status === 401) {
      return null;
    }
    const message = error.response?.data?.message;
    if (typeof message === "string" && message.length > 0) {
      return message;
    }
    if (error.code === "ERR_NETWORK") {
      return "Cannot reach the API. Check that the backend is running.";
    }
  }
  return fallback;
}

function formatDate(value: string, language: string): string {
  return new Date(value).toLocaleString(language === "zh" ? "zh-CN" : "en-GB");
}

export function HistoryPage() {
  const { language, ui } = useUiLanguage();
  const historyUi = ui.history;
  const riskLabels = ui.analysis.riskLabels;

  const [items, setItems] = useState<AnalysisSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await listAnalyses();
      setItems(data);
    } catch (err) {
      setError(getErrorMessage(err, historyUi.failed));
    } finally {
      setLoading(false);
    }
  }, [historyUi.failed]);

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  async function handleClearHistory() {
    if (!window.confirm(historyUi.clearConfirm)) {
      return;
    }

    setClearing(true);
    setError(null);
    setNotice(null);

    try {
      await clearAnalyses();
      setItems([]);
      setNotice(historyUi.cleared);
    } catch (err) {
      setError(getErrorMessage(err, historyUi.clearFailed));
    } finally {
      setClearing(false);
    }
  }

  return (
    <section className="history-page">
      <div className="history-page-header">
        <div>
          <h1>{historyUi.title}</h1>
          <p className="page-intro">{historyUi.intro}</p>
        </div>
        {!loading && items.length > 0 && (
          <button
            type="button"
            className="secondary-button history-clear-button"
            onClick={() => void handleClearHistory()}
            disabled={clearing}
          >
            {clearing ? historyUi.clearing : historyUi.clearAll}
          </button>
        )}
      </div>

      {loading && <p className="loading-banner">{historyUi.loading}</p>}
      {notice && <p className="saved-banner">{notice}</p>}
      {error && (
        <p className="error-banner" role="alert">
          {error}
        </p>
      )}

      {!loading && !error && items.length === 0 && <p>{historyUi.empty}</p>}

      {!loading && !error && items.length > 0 && (
        <ul className="history-list">
          {items.map((item) => (
            <li key={item.id} className="history-item">
              <div className="history-item-header">
                <span className={`risk-badge risk-${item.riskLevel}`}>
                  {riskLabels[item.riskLevel as keyof typeof riskLabels] ?? item.riskLevel}
                </span>
                <span className="history-date">{formatDate(item.createdAt, language)}</span>
              </div>
              <p className="history-snippet">
                {item.inputText.length > 120
                  ? `${item.inputText.slice(0, 120)}…`
                  : item.inputText}
              </p>
              <Link to={`/history/${item.id}`}>{historyUi.viewDetails}</Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
