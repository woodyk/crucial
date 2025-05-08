<?php
$canvas_id = basename($_GET['id'] ?? $_SERVER['REQUEST_URI']);
$canvas_id = preg_replace('/\.png$/', '', $canvas_id);
if (!$canvas_id) {
    http_response_code(400);
    echo "Missing canvas ID";
    exit;
}

$escaped_id = escapeshellarg($canvas_id);

// Run a headless browser to capture PNG
$tmpfile = tempnam(sys_get_temp_dir(), 'canvas') . '.png';
$cmd = "node render-canvas.js $escaped_id $tmpfile";
exec($cmd, $output, $status);

if ($status !== 0 || !file_exists($tmpfile)) {
    http_response_code(500);
    echo "Failed to render canvas.";
    exit;
}

// Serve the PNG
header('Content-Type: image/png');
header('Content-Disposition: inline; filename="' . $canvas_id . '.png"');
readfile($tmpfile);
unlink($tmpfile);
?>

