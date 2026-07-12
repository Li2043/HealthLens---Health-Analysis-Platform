export type HealthStatus = {
  status: string;
  service: string;
};

export type {
  AnalysisDetail,
  AnalysisMode,
  AnalysisRequest,
  AnalysisResponse,
  AnalysisSummary,
  Language,
  RiskAdjudication,
  RiskLevel,
  TriageTier,
} from "./analysis";

export type {
  AuthResponse,
  AuthUser,
  LoginRequest,
  RegisterRequest,
} from "./auth";
