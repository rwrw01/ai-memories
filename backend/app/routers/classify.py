from fastapi import APIRouter

from app.schemas.flow import ClassifyRequest, ClassifyResponse
from app.services.classify_service import classify

router = APIRouter()


@router.post("/api/classify", response_model=ClassifyResponse)
async def classify_endpoint(req: ClassifyRequest) -> ClassifyResponse:
    """Classify a Dutch transcription into an intent with parameters."""
    result = await classify(req.text)
    return ClassifyResponse(**result)
