import { BrowserRouter } from "react-router-dom";
import { AnalysisModeProvider } from "./analysis/AnalysisModeContext";
import { AuthProvider } from "./auth/AuthContext";
import { UiLanguageProvider } from "./i18n/UiLanguageContext";
import { AppRoutes } from "./routes/AppRoutes";

export default function App() {
  return (
    <BrowserRouter>
      <UiLanguageProvider>
        <AnalysisModeProvider>
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </AnalysisModeProvider>
      </UiLanguageProvider>
    </BrowserRouter>
  );
}
