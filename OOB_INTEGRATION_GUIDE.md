# دليل دمج Interactsh OOB Polling مع Webhook Receiver

## نظرة عامة على المشروع

تم تحديث تطبيق **Webhook Receiver** ليشمل ميزة جديدة قوية: **OOB (Out-of-Band) Data Polling** باستخدام خدمة Interactsh. التطبيق الآن يعمل على مستويين:

1. **Webhook Receiver:** استقبال البيانات والملفات من الأجهزة الخارجية
2. **OOB Polling:** سحب البيانات من خدمة Interactsh كل 60 ثانية تلقائياً

---

## المعمارية التقنية

### المكونات الرئيسية

| المكون | الوصف | الملف |
| :--- | :--- | :--- |
| **FastAPI Backend** | خادم الويب الرئيسي | `main.py` |
| **OOB Scheduler** | وحدة جدولة المهام والاتصال بـ Interactsh | `oob_scheduler.py` |
| **APScheduler** | مكتبة جدولة المهام في الخلفية | `requirements.txt` |
| **Requests** | مكتبة للاتصال بـ Interactsh API | `requirements.txt` |

### سير العمل

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │  Webhook Handler │          │  OOB Scheduler   │        │
│  │  (POST /upload)  │          │  (Background)    │        │
│  └────────┬─────────┘          └────────┬─────────┘        │
│           │                             │                  │
│           ▼                             ▼                  │
│      ┌─────────────┐            ┌──────────────┐          │
│      │ Local Files │            │ Interactsh   │          │
│      │ (uploads/)  │            │ API (Poll)   │          │
│      └─────────────┘            └──────────────┘          │
│           │                             │                  │
│           └─────────────┬───────────────┘                  │
│                         ▼                                   │
│                  ┌─────────────────┐                       │
│                  │ JSON Archive    │                       │
│                  │ (oob_interactions.json)                 │
│                  └─────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## المسارات (API Endpoints)

### 1. Webhook Endpoints

#### أ. فحص الحالة
```http
GET /
```

**الاستجابة:**
```json
{
  "status": "online",
  "message": "Server is Online",
  "timestamp": "2026-03-23T22:13:42.555474",
  "features": ["webhook_receiver", "oob_polling"]
}
```

#### ب. رفع البيانات والملفات
```http
POST /upload
Content-Type: multipart/form-data

info=معلومات النظام
file=@image.jpg
```

**الاستجابة:**
```json
{
  "status": "success",
  "received_data": {
    "info": "معلومات النظام",
    "original_filename": "image.jpg",
    "saved_as": "image_20260323_221342.jpg",
    "size": 12345
  }
}
```

---

### 2. OOB Polling Endpoints

#### أ. حالة خدمة OOB
```http
GET /oob/status
```

**الاستجابة:**
```json
{
  "status": "active",
  "total_interactions": 5,
  "last_updated": "2026-03-23T22:13:42.555474",
  "polling_interval": "60 seconds"
}
```

#### ب. الحصول على التفاعلات
```http
GET /oob/interactions?limit=10
```

**الاستجابة:**
```json
{
  "status": "success",
  "total_count": 5,
  "returned_count": 5,
  "interactions": [
    {
      "timestamp": "2026-03-23T22:13:42.555474",
      "protocol": "http",
      "remote_address": "192.168.1.100",
      "request": "GET /test HTTP/1.1",
      "response": "HTTP/1.1 200 OK"
    }
  ]
}
```

#### ج. سحب البيانات فوراً
```http
POST /oob/poll-now
```

**الاستجابة:**
```json
{
  "status": "success",
  "message": "OOB poll triggered successfully",
  "total_interactions": 6,
  "timestamp": "2026-03-23T22:13:42.555474"
}
```

#### د. مسح بيانات OOB
```http
DELETE /oob/clear
```

**الاستجابة:**
```json
{
  "status": "success",
  "message": "OOB data cleared successfully",
  "timestamp": "2026-03-23T22:13:42.555474"
}
```

---

### 3. معلومات API
```http
GET /api/info
```

**الاستجابة:**
```json
{
  "api_name": "Webhook & OOB Receiver",
  "version": "2.0",
  "features": {
    "webhook_receiver": "استقبال البيانات والملفات من الأجهزة الخارجية",
    "oob_polling": "سحب البيانات من خدمة Interactsh كل 60 ثانية",
    "data_archiving": "أرشفة البيانات في مسار /uploads"
  },
  "endpoints": { ... }
}
```

