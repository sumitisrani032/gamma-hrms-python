from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health Check")
def health_check():
    """
    Check the health status of the python backend module.
    """
    return {"status": "ok", "message": "Python backend service is running and healthy"}
