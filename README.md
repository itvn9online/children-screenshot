# Hướng dẫn cài đặt và sử dụng ứng dụng chụp màn hình tự động

https://github.com/itvn9online/children-screenshot

## 1. Cài đặt Python và các thư viện cần thiết

- Cài Python 3 nếu máy chưa có: https://www.python.org/downloads/
- Mở PowerShell, chuyển đến thư mục dự án và chạy lệnh:
  ```
  cd D:\children-screenshot
  pip install -r requirements.txt
  ```

## 2. Cấu hình ứng dụng

### 2.1. Cấu hình FTP (tùy chọn)

- Copy file `ftp_config-sample.json` thành `ftp_config.json`
- Chỉnh sửa thông tin FTP server và mật khẩu thoát ứng dụng:
  ```json
  {
  	"host": "your-ftp-server.com",
  	"user": "username",
  	"pass": "password",
  	"dir": "/screenshots",
  	"interval": 60
  }
  ```

## 3. Sử dụng ứng dụng

### 3.1. Chạy từ Python

- Chạy lệnh:
  ```
  python screenshot_auto.py
  ```

### 3.2. Chạy từ file .exe

- Tạo file .exe (chạy ở system tray):
  ```
  pip install pyinstaller
  pyinstaller --noconsole --onefile screenshot_auto.py
  ```
- File .exe sẽ nằm trong thư mục `dist`
- Tham số `--noconsole`: Không hiển thị cửa sổ console, chạy với system tray

## 4. Sử dụng System Tray

- Sau khi khởi động, chương trình sẽ chạy ở system tray (khay hệ thống)
- Click phải vào icon để xem menu:
  - **Trạng thái**: Xem thông tin trạng thái hiện tại
  - **Thoát**: Thoát chương trình ngay lập tức

## 5. Tính năng chính

- **Chụp màn hình tự động**: Mỗi 60 giây (có thể thay đổi trong cấu hình)
- **Phát hiện user inactive**: Không chụp khi user không hoạt động > 30 giây
- **Upload FTP tự động**: Upload và xóa file local sau khi upload thành công
- **Tự động dọn dẹp**: Xóa file cũ hơn 7 ngày
- **System tray**: Chạy ẩn với menu điều khiển đơn giản

## 6. Web Interface

- File `index.php` cung cấp giao diện web để xem ảnh đã chụp
- Đặt file PHP trong thư mục web server cùng với thư mục screenshots
- Truy cập qua browser để xem danh sách và preview ảnh

## 7. Thiết lập khởi động cùng Windows

- Copy file `.exe` vào thư mục Startup:
  - Nhấn `Win + R`, nhập `shell:startup` rồi Enter
  - Dán file .exe vào thư mục vừa mở
