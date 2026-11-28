<?php
set_time_limit(0);
ini_set('max_execution_time', 0);
ini_set('zlib.output_compression', 'Off');
while (ob_get_level()) {
ob_end_clean();
}
$streamUrl = 'http://79.111.14.76:8002/beatdown';
$context = stream_context_create([
'http' => [
'method' => 'GET',
'timeout' => 10,
'protocol_version' => 1.1,
'header' => "User-Agent: Mozilla/5.0\r\n" .
"Connection: close\r\n"
]
]);
$fp = @fopen($streamUrl, 'rb', false, $context);
if (!$fp) {
http_response_code(502);
exit;
}
header('Content-Type: audio/aac');
header('Cache-Control: no-cache, no-store, must-revalidate');
header('Pragma: no-cache');
header('Expires: 0');
header('Accept-Ranges: none');
header('X-Accel-Buffering: no');
fpassthru($fp);
fclose($fp);