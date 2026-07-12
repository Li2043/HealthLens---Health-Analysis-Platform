"""Extensible LLM provider for explaining rule-based risk results."""

import os
import re
from abc import ABC, abstractmethod

from app.escalation import detect_emergency_patterns
from app.extraction_validator import blood_pressure_mentioned
from app.schemas import Language, RiskAdjudication, RiskLevel, RiskResult, StructuredHealthInput

SYSTEM_PROMPT = """You help users understand what their described health situation may mean in plain language.

You must:
- Speak directly to the user about their symptoms, vitals, mood, and sleep — not about software, workflows, or rule engines.
- NOT diagnose disease or name a specific medical condition as confirmed.
- NOT prescribe medication.
- ALWAYS end with a clear statement that this is not a medical diagnosis.
- Recommend professional medical advice when symptoms are concerning, unusual, persistent, worsening, or when risk is moderate or higher.
- Tailor the closing guidance to risk_level:
  - low: reassure the user there is no strong reason to worry right now, then suggest practical daily self-care improvements.
  - moderate: suggest possible non-diagnostic causes and practical self-care or monitoring steps; advise medical review if symptoms persist or worsen.
  - high or emergency: use a serious tone; for English use UK emergency number 999, for Chinese use 120; tell the user to call emergency services or go to A&E/急诊 now; include safe immediate first-step actions based on symptoms (e.g. rest, stop exertion, do not drive yourself) without prescribing medication.
- Use simple, calm plain text only. Do NOT use Markdown formatting.
- Base your explanation ONLY on the structured input, original user text, and risk flags provided.
- Do NOT mention missing blood pressure unless blood pressure was mentioned in the original user input.
"""

SYSTEM_PROMPT_ZH = """你用通俗易懂的语言，向用户说明其描述的健康情况可能意味着什么。

必须遵守：
- 直接围绕用户的症状、体征、情绪与睡眠进行说明，不要讨论软件、工作流、规则引擎或 AI 裁定过程。
- 不得确诊疾病，不得将某种疾病表述为已确认结论。
- 不得给出用药建议。
- 结尾必须明确说明这不是医疗诊断。
- 若症状令人担忧、异常、持续、加重，或风险为中高，应建议寻求专业医疗帮助。
- 根据 risk_level 调整结尾建议：
  - low：安慰用户目前不必过度担心，并给出可执行的日常改善建议。
  - moderate：说明可能原因（不作确诊），给出可尝试的应对与自我照护措施；若持续或加重应就医。
  - high 或 emergency：语气严肃；中文必须写明急救电话 120；英文必须写明英国急救电话 999；明确建议立即拨打急救电话或前往急诊，并给出安全的第一步措施（如停止活动、休息、不要自行驾车），不得给出用药建议。
- 仅使用简洁、平实的纯文本，不要使用 Markdown。
- 解释必须仅基于提供的原始输入、结构化输入和风险标志。
- 除非原始输入提及血压，否则不要提及缺失的血压数据。
- 必须使用简体中文回复。
"""

_FLAG_PLAIN_LANGUAGE = {
    "very_high_systolic_bp": "very high systolic blood pressure",
    "very_high_diastolic_bp": "very high diastolic blood pressure",
    "elevated_blood_pressure": "elevated blood pressure",
    "elevated_heart_rate": "an elevated heart rate",
    "very_elevated_heart_rate": "a very elevated heart rate",
    "borderline_heart_rate": "a borderline heart rate",
    "anxiety_or_stress_flag": "signs of anxiety or stress",
    "low_mood_flag": "a low mood",
    "poor_sleep": "poor sleep quality",
    "incomplete_measurement": "incomplete or ambiguous measurements",
    "emergency_symptoms": "emergency symptom patterns",
    "rule_safety_override": "rule safety net elevation",
    "ai_limited_signals": "limited quantified signals for AI assessment",
}

_FLAG_PLAIN_LANGUAGE_ZH = {
    "very_high_systolic_bp": "收缩压非常高",
    "very_high_diastolic_bp": "舒张压非常高",
    "elevated_blood_pressure": "血压升高",
    "elevated_heart_rate": "心率偏高",
    "very_elevated_heart_rate": "心率明显偏高",
    "borderline_heart_rate": "心率临界偏高",
    "anxiety_or_stress_flag": "焦虑或压力迹象",
    "low_mood_flag": "情绪低落",
    "poor_sleep": "睡眠质量不佳",
    "incomplete_measurement": "测量不完整或存在歧义",
    "emergency_symptoms": "紧急症状模式",
    "rule_safety_override": "规则安全网提升",
    "ai_limited_signals": "AI 可评估的量化信号有限",
}

