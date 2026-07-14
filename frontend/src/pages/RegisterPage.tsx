import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { getAuthErrorMessage } from "../api/authErrors";
import { useAuth } from "../auth/AuthContext";
import { useUiLanguage } from "../i18n/UiLanguageContext";

export function RegisterPage() {
  const { register, isAuthenticated } = useAuth();
  const { ui } = useUiLanguage();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/analyse" replace />;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await register(email.trim(), password);
      navigate("/analyse", { replace: true });
    } catch (err) {
      setError(getAuthErrorMessage(err, ui.register));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="auth-page">
      <h1>{ui.register.title}</h1>
      <p className="page-intro">{ui.register.intro}</p>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label className="field-label" htmlFor="register-email">
          {ui.register.email}
        </label>
        <input
          id="register-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          required
          disabled={loading}
        />

        <label className="field-label" htmlFor="register-password">
          {ui.register.password}
        </label>
        <input
          id="register-password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
          disabled={loading}
        />

        <button type="submit" disabled={loading}>
          {loading ? ui.register.submitting : ui.register.submit}
        </button>
      </form>

      {error && (
        <p className="error-banner" role="alert">
          {error}
        </p>
      )}

      <p>
        {ui.register.hasAccount}{" "}
        <Link to="/login">{ui.register.loginLink}</Link>
      </p>
    </section>
  );
}
