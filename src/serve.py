from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os

app = FastAPI()

# Đọc tên bucket từ biến môi trường
GCS_BUCKET = os.environ.get("GCS_BUCKET", "YOUR_BUCKET_NAME")
GCS_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")

def download_model():
    """Tải file model.pkl từ AWS S3 về máy khi server khởi động."""
    print("Downloading model from S3...")
    s3 = boto3.client('s3')
    
    # Tạo thư mục chứa model nếu chưa có
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Tải file từ S3
    s3.download_file(GCS_BUCKET, GCS_MODEL_KEY, MODEL_PATH)
    print("Model downloaded successfully from S3!")

# Tải model khi khởi động
download_model()
model = joblib.load(MODEL_PATH)

class PredictRequest(BaseModel):
    features: list[float]

@app.get("/health")
def health():
    """Endpoint kiểm tra sức khỏe server."""
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    """Endpoint suy luận."""
    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")

    preds = model.predict([req.features])
    pred_val = int(preds[0])
    
    labels = {0: "thap", 1: "trung_binh", 2: "cao"}
    return {"prediction": pred_val, "label": labels.get(pred_val, "unknown")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
