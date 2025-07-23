# follow_like.py (trên Termux)
import os
import time
import subprocess
from datetime import datetime
import requests
import json

# Thiết lập thư mục log
log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'follow_client.log')

def log(message):
    """Ghi log vào console và file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {message}\n")

# Hàm này KHÔNG được sử dụng trong luồng mới khi PC điều khiển.
# Giữ lại nếu bạn muốn có tùy chọn chạy Follow trực tiếp trên Termux sau này.
def perform_action(action_type):
    """Thực hiện hành động Follow trên TikTok sử dụng Termux API (không dùng trong luồng này)"""
    try:
        if action_type.lower() != 'follow':
            log(f"Hành động {action_type} không được hỗ trợ!")
            return "Error: Unsupported action"

        # Giả lập nhấn nút Follow trên TikTok
        # Tọa độ (x, y) cần điều chỉnh tùy thiết bị
        x, y = 500, 600  # Tọa độ giả định cho nút Follow
        cmd = f"termux-toast 'Thực hiện Follow' && input tap {x} {y}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            log("Đã nhấn Follow thành công (Local Termux)")
            time.sleep(1)
            return "Follow ok (Local Termux)"
        else:
            log(f"Lỗi khi nhấn Follow (Local Termux): {result.stderr}")
            return "Nhả follow (Local Termux)"
    except Exception as e:
        log(f"Lỗi khi thực hiện Follow (Local Termux): {str(e)}")
        return f"Error (Local Termux): {str(e)}"

def send_follow_request(server_url='http://10.0.0.17:8000/follow', device_id=''): # Đặt IP của PC thứ 2 vào đây
    """Hàm để gửi yêu cầu Follow đến web server trên PC."""
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'device_id': device_id, 'task': 'FOLLOW'} # Gửi device_id và task đến PC
        log(f"Đang gửi yêu cầu follow tới web server ({server_url}) cho device: {device_id}...")
        response = requests.post(server_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Bắt lỗi HTTP
        result = response.json()
        log(f"Phản hồi từ server PC: {result}")
        if result.get('status') == 'success':
            return result.get('result')
        else:
            return f"Error: {result.get('result', 'Lỗi không xác định từ server PC')}"
    except requests.exceptions.ConnectionError as e:
        log(f"Error: Không thể kết nối đến server PC ({server_url}). Đảm bảo server đang chạy và IP đúng. Lỗi: {e}")
        return f"Error: Không thể kết nối đến server PC. Lỗi: {e}"
    except requests.exceptions.RequestException as e:
        log(f"Error: Lỗi khi gửi yêu cầu tới server PC: {e}")
        return f"Error: Lỗi khi gửi yêu cầu tới server PC: {e}"
    except json.JSONDecodeError as e:
        log(f"Error: Lỗi giải mã JSON từ server PC: {e}. Phản hồi: {response.text}")
        return f"Error: Lỗi giải mã JSON từ server PC: {e}. Phản hồi: {response.text}"
    except Exception as e:
        log(f"Error: Lỗi không xác định khi gửi yêu cầu đến server PC: {e}")
        return f"Error: Lỗi không xác định khi gửi yêu cầu đến server PC: {e}"

# Không cần block __main__ ở đây nếu file này chỉ là module được import.
