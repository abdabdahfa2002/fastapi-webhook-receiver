
import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

UPLOAD_DIRECTORY = "uploads"

@app.on_event("startup")
async def startup_event():
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.get("/", summary="Health Check Endpoint")
async def health_check():
    return {"message": "Server is Online"}

@app.post("/upload", summary="Data and File Upload Endpoint")
async def upload_data_and_file(info: str = Form(...), file: UploadFile = File(...)):
    try:
        # Generate a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename_without_ext, file_extension = os.path.splitext(file.filename)
        new_filename = f"{filename_without_ext}_{timestamp}{file_extension}"
        file_path = os.path.join(UPLOAD_DIRECTORY, new_filename)

        # Save the file locally
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Log the info and filename to console
        print(f"Received Info: {info}")
        print(f"Saved File: {new_filename}")

        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Data and file received successfully",
            "info_received": info,
            "filename_saved": new_filename
        })
    except Exception as e:
        print(f"Error during upload: {e}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
