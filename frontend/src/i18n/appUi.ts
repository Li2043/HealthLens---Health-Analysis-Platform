import type { Language, RiskLevel, TriageTier } from "../types/analysis";

export type AnalysisUiCopy = {
  pageTitle: string;
  pageIntro: string;
  healthNote: string;
  placeholder: string;
  analysisModeLabel: string;
  modeMock: string;
  modeOpenAi: string;
  modeDeepSeek: string;
  modeMockHint: string;
  modeOpenAiHint: string;
  modeDeepSeekHint: string;
  modeMockConfirmTitle: string;
  modeMockConfirmMessage: string;
  modeMockConfirmOk: string;
  modeMockConfirmCancel: string;
  openaiRegionNotice: string;
  openaiRegionLinkLabel: string;
  useSample: string;
  analyse: string;
  analysing: string;
  loading: string;
  saved: string;
  viewInHistory: string;
  emptyInput: string;
  analysisFailed: string;
  dailyLimitExceeded: string;
  dailyQuotaFooter: string;
  timeout: string;
  possibleEmergency: string;
  triage: string;
  vitalsRisk: string;
  emergencyOverrideNote: string;
  ruleSafetyOverrideNote: string;
  aiAdjudicationNote: string;
  providerLabel: string;
  explanation: string;
  detectedSignals: string;
  safetyCheck: string;
  safetyPassed: string;
  safetyFailed: string;
  riskLabels: Record<RiskLevel, string>;
  triageLabels: Record<TriageTier, string>;
};

export type AppUiCopy = {
  appName: string;
  languageLabel: string;
  nav: {
    analyse: string;
    history: string;
    login: string;
    register: string;
    logout: string;
  };
  login: {
    title: string;
    intro: string;
    email: string;
    password: string;
    submit: string;
    submitting: string;
    needAccount: string;
    registerLink: string;
    failed: string;
    demoNotice: string;
    demoFill: string;
    networkError: string;
    serverUnavailable: string;
  };
  register: {
    title: string;
    intro: string;
    email: string;
    password: string;
    submit: string;
    submitting: string;
    hasAccount: string;
    loginLink: string;
    failed: string;
    networkError: string;
    serverUnavailable: string;
  };
  analysis: AnalysisUiCopy;
  history: {
    title: string;
    intro: string;
    loading: string;
    failed: string;
    empty: string;
    viewDetails: string;
    clearAll: string;
    clearing: string;
    clearConfirm: string;
    clearFailed: string;
    cleared: string;
  };
  detail: {
    title: string;
    back: string;
    loading: string;
    savedAt: string;
  };
};