---

## كيفية الاستخدام

### 1. رفع البيانات عبر Webhook
```bash
curl -X POST "https://fastapi-webhook-receiver.onrender.com/upload" \
     -F "info=Device Status: OK, CPU: 45%, Memory: 60%" \
     -F "file=@system_report.txt"
```

### 2. الحصول على حالة OOB
```bash
curl https://fastapi-webhook-receiver.onrender.com/oob/status
```

### 3. استرجاع آخر 5 تفاعلات
```bash
curl "https://fastapi-webhook-receiver.onrender.com/oob/interactions?limit=5"
```

### 4. سحب البيانات فوراً
```bash
curl -X POST "https://fastapi-webhook-receiver.onrender.com/oob/poll-now"
```

---

## الملفات والمسارات

| المسار | الوصف |
| :--- | :--- |
| `/uploads/` | مجلد تخزين الملفات المرفوعة |
| `/uploads/oob_interactions.json` | ملف أرشيف بيانات OOB |
| `main.py` | التطبيق الرئيسي |
| `oob_scheduler.py` | وحدة جدولة المهام |
| `requirements.txt` | المكتبات المطلوبة |

---

## آلية عمل OOB Polling

### الخطوات:

1. **التهيئة (Startup):** عند بدء التطبيق، يتم إنشاء عميل Interactsh جديد
2. **الجدولة:** يتم بدء جدولة مهمة تعمل كل 60 ثانية
3. **السحب:** كل 60 ثانية، يتم استدعاء Interactsh API للحصول على التفاعلات الجديدة
4. **الأرشفة:** يتم حفظ البيانات في ملف JSON في مسار `/uploads/oob_interactions.json`
5. **التسجيل:** يتم طباعة البيانات في السجلات (Logs) في Render Dashboard

### مثال على السجلات:
```
[Scheduler] بدء سحب البيانات في 2026-03-23T22:13:42.555474
[Interactsh] تم استقبال 2 تفاعل جديد
[Interactsh] تفاعل جديد:
  - البروتوكول: http
  - العنوان البعيد: 192.168.1.100
[Storage] تم حفظ 7 تفاعل في uploads/oob_interactions.json
```

---

## المتطلبات والتثبيت

### المكتبات المطلوبة:
```
fastapi
uvicorn
python-multipart
apscheduler
requests
aiofiles
```

### التثبيت:
```bash
pip install -r requirements.txt
```

---

## النشر على Render.com

### الخطوات:

1. تأكد من أن جميع الملفات موجودة في المستودع على GitHub
2. ربط المستودع بـ Render.com
3. اختيار **Python** كـ Runtime
4. تعيين أوامر البناء والتشغيل:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## ملاحظات مهمة

### 1. التخزين المؤقت (Ephemeral Storage)
في الخطة المجانية لـ Render، الملفات تُحذف عند إعادة التشغيل. اعتمد على الـ **Logs** و **JSON Archive** للاحتفاظ بالبيانات.

### 2. جدولة المهام
- تعمل المهمة في الخلفية بدون التأثير على الطلبات الواردة
- يمكن تشغيل السحب فوراً عبر المسار `/oob/poll-now`

### 3. الأمان
- تأكد من تأمين المسارات الحساسة إذا كنت تستخدمها في الإنتاج
- استخدم متغيرات البيئة للبيانات الحساسة

---

## استكشاف الأخطاء

### المشكلة: لا توجد تفاعلات جديدة
**الحل:** تأكد من أن Interactsh API متاح وأن الاتصال بالإنترنت يعمل بشكل صحيح.

### المشكلة: الملفات تُحذف بعد إعادة التشغيل
**الحل:** هذا سلوك طبيعي في الخطة المجانية. استخدم قاعدة بيانات خارجية للتخزين الدائم.

### المشكلة: الجدولة لا تعمل
**الحل:** تحقق من سجلات Render Dashboard للأخطاء المتعلقة بـ APScheduler.

---

## الخلاصة

المشروع الآن يوفر حلاً متكاملاً لـ:
- ✅ استقبال البيانات والملفات من الأجهزة الخارجية
- ✅ سحب البيانات من خدمة OOB (Interactsh) تلقائياً
- ✅ أرشفة جميع البيانات في مسار محلي
- ✅ مراقبة الحالة والتفاعلات عبر API

**رابط التطبيق:** https://fastapi-webhook-receiver.onrender.com
**المستودع:** https://github.com/abdabdahfa2002/fastapi-webhook-receiver