_MOOD_ZH = {
    "anxious": "焦虑",
    "stressed": "压力",
    "low": "低落",
    "calm": "平静",
    "unknown": "未知",
}

_SLEEP_ZH = {"good": "良好", "poor": "不佳", "unknown": "未知"}

_META_FLAGS = frozenset({"rule_safety_override", "ai_limited_signals"})

_EMERGENCY_NUMBER = {"en": "999", "zh": "120"}

_FLAG_POSSIBLE_CAUSES_EN: dict[str, str] = {
    "elevated_heart_rate": "stress, anxiety, caffeine, dehydration, poor sleep, or recent exertion",
    "very_elevated_heart_rate": "acute stress, dehydration, infection, arrhythmia, or intense exertion",
    "borderline_heart_rate": "mild stress, caffeine, poor sleep, or being recently active",
    "elevated_blood_pressure": "stress, high salt intake, lack of sleep, anxiety, or temporary exertion",
    "very_high_systolic_bp": "severe hypertension, acute stress, or a need for urgent medical review",
    "very_high_diastolic_bp": "severe hypertension, acute stress, or a need for urgent medical review",
    "anxiety_or_stress_flag": "psychological stress, workload, poor sleep, or life pressures",
    "low_mood_flag": "stress, poor sleep, social pressures, or low energy from lifestyle factors",
    "poor_sleep": "stress, irregular routines, screen use before bed, caffeine, or anxiety",
    "emergency_symptoms": "a potentially urgent medical event that needs immediate assessment",
}

_FLAG_POSSIBLE_CAUSES_ZH: dict[str, str] = {
    "elevated_heart_rate": "压力、焦虑、咖啡因、脱水、睡眠不足或近期活动",
    "very_elevated_heart_rate": "急性压力、脱水、感染、心律异常或剧烈活动",
    "borderline_heart_rate": "轻度压力、咖啡因、睡眠不足或刚活动完",
    "elevated_blood_pressure": "压力、高盐饮食、睡眠不足、焦虑或短暂劳累",
    "very_high_systolic_bp": "严重高血压、急性压力或需要尽快医学评估",
    "very_high_diastolic_bp": "严重高血压、急性压力或需要尽快医学评估",
    "anxiety_or_stress_flag": "心理压力、工作负担、睡眠不足或生活压力",
    "low_mood_flag": "压力、睡眠不足、社交压力或生活方式导致的精力不足",
    "poor_sleep": "压力、作息紊乱、睡前使用屏幕、咖啡因或焦虑",
    "emergency_symptoms": "可能需要立即评估的紧急医疗情况",
}

_FLAG_DAILY_TIPS_EN: dict[str, str] = {
    "poor_sleep": "Keep a regular sleep schedule, limit screens for an hour before bed, and keep your bedroom cool and dark.",
    "anxiety_or_stress_flag": "Try slow breathing for a few minutes, reduce caffeine, and take short breaks during stressful periods.",
    "low_mood_flag": "Maintain regular meals, gentle daily movement, daylight exposure, and time with supportive people.",
    "elevated_heart_rate": "Rest, drink water, reduce caffeine, and recheck how you feel after calming down.",
    "borderline_heart_rate": "Rest briefly, hydrate, and avoid extra caffeine until you feel settled.",
    "elevated_blood_pressure": "Rest, reduce salty foods today, and avoid strenuous activity until you feel better.",
}

_FLAG_DAILY_TIPS_ZH: dict[str, str] = {
    "poor_sleep": "尽量固定作息时间，睡前一小时减少屏幕使用，并保持卧室凉爽、昏暗、安静。",
    "anxiety_or_stress_flag": "可尝试缓慢深呼吸几分钟，减少咖啡因，并在压力大时安排短暂休息。",
    "low_mood_flag": "保持规律饮食、适度活动、接触日光，并与支持你的人保持联系。",
    "elevated_heart_rate": "先休息并补充水分，减少咖啡因，平静后再次感受身体变化。",
    "borderline_heart_rate": "短暂休息、补充水分，在感觉平稳前避免额外咖啡因。",
    "elevated_blood_pressure": "先休息，今日减少高盐食物，并在感觉好转前避免剧烈活动。",
}

