"""
OOB Data Polling Scheduler - نظام مستقل
يقوم بإنشاء معرّف فريد محلي وسحب البيانات كل 60 ثانية
"""

import os
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler

# إعدادات المسارات
UPLOAD_DIRECTORY = "uploads"
OOB_DATA_FILE = os.path.join(UPLOAD_DIRECTORY, "oob_interactions.json")
OOB_CONFIG_FILE = os.path.join(UPLOAD_DIRECTORY, "oob_config.json")

# إنشاء مجلد uploads إذا لم يكن موجوداً
Path(UPLOAD_DIRECTORY).mkdir(exist_ok=True)

# متغيرات عامة
oob_url = None
oob_token = None
scheduler = None
oob_interactions = []


def generate_oob_credentials():
    """
    إنشاء معرّف فريد محلي (بدلاً من Interactsh)
    يتم إنشاء URL و Token فريد لكل جلسة
    """
    global oob_url, oob_token
    
    try:
        # إنشاء معرّف فريد
        unique_id = str(uuid.uuid4())[:16]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # إنشاء URL محلي
        oob_url = f"{unique_id}.oob.local"
        
        # إنشاء Token
        token_data = f"{unique_id}{timestamp}{os.urandom(16).hex()}"
        oob_token = hashlib.sha256(token_data.encode()).hexdigest()[:32]
        
        # حفظ الإعدادات
        config = {
            "oob_url": oob_url,
            "oob_token": oob_token,
            "created_at": datetime.now().isoformat(),
            "unique_id": unique_id
        }
        
        with open(OOB_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"[OOB] تم إنشاء معرّف جديد")
        print(f"[OOB] الـ URL: {oob_url}")
        print(f"[OOB] الـ Token: {oob_token}")
        
        return True
        
    except Exception as e:
        print(f"[OOB] خطأ في إنشاء المعرّف: {str(e)}")
        return False


def initialize_oob():
    """
    تهيئة نظام OOB المستقل
    """
    global oob_url, oob_token
    
    try:
        # محاولة تحميل الإعدادات السابقة
        if os.path.exists(OOB_CONFIG_FILE):
            with open(OOB_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                oob_url = config.get("oob_url")
                oob_token = config.get("oob_token")
                print(f"[OOB] تم تحميل المعرّف السابق: {oob_url}")
                return True
        else:
            # إنشاء معرّف جديد
            return generate_oob_credentials()
            
    except Exception as e:
        print(f"[OOB] خطأ في التهيئة: {str(e)}")
        return False


def poll_oob_data():
    """
    وظيفة سحب البيانات المحلية كل 60 ثانية
    في النسخة المستقلة، نقوم بمسح الملفات المحلية والبحث عن البيانات
    """
    global oob_interactions
    
    try:
        print(f"\n[Scheduler] بدء سحب البيانات في {datetime.now().isoformat()}")
        
        # البحث عن ملفات جديدة في مجلد uploads
        oob_files_dir = os.path.join(UPLOAD_DIRECTORY, "oob_data")
        
        if os.path.exists(oob_files_dir):
            files = os.listdir(oob_files_dir)
            
            if files:
                print(f"[OOB] تم العثور على {len(files)} ملف جديد")
                
                for filename in files:
                    filepath = os.path.join(oob_files_dir, filename)
                    
                    try:
                        # قراءة محتوى الملف
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # إضافة البيانات إلى قائمة التفاعلات
                        interaction_data = {
                            "timestamp": datetime.now().isoformat(),
                            "protocol": "file_based",
                            "source": filename,
                            "data": content[:500],  # أول 500 حرف
                            "size": len(content),
                            "full_data": content
                        }
                        
                        oob_interactions.append(interaction_data)
                        
                        print(f"[OOB] تم معالجة الملف: {filename}")
                        
                        # حذف الملف بعد معالجته
                        os.remove(filepath)
                        
                    except Exception as e:
                        print(f"[OOB] خطأ في معالجة الملف {filename}: {str(e)}")
            else:
                print("[Scheduler] لا توجد بيانات جديدة")
        else:
            print("[Scheduler] مجلد البيانات غير موجود")
        
        # حفظ البيانات
        save_oob_data()
        
    except Exception as e:
        print(f"[Scheduler] خطأ أثناء سحب البيانات: {str(e)}")


def save_oob_data():
    """
    حفظ بيانات OOB في ملف JSON
    """
    global oob_interactions
    
    try:
        with open(OOB_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "total_interactions": len(oob_interactions),
                "oob_url": oob_url,
                "oob_token": oob_token,
                "interactions": oob_interactions[-100:]  # احفظ آخر 100 تفاعل فقط
            }, f, ensure_ascii=False, indent=2)
        
        print(f"[Storage] تم حفظ {len(oob_interactions)} تفاعل في {OOB_DATA_FILE}")
    except Exception as e:
        print(f"[Storage] خطأ في حفظ البيانات: {str(e)}")


