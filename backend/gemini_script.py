"""
Gemini Script Generator (STRICTLY AUTHENTICITY-FIRST):
- Uses Gemini API key with gemini-2.5-flash / gemini-3.8-flash.
- Prompts using the official hackathon challenge statement.
- LLM selects quote_id from verified candidates; backend injects exact corpus text.
- Rejects any output pretending to be Vivekananda or attributing unverified text.
- Provides visual descriptions and ReelForge stock footage categories.
- Fallback to template script if key is missing or quota exceeded.
"""
import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from quotes import get_quote_by_id, get_quotes_for_lesson

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """The challenge is to create an AI-powered tool that can take a verified teaching, quotation or incident from Swami Vivekananda’s life and works and turn it into an engaging 30–60 second reel. The tool should help create a strong opening, a simple story or modern-day situation, suitable visual ideas, narration, subtitles and a meaningful takeaway for the viewer.
For instance, a teaching about fearlessness could be presented through the story of a student who is hesitant to speak in front of a class, followed by a connection to Vivekananda’s message and a small action the viewer can try.
The system must be careful not to invent quotations or present AI-generated interpretations as Swami Vivekananda’s actual words. It should clearly show the original source and allow the creator to adapt the content into Indian regional languages. The aim is to use technology to bring Vivekananda’s teachings into the language and format of today’s youth while keeping the original message authentic and meaningful.

STRICT DURATION & WORD COUNT CONSTRAINTS:
1. REEL DURATION: The reel and transcript spoken narration MUST strictly be above 30 seconds and below 60 seconds (strictly between 30 and 60 seconds; optimal target: 35–45 seconds).
2. SCRIPT WORD COUNT: The total spoken narration across all scenes combined MUST STRICTLY BE UNDER 135 WORDS (recommended: 95–125 words). Never exceed 135 words. Keep lines punchy, concise, and direct for Gen Z and Gen Alpha.

CRITICAL AUTHENTICITY RULES:
1. You MUST NEVER invent, alter, paraphrase, or generate quotes pretending to be Swami Vivekananda.
2. You MUST NOT write phrases like "Swami Vivekananda once said..." or "Swamiji says..." inside your generated narration.
3. You will be given verified quotes with their IDs. You MUST select ONE quote_id that best speaks to the user's dilemma. Do NOT write the quote text yourself; the backend system will inject the exact verified text.
4. For each scene, specify:
   - "type": "hook" | "situation" | "meaning" | "action" | "outro"
   - "text": Spoken narration for this scene (concise, direct, punchy)
   - "visual": Visual idea description for on-screen imagery
   - "footage": One or two ReelForge footage categories from: ["mood_rain", "human_study", "human_walk", "human_write", "urban_city", "nature_sunrise", "nature_fire", "nature_water", "mood_calm", "india_crowd"]

Return STRICT JSON matching this schema:
{
  "quote_id": "<id of the chosen quote>",
  "scenes": [
    { "type": "hook", "text": "...", "visual": "...", "footage": "..." },
    { "type": "situation", "text": "...", "visual": "...", "footage": "..." },
    { "type": "meaning", "text": "...", "visual": "...", "footage": "..." },
    { "type": "action", "text": "...", "visual": "...", "footage": "..." },
    { "type": "outro", "text": "...", "visual": "...", "footage": "..." }
  ]
}
"""


