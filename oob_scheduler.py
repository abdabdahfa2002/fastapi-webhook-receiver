"""
OOB Data Polling Scheduler
يقوم بسحب البيانات من خدمة Interactsh كل 60 ثانية وأرشفتها
استخدام Interactsh API مباشرة مع مكتبة requests
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler

# إعدادات المسارات
UPLOAD_DIRECTORY = "uploads"
OOB_DATA_FILE = os.path.join(UPLOAD_DIRECTORY, "oob_interactions.json")

# إنشاء مجلد uploads إذا لم يكن موجوداً
Path(UPLOAD_DIRECTORY).mkdir(exist_ok=True)

# متغيرات عامة
interactsh_url = None
interactsh_token = None
scheduler = None
oob_interactions = []


def initialize_interactsh():
    """
    تهيئة عميل Interactsh باستخدام API
    """
    global interactsh_url, interactsh_token
    try:
        # إنشاء تفاعل جديد على Interactsh
        response = requests.get("https://interactsh.com/register", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            interactsh_url = data.get("url", "")
            interactsh_token = data.get("token", "")
            
            print(f"[Interactsh] تم إنشاء عميل جديد")
            print(f"[Interactsh] رابط التفاعل: {interactsh_url}")
            return True
        else:
            print(f"[Interactsh] فشل الاتصال بـ Interactsh: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[Interactsh] خطأ في التهيئة: {str(e)}")
        return False


def poll_oob_data():
    """
    وظيفة سحب البيانات من Interactsh كل 60 ثانية
    """
    global interactsh_url, interactsh_token, oob_interactions
    
    if not interactsh_url or not interactsh_token:
        print("[Scheduler] عميل Interactsh لم يتم تهيئته بعد")
        return
    
    try:
        print(f"\n[Scheduler] بدء سحب البيانات في {datetime.now().isoformat()}")
        
        # استدعاء API للحصول على التفاعلات
        headers = {"Authorization": f"Bearer {interactsh_token}"}
        response = requests.get(
            f"https://interactsh.com/poll",
            headers=headers,
            params={"token": interactsh_token},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            interactions = data.get("interactions", [])
            
            if interactions:
                print(f"[Interactsh] تم استقبال {len(interactions)} تفاعل جديد")
                
                for interaction in interactions:
                    # معالجة كل تفاعل
                    interaction_data = {
                        "timestamp": datetime.now().isoformat(),
                        "protocol": interaction.get("protocol", "unknown"),
                        "remote_address": interaction.get("remote_address", ""),
                        "request": interaction.get("request", "")[:200],  # أول 200 حرف
                        "response": interaction.get("response", "")[:200],
                        "full_data": interaction
                    }
                    
                    oob_interactions.append(interaction_data)
                    
                    print(f"[Interactsh] تفاعل جديد:")
                    print(f"  - البروتوكول: {interaction_data['protocol']}")
                    print(f"  - العنوان البعيد: {interaction_data['remote_address']}")
            else:
                print("[Scheduler] لا توجد تفاعلات جديدة")
        else:
            print(f"[Scheduler] خطأ في الاستجابة: {response.status_code}")
        
        # حفظ البيانات في ملف JSON
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
                "interactions": oob_interactions
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


def get_interactsh_url():
    """
    الحصول على رابط Interactsh
    """
    global interactsh_url
    return interactsh_url