_FIRST_AID_EN: dict[str, str] = {
    "chest_pain": (
        "Stop activity and rest sitting down. Loosen tight clothing. Do not drive yourself. "
        "If the pain is severe, sudden, or comes with breathlessness, sweating, or nausea, call 999 immediately."
    ),
    "breathing_difficulty": (
        "Sit upright, stay as calm as possible, and take slow breaths. "
        "If breathing is severely difficult or worsening, call 999 immediately."
    ),
    "stroke_signs": (
        "Note the time symptoms began. Do not eat or drink. Call 999 immediately and wait for emergency help."
    ),
    "loss_of_consciousness": (
        "Check whether the person responds. Call 999 immediately. "
        "If trained, place them in the recovery position and stay with them."
    ),
    "severe_bleeding": (
        "Apply firm, direct pressure with a clean cloth. Call 999 immediately if bleeding is heavy or will not stop."
    ),
    "anaphylaxis": (
        "Help the person sit upright if breathing is difficult. Call 999 immediately. "
        "Use an adrenaline auto-injector only if one is available and you know how to use it."
    ),
    "seizure": (
        "Clear nearby hazards, protect the head, and do not restrain the person. "
        "After the seizure, place them on their side if possible and call 999 if it lasts more than five minutes or they do not recover."
    ),
    "suicidal_ideation": (
        "You do not have to face this alone. Call 999 if you are in immediate danger, "
        "or contact Samaritans on 116 123 for urgent emotional support in the UK."
    ),
}

_FIRST_AID_ZH: dict[str, str] = {
    "chest_pain": (
        "立即停止活动，坐下休息，松开紧身衣物，不要自行驾车。"
        "若疼痛剧烈、突发，或伴有气短、出汗、恶心，请立即拨打 120。"
    ),
    "breathing_difficulty": (
        "保持坐位或半坐位，尽量放松，缓慢呼吸。"
        "若呼吸困难明显或加重，请立即拨打 120。"
    ),
    "stroke_signs": (
        "记录症状开始时间，不要进食或饮水，立即拨打 120 并等待救援。"
    ),
    "loss_of_consciousness": (
        "判断是否有反应，立即拨打 120。"
        "若受过培训，可将患者置于复苏体位并持续陪伴。"
    ),
    "severe_bleeding": (
        "用干净敷料持续加压止血。若出血量大或止不住，立即拨打 120。"
    ),
    "anaphylaxis": (
        "若呼吸费力，尽量保持坐位。立即拨打 120。"
        "仅在身边有肾上腺素自动注射笔且会使用时可考虑使用。"
    ),
    "seizure": (
        "移开周围危险物，保护头部，不要强行约束。"
        "发作结束后尽量侧卧；若持续超过五分钟或意识未恢复，立即拨打 120。"
    ),
    "suicidal_ideation": (
        "你不必独自承受。若处于立即危险，请拨打 120；"
        "也可拨打心理危机干预热线 400-161-9995 寻求支持。"
    ),
}


class LLMService(ABC):
    @abstractmethod
    def generate_explanation(
        self,
        structured: StructuredHealthInput,
        risk: RiskResult,
        source_text: str = "",
        language: Language = "en",
        adjudication: RiskAdjudication | None = None,
    ) -> str:
        pass

    def explain(self, structured: StructuredHealthInput, risk: RiskResult) -> str:
        """Backward-compatible alias."""
        return self.generate_explanation(structured, risk)


