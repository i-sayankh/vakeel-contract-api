from fastapi import APIRouter, HTTPException, status
from config import GEMINI_API_KEY
from database import contracts_collection, analysis_collection
from service.gemini_analysis import analyze_contract
from models import AnalysisResult

analysis_router = APIRouter(prefix="/analysis", tags=["Analysis"])


@analysis_router.post("/analyse/{contract_id}")
async def analyse_contract(contract_id: str):
    """
    Analyse a contract using AI and return insights
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key isn't configured!",
        )

    contract = contracts_collection.find_one({"id": contract_id})
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
        )

    if not contract.get("text_content"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract has no text content for analysis",
        )

    contracts_collection.update_one(
        {"id": contract_id}, {"$set": {"analysis_status": "in_progress"}}
    )

    result = await analyze_contract(contract_id, contract["text_content"])

    doc = result.model_dump()
    insert_result = analysis_collection.insert_one(doc)
    result.id = str(insert_result.inserted_id)
    analysis_collection.update_one(
        {"_id": insert_result.inserted_id}, {"$set": {"id": result.id}}
    )

    contracts_collection.update_one(
        {"id": contract_id}, {"$set": {"analysis_status": "completed"}}
    )

    return {
        "message": "Contract analyzed successfully",
        "analysis": result.model_dump(),
        "id": result.id,
    }


@analysis_router.get("/{analysis_id}")
def get_analysis(analysis_id: str):
    """
    Retrieve the results of a specific analysis by ID.
    """
    doc = analysis_collection.find_one({"id": analysis_id})

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found"
        )

    analysis = AnalysisResult(**doc)

    return {"analysis": analysis.model_dump()}


@analysis_router.get("/")
def list_analyses():
    """
    List all analyses performed.
    """

    def _convert_obj(obj):
        # recursively convert ObjectId to str for JSON serialization
        if isinstance(obj, list):
            return [_convert_obj(v) for v in obj]
        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                if k == "_id":
                    new["id"] = str(v)
                else:
                    new[k] = _convert_obj(v)
            return new
        try:
            from bson import ObjectId

            if isinstance(obj, ObjectId):
                return str(obj)
        except Exception:
            pass
        return obj

    analyses = [_convert_obj(doc) for doc in analysis_collection.find({})]
    return {"analyses": analyses}


@analysis_router.get("/contract/{contract_id}")
async def get_analyses_for_contract(contract_id: str):
    """Get all analyses for a specific contract."""
    analyses = []
    cursor = analysis_collection.find({"contract_id": contract_id})

    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        analyses.append(doc)

    return {"analyses": analyses, "total": len(analyses)}