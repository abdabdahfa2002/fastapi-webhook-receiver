
import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Webhook Receiver API")

# Render uses ephemeral storage for free instances. 
# Files will be deleted when the service restarts.
UPLOAD_DIRECTORY = "uploads"

@app.on_event("startup")
async def startup_event():
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.get("/", summary="Health Check Endpoint")
async def health_check():
    """
    التحقق من حالة السيرفر
    """
    return {"status": "online", "message": "Server is Online", "timestamp": datetime.now().isoformat()}

@app.post("/upload", summary="Data and File Upload Endpoint")
async def upload_data_and_file(info: str = Form(...), file: UploadFile = File(...)):
    """
    استقبال البيانات النصية والملفات وحفظها محلياً
    """
    try:
        # Generate a timestamp for the filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_without_ext, file_extension = os.path.splitext(file.filename)
        new_filename = f"{filename_without_ext}_{timestamp}{file_extension}"
        file_path = os.path.join(UPLOAD_DIRECTORY, new_filename)

        # Save the file locally in the uploads/ directory
        contents = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        # CRITICAL: Console logging for Render Dashboard visibility
        print(f"--- NEW WEBHOOK RECEIVED ---")
        print(f"TIMESTAMP: {datetime.now().isoformat()}")
        print(f"INFO FIELD: {info}")
        print(f"SAVED FILE: {new_filename}")
        print(f"FILE SIZE: {len(contents)} bytes")
        print(f"-----------------------------")

        return JSONResponse(status_code=200, content={
            "status": "success",
            "received_data": {
                "info": info,
                "original_filename": file.filename,
                "saved_as": new_filename,
                "size": len(contents)
            }
        })
    except Exception as e:
        print(f"ERROR: Failed to process upload - {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": f"Internal Server Error: {str(e)}"
        })

if __name__ == "__main__":
    # For local testing, use port 8000 or the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
