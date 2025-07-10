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

    // kiểm tra nếu username không rỗng và tồn tại trong file username.txt
    if (strpos(file_get_contents('../username.txt'), $username) !== false) {
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
            padding-bottom: 90px;
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

        .click-open-img a.clicked {
            color: red;
            /* Đổi màu chữ thành đỏ khi link được click */
        }
    </style>
</head>

<body>
    <h1><a href="index.php">Quản lý ảnh</a></h1>
    <?php

    // kiểm tra xem người dùng đã đăng nhập chưa
    if (!isset($_SESSION['loggedin']) || strpos(file_get_contents('../username.txt'), $_SESSION['loggedin']) === false) {
        // hiển thị form đăng nhập
    ?>
        <div>
            <p class="for-check_login"><?php echo check_login(); ?></p>
            <h2>Đăng nhập</h2>
            <p>Vui lòng nhập tên người dùng để truy cập vào danh sách ảnh.</p>
            <p>Chỉ có thể đăng nhập bằng tên người dùng đã được lưu trong file <strong>username.txt</strong>.</p>
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
                    // hoặc image/png, image/gif tùy theo loại ảnh
                    if (strpos($img, '.png')) {
                        header('Content-Type: image/png');
                    } else {
                        header('Content-Type: image/jpeg');
                    }
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
        <?php

        // 
        $days = [];
        for ($i = 0; $i < 7; $i++) {
            $day = date('Y-m-d', strtotime("-$i day"));
            $days[] = "<a href='index.php?day=$day'>$day</a>";
        }
        echo "<p>Chọn ngày để xem ảnh: " . implode(' | ', $days) . "</p>";

        ?>
        <ul class="click-open-img">
            <?php

            // lấy ngày cần hiển thị, mặc định là hôm nay
            $filter_day = isset($_GET['day']) ? $_GET['day'] : date('Y-m-d');

            // 
            foreach ($images as $image) {
                // kiểm tra nếu file là ảnh
                if (preg_match('/\.(jpg|jpeg|png|gif)$/i', $image)) {
                    // nếu ảnh có ngày cần tìm thì mới hiển thị
                    if (strpos($image, $filter_day . '_screenshot_') === false) {
                        continue; // bỏ qua ảnh không phải cần tìm
                    }

                    // 
                    echo "<li><a href='index.php?img=$image' target='target_eb_iframe'>$image</a></li>";
                }
            }
            ?>
        </ul>
        <div><a href="index.php">Tải lại trang...</a></div>
        <script>
            // Hiển thị iframe khi click vào link trong danh sách ảnh
            document.addEventListener('DOMContentLoaded', function() {
                const iframe = document.getElementById('target_eb_iframe');
                const imageLinks = document.querySelectorAll('.click-open-img a');

                imageLinks.forEach(function(link) {
                    link.addEventListener('click', function(e) {
                        // Hiển thị iframe
                        iframe.classList.add('show');

                        // bỏ clicked ở các link khác
                        imageLinks.forEach(function(otherLink) {
                            otherLink.classList.remove('clicked');
                        });
                        // thêm class đánh dấu đỏ khi click vào link
                        link.classList.add('clicked');

                        // cắt lấy tên ảnh từ href
                        const imgName = link.getAttribute('href').split('=')[1];
                        // thay đổi url hiện tại của web
                        history.pushState(null, '', 'index.php?show_img=' + imgName);
                    });
                });

                // nếu có tham số 'img' trong URL thì tự động mở ảnh
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.has('show_img')) {
                    setTimeout(function() {
                        const imgName = urlParams.get('show_img');
                        // tìm link tương ứng với ảnh
                        const link = document.querySelector('.click-open-img a[href="index.php?img=' + imgName + '"]');
                        if (link) {
                            link.click(); // tự động click vào link để mở ảnh
                        }
                    }, 500);
                } else {
                    // Tự động cuộn xuống cuối trang chỉ một lần khi nạp trang
                    setTimeout(function() {
                        window.scrollTo(0, document.body.scrollHeight);

                        // tự động mở ảnh cuôi cùng nếu có
                        const lastImage = document.querySelector('.click-open-img li:last-child a');
                        if (lastImage) {
                            lastImage.click(); // tự động click vào ảnh cuối cùng
                        }
                    }, 500);
                }

                // tự động tải lại trang sau mỗi 5 phút
                setTimeout(function() {
                    // location.reload();
                    window.location = 'https://<?php echo $_SERVER['HTTP_HOST']; ?>/index.php'; // quay về trang chính
                }, 5 * 60 * 1000); // 5 phút
            });

            // Ẩn iframe khi bấm escape
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape') {
                    const iframe = document.getElementById('target_eb_iframe');
                    const imageLinks = document.querySelectorAll('.click-open-img a');

                    iframe.classList.remove('show'); // ẩn iframe
                    // xóa class clicked ở tất cả các link
                    imageLinks.forEach(function(link) {
                        link.classList.remove('clicked');
                    });
                    // quay về trang chính
                    history.pushState(null, '', 'index.php');
                }
            });
        </script>
        <iframe id="target_eb_iframe" name="target_eb_iframe" title="EB iframe" src="about:blank" width="333" height="550"></iframe>
    <?php
    }
    ?>
</body>