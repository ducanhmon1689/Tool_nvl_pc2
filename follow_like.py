import requests
import json

# --- THÔNG TIN CẤU HÌNH ---
# Thay 'YOUR_DEVICE_ID' bằng ID thiết bị bạn lấy được ở Bước 4
DEVICE_ID = "YOUR_DEVICE_ID" 

# IP của PC 2 đang chạy web server
SERVER_IP = "10.0.0.17"

# Port mà web server đang lắng nghe
SERVER_PORT = 8000
# -------------------------

def send_follow_request():
    """
    Gửi yêu cầu thực hiện hành động FOLLOW đến web server.
    """
    url = f"http://{SERVER_IP}:{SERVER_PORT}/follow"
    payload = {
        "device_id": DEVICE_ID,
        "task": "FOLLOW"
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Gửi yêu cầu POST đến server
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)

        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") == "success":
                return response_data.get("result", "No result returned")
            else:
                error_message = response_data.get("result", "Unknown error from server")
                return f"Error: {error_message}"
        else:
            return f"Error: Server returned status code {response.status_code}"

    except requests.exceptions.RequestException as e:
        # Bắt các lỗi liên quan đến kết nối (không tìm thấy server, timeout,...)
        return f"Error: Could not connect to the server at {url}. Details: {e}"

if __name__ == '__main__':
    # Phần này để bạn có thể chạy thử trực tiếp tệp này để kiểm tra
    print("Đang gửi yêu cầu follow thử...")
    result = send_follow_request()
    print(f"Kết quả nhận được: {result}")
