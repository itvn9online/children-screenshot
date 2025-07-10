# Import các thư viện cần thiết
import os                    # Thao tác với file và thư mục
import time                  # Xử lý thời gian, sleep
from datetime import datetime, timedelta # Lấy thời gian hiện tại và tính toán ngày
import pyautogui            # Chụp màn hình
import threading            # Xử lý đa luồng
import win32con             # Hằng số của Windows API
import win32gui             # Windows GUI API
import ftplib               # Upload file lên FTP server
import json                 # Đọc file cấu hình JSON
import shutil               # Xóa thư mục và file

# Cấu hình thư mục và tham số
# Thư mục lưu ảnh gốc
save_dir = r'D:\children-screenshot'
# Tạo thư mục lưu ảnh nếu chưa tồn tại
os.makedirs(save_dir, exist_ok=True)

# Khai báo biến toàn cục cho thông tin FTP
# Đọc thông tin FTP từ file cấu hình ngoài (ftp_config.json)
FTP_HOST = None  # Địa chỉ FTP server
FTP_USER = None  # Tên đăng nhập FTP
FTP_PASS = None  # Mật khẩu FTP
FTP_DIR = None   # Thư mục trên FTP server
INTERVAL = 30    # Thời gian lặp lại (giây), mặc định 30 giây

# Tạo đường dẫn tới file cấu hình FTP
ftp_config_path = os.path.join(os.path.dirname(__file__), 'ftp_config.json')
# Kiểm tra nếu file cấu hình FTP tồn tại
if not os.path.exists(ftp_config_path):
    # thiết lập path tĩnh dựa theo save_dir
    ftp_config_path = os.path.join(save_dir, 'ftp_config.json')