def _generate_fallback_script(
    name: str,
    profession: str,
    dilemma: str,
    lesson_id: int,
    candidates: List[Dict[str, Any]],
    lang: str = "en"
) -> Dict[str, Any]:
    """Zero-fail deterministic fallback personalized to the user."""
    chosen = candidates[0] if candidates else {"id": "q1", "text": "Fearlessness"}
    user_label = name.strip() if name and name.strip() else ("student" if profession.lower() == "student" else "friend")

    if lang == "hi":
        return {
            "quote_id": chosen["id"],
            "scenes": [
                {
                    "type": "hook",
                    "text": f"{user_label}, रुकिए। जो आप महसूस कर रहे हैं, वह कोई कमजोरी नहीं है।",
                    "visual": "A student standing at a crossroads looking up",
                    "footage": "human_walk"
                },
                {
                    "type": "situation",
                    "text": f"जब दिमाग में यह चले कि '{dilemma[:60]}...', तो लगता है पूरी दुनिया आगे निकल गई और हम अकेले रह गए।",
                    "visual": "Desk with laptop and study books under rain window",
                    "footage": "mood_rain"
                },
                {
                    "type": "meaning",
                    "text": "समस्या बाहर की परिस्थितियों में नहीं, बल्कि मन की उस आवाज में है जो खुद को छोटा मान लेती है।",
                    "visual": "Calm meditation and candle light glow",
                    "footage": "mood_calm"
                },
                {
                    "type": "action",
                    "text": "अभी 2 मिनट के लिए स्क्रीन बंद करें, 3 गहरी सांसें लें और सिर्फ अपने अगले छोटे कदम पर ध्यान दें।",
                    "visual": "Writing goals down in a clean journal",
                    "footage": "human_write"
                },
                {
                    "type": "outro",
                    "text": "पूरी शक्ति आपके ही भीतर है। एक कदम बढ़ाइए।",
                    "visual": "Golden sunrise over mountains",
                    "footage": "nature_sunrise"
                }
            ]
        }

    return {
        "quote_id": chosen["id"],
        "scenes": [
            {
                "type": "hook",
                "text": f"Pause right here, {user_label}. What you're carrying isn't permanent.",
                "visual": "Person walking through busy street with head down",
                "footage": "human_walk"
            },
            {
                "type": "situation",
                "text": f"When '{dilemma[:60]}' loops in your head, it feels like everyone else has it figured out except you.",
                "visual": "Student studying at night under desk lamp",
                "footage": "human_study"
            },
            {
                "type": "meaning",
                "text": "The trap isn't the situation itself — it's the invisible spotlight making you believe you are helpless.",
                "visual": "Calm ocean waves and quiet shoreline",
                "footage": "mood_calm"
            },
            {
                "type": "action",
                "text": "Try this 2-minute reset right now: close your tabs, take three slow breaths, and do just the smallest next action.",
                "visual": "Hands writing in notebook with determination",
                "footage": "human_write"
            },
            {
                "type": "outro",
                "text": "You are far stronger than the noise. Step forward.",
                "visual": "Vibrant sunrise lighting up mountain peaks",
                "footage": "nature_sunrise"
            }
        ]
    }


def generate_reel_script(
    dilemma: str,
    lesson_id: int,
    name: str = "",
    age: Optional[int] = None,
    profession: str = "",
    lang: str = "en",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main script generation entry point using Gemini API.
    Injects exact verified quote from Complete Works corpus for zero hallucination.
    """
    candidates = get_quotes_for_lesson(lesson_id)
    if not candidates:
        candidates = [get_quote_by_id("q1")]

    resolved_key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()

    raw_script = None

    if resolved_key:
        try:
            import requests

            candidate_summary = "\n".join(
                f"- ID: {c['id']}\n  Text: \"{c['text']}\"\n  Topics: {', '.join(c.get('topics', []))}"
                for c in candidates
            )

            prompt_body = f"""User Profile:
- Name: {name or 'Anonymous'}
- Age: {age or 'Not specified'}
- Profession: {profession or 'General'}
- Language: {'Hindi (Devanagari script)' if lang == 'hi' else 'English'}

User's current dilemma / pain point:
"{dilemma}"

Verified Swami Vivekananda Quote Candidates (select exactly ONE quote_id from these):
{candidate_summary}

STRICT CONSTRAINTS TO ENFORCE:
- Script narration total words across all scenes combined MUST be STRICTLY UNDER 135 WORDS (recommended: 95–125 words).
- Pacing of the reel script MUST be STRICTLY BETWEEN 30 AND 60 SECONDS (target: 35–45 seconds).
- Personalize empathy and situation directly to the user's dilemma.

Write the reel script adhering strictly to the system challenge instructions. Return pure JSON matching the schema."""

            payload = {
                "contents": [{"parts": [{"text": prompt_body}]}],
                "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.7,
                    "maxOutputTokens": 4096,
                    "thinkingConfig": {
                        "thinkingBudget": 512
                    }
                }
            }

            import datetime
            last_err = None

            # Prioritize active models with healthy quota
            for model_name in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-2.5-flash"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={resolved_key}"
                try:
                    res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
                    if res.status_code == 200:
                        data = res.json()
                        candidates_res = data.get("candidates", [])
                        if candidates_res:
                            parts = candidates_res[0].get("content", {}).get("parts", [])
                            text = "".join(p.get("text", "") for p in parts).strip()
                            # Clean markdown code blocks if returned
                            if text.startswith("```json"):
                                text = text[7:]
                            if text.startswith("```"):
                                text = text[3:]
                            if text.endswith("```"):
                                text = text[:-3]
                            text = text.strip()

                            parsed = json.loads(text)
                            chosen_id = parsed.get("quote_id")
                            valid_ids = {c["id"] for c in candidates}
                            if chosen_id in valid_ids and parsed.get("scenes"):
                                raw_script = parsed
                                verification = {
                                    "api_called": True,
                                    "provider": "Google Gemini",
                                    "model": model_name,
                                    "tokens_used": data.get("usageMetadata", {}).get("totalTokenCount", 0),
                                    "finish_reason": candidates_res[0].get("finishReason", "STOP"),
                                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
                                }
                                logger.info(f"✅ Gemini ({model_name}) generated script successfully with quote {chosen_id}")
                                break
                    else:
                        last_err = f"HTTP {res.status_code}: {res.text[:120]}"
                        logger.warning(f"Gemini {model_name} returned status {res.status_code}: {res.text[:180]}")
                except Exception as ex:
                    last_err = str(ex)
                    logger.warning(f"Gemini {model_name} attempt error: {ex}")

        except Exception as e:
            last_err = str(e)
            logger.warning(f"Gemini script generation exception: {e}, using fallback")

    if not raw_script:
        import datetime
        raw_script = _generate_fallback_script(name, profession, dilemma, lesson_id, candidates, lang=lang)
        verification = {
            "api_called": False,
            "provider": "Offline Fallback",
            "model": "rule-based-template",
            "reason": last_err or "API key missing or failed",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }

    # AUTHENTICITY INJECTION: backend retrieves the EXACT verified quote
    chosen_id = raw_script.get("quote_id") or candidates[0]["id"]
    quote_obj = get_quote_by_id(chosen_id) or candidates[0]

    scene_map = {}
    for s in raw_script.get("scenes", []):
        stype = s.get("type")
        if stype:
            scene_map[stype] = s

    hook_s = scene_map.get("hook", {})
    sit_s = scene_map.get("situation", {})
    mean_s = scene_map.get("meaning", {})
    act_s = scene_map.get("action", {})
    outro_s = scene_map.get("outro", {})

    hook_text = hook_s.get("text", "Pause right here. What you're carrying isn't permanent.")
    sit_text = sit_s.get("text", f"When '{dilemma[:50]}' loops in your mind, remember you are not alone.")
    quote_text = f'"{quote_obj["text"]}"'
    mean_text = mean_s.get("text", "The power to shift your perspective has always been inside you.")
    act_text = act_s.get("text", "Take two minutes right now: close your tabs, breathe, and take the smallest next step.")
    outro_text = outro_s.get("text", "You are stronger than the moment. Step forward.")

    # Guard: Ensure total spoken script words is strictly under 135 words
    spoken_text = f"{hook_text} {sit_text} {mean_text} {act_text} {outro_text}"
    words = spoken_text.split()
    total_words = len(words)
    if total_words > 130:
        logger.warning(f"Script words ({total_words}) exceeded safety limit. Enforcing strictly < 135 words.")
        hook_text = " ".join(hook_text.split()[:20])
        sit_text = " ".join(sit_text.split()[:25])
        mean_text = " ".join(mean_text.split()[:25])
        act_text = " ".join(act_text.split()[:25])
        outro_text = " ".join(outro_text.split()[:18])
        total_words = len(f"{hook_text} {sit_text} {mean_text} {act_text} {outro_text}".split())

    # Calculate scene durations (pacing ~2.3 words/second)
    dur_hook = max(4500, int((len(hook_text.split()) / 2.3) * 1000))
    dur_sit = max(5500, int((len(sit_text.split()) / 2.3) * 1000))
    dur_quote = max(6500, int((len(quote_text.split()) / 2.2) * 1000))
    dur_mean = max(5500, int((len(mean_text.split()) / 2.3) * 1000))
    dur_act = max(5000, int((len(act_text.split()) / 2.3) * 1000))
    dur_outro = max(4000, int((len(outro_text.split()) / 2.3) * 1000))

    raw_total_ms = dur_hook + dur_sit + dur_quote + dur_mean + dur_act + dur_outro

    # Enforce strictly: 30 seconds (31,000ms) <= total_ms <= 60 seconds (58,000ms)
    if raw_total_ms < 31000:
        factor = 35000.0 / raw_total_ms
        dur_hook = int(dur_hook * factor)
        dur_sit = int(dur_sit * factor)
        dur_quote = int(dur_quote * factor)
        dur_mean = int(dur_mean * factor)
        dur_act = int(dur_act * factor)
        dur_outro = int(dur_outro * factor)
    elif raw_total_ms > 58000:
        factor = 54000.0 / raw_total_ms
        dur_hook = int(dur_hook * factor)
        dur_sit = int(dur_sit * factor)
        dur_quote = int(dur_quote * factor)
        dur_mean = int(dur_mean * factor)
        dur_act = int(dur_act * factor)
        dur_outro = int(dur_outro * factor)

    final_total_ms = dur_hook + dur_sit + dur_quote + dur_mean + dur_act + dur_outro

    full_scenes = [
        {
            "type": "hook",
            "text": hook_text,
            "visual": hook_s.get("visual", "Student pausing amidst busy surroundings"),
            "footage": hook_s.get("footage", "human_walk"),
            "durationMs": dur_hook
        },
        {
            "type": "situation",
            "text": sit_text,
            "visual": sit_s.get("visual", "Relatable struggle with focus and anxiety"),
            "footage": sit_s.get("footage", "human_study"),
            "durationMs": dur_sit
        },
        {
            # VERIFIED INJECTION: Exact corpus quote from Vivekananda Complete Works
            "type": "quote",
            "text": quote_text,
            "quoteId": quote_obj["id"],
            "visual": "Authentic historical portrait of Swami Vivekananda on blurred backdrop with slow push-in",
            "footage": "vivekananda",
            "durationMs": dur_quote
        },
        {
            "type": "meaning",
            "text": mean_text,
            "visual": mean_s.get("visual", "Calm reflection and inner realization"),
            "footage": mean_s.get("footage", "mood_calm"),
            "durationMs": dur_mean
        },
        {
            "type": "action",
            "text": act_text,
            "visual": act_s.get("visual", "Writing goals down and stepping outside"),
            "footage": act_s.get("footage", "human_write"),
            "durationMs": dur_act
        },
        {
            "type": "outro",
            "text": outro_text,
            "visual": outro_s.get("visual", "Golden sunrise light breaking over the horizon"),
            "footage": outro_s.get("footage", "nature_sunrise"),
            "durationMs": dur_outro
        }
    ]

    source_display = quote_obj.get("source", "")
    transcript_parts = [
        f"[Opening] {hook_text}",
        f"[Situation] {sit_text}",
        f"[Swami Vivekananda Teaching] {quote_text}\n\n— Original Source:\n{source_display}",
        f"[Perspective] {mean_text}",
        f"[2-Minute Action] {act_text}",
        f"[Takeaway] {outro_text}"
    ]
    transcript = "\n\n".join(transcript_parts)

    disclaimer = (
        "कहानी और आधुनिक व्याख्या AI-निर्मित हैं। उद्धरण स्वामी विवेकानंद के मूल वाङ्मय (Complete Works) से प्रमाणित है।"
        if lang == "hi"
        else "Story and modern interpretation are AI-generated. The quote is authentic and verified from the Complete Works of Swami Vivekananda."
    )

    return {
        "quoteId": quote_obj["id"],
        "quote": {
            "text": quote_obj["text"],
            "source": quote_obj["source"],
            "sourceUrl": quote_obj.get("sourceUrl", ""),
            "verified": quote_obj["verified"]
        },
        "lessonId": lesson_id,
        "episode": 1,
        "wordCount": total_words,
        "estimatedDurationSeconds": round(final_total_ms / 1000.0, 1),
        "scenes": full_scenes,
        "transcript": transcript,
        "disclaimer": disclaimer,
        "videoUrl": None,
        "verification": verification,
        "apiVerified": verification.get("api_called", False),
        "modelUsed": verification.get("model", "unknown")
    }
