from flask import Flask, request, jsonify
import subprocess
import time
import uiautomator2 as u2
import cv2
import numpy as np
import logging
import os
import sys

app = Flask(__name__)

# Thiết lập logging
logger = logging.getLogger("follow_like_web_server")
logger.setLevel(logging.INFO)
logger.handlers = []

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'follow_like_web_server.log'), encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(console_formatter)
logger.addHandler(file_handler)

def find_template_on_screen(device, template_path, threshold=0.8):
    """Tìm ảnh mẫu trên màn hình thiết bị và trả về True nếu tìm thấy."""
    try:
        screenshot = device.screenshot()
        screenshot_path = os.path.join(os.path.dirname(__file__), 'screenshots', f"screenshot_{device.serial}_{int(time.time())}.png")
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        screenshot.save(screenshot_path)
        
        screen_img = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        result = cv2.matchTemplate(screen_img, template_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"[{device.serial}] Lỗi khi so sánh ảnh: {str(e)}")
        return False
    finally:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

def perform_action(device_id, task_type):
    """Thực hiện Follow dựa trên task_type sử dụng uiautomator2."""
    try:
        d = u2.connect(device_id)
        if task_type == "follow":
            follow_button = d(text="Follow")
            if follow_button.exists:
                follow_button.click()
                time.sleep(2)
                subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'swipe', '788', '268', '788', '902', '300'])
                time.sleep(2)
                sample_image_path = os.path.join(os.path.dirname(__file__), 'fl.png')
                if os.path.exists(sample_image_path):
                    if find_template_on_screen(d, sample_image_path):
                        logger.info(f"[{device_id}] Nhả follow")
                        result = "Nhả follow"
                    else:
                        logger.info(f"[{device_id}] Follow ok")
                        result = "Follow ok"
                    # Thực hiện hành động back và nhấn vào com.zhiliaoapp.musically:id/kt6 chỉ khi có "Follow ok" hoặc "Nhả follow"
                    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'keyevent', 'KEYCODE_BACK'])
                    time.sleep(1)
                    d(resourceId="com.zhiliaoapp.musically:id/kt6").click()
                    time.sleep(1)
                    return result
                else:
                    logger.error(f"[{device_id}] Ảnh mẫu {sample_image_path} không tồn tại")
                    return "Error: Template image not found"
            else:
                logger.warning(f"[{device_id}] Không tìm thấy nút Follow")
                return "Error: Follow button not found"
        else:
            logger.error(f"[{device_id}] Task type không hợp lệ: {task_type}")
            return "Error: Invalid task type"
    except Exception as e:
        logger.error(f"[{device_id}] Lỗi khi thực hiện {task_type}: {e}")
        return f"Error: {str(e)}"

@app.route('/follow', methods=['POST'])
def handle_follow():
    """Xử lý yêu cầu Follow từ Termux"""
    try:
        data = request.json
        device_id = data.get('device_id')
        if not device_id:
            logger.warning("Yêu cầu không có device_id")
            return jsonify({"status": "error", "result": "Missing device_id"})
        if data.get('task') == 'FOLLOW':
            logger.info(f"Nhận yêu cầu Follow từ Termux: {data}")
            result = perform_action(device_id, "follow")
            return jsonify({"status": "success", "result": result})
        else:
            logger.warning(f"Yêu cầu không hợp lệ: {data}")
            return jsonify({"status": "error", "result": "Invalid request"})
    except Exception as e:
        logger.error(f"Lỗi khi xử lý yêu cầu: {e}")
        return jsonify({"status": "error", "result": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)