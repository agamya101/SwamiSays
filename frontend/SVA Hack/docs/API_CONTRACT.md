# API CONTRACT — Arise Backend Specification
This document outlines the contracts for all endpoints required by the Arise front-end.
The frontend connects via `src/lib/api.ts`.
When `VITE_USE_MOCK=false`, the client fetches from `VITE_API_BASE_URL`.

---

## 1. POST /api/reel (Core Generator)

Generates a tailored 30–60 second micro-reel response for a user crisis / distress query.

### Request Body
- Content-Type: `application/json`
```json
{
  "prompt": "I failed my semester test and I feel like an imposter",
  "lang": "en"
}
```
| Field | Type | Required | Description |
|---|---|---|---|
| `prompt` | `string` | Yes | User's distress/problem statement (min 10 chars, max 400 chars) |
| `lang` | `"en" \| "hi" \| "bn"` | Yes | Target language for hook, situation, meaning, action, outro |

### Response Body
- Content-Type: `application/json`
- Status: `200 OK`
```json
{
  "quoteId": "q3",
  "quote": {
    "text": "All power is within you; you can do anything and everything. Believe in that, do not believe that you are weak.",
    "source": "Complete Works of Swami Vivekananda, Vol 3, p. 284",
    "sourceUrl": "https://www.ramakrishnavivekananda.info/vivekananda/volume_3/lectures_from_colombo_to_almora/the_future_of_india.htm",
    "verified": true
  },
  "lessonId": 2,
  "episode": 2,
  "scenes": [
    {
      "type": "hook",
      "text": "Stop spiraling. Here is what is really happening with your test results:",
      "durationMs": 6500
    },
    {
      "type": "situation",
      "text": "When you pour weeks into preparation and the score sheet betrays you, your mind equates an outcome with your entire worth.",
      "durationMs": 7000
    },
    {
      "type": "quote",
      "text": "\"All power is within you; you can do anything and everything. Believe in that, do not believe that you are weak.\"",
      "durationMs": 8500,
      "quoteId": "q3"
    },
    {
      "type": "meaning",
      "text": "Swami Vivekananda cut through this illusion: you are not an exam score. The infinite reservoir of capability remains untouched.",
      "durationMs": 7500
    },
    {
      "type": "action",
      "text": "Take a sheet of paper. Write down three hard skills you gained during this semester, regardless of the test grade.",
      "durationMs": 7000
    },
    {
      "type": "outro",
      "text": "You have all the strength inside you. Take a breath and step forward.",
      "durationMs": 5500
    }
  ],
  "transcript": "Full text transcript of all scenes...",
  "disclaimer": "Story and interpretation are AI-generated. The quote in the gold card is authentic and verified.",
  "videoUrl": "https://cdn.example.com/videos/reel-123.mp4"
}
```

#### Field Notes
- `quoteId`: Identifier matching the verified quote library (`quotes.json`).
- `quote`: Must contain authentic Vivekananda quote with citation. Server MUST NOT let LLM fabricate quotes.
- `lessonId`: Integer 1–8 matching the 8 Life Lessons in Arise.
- `episode`: Integer 1–6 matching the nearest episode in that lesson.
- `scenes`: Array of 5–6 scenes (`hook`, `situation`, `quote`, `meaning`, `action`, `outro`). Sum of `durationMs` should be 30,000–60,000 ms.
- `videoUrl` (optional): If present, the front-end `ReelPlayer` will stream this video directly with native player controls while displaying transcript & sources.

---

## 2. GET /api/lessons (Optional / Phase 2)
Returns list of the 8 Lessons.

## 3. GET /api/episodes?lessonId=:id (Optional / Phase 2)
Returns episodes for a given lesson.

## 4. GET /api/quote/daily (Optional / Phase 2)
Returns the verified quote of the day.

---

## 5. Safety Protocol
If the user prompt triggers self-harm / crisis detection (`suicide`, `kill myself`, `end my life`, etc.), the client-side intercepts it directly and shows the national crisis helplines (Tele-MANAS `14416`, KIRAN `1800-599-0019`).
If received by the backend, the backend should return HTTP 400 with:
```json
{
  "error": "CRISIS_DETECTED",
  "message": "Crisis keywords detected. Please access emergency support.",
  "helpline": "14416 (Tele-MANAS)"
}
```
