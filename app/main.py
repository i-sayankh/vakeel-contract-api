from fastapi import FastAPI
from database import init_db
from routes.contracts_router import contracts_router

app = FastAPI(
    title="Vakeel Contracts API",
    description="AI Powered contract analysis using Gemini API",
    version="0.0.1",
)


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    return {
        "app": "Vakeel Contract API",
        "version": "0.0.1",
        "endpoints": {
            "POST /contracts/upload": "Upload a PDF or TXT contract for analysis",
            "GET /contracts/": "Retrieve a list of all uploaded contracts",
            "GET /contracts/{id}": "Retrieve details of a specific contract by ID",
            "POST /analysis/analyse/{contract_id}": "Analyze a contract using AI and return insights",
            "GET /analysis/{analysis_id}": "Retrieve the results of a specific analysis by ID",
            "GET /analysis/contract/{contract_id}": "Retrieve a list of all analyses performed for a specific contract",
        },
    }


app.include_router(contracts_router)
