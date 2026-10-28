from fastapi import APIRouter, Depends, status
from app.api.deps import require_authenticated_user
from app.models.user import User
from app.schemas.ai import AIRiskPredictionRequest, AIRiskPredictionResponse
from app.services.ai_risk_service import AIRiskPredictionPipeline

router = APIRouter()


@router.post(
    "/risk/predict",
    response_model=AIRiskPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict disaster risk level and score using AI models",
)
def predict_disaster_risk(
    request: AIRiskPredictionRequest,
    current_user: User = Depends(require_authenticated_user),
):
    """
    Executes real-time inference using trained Random Forest or Gradient Boosting models.
    Returns predicted continuous risk score, categorical risk tier, actual model evaluation metrics,
    and simulated data transparency disclaimer.
    """
    prediction = AIRiskPredictionPipeline.predict_risk(request)
    return prediction
