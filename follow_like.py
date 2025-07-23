import os
import requests
from datetime import datetime

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

def send_follow_request(url='http://10.0.0.17:8000/follow', device_id='emulator-5554'):
    """Gửi yêu cầu Follow tới PC và nhận kết quả"""
    try:
        # Gửi yêu cầu HTTP POST tới server trên PC
        payload = {'device_id': device_id, 'task': 'FOLLOW'}
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('status')
            result_msg = result.get('result')
            log(f"Nhận phản hồi từ server: {status} - {result_msg}")
            return result_msg
        else:
            log(f"Lỗi khi gửi yêu cầu tới server: HTTP {response.status_code}")
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        log(f"Lỗi khi gửi yêu cầu tới server: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Thay 'emulator-5554' bằng device ID thực tế của bạn
    result = send_follow_request(device_id='emulator-5554')
    print(result)