def _strip_markdown(text: str) -> str:
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    cleaned = re.sub(r"\*(.*?)\*", r"\1", cleaned)
    cleaned = re.sub(r"`(.*?)`", r"\1", cleaned)
    cleaned = re.sub(r"^#+\s*", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()


def _format_flags_plain(flags: list[str], language: Language = "en") -> str:
    mapping = _FLAG_PLAIN_LANGUAGE_ZH if language == "zh" else _FLAG_PLAIN_LANGUAGE
    if not flags:
        return "无规则标志" if language == "zh" else "no rule-based flags"
    descriptions = [mapping.get(flag, flag.replace("_", " ")) for flag in flags]
    if language == "zh":
        if len(descriptions) == 1:
            return descriptions[0]
        return "、".join(descriptions[:-1]) + f"以及{descriptions[-1]}"
    if len(descriptions) == 1:
        return descriptions[0]
    return ", ".join(descriptions[:-1]) + f", and {descriptions[-1]}"


def _format_signals(
    structured: StructuredHealthInput, source_text: str, language: Language = "en"
) -> str:
    signals: list[str] = []
    if structured.heart_rate is not None:
        if language == "zh":
            signals.append(f"心率 {structured.heart_rate} 次/分")
        else:
            signals.append(f"heart rate of {structured.heart_rate} bpm")
    if blood_pressure_mentioned(source_text):
        if structured.systolic_bp is not None and structured.diastolic_bp is not None:
            if language == "zh":
                signals.append(f"血压 {structured.systolic_bp}/{structured.diastolic_bp}")
            else:
                signals.append(
                    f"blood pressure of {structured.systolic_bp}/{structured.diastolic_bp}"
                )
        elif structured.systolic_bp is not None:
            if language == "zh":
                signals.append(f"收缩压 {structured.systolic_bp}")
            else:
                signals.append(f"systolic blood pressure of {structured.systolic_bp}")
    if structured.mood:
        mood_label = (
            _MOOD_ZH.get(structured.mood, structured.mood)
            if language == "zh"
            else structured.mood
        )
        if language == "zh":
            signals.append(f"情绪为{mood_label}")
        else:
            signals.append(f"mood described as {mood_label}")
    if structured.sleep_quality:
        sleep_label = (
            _SLEEP_ZH.get(structured.sleep_quality, structured.sleep_quality)
            if language == "zh"
            else structured.sleep_quality
        )
        if language == "zh":
            signals.append(f"睡眠质量为{sleep_label}")
        else:
            signals.append(f"sleep quality described as {sleep_label}")
    if structured.symptoms:
        if language == "zh":
            signals.append(f"提及症状：{', '.join(structured.symptoms)}")
        else:
            signals.append(f"symptoms noted: {', '.join(structured.symptoms)}")
    if language == "zh":
        return "、".join(signals) if signals else "结构化信号有限"
    return ", ".join(signals) if signals else "limited structured signals"


def _trim_source_text(text: str, max_len: int = 120) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."


def _user_facing_flags(flags: list[str]) -> list[str]:
    return [flag for flag in flags if flag not in _META_FLAGS]


def _compose_health_observation(
    structured: StructuredHealthInput,
    source_text: str,
    language: Language,
) -> str:
    details = _format_signals(structured, source_text, language)
    snippet = _trim_source_text(source_text)

    if language == "zh":
        if details != "结构化信号有限":
            if snippet:
                return f"根据您的描述（“{snippet}”），我们注意到{details}。"
            return f"根据您的描述，我们注意到{details}。"
        if snippet:
            return f"根据您的描述：“{snippet}”。"
        return "根据您提供的信息，可分析的健康信号较为有限。"

    if details != "limited structured signals":
        if snippet:
            return f'From your description ("{snippet}"), we noted {details}.'
        return f"From your description, we noted {details}."
    if snippet:
        return f'From your description: "{snippet}".'
    return (
        "Based on the information provided, there are limited measurable "
        "health signals to interpret."
    )


def _compose_health_concerns(flags: list[str], language: Language) -> str | None:
    user_flags = _user_facing_flags(flags)
    if not user_flags:
        return None
    concerns = _format_flags_plain(user_flags, language)
    if language == "zh":
        return f"这些情况可能与{concerns}有关，值得继续留意。"
    return f"These patterns may be related to {concerns}, which are worth monitoring."


def _tips_for_flags(
    flags: list[str],
    tips_map: dict[str, str],
    language: Language,
) -> list[str]:
    user_flags = _user_facing_flags(flags)
    tips: list[str] = []
    seen: set[str] = set()
    for flag in user_flags:
        tip = tips_map.get(flag)
        if tip and tip not in seen:
            tips.append(tip)
            seen.add(tip)
    if tips:
        return tips
    if language == "zh":
        return [
            "保持规律作息、均衡饮食、适度活动和充足饮水，并持续观察身体变化。"
        ]
    return [
        "Keep regular sleep, balanced meals, light activity, good hydration, "
        "and continue monitoring how you feel."
    ]


def _possible_causes_for_flags(flags: list[str], language: Language) -> str:
    mapping = _FLAG_POSSIBLE_CAUSES_ZH if language == "zh" else _FLAG_POSSIBLE_CAUSES_EN
    user_flags = _user_facing_flags(flags)
    causes = [mapping[flag] for flag in user_flags if flag in mapping]
    if not causes:
        if language == "zh":
            return "压力、睡眠不足、脱水、劳累或暂时性生活方式因素。"
        return "stress, poor sleep, dehydration, fatigue, or temporary lifestyle factors."
    if language == "zh":
        if len(causes) == 1:
            return causes[0]
        return "、".join(causes[:-1]) + f"或{causes[-1]}"
    if len(causes) == 1:
        return causes[0]
    return ", ".join(causes[:-1]) + f", or {causes[-1]}"


def _first_aid_steps(source_text: str, language: Language) -> list[str]:
    patterns = detect_emergency_patterns(source_text)
    aid_map = _FIRST_AID_ZH if language == "zh" else _FIRST_AID_EN
    steps = [aid_map[pattern] for pattern in patterns if pattern in aid_map]
    if steps:
        return steps
    number = _EMERGENCY_NUMBER[language]
    if language == "zh":
        return [
            f"请立即拨打 120 或尽快前往最近急诊。"
            f"在等待救援时，停止剧烈活动，坐下或半卧休息，并保持冷静。"
        ]
    return [
        f"Call {number} now or go to the nearest A&E department without delay. "
        "While waiting for help, stop strenuous activity, rest sitting or semi-upright, "
        "and stay as calm as possible."
    ]


def _compose_low_risk_guidance(
    flags: list[str],
    language: Language,
) -> list[str]:
    if language == "zh":
        parts = [
            "目前来看，您不必过度担心，这更像需要留意而非紧急的情况。",
            "日常改善建议："
            + " ".join(_tips_for_flags(flags, _FLAG_DAILY_TIPS_ZH, language)),
        ]
    else:
        parts = [
            "Based on what you shared, there is no strong reason to worry right now; "
            "this looks more like something to monitor than an emergency.",
            "Daily self-care suggestions: "
            + " ".join(_tips_for_flags(flags, _FLAG_DAILY_TIPS_EN, language)),
        ]
    return parts


def _compose_moderate_risk_guidance(
    flags: list[str],
    language: Language,
) -> list[str]:
    causes = _possible_causes_for_flags(flags, language)
    if language == "zh":
        return [
            "这些情况需要重视，但通常不必立刻恐慌。",
            f"可能相关的原因包括：{causes}。",
            "建议应对措施：先休息并补充水分，减少咖啡因和酒精，记录症状变化；"
            "若 24–48 小时内未见好转、症状加重或影响日常生活，请尽快就医评估。",
        ]
    return [
        "These findings deserve attention, but they do not usually mean you should panic.",
        f"Possible contributing factors may include: {causes}.",
        "Suggested next steps: rest, hydrate, reduce caffeine and alcohol, and track how "
        "symptoms change; if there is no improvement within 24–48 hours, symptoms worsen, "
        "or daily life is affected, seek medical review promptly.",
    ]


def _compose_high_risk_guidance(
    source_text: str,
    language: Language,
) -> list[str]:
    number = _EMERGENCY_NUMBER[language]
    first_aid = _first_aid_steps(source_text, language)
    if language == "zh":
        parts = [
            "需要严肃对待：当前信息提示较高健康风险，请不要拖延就医。",
            f"请立即拨打急救电话 {number}，或尽快前往最近医院急诊。",
            "在等待或前往就医时，您可以先采取以下第一步措施：",
            " ".join(first_aid),
            "不要自行驾车前往医院，尽量让他人陪同或等待救护车。",
        ]
    else:
        parts = [
            "Please take this seriously: the information you shared suggests a higher level "
            "of health risk, and you should not delay getting help.",
            f"Call the UK emergency number {number} now, or go to the nearest A&E department immediately.",
            "While waiting for help, you can take these first steps:",
            " ".join(first_aid),
            "Do not drive yourself; ask someone to stay with you or wait for an ambulance.",
        ]
    return parts


def _compose_risk_level_guidance(
    risk_level: RiskLevel,
    flags: list[str],
    source_text: str,
    language: Language,
) -> list[str]:
    if risk_level == "low":
        return _compose_low_risk_guidance(flags, language)
    if risk_level == "moderate":
        return _compose_moderate_risk_guidance(flags, language)
    if risk_level in ("high", "emergency"):
        return _compose_high_risk_guidance(source_text, language)
    return []


def _compose_disclaimer(risk_level: RiskLevel, language: Language) -> str:
    if language == "zh":
        if risk_level in ("high", "emergency"):
            return "以上建议不能替代专业医疗判断。这不是医疗诊断。"
        return "若症状令人担忧、异常、持续或加重，请寻求专业医疗帮助。这不是医疗诊断。"
    if risk_level in ("high", "emergency"):
        return (
            "This guidance does not replace professional medical judgment. "
            "This is not a medical diagnosis."
        )
    return (
        "If your symptoms feel concerning, unusual, persistent, or worsening, "
        "please seek professional medical advice. This is not a medical diagnosis."
    )


def _compose_health_explanation(
    structured: StructuredHealthInput,
    risk: RiskResult,
    source_text: str,
    language: Language,
) -> str:
    parts: list[str] = [
        _compose_health_observation(structured, source_text, language),
    ]
    concerns = _compose_health_concerns(risk.flags, language)
    if concerns:
        parts.append(concerns)

    parts.extend(
        _compose_risk_level_guidance(
            risk.risk_level,
            risk.flags,
            source_text,
            language,
        )
    )

    if structured.extraction_notes and blood_pressure_mentioned(source_text):
        note = structured.extraction_notes.rstrip(".")
        parts.append(note + ("。" if language == "zh" else "."))

    parts.append(_compose_disclaimer(risk.risk_level, language))
    return _strip_markdown(" ".join(parts))


class MockLLMService(LLMService):
    """Deterministic mock provider for testing and default operation."""

    def generate_explanation(
        self,
        structured: StructuredHealthInput,
        risk: RiskResult,
        source_text: str = "",
        language: Language = "en",
        adjudication: RiskAdjudication | None = None,
    ) -> str:
        return _compose_health_explanation(structured, risk, source_text, language)


class OpenAILLMService(LLMService):
    """OpenAI Responses API provider. Falls back gracefully if SDK or key is missing."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate_explanation(
        self,
        structured: StructuredHealthInput,
        risk: RiskResult,
        source_text: str = "",
        language: Language = "en",
        adjudication: RiskAdjudication | None = None,
    ) -> str:
        if language == "zh":
            user_prompt = (
                f"原始用户输入：{source_text}\n"
                f"结构化输入：{structured.model_dump_json()}\n"
                f"风险结果：{risk.model_dump_json()}\n"
                f"风险等级：{risk.risk_level}\n"
                "请用简体中文，向用户说明其当前健康状况可能意味着什么。"
                "只写健康情况解读（症状、体征、情绪、睡眠及需留意之处），"
                "不要写急救电话、就医步骤或日常改善建议（这些会由系统另行补充）。"
                "不要描述系统如何工作。"
            )
            instructions = SYSTEM_PROMPT_ZH
        else:
            user_prompt = (
                f"Original user input: {source_text}\n"
                f"Structured input: {structured.model_dump_json()}\n"
                f"Risk result: {risk.model_dump_json()}\n"
                f"Risk level: {risk.risk_level}\n"
                "Explain what the user's health situation may mean. "
                "Write only the health interpretation (symptoms, vitals, mood, sleep, "
                "and what to watch for). Do not include emergency numbers, care steps, "
                "or daily self-care advice; those are appended separately. "
                "Do not describe how the system works."
            )
            instructions = SYSTEM_PROMPT

        client = self._get_client()
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=instructions,
            input=user_prompt,
        )
        llm_summary = _strip_markdown(response.output_text)
        parts = [llm_summary]
        parts.extend(
            _compose_risk_level_guidance(
                risk.risk_level,
                risk.flags,
                source_text,
                language,
            )
        )
        parts.append(_compose_disclaimer(risk.risk_level, language))
        return _strip_markdown(" ".join(parts))


def get_llm_service_for_mode(mode: str = "mock") -> LLMService:
    """Return LLM provider for explanation generation based on analysis mode."""
    if mode == "ai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                return OpenAILLMService(api_key=api_key)
            except Exception:
                return MockLLMService()
    return MockLLMService()


def get_llm_service() -> LLMService:
    """Return the configured LLM provider. Defaults to mock; falls back if OpenAI unavailable."""
    provider = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return MockLLMService()
        try:
            return OpenAILLMService(api_key=api_key)
        except Exception:
            return MockLLMService()

    return MockLLMService()


def get_llm_provider_name_for_mode(mode: str = "mock") -> str:
    if mode == "ai" and os.getenv("OPENAI_API_KEY"):
        return "openai"
    if mode == "ai":
        return "mock-ai"
    return get_llm_provider_name()


def get_llm_provider_name() -> str:
    """Return the active LLM provider label for API responses."""
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "mock"
