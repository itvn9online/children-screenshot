# Import các thư viện cần thiết
import os                    # Thao tác với file và thư mục
import time                  # Xử lý thời gian, sleep
from datetime import datetime, timedelta # Lấy thời gian hiện tại và tính toán ngày
import pyautogui            # Chụp màn hình
import threading            # Xử lý đa luồng
import win32con             # Hằng số của Windows API
import win32gui             # Windows GUI API
import win32api             # Windows API để lấy thông tin idle time
import ftplib               # Upload file lên FTP server
import json                 # Đọc file cấu hình JSON
import shutil               # Xóa thư mục và file
import ctypes               # Gọi Windows API
from ctypes import wintypes # Kiểu dữ liệu Windows
import sys                  # Thông tin hệ thống để kiểm tra .exe

# Cấu hình thư mục và tham số
# Xác định thư mục lưu ảnh dựa trên cách chạy chương trình
if getattr(sys, 'frozen', False):
    # Nếu chạy từ file .exe (PyInstaller), lùi lại 1 thư mục
    exe_dir = os.path.dirname(sys.executable)
    save_dir = os.path.dirname(exe_dir)  # Lùi lại 1 thư mục
else:
    # Nếu chạy trực tiếp từ file .py, sử dụng thư mục hiện tại
    save_dir = os.path.dirname(os.path.abspath(__file__))

# Khai báo biến toàn cục cho thông tin FTP
# Đọc thông tin FTP từ file cấu hình ngoài (ftp_config.json)
FTP_HOST = None  # Địa chỉ FTP server
FTP_USER = None  # Tên đăng nhập FTP
FTP_PASS = None  # Mật khẩu FTP
FTP_DIR = None   # Thư mục trên FTP server
INTERVAL = 60    # Thời gian lặp lại (giây), mặc định 60 giây

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
            INTERVAL = cfg.get('interval', 60)  # Lấy thời gian interval, mặc định 60 giây
    except Exception as e:
        print(f'Lỗi đọc file cấu hình FTP: {e}')

# Hàm upload file lên FTP server
def upload_to_ftp(local_file, remote_file):
    # Kiểm tra xem có đủ thông tin FTP không
    if not (FTP_HOST and FTP_USER and FTP_PASS):
        return False  # Không upload nếu thiếu thông tin
    try:
        # Kết nối FTP và upload file
        with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
            # Chuyển tới thư mục đích trên FTP (nếu có)
            if FTP_DIR:
                ftp.cwd(FTP_DIR)
            # Mở file local và upload lên FTP
            with open(local_file, "rb") as f:
                ftp.storbinary(f"STOR {remote_file}", f)
        print(f"Đã upload lên FTP: {remote_file} via {FTP_USER}:{FTP_HOST}")
        return True  # Upload thành công
    except Exception as e:
        print(f"Lỗi upload FTP: {e}")
        return False  # Upload thất bại

# Hàm kiểm tra thời gian idle của người dùng (không có hoạt động chuột/bàn phím)
def get_idle_time():
    """
    Lấy thời gian idle của người dùng tính bằng mili giây
    Trả về số giây người dùng không có hoạt động
    """
    try:
        # Sử dụng Windows API để lấy thời gian cuối cùng có input
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [
                ('cbSize', wintypes.UINT),
                ('dwTime', wintypes.DWORD),
            ]
        
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
        
        # Gọi GetLastInputInfo để lấy thời gian input cuối cùng
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
            # Lấy thời gian hiện tại
            current_time = ctypes.windll.kernel32.GetTickCount()
            # Tính thời gian idle (mili giây)
            idle_time_ms = current_time - lastInputInfo.dwTime
            # Chuyển đổi sang giây
            return idle_time_ms / 1000.0
        else:
            return 0
    except Exception as e:
        print(f"Lỗi khi lấy idle time: {e}")
        return 0

# Đã thay đổi từ kiểm tra sleep sang kiểm tra idle time của người dùng
# Không cần PowerBroadcast nữa

print(f'Bắt đầu chụp màn hình mỗi {INTERVAL} giây. Ảnh sẽ lưu ở {save_dir}')
print('Chương trình sẽ bỏ qua chụp ảnh nếu người dùng không hoạt động quá 30 giây.')

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
        # Kiểm tra thời gian idle của người dùng
        idle_time = get_idle_time()
        
        # Nếu người dùng không hoạt động quá 30 giây thì bỏ qua việc chụp ảnh
        if idle_time > 30:
            print(f'Người dùng không hoạt động trong {idle_time:.1f} giây, bỏ qua chụp ảnh.')
            time.sleep(10)  # Chờ 10 giây rồi kiểm tra lại
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
        upload_success = upload_to_ftp(filepath, remote_filename)
        
        # Nếu upload thành công thì xóa file local
        if upload_success:
            try:
                os.remove(filepath)
                print(f"Đã xóa file local: {filepath}")
            except Exception as e:
                print(f"Lỗi khi xóa file local: {e}")
        else:
            print(f"Giữ lại file local do upload thất bại: {filepath}")
        
        # Đợi theo thời gian interval được cấu hình trước khi chụp tiếp
        time.sleep(INTERVAL)
        
except KeyboardInterrupt:
    # Thoát chương trình khi nhấn Ctrl+C
    print('Đã dừng chương trình.')