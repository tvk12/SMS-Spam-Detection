from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.model_loader import load_model, predict_sms
from app.database import log_prediction, update_feedback, get_stats, create_api_key, check_api_key_valid, get_recent_logs, get_daily_stats, clear_all_logs
import os

app = FastAPI(title="SMS Spam Detector")

# API Security
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key and check_api_key_valid(api_key):
        return api_key
    raise HTTPException(status_code=403, detail="Could not validate credentials")

# Initialize global variables for model
model = None
tokenizer = None
device = None

class SMSRequest(BaseModel):
    text: str

class FeedbackRequest(BaseModel):
    feedback: str

@app.on_event("startup")
async def startup_event():
    global model, tokenizer, device
    model, tokenizer, device = load_model()

@app.post("/auth/generate-key")
async def generate_api_key():
    """Generate a new API key."""
    try:
        new_key = create_api_key()
        return {"api_key": new_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict(request: SMSRequest, api_key: str = Depends(verify_api_key)):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        result = predict_sms(model, tokenizer, device, request.text)
        # Log to DB
        log_id = log_prediction(request.text, result)
        return {"prediction": result, "log_id": log_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback/{log_id}")
async def submit_feedback(log_id: int, request: FeedbackRequest):
    try:
        update_feedback(log_id, request.feedback)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_dashboard_stats():
    try:
        stats = get_stats()
        stats["recent_logs"] = get_recent_logs()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/history")
async def get_history():
    try:
        return get_daily_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/admin/logs")
async def clear_logs_endpoint(api_key: str = Depends(verify_api_key)):
    # In a real app, this would check for ADMIN role, not just any key.
    # For this demo, any valid key user can text "Reset".
    try:
        clear_all_logs()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (Frontend)
# We mount this last so it doesn't interfere with API routes
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
