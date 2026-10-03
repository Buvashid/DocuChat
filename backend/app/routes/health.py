from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
	"""Report whether the API process is available."""

	return HealthResponse(
		status="ok",
		service=settings.app_name,
		version=settings.app_version,
	)
