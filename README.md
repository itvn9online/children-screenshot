# Hướng dẫn cài đặt và sử dụng ứng dụng chụp màn hình tự động

https://github.com/itvn9online/children-screenshot

## 1. Cài đặt Python và các thư viện cần thiết

- Cài Python 3 nếu máy chưa có: https://www.python.org/downloads/
- Mở PowerShell, chạy lệnh:
  ```
  pip install pyautogui pillow
  ```

## 2. Cài đặt PyInstaller (nếu muốn tạo file .exe)

- Chạy lệnh:
  ```
  pip install pyinstaller
  ```

### 2.1. Để script tự động dừng khi máy sleep và tiếp tục khi máy resume trên Windows

- Chạy lệnh:
  ```
  pip install pywin32
  ```

## 3. Sử dụng script Python

- File chính: `screenshot_auto.py` trong thư mục `D:\children-screenshot`
- Để chạy script, dùng lệnh:
  ```
  python D:\children-screenshot\screenshot_auto.py
  ```
- Ảnh sẽ được lưu tự động vào thư mục con theo ngày trong `D:\children-screenshot`

## 4. Đóng gói thành file .exe chạy ẩn

- Mở PowerShell, chuyển đến thư mục chứa script:
  ```
  cd D:\children-screenshot
  ```
- Tạo file .exe chạy ẩn:
  ```
  pyinstaller --noconsole --onefile screenshot_auto.py
  ```
- File .exe sẽ nằm trong thư mục `dist`.

## 5. Thiết lập khởi động cùng Windows

- Copy file `.exe` hoặc file batch `run_screenshot_auto.bat` vào thư mục Startup:
  - Nhấn `Win + R`, nhập `shell:startup` rồi Enter.
  - Dán file vào thư mục vừa mở.

## 6. Lưu ý

- Để dừng chương trình, nhấn `Ctrl + C` nếu chạy bằng cửa sổ dòng lệnh.
- Nếu chạy file .exe, chương trình sẽ chạy ẩn, chỉ có thể dừng bằng Task Manager.