# Kiểm tra và đọc file cấu hình FTP nếu tồn tại
if os.path.exists(ftp_config_path):
    try:
        with open(ftp_config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            FTP_HOST = cfg.get('host')          # Lấy địa chỉ FTP
            FTP_USER = cfg.get('user')          # Lấy username
            FTP_PASS = cfg.get('pass')          # Lấy password
            FTP_DIR = cfg.get('dir', '/')       # Lấy thư mục, mặc định là /
            INTERVAL = cfg.get('interval', 30)  # Lấy thời gian interval, mặc định 30 giây
    except Exception as e:
        print(f'Lỗi đọc file cấu hình FTP: {e}')

# Hàm upload file lên FTP server
def upload_to_ftp(local_file, remote_file):
    # Kiểm tra xem có đủ thông tin FTP không
    if not (FTP_HOST and FTP_USER and FTP_PASS):
        return  # Không upload nếu thiếu thông tin
    try:
        # Kết nối FTP và upload file
        with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
            # Chuyển tới thư mục đích trên FTP (nếu có)
            if FTP_DIR:
                ftp.cwd(FTP_DIR)
            # Mở file local và upload lên FTP
            with open(local_file, "rb") as f:
                ftp.storbinary(f"STOR {remote_file}", f)
        print(f"Đã upload lên FTP: {remote_file}")
    except Exception as e:
        print(f"Lỗi upload FTP: {e}")

# Event để đồng bộ trạng thái sleep/wake của máy tính
sleeping = threading.Event()

# Lớp xử lý sự kiện power management của Windows
class PowerBroadcast:
    def __init__(self):
        self.hwnd = None  # Handle của window
        # Tạo thread để lắng nghe sự kiện power
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()

    def listen(self):
        # Tạo window class để nhận message từ Windows
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc          # Gán hàm xử lý message
        wc.lpszClassName = 'PowerBroadcastListener'  # Tên class
        
        # Đăng ký window class
        class_atom = win32gui.RegisterClass(wc)
        
        # Tạo window ẩn để nhận power broadcast message
        self.hwnd = win32gui.CreateWindow(
            class_atom, 'PowerBroadcastListener', 0, 0, 0, 0, 0, 0, 0, 0, None
        )
        
        # Bắt đầu lắng nghe message
        win32gui.PumpMessages()

    # Hàm xử lý các Windows message
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        # Kiểm tra nếu là power broadcast message
        if msg == win32con.WM_POWERBROADCAST:
            # Máy tính chuẩn bị sleep/suspend
            if wparam == win32con.PBT_APMSUSPEND:
                print('Phát hiện máy sleep, tạm dừng chụp ảnh.')
                sleeping.set()  # Đặt flag để dừng chụp ảnh
            # Máy tính đã wake up/resume
            elif wparam in (
                win32con.PBT_APMRESUMEAUTOMATIC,   # Resume tự động
                win32con.PBT_APMRESUMECRITICAL,    # Resume khẩn cấp
                win32con.PBT_APMRESUMESUSPEND,     # Resume từ suspend
            ):
                print('Máy đã resume, tiếp tục chụp ảnh.')
                sleeping.clear()  # Xóa flag để tiếp tục chụp ảnh
        
        # Gọi hàm xử lý message mặc định
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

# Khởi tạo PowerBroadcast để lắng nghe sự kiện power
PowerBroadcast()

print(f'Bắt đầu chụp màn hình mỗi {INTERVAL} giây. Ảnh sẽ lưu ở {save_dir}')

# Hàm xóa file và thư mục cũ hơn số ngày được chỉ định
def cleanup_old_files(base_dir, days_to_keep=7):
    """
    Xóa các thư mục và file cũ hơn số ngày được chỉ định
    
    Args:
        base_dir: Thư mục gốc chứa các thư mục con theo ngày
        days_to_keep: Số ngày muốn giữ lại (mặc định 7 ngày)
    """
    try:
        # Tính toán ngày cắt (ngày cũ nhất được phép giữ lại)
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Kiểm tra nếu thư mục gốc không tồn tại
        if not os.path.exists(base_dir):
            return
        
        # Duyệt qua tất cả các thư mục con
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            
            # Chỉ xử lý thư mục
            if os.path.isdir(item_path):
                try:
                    # Kiểm tra xem tên thư mục có đúng định dạng YYYY-MM-DD không
                    folder_date = datetime.strptime(item, '%Y-%m-%d')
                    
                    # Nếu thư mục cũ hơn ngày cắt, xóa nó
                    if folder_date < cutoff_date:
                        print(f'Đang xóa thư mục cũ: {item_path}')
                        shutil.rmtree(item_path)  # Xóa thư mục và tất cả nội dung bên trong
                        print(f'Đã xóa thư mục: {item_path}')
                        
                except ValueError:
                    # Bỏ qua nếu tên thư mục không đúng định dạng ngày
                    print(f'Bỏ qua thư mục không đúng định dạng: {item}')
                    continue
                    
    except Exception as e:
        print(f'Lỗi khi xóa file cũ: {e}')

# Dọn dẹp file cũ hơn 7 ngày khi khởi động chương trình
print('Bắt đầu dọn dẹp file cũ hơn 7 ngày...')
cleanup_old_files(save_dir, days_to_keep=7)
print('Hoàn thành dọn dẹp file cũ.')

# Vòng lặp chính của chương trình
try:
    while True:
        # Kiểm tra xem máy có đang sleep không
        if sleeping.is_set():
            time.sleep(1)  # Chờ 1 giây rồi kiểm tra lại
            continue
        
        # Lấy thời gian hiện tại
        now = datetime.now()
        
        # Tạo tên thư mục theo định dạng năm-tháng-ngày
        date_folder = now.strftime('%Y-%m-%d')
        folder_path = os.path.join(save_dir, date_folder)
        
        # Tạo thư mục ngày nếu chưa có
        os.makedirs(folder_path, exist_ok=True)
        
        # Đặt tên file ảnh theo thời gian chụp (giờ-phút-giây)
        filename = f'screenshot_{now.strftime('%H%M%S')}.png'
        filepath = os.path.join(folder_path, filename)
        
        # Chụp màn hình
        screenshot = pyautogui.screenshot()
        
        # Lưu ảnh vào file
        screenshot.save(filepath)
        print(f'Đã lưu: {filepath}')
        
        # Upload ảnh lên FTP server (nếu có cấu hình)
        # Tạo tên file trên FTP bao gồm ngày tháng năm (tái sử dụng date_folder)
        remote_filename = f"{date_folder}_{filename}"  # Tên file trên FTP server với ngày
        upload_to_ftp(filepath, remote_filename)
        
        # Đợi theo thời gian interval được cấu hình trước khi chụp tiếp
        time.sleep(INTERVAL)
        
except KeyboardInterrupt:
    # Thoát chương trình khi nhấn Ctrl+C
    print('Đã dừng chương trình.')