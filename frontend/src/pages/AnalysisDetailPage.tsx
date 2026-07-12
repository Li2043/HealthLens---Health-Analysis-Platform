import { isAxiosError } from "axios";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getAnalysis } from "../api/analysisApi";
import { AnalysisResultPanel } from "../components/AnalysisResultPanel";
import { useUiLanguage } from "../i18n/UiLanguageContext";
import type { AnalysisDetail } from "../types/analysis";

function getErrorMessage(error: unknown, fallback: string): string {
  if (isAxiosError(error)) {
    const message = error.response?.data?.message;
    if (typeof message === "string" && message.length > 0) {
      return message;
    }
  }
  return fallback;
}

export function AnalysisDetailPage() {
  const { language, ui } = useUiLanguage();
  const detailUi = ui.detail;
  const analysisUi = ui.analysis;

  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<AnalysisDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError("Missing analysis id.");
      setLoading(false);
      return;
    }

    async function loadDetail(analysisId: string) {
      setLoading(true);
      setError(null);

      try {
        const data = await getAnalysis(analysisId);
        setDetail(data);
      } catch (err) {
        setError(getErrorMessage(err, analysisUi.analysisFailed));
      } finally {
        setLoading(false);
      }
    }

    void loadDetail(id);
  }, [id, analysisUi.analysisFailed]);

  return (
    <section className="history-detail-page">
      <p>
        <Link to="/history">{detailUi.back}</Link>
      </p>
      <h1>{detailUi.title}</h1>

      {loading && <p className="loading-banner">{detailUi.loading}</p>}
      {error && (
        <p className="error-banner" role="alert">
          {error}
        </p>
      )}

      {detail && (
        <>
          <p className="page-intro">
            {detailUi.savedAt}{" "}
            {new Date(detail.createdAt).toLocaleString(language === "zh" ? "zh-CN" : "en-GB")}
          </p>
          <div className="explanation-block">
            <h2>{analysisUi.healthNote}</h2>
            <p className="explanation-text">{detail.inputText}</p>
          </div>
          <AnalysisResultPanel result={detail.result} />
        </>
      )}
    </section>
  );
}
