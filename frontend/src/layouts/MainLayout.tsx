import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { LanguageToggle } from "../components/LanguageToggle";
import { useUiLanguage } from "../i18n/UiLanguageContext";

export function MainLayout() {
  const { isAuthenticated, user, logout } = useAuth();
  const { ui } = useUiLanguage();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <strong>{ui.appName}</strong>
        <div className="app-header-actions">
          <div className="app-header-toggles">
            <LanguageToggle />
          </div>
          <nav className="app-nav">
            {isAuthenticated && (
              <>
                <Link to="/analyse">{ui.nav.analyse}</Link>
                <Link to="/history">{ui.nav.history}</Link>
                <span className="nav-user">{user?.email}</span>
                <button type="button" className="nav-logout" onClick={handleLogout}>
                  {ui.nav.logout}
                </button>
              </>
            )}
            {!isAuthenticated && (
              <>
                <Link to="/login">{ui.nav.login}</Link>
                <Link to="/register">{ui.nav.register}</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
