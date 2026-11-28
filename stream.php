<?php
set_time_limit(0);
ini_set('zlib.output_compression', 'Off');
while (ob_get_level()) ob_end_clean();
$fp = @fopen('http://79.111.14.76:8002/beatdown', 'rb');
if (!$fp) { http_response_code(502); exit; }
header('Content-Type: audio/aac');
header('Cache-Control: no-store');
header('X-Accel-Buffering: no');
fpassthru($fp);
fclose($fp);
