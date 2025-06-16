import os
import time
from datetime import datetime
import pyautogui
import threading
import win32con
import win32gui

sleeping = threading.Event()

class PowerBroadcast:
    def __init__(self):
        self.hwnd = None
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()

    def listen(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = 'PowerBroadcastListener'
        class_atom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(
            class_atom, 'PowerBroadcastListener', 0, 0, 0, 0, 0, 0, 0, 0, None
        )
        win32gui.PumpMessages()

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_POWERBROADCAST:
            if wparam == win32con.PBT_APMSUSPEND:
                print('Phát hiện máy sleep, tạm dừng chụp ảnh.')
                sleeping.set()
            elif wparam in (
                win32con.PBT_APMRESUMEAUTOMATIC,
                win32con.PBT_APMRESUMECRITICAL,
                win32con.PBT_APMRESUMESUSPEND,
            ):
                print('Máy đã resume, tiếp tục chụp ảnh.')
                sleeping.clear()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

PowerBroadcast()

# Thư mục lưu ảnh gốc
save_dir = r'D:\children-screenshot'
# Tạo thư mục lưu ảnh nếu chưa tồn tại
os.makedirs(save_dir, exist_ok=True)

interval = 30  # Thời gian lặp lại (giây)
print(f'Bắt đầu chụp màn hình mỗi {interval} giây. Ảnh sẽ lưu ở {save_dir}')

try:
    while True:
        if sleeping.is_set():
            time.sleep(1)
            continue
        # Lấy thời gian hiện tại
        now = datetime.now()
        # Tạo tên thư mục theo định dạng năm-tháng-ngày
        date_folder = now.strftime('%Y-%m-%d')
        folder_path = os.path.join(save_dir, date_folder)
        # Tạo thư mục ngày nếu chưa có
        os.makedirs(folder_path, exist_ok=True)
        # Đặt tên file ảnh theo thời gian chụp
        filename = f'screenshot_{now.strftime('%H%M%S')}.png'
        filepath = os.path.join(folder_path, filename)
        # Chụp màn hình
        screenshot = pyautogui.screenshot()
        # Lưu ảnh vào file
        screenshot.save(filepath)
        print(f'Đã lưu: {filepath}')
        # Đợi 30 giây trước khi chụp tiếp
        time.sleep(interval)
except KeyboardInterrupt:
    # Thoát chương trình khi nhấn Ctrl+C
    print('Đã dừng chương trình.')