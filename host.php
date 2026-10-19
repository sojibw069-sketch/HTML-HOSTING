<?php
/*
  CXOFB SECURE STORAGE SERVER
*/

$uploadDir = "uploads/";
$secretToken = "CXOFB_SECURE_TOKEN_2026"; //    

if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}

//       
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo "<!DOCTYPE html>
    <html>
    <head>
        <title>CXOFB FREE HOSTING</title>
        <style>
            body { background: #0b0b0b; color: #00d4ff; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { border: 2px solid #00d4ff; padding: 40px; border-radius: 20px; text-align: center; background: #121212; box-shadow: 0 0 20px rgba(0,212,255,0.2); }
            h1 { margin: 0; letter-spacing: 3px; }
            p { color: #888; }
        </style>
    </head>
    <body>
        <div class='card'>
            <h1>CXOFB FREE HOSTING</h1>
            <p> Direct Upload Disabled. Use our Telegram Bot.</p>
        </div>
    </body>
    </html>";
    exit;
}

//      
if (isset($_POST['token']) && $_POST['token'] === $secretToken) {
    if (isset($_FILES['file'])) {
        $fileName = $_FILES['file']['name'];
        $fileTmp = $_FILES['file']['tmp_name'];
        $fileExt = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

        //  HTML  Image 
        $allowed = ['html', 'jpg', 'jpeg', 'png', 'css', 'js'];
        if (!in_array($fileExt, $allowed)) {
            echo json_encode(["status" => "error", "message" => "Restricted file type!"]);
            exit;
        }

        $finalName = time() . "_" . $fileName;
        $targetPath = $uploadDir . $finalName;

        if (move_uploaded_file($fileTmp, $targetPath)) {
            $protocol = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') ? "https" : "http";
            echo json_encode([
                "status" => "success",
                "url" => "$protocol://mahfuzahmedchy.com/$targetPath"
            ]);
        } else {
            echo json_encode(["status" => "error", "message" => "Server upload failed!"]);
        }
    }
} else {
    echo json_encode(["status" => "error", "message" => "Unauthorized Access!"]);
}
?>
