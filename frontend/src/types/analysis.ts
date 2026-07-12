export type Language = "en" | "zh";
export type AnalysisMode = "mock" | "ai";
export type RiskLevel = "low" | "moderate" | "high" | "emergency";
export type TriageTier = "low" | "moderate" | "high" | "emergency";

export type AnalysisRequest = {
  text: string;
  language: Language;
  mode: AnalysisMode;
};

export type RiskAdjudication = {
  mode: AnalysisMode;
  ai_risk_level?: RiskLevel;
  rule_risk_level: RiskLevel;
  final_risk_level: RiskLevel;
  adjudicated_by:
    | "rules"
    | "ai"
    | "ai_with_rule_override"
    | "ai_with_emergency_override";
  rule_override_applied: boolean;
  override_reason?: string;
};

export type RiskResult = {
  risk_level: RiskLevel;
  flags: string[];
  rule_explanation: string;
};

export type EscalationResult = {
  level: string;
  triage_tier: TriageTier;
  is_emergency: boolean;
  matched_patterns: string[];
  recommended_action: string;
};

export type SafetyCheck = {
  contains_disclaimer: boolean;
  contains_diagnostic_language: boolean;
  contains_medication_advice: boolean;
  passed: boolean;
};

export type AnalysisResponse = {
  structured_input: Record<string, unknown>;
  risk_result: RiskResult;
  escalation: EscalationResult;
  explanation: string;
  safety_check: SafetyCheck;
  extractor_provider: string;
  llm_provider: string;
  analysis_mode?: AnalysisMode;
  risk_adjudication?: RiskAdjudication;
  provider_warning?: string;
};

export type AnalysisSummary = {
  id: string;
  inputText: string;
  language: Language;
  riskLevel: RiskLevel;
  triageTier: TriageTier;
  createdAt: string;
};

export type AnalysisDetail = {
  id: string;
  inputText: string;
  language: Language;
  riskLevel: RiskLevel;
  triageTier: TriageTier;
  createdAt: string;
  result: AnalysisResponse;
};