const EN: AppUiCopy = {
  appName: "HealthLens Platform",
  languageLabel: "Language",
  nav: {
    analyse: "Analyse",
    history: "History",
    login: "Login",
    register: "Register",
    logout: "Logout",
  },
  login: {
    title: "Login",
    intro: "Sign in to run health analysis workflows.",
    email: "Email",
    password: "Password",
    submit: "Login",
    submitting: "Signing in…",
    needAccount: "Need an account?",
    registerLink: "Register",
    failed: "Login failed. Please check your credentials.",
    demoNotice:
      "Demo account ({limit} analyses/day): {email} / {password}",
    demoFill: "Use demo account",
    networkError:
      "Cannot reach the API server. Open http://localhost:5173 and ensure Docker backend is running.",
    serverUnavailable: "Request timed out. The server may be starting — try again shortly.",
  },
  register: {
    title: "Register",
    intro: "Create an account to access analysis features.",
    email: "Email",
    password: "Password",
    submit: "Register",
    submitting: "Creating account…",
    hasAccount: "Already have an account?",
    loginLink: "Login",
    failed: "Registration failed. Please try again.",
    networkError:
      "Cannot reach the API server. Open http://localhost:5173 and ensure Docker backend is running.",
    serverUnavailable: "Request timed out. The server may be starting — try again shortly.",
  },
  analysis: {
    pageTitle: "Health Analysis",
    pageIntro:
      "Enter a short health note for a demo consultation workflow. This is not for clinical decision-making.",
    healthNote: "Health note",
    placeholder: "e.g. My heart rate is 100 and I cannot sleep.",
    analysisModeLabel: "Analysis mode",
    modeMock: "Mock",
    modeOpenAi: "OpenAI",
    modeDeepSeek: "DeepSeek",
    modeMockHint: "Rules only — less accurate; for testing and offline use.",
    modeOpenAiHint: "OpenAI adjudicates risk first; rules catch missed major risks.",
    modeDeepSeekHint: "DeepSeek adjudicates risk first; rules catch missed major risks.",
    modeMockConfirmTitle: "Switch to Mock mode?",
    modeMockConfirmMessage:
      "Mock mode uses rule-based matching only. Results are less accurate and are intended for testing and offline use. For real analysis, please use OpenAI or DeepSeek.",
    modeMockConfirmOk: "Switch to Mock",
    modeMockConfirmCancel: "Stay on current mode",
    openaiRegionNotice: "OpenAI may not be available in all regions.",
    openaiRegionLinkLabel: "OpenAI supported countries and regional availability",
    useSample: "Use sample",
    analyse: "Analyse",
    analysing: "Analysing…",
    loading: "Running analysis pipeline…",
    saved: "Analysis saved.",
    viewInHistory: "View in history",
    emptyInput: "Please enter your health note.",
    analysisFailed: "Analysis failed. Please try again.",
    dailyLimitExceeded:
      "Daily analysis limit reached (10 per day). Try again tomorrow.",
    dailyQuotaFooter: "Daily limit: {used} / {limit} analyses per account (resets at UTC midnight).",
    timeout: "Analysis timed out. Please try again.",
    possibleEmergency: "Possible emergency",
    triage: "Triage",
    vitalsRisk: "Risk",
    emergencyOverrideNote:
      "Emergency symptoms were detected. Risk and triage are both elevated.",
    ruleSafetyOverrideNote:
      "Rule safety net elevated risk above the AI assessment to catch a major risk the AI missed.",
    aiAdjudicationNote: "Risk adjudicated by AI with rule safety net.",
    providerLabel: "Provider",
    explanation: "What this may mean",
    detectedSignals: "Detected signals",
    safetyCheck: "Safety check",
    safetyPassed: "Passed",
    safetyFailed: "Failed",
    riskLabels: { low: "Low", moderate: "Moderate", high: "High", emergency: "Emergency" },
    triageLabels: {
      low: "Low",
      moderate: "Moderate",
      high: "High",
      emergency: "Emergency",
    },
  },
  history: {
    title: "Analysis History",
    intro: "Your saved consultation analyses.",
    loading: "Loading history…",
    failed: "Failed to load analysis history.",
    empty: "No saved analyses yet. Run one from the Analyse page.",
    viewDetails: "View details",
    clearAll: "Clear history",
    clearing: "Clearing…",
    clearConfirm: "Delete all saved analyses for your account? This cannot be undone.",
    clearFailed: "Failed to clear analysis history.",
    cleared: "History cleared.",
  },
  detail: {
    title: "Analysis Detail",
    back: "Back to history",
    loading: "Loading analysis…",
    savedAt: "Saved",
  },
};

