import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { getAuthErrorMessage } from "../api/authErrors";
import { useAuth } from "../auth/AuthContext";
import { demoAccountConfig } from "../config/demoAccount";
import { useUiLanguage } from "../i18n/UiLanguageContext";

function formatDemoNotice(template: string): string {
  return template
    .replaceAll("{email}", demoAccountConfig.email)
    .replaceAll("{password}", demoAccountConfig.password)
    .replaceAll("{limit}", String(demoAccountConfig.dailyLimit));
}

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const { ui } = useUiLanguage();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as { from?: string } | null)?.from ?? "/analyse";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(email.trim(), password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(getAuthErrorMessage(err, ui.login));
    } finally {
      setLoading(false);
    }
  }

  function fillDemoAccount() {
    setEmail(demoAccountConfig.email);
    setPassword(demoAccountConfig.password);
    setError(null);
  }

  return (
    <section className="auth-page">
      <h1>{ui.login.title}</h1>
      <p className="page-intro">{ui.login.intro}</p>

      {demoAccountConfig.enabled && (
        <div className="demo-account-panel">
          <p>{formatDemoNotice(ui.login.demoNotice)}</p>
          <button
            type="button"
            className="secondary-button"
            onClick={fillDemoAccount}
            disabled={loading}
          >
            {ui.login.demoFill}
          </button>
        </div>
      )}

      <form className="auth-form" onSubmit={handleSubmit}>
        <label className="field-label" htmlFor="login-email">
          {ui.login.email}
        </label>
        <input
          id="login-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          required
          disabled={loading}
        />

        <label className="field-label" htmlFor="login-password">
          {ui.login.password}
        </label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
          disabled={loading}
        />

        <button type="submit" disabled={loading}>
          {loading ? ui.login.submitting : ui.login.submit}
        </button>
      </form>

      {error && (
        <p className="error-banner" role="alert">
          {error}
        </p>
      )}

      <p>
        {ui.login.needAccount}{" "}
        <Link to="/register">{ui.login.registerLink}</Link>
      </p>
    </section>
  );
}
