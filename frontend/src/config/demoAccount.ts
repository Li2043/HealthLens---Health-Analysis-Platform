export const demoAccountConfig = {
  enabled: import.meta.env.VITE_DEMO_ACCOUNT_ENABLED !== "false",
  email: import.meta.env.VITE_DEMO_ACCOUNT_EMAIL ?? "demo@healthlens.demo",
  password: import.meta.env.VITE_DEMO_ACCOUNT_PASSWORD ?? "demo1234",
  dailyLimit: Number(import.meta.env.VITE_DEMO_ANALYSIS_DAILY_LIMIT ?? "20"),
};
