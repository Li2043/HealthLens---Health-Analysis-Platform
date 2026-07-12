import { useUiLanguage } from "../i18n/UiLanguageContext";

export function LanguageToggle() {
  const { language, setLanguage, ui } = useUiLanguage();

  function toggle() {
    setLanguage(language === "en" ? "zh" : "en");
  }

  return (
    <button
      type="button"
      className={`pill-toggle language-toggle ${language}`}
      role="switch"
      aria-checked={language === "zh"}
      aria-label={ui.languageLabel}
      onClick={toggle}
    >
      <span className="pill-toggle-slider" aria-hidden="true" />
      <span className={`pill-toggle-option ${language === "en" ? "active" : ""}`}>
        English
      </span>
      <span className={`pill-toggle-option ${language === "zh" ? "active" : ""}`}>
        中文
      </span>
    </button>
  );
}
