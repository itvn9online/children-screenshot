<?php

/**
 * File này sẽ up lên host cùng config ftp
 * Liệt kê các file ảnh trong thư mục ../screenshot và hiển thị mỗi người người dùng bấm vào ảnh
 */

// làm chức năng đăng nhập
session_start();

// function đăng nhập
function check_login()
{
    // nếu không phải phương thức POST thì không làm gì cả
    if ($_SERVER['REQUEST_METHOD'] != 'POST') {
        return null;
    }

    // kiểm tra xem file username.txt có tồn tại không
    if (!file_exists('../username.txt')) {
        return "File username.txt không tồn tại. Vui lòng tạo file này với tên người dùng.";
    }

    // kiểm tra thông tin đăng nhập
    $username = $_POST['username'] ?? '';

    // kiểm tra xem người dùng nhập đúng tên trong file username.txt không
    if (empty($username)) {
        return "Vui lòng nhập tên người dùng.";
    }

    // so sánh tên người dùng nhập vào với tên trong file username.txt
    // nếu đúng thì đăng nhập thành công
    if ($username === file_get_contents('../username.txt')) {
        $_SESSION['loggedin'] = $username;

        sleep(1); // tạm dừng 1 giây để tránh spam đăng nhập

        // tìm và xóa các ảnh quá 7 ngày trước
        $dir = '../screenshot'; // thư mục chứa ảnh
        $files = scandir($dir);
        $now = time();
        foreach ($files as $file) {
            // kiểm tra nếu file là ảnh và có định dạng hợp lệ
            if (preg_match('/\.(jpg|jpeg|png|gif)$/i', $file)) {
                $filePath = $dir . '/' . $file;
                // kiểm tra thời gian sửa đổi của file
                if (filemtime($filePath) < ($now - 7 * 24 * 60 * 60)) { // nếu file cũ hơn 7 ngày
                    unlink($filePath); // xóa file
                }
            }
        }

        sleep(1); // tạm dừng 1 giây để tránh spam đăng nhập

        // chuyển hướng đến trang chính sau khi đăng nhập
        header('Location: index.php');
        exit;
    }

    // 
    return "Thông tin đăng nhập không hợp lệ.";
}

?>
<!DOCTYPE html>
<html lang="vi">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Quản lý ảnh</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }

        h1 {
            color: #333;
        }

        ul {
            list-style-type: none;
            padding: 0;
        }

        li {
            margin: 10px 0;
        }

        a {
            text-decoration: none;
            color: #007BFF;
        }

        a:hover {
            text-decoration: underline;
        }

        form {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 5px;
        }

        input[type="text"],
        input[type="password"] {
            width: 200px;
            padding: 5px;
            margin-bottom: 10px;
        }

        button {
            padding: 5px 10px;
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
        }

        button:hover {
            background-color: #0056b3;
        }

        .for-check_login:empty {
            display: none;
        }

        .for-check_login {
            color: red;
            font-weight: bold;
        }

        #target_eb_iframe {
            position: fixed;
            right: 0;
            top: 0;
            /* bottom: 20px; */
            width: 66%;
            height: 99%;
            border: 1px solid #ccc;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            background-color: #f9f9f9;
            z-index: 1000;
            display: none;
            /* Ẩn iframe ban đầu */
        }

        #target_eb_iframe.show {
            display: block;
            /* Hiển thị iframe khi có class 'show' */
        }
    </style>
    <script>
        // Hiển thị iframe khi click vào link trong danh sách ảnh
        document.addEventListener('DOMContentLoaded', function() {
            const iframe = document.getElementById('target_eb_iframe');
            const imageLinks = document.querySelectorAll('.click-open-img a');

            imageLinks.forEach(function(link) {
                link.addEventListener('click', function(e) {
                    // Hiển thị iframe
                    iframe.classList.add('show');
                });
            });
        });
    </script>
</head>

<body>
    <h1>Quản lý ảnh</h1>
    <?php

    // kiểm tra xem người dùng đã đăng nhập chưa
    if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] != file_get_contents('../username.txt')) {
        // hiển thị form đăng nhập
    ?>
        <div>
            <p class="for-check_login"><?php echo check_login(); ?></p>
            <h2>Đăng nhập</h2>
            <p>Vui lòng nhập tên người dùng để truy cập vào danh sách ảnh.</p>
            <p>Chỉ có thể đăng nhập bằng tên người dùng đã được lưu trong file <code>username.txt</code>.</p>
            <p>File này sẽ được tạo trong quá trình cài đặt.</p>
            <form method="post" action="">
                <label for="username">Username:</label>
                <input type="text" name="username" id="username" required>
                <br>
                <button type="submit">Đăng nhập</button>
            </form>
        </div>
        <?php
    } else {
        $dir = '../screenshot'; // thư mục chứa ảnh

        // nếu có tham số img trong URL thì hiển thị ảnh
        if (isset($_GET['img'])) {
            // xóa các html đã sinh ra trước đó
            ob_clean();

            $img = basename($_GET['img']); // lấy tên ảnh từ tham số img

            // kiểm tra nếu file ảnh tồn tại
            if (!empty($img) && file_exists($dir . '/' . $img) && preg_match('/\.(jpg|jpeg|png|gif)$/i', $img)) {
                // nếu có tham số 'raw' thì hiển thị ảnh trực tiếp
                if (isset($_GET['raw'])) {
                    // đọc file ảnh và hiển thị ảnh bằng php
                    header('Content-Type: image/jpeg'); // hoặc image/png, image/gif tùy theo loại ảnh
                    readfile($dir . '/' . $img);
                } else {
                    // hiển thị ảnh trong HTML wrapper với CSS để fit iframe
        ?>
                    <!DOCTYPE html>
                    <html>

                    <head>
                        <meta charset="UTF-8">
                        <title>Xem ảnh: <?php echo htmlspecialchars($img); ?></title>
                        <style>
                            body {
                                margin: 0;
                                padding: 0;
                                background-color: #f0f0f0;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                min-height: 100vh;
                            }

                            img {
                                max-width: 99%;
                                max-height: 100vh;
                                width: auto;
                                height: auto;
                                object-fit: contain;
                                border: 1px solid #ddd;
                                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                            }
                        </style>
                    </head>

                    <body>
                        <img src="index.php?img=<?php echo urlencode($img); ?>&raw=1" alt="<?php echo htmlspecialchars($img); ?>">
                    </body>

                    </html>
        <?php
                }
            }
            exit;
        }

        // lấy danh sách ảnh trong thư mục screenshot
        $images = array_diff(scandir($dir), array('..', '.'));
        // kiểm tra nếu không có ảnh nào thì thông báo
        if (empty($images)) {
            echo "Không có ảnh nào trong thư mục screenshot.";
            exit;
        }

        // hiển thị danh sách ảnh
        ?>
        <h1>Danh sách ảnh trong thư mục screenshot</h1>
        <ul class="click-open-img">
            <?php
            foreach ($images as $image) {
                // kiểm tra nếu file là ảnh
                if (preg_match('/\.(jpg|jpeg|png|gif)$/i', $image)) {
                    echo "<li><a href='index.php?img=$image' target='target_eb_iframe'>$image</a></li>";
                }
            }
            ?>
        </ul>
        <iframe id="target_eb_iframe" name="target_eb_iframe" title="EB iframe" src="about:blank" width="333" height="550"></iframe>
    <?php
    }
    ?>
</body>