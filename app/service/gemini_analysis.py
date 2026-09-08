import httpx
import json
from config import GEMINI_API_KEY
from service.prompt import CONTRACT_ANALYSIS_PROMPT
from models import AnalysisResult, ClauseAnalysis, RiskFlag

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"


async def analyze_contract(contract_id: str, text_content: str):
    prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text=text_content[:15000])

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 4096,
                },
            },
            timeout=60.0,
        )

        response.raise_for_status()
        data = response.json()

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

        raw_text = raw_text.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        analysis_data = json.loads(raw_text)

        key_clauses = [
            ClauseAnalysis(**clause) for clause in analysis_data.get("key_clauses", [])
        ]

        risk_flags = [RiskFlag(**risk) for risk in analysis_data.get("risk_flags", [])]

        result = AnalysisResult(
            contract_id=contract_id,
            summary=analysis_data.get("summary", ""),
            contract_type=analysis_data.get("contract_type", "Unknown"),
            key_clauses=key_clauses,
            risk_flags=risk_flags,
            overall_risk_level=analysis_data.get("overall_risk_level", "low"),
            recommendations=analysis_data.get("recommendations", []),
        )

        return result