def load_oob_data():
    """
    تحميل بيانات OOB من ملف JSON
    """
    global oob_interactions
    
    try:
        if os.path.exists(OOB_DATA_FILE):
            with open(OOB_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                oob_interactions = data.get("interactions", [])
                print(f"[Storage] تم تحميل {len(oob_interactions)} تفاعل من الملف")
        else:
            print("[Storage] ملف البيانات غير موجود، سيتم إنشاء ملف جديد")
    except Exception as e:
        print(f"[Storage] خطأ في تحميل البيانات: {str(e)}")


def start_scheduler():
    """
    بدء جدولة المهام في الخلفية
    """
    global scheduler
    
    try:
        scheduler = BackgroundScheduler()
        
        # إضافة مهمة سحب البيانات كل 60 ثانية
        scheduler.add_job(
            poll_oob_data,
            'interval',
            seconds=60,
            id='oob_polling',
            name='OOB Data Polling',
            replace_existing=True
        )
        
        scheduler.start()
        print("[Scheduler] تم بدء جدولة المهام - سيتم سحب البيانات كل 60 ثانية")
        
    except Exception as e:
        print(f"[Scheduler] خطأ في بدء الجدولة: {str(e)}")


def stop_scheduler():
    """
    إيقاف جدولة المهام
    """
    global scheduler
    
    try:
        if scheduler and scheduler.running:
            scheduler.shutdown()
            print("[Scheduler] تم إيقاف جدولة المهام")
    except Exception as e:
        print(f"[Scheduler] خطأ في إيقاف الجدولة: {str(e)}")


def get_oob_interactions():
    """
    الحصول على قائمة التفاعلات المحفوظة
    """
    global oob_interactions
    return oob_interactions


def clear_oob_data():
    """
    مسح بيانات OOB
    """
    global oob_interactions
    
    try:
        oob_interactions = []
        save_oob_data()
        print("[Storage] تم مسح بيانات OOB")
        return True
    except Exception as e:
        print(f"[Storage] خطأ في مسح البيانات: {str(e)}")
        return False


def get_oob_url():
    """
    الحصول على رابط OOB
    """
    global oob_url
    return oob_url


def get_oob_token():
    """
    الحصول على توكن OOB
    """
    global oob_token
    return oob_token


def get_oob_credentials():
    """
    الحصول على بيانات OOB كاملة (URL و Token)
    """
    global oob_url, oob_token
    return {
        "url": oob_url,
        "token": oob_token,
        "status": "active" if (oob_url and oob_token) else "inactive",
        "type": "standalone_oob"
    }


def add_oob_interaction(data):
    """
    إضافة تفاعل جديد يدويًا (للاختبار)
    """
    global oob_interactions
    
    try:
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "protocol": data.get("protocol", "manual"),
            "source": data.get("source", "unknown"),
            "data": data.get("data", ""),
            "size": len(str(data.get("data", "")))
        }
        
        oob_interactions.append(interaction)
        save_oob_data()
        
        print(f"[OOB] تم إضافة تفاعل جديد")
        return True
        
    except Exception as e:
        print(f"[OOB] خطأ في إضافة التفاعل: {str(e)}")
        return False