const ZH: AppUiCopy = {
  appName: "HealthLens 平台",
  languageLabel: "语言",
  nav: {
    analyse: "分析",
    history: "历史",
    login: "登录",
    register: "注册",
    logout: "退出",
  },
  login: {
    title: "登录",
    intro: "登录后即可使用健康分析工作流。",
    email: "邮箱",
    password: "密码",
    submit: "登录",
    submitting: "登录中…",
    needAccount: "还没有账号？",
    registerLink: "去注册",
    failed: "登录失败，请检查邮箱和密码。",
    demoNotice: "演示账号（每日 {limit} 次）：{email} / {password}",
    demoFill: "填入演示账号",
    networkError: "无法连接 API 服务器。请通过 http://localhost:5173 访问，并确认 Docker 后端已启动。",
    serverUnavailable: "请求超时，服务器可能仍在启动，请稍后重试。",
  },
  register: {
    title: "注册",
    intro: "创建账号以使用分析功能。",
    email: "邮箱",
    password: "密码",
    submit: "注册",
    submitting: "注册中…",
    hasAccount: "已有账号？",
    loginLink: "去登录",
    failed: "注册失败，请重试。",
    networkError: "无法连接 API 服务器。请通过 http://localhost:5173 访问，并确认 Docker 后端已启动。",
    serverUnavailable: "请求超时，服务器可能仍在启动，请稍后重试。",
  },
  analysis: {
    pageTitle: "健康分析",
    pageIntro: "输入简短健康描述，体验演示版问诊流程。本工具不用于临床决策。",
    healthNote: "健康描述",
    placeholder: "例如：心率 100，睡不着。",
    analysisModeLabel: "分析模式",
    modeMock: "Mock",
    modeOpenAi: "OpenAI",
    modeDeepSeek: "DeepSeek",
    modeMockHint: "仅规则匹配，准确性较低，仅供测试与离线使用。",
    modeOpenAiHint: "OpenAI 先裁定风险；规则安全网弥补 AI 遗漏的重大风险。",
    modeDeepSeekHint: "DeepSeek 先裁定风险；规则安全网弥补 AI 遗漏的重大风险。",
    modeMockConfirmTitle: "切换到 Mock 模式？",
    modeMockConfirmMessage:
      "Mock 模式仅使用规则匹配，结果准确性较低，仅供测试和离线演示。正式分析请使用 OpenAI 或 DeepSeek。",
    modeMockConfirmOk: "切换到 Mock",
    modeMockConfirmCancel: "保持当前模式",
    openaiRegionNotice: "OpenAI 可能在部分地区无法使用。",
    openaiRegionLinkLabel: "查看 OpenAI 支持的国家与地区说明",
    useSample: "使用示例",
    analyse: "开始分析",
    analysing: "分析中…",
    loading: "正在运行分析流程…",
    saved: "分析结果已保存。",
    viewInHistory: "查看历史记录",
    emptyInput: "请输入健康描述。",
    analysisFailed: "分析失败，请重试。",
    dailyLimitExceeded: "今日分析次数已达上限（每日 10 次），请明天再试。",
    dailyQuotaFooter: "每账户每日限额 {limit} 次分析（UTC 零点重置），今日已用 {used} / {limit} 次。",
    timeout: "分析超时，请重试。",
    possibleEmergency: "疑似紧急情况",
    triage: "分诊等级",
    vitalsRisk: "风险等级",
    emergencyOverrideNote: "检测到紧急症状，风险与分诊等级均已提升为紧急。",
    ruleSafetyOverrideNote:
      "规则安全网将风险提升至高于 AI 评估的等级，以弥补 AI 可能遗漏的重大风险。",
    aiAdjudicationNote: "风险由 AI 裁定，并由规则安全网复核。",
    providerLabel: "提供方",
    explanation: "情况说明",
    detectedSignals: "检测到的信号",
    safetyCheck: "安全校验",
    safetyPassed: "通过",
    safetyFailed: "未通过",
    riskLabels: { low: "低", moderate: "中", high: "高", emergency: "紧急" },
    triageLabels: {
      low: "低",
      moderate: "中",
      high: "高",
      emergency: "紧急",
    },
  },
  history: {
    title: "分析历史",
    intro: "你已保存的问诊分析记录。",
    loading: "加载历史中…",
    failed: "加载历史记录失败。",
    empty: "暂无分析记录，请先在分析页提交一次。",
    viewDetails: "查看详情",
    clearAll: "清空历史",
    clearing: "清空中…",
    clearConfirm: "确定删除你账号下的全部分析记录吗？此操作无法撤销。",
    clearFailed: "清空历史记录失败。",
    cleared: "历史记录已清空。",
  },
  detail: {
    title: "分析详情",
    back: "返回历史",
    loading: "加载分析中…",
    savedAt: "保存于",
  },
};

export function getAppUi(language: Language): AppUiCopy {
  return language === "zh" ? ZH : EN;
}

export function getAnalysisUi(language: Language): AnalysisUiCopy {
  return getAppUi(language).analysis;
}
