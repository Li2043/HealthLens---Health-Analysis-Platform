import type { AnalysisResponse } from "../types/analysis";
import { isPaidAnalysisMode } from "../analysis/AnalysisModeContext";
import { useUiLanguage } from "../i18n/UiLanguageContext";

type AnalysisResultPanelProps = {
  result: AnalysisResponse;
};

export function AnalysisResultPanel({ result }: AnalysisResultPanelProps) {
  const { ui } = useUiLanguage();
  const analysisUi = ui.analysis;
  const { risk_result, escalation, explanation, safety_check, risk_adjudication } =
    result;
  const triageLabel =
    analysisUi.triageLabels[escalation.triage_tier] ?? escalation.triage_tier;
  const riskLabel =
    analysisUi.riskLabels[risk_result.risk_level] ?? risk_result.risk_level;

  return (
    <div className="analysis-result">
      {result.provider_warning && (
        <p className="provider-warning">{result.provider_warning}</p>
      )}

      <div className="result-provider-meta">
        <span className="provider-badge">
          {analysisUi.providerLabel}: {result.llm_provider}
        </span>
        {result.analysis_mode && (
          <span className="provider-badge">
            {analysisUi.analysisModeLabel}: {result.analysis_mode.toUpperCase()}
          </span>
        )}
      </div>

      {escalation.is_emergency && (
        <div className="escalation-banner emergency" role="alert">
          <strong>{analysisUi.possibleEmergency}</strong>
          <p>{escalation.recommended_action}</p>
        </div>
      )}

      <div className="result-meta">
        <span
          className={`triage-badge ${escalation.is_emergency ? "triage-emergency" : ""}`}
        >
          {analysisUi.triage}: {triageLabel}
        </span>
        <span className={`risk-badge risk-${risk_result.risk_level}`}>
          {analysisUi.vitalsRisk}: {riskLabel}
        </span>
      </div>

      {risk_adjudication?.mode && isPaidAnalysisMode(risk_adjudication.mode) && (
        <p className="adjudication-note">{analysisUi.aiAdjudicationNote}</p>
      )}

      {risk_adjudication?.rule_override_applied && risk_adjudication.override_reason && (
        <p className="emergency-override-note">
          {risk_adjudication.override_reason}
        </p>
      )}

      {!escalation.is_emergency && (
        <p className="escalation-action">{escalation.recommended_action}</p>
      )}

      <div className="explanation-block">
        <h2>{analysisUi.explanation}</h2>
        <p className="explanation-text">{explanation}</p>
      </div>

      {risk_result.flags.length > 0 && (
        <div className="flags-block">
          <h3>{analysisUi.detectedSignals}</h3>
          <ul>
            {risk_result.flags.map((flag) => (
              <li key={flag}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      <p className={`safety-note ${safety_check.passed ? "passed" : "failed"}`}>
        {analysisUi.safetyCheck}:{" "}
        {safety_check.passed ? analysisUi.safetyPassed : analysisUi.safetyFailed}
      </p>
    </div>
  );
}
