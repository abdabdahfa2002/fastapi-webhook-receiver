
import os
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# استيراد وحدة OOB Scheduler
from oob_scheduler import (
    initialize_interactsh,
    start_scheduler,
    stop_scheduler,
    get_oob_interactions,
    clear_oob_data,
    poll_oob_data
)

app = FastAPI(title="Webhook & OOB Receiver API")

# Render uses ephemeral storage for free instances. 
# Files will be deleted when the service restarts.
UPLOAD_DIRECTORY = "uploads"

@app.on_event("startup")
async def startup_event():
    """
    تهيئة التطبيق عند البدء
    """
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    
    # تهيئة عميل Interactsh
    print("[App] تهيئة عميل Interactsh...")
    if initialize_interactsh():
        print("[App] تم تهيئة Interactsh بنجاح")
        
        # بدء جدولة المهام
        print("[App] بدء جدولة سحب البيانات...")
        start_scheduler()
        print("[App] تم بدء جدولة المهام")
    else:
        print("[App] فشل تهيئة Interactsh - سيتم المتابعة بدونه")

@app.on_event("shutdown")
async def shutdown_event():
    """
    إيقاف التطبيق
    """
    print("[App] إيقاف جدولة المهام...")
    stop_scheduler()
    print("[App] تم إيقاف التطبيق")

@app.get("/", summary="Health Check Endpoint")
async def health_check():
    """
    التحقق من حالة السيرفر
    """
    return {
        "status": "online",
        "message": "Server is Online",
        "timestamp": datetime.now().isoformat(),
        "features": ["webhook_receiver", "oob_polling"]
    }

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

@app.get("/oob/status", summary="OOB Polling Status")
async def oob_status():
    """
    الحصول على حالة خدمة OOB Polling
    """
    interactions = get_oob_interactions()
    return JSONResponse(status_code=200, content={
        "status": "active",
        "total_interactions": len(interactions),
        "last_updated": datetime.now().isoformat(),
        "polling_interval": "60 seconds"
    })

@app.get("/oob/interactions", summary="Get OOB Interactions")
async def get_interactions(limit: int = 10):
    """
    الحصول على قائمة التفاعلات المحفوظة من Interactsh
    """
    interactions = get_oob_interactions()
    
    # إرجاع آخر N تفاعل
    recent_interactions = interactions[-limit:] if limit > 0 else interactions
    
    return JSONResponse(status_code=200, content={
        "status": "success",
        "total_count": len(interactions),
        "returned_count": len(recent_interactions),
        "interactions": recent_interactions
    })

@app.post("/oob/poll-now", summary="Trigger OOB Poll Immediately")
async def trigger_poll():
    """
    تشغيل سحب البيانات من Interactsh فوراً (بدلاً من الانتظار 60 ثانية)
    """
    try:
        print("[API] تم طلب سحب البيانات الفوري من Interactsh")
        poll_oob_data()
        
        interactions = get_oob_interactions()
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "OOB poll triggered successfully",
            "total_interactions": len(interactions),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"[API] خطأ في سحب البيانات: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

@app.delete("/oob/clear", summary="Clear OOB Data")
async def clear_interactions():
    """
    مسح جميع بيانات OOB المحفوظة
    """
    try:
        if clear_oob_data():
            return JSONResponse(status_code=200, content={
                "status": "success",
                "message": "OOB data cleared successfully",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return JSONResponse(status_code=500, content={
                "status": "error",
                "message": "Failed to clear OOB data"
            })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

@app.get("/api/info", summary="API Information")
async def api_info():
    """
    معلومات عن API والمسارات المتاحة
    """
    return JSONResponse(status_code=200, content={
        "api_name": "Webhook & OOB Receiver",
        "version": "2.0",
        "features": {
            "webhook_receiver": "استقبال البيانات والملفات من الأجهزة الخارجية",
            "oob_polling": "سحب البيانات من خدمة Interactsh كل 60 ثانية",
            "data_archiving": "أرشفة البيانات في مسار /uploads"
        },
        "endpoints": {
            "GET /": "فحص حالة السيرفر",
            "POST /upload": "رفع البيانات والملفات",
            "GET /oob/status": "حالة خدمة OOB",
            "GET /oob/interactions": "قائمة التفاعلات",
            "POST /oob/poll-now": "سحب البيانات فوراً",
            "DELETE /oob/clear": "مسح البيانات",
            "GET /api/info": "معلومات API"
        }
    })

if __name__ == "__main__":
    # For local testing, use port 8000 or the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
