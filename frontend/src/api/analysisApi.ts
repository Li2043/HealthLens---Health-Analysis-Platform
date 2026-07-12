import type {
  AnalysisDetail,
  AnalysisRequest,
  AnalysisSummary,
} from "../types/analysis";
import { apiClient } from "./client";

export async function submitAnalysis(
  request: AnalysisRequest,
): Promise<AnalysisDetail> {
  const { data } = await apiClient.post<AnalysisDetail>("/analysis", request);
  return data;
}

export async function listAnalyses(): Promise<AnalysisSummary[]> {
  const { data } = await apiClient.get<AnalysisSummary[]>("/analysis");
  return data;
}

export async function clearAnalyses(): Promise<void> {
  await apiClient.delete("/analysis");
}

export async function getAnalysis(id: string): Promise<AnalysisDetail> {
  const { data } = await apiClient.get<AnalysisDetail>(`/analysis/${id}`);
  return data;
}
