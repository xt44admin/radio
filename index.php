<?php
@set_time_limit(0);
@ini_set('max_execution_time', 0);
@ini_set('zlib.output_compression', 'Off');
while (ob_get_level()) { ob_end_clean(); }
$files = glob(__DIR__ . '/*.mp3');
if (!$files) { http_response_code(404); exit('No MP3 files found.'); }
sort($files);
$bytesPerSecond = 12000;
$playlist = [];
$totalSize = 0;
foreach ($files as $f) {
$sz = filesize($f);
if ($sz > 0) { $playlist[] = ['file' => $f, 'size' => $sz]; $totalSize += $sz; }
}
$totalDuration = max(1, (int) floor($totalSize / $bytesPerSecond));
function getShuffledOrder($list, $seed) {
mt_srand($seed);
$count = count($list);
for ($i = $count - 1; $i > 0; $i--) {
$j = mt_rand(0, $i);
$tmp = $list[$i]; $list[$i] = $list[$j]; $list[$j] = $tmp;
}
return $list;
}
$bufferSeconds = 3;
$liveTime = max(0, time() - $bufferSeconds);
$cycle = (int) floor($liveTime / $totalDuration);
$cycleOffsetBytes = ($liveTime % $totalDuration) * $bytesPerSecond;
$currentOrder = getShuffledOrder($playlist, $cycle);
$trackIdx = 0;
$acc = 0;
foreach ($currentOrder as $idx => $item) {
if ($acc + $item['size'] > $cycleOffsetBytes) { $trackIdx = $idx; break; }
$acc += $item['size'];
}
$trackOffset = $cycleOffsetBytes - $acc;
$fp = fopen($currentOrder[$trackIdx]['file'], 'rb');
fseek($fp, $trackOffset);
$syncSearch = fread($fp, 4096);
$syncPos = 0;
for ($i = 0; $i < strlen($syncSearch) - 1; $i++) {
if (ord($syncSearch[$i]) === 0xFF && (ord($syncSearch[$i + 1]) & 0xE0) === 0xE0) { $syncPos = $i; break; }
}
fseek($fp, $trackOffset + $syncPos);
header('Content-Type: audio/mpeg');
header('Cache-Control: no-cache, no-store, must-revalidate');
header('Pragma: no-cache');
header('Expires: 0');
header('Accept-Ranges: none');
header('X-Accel-Buffering: no');
function readPlaylistChunk(&$fp, &$currentOrder, &$trackIdx, &$cycle, $playlist, $bytesNeeded) {
$buffer = '';
while (strlen($buffer) < $bytesNeeded) {
$chunk = fread($fp, $bytesNeeded - strlen($buffer));
if ($chunk === false || strlen($chunk) === 0) {
fclose($fp);
$trackIdx++;
if ($trackIdx >= count($currentOrder)) {
$cycle++;
$currentOrder = getShuffledOrder($playlist, $cycle);
$trackIdx = 0;
}
$fp = fopen($currentOrder[$trackIdx]['file'], 'rb');
} else {
$buffer .= $chunk;
}
}
return $buffer;
}
echo readPlaylistChunk($fp, $currentOrder, $trackIdx, $cycle, $playlist, $bytesPerSecond * $bufferSeconds);
flush();
$interval = 0.5;
$chunkSize = 6000;
$nextTick = microtime(true) + $interval;
while (!connection_aborted()) {
echo readPlaylistChunk($fp, $currentOrder, $trackIdx, $cycle, $playlist, $chunkSize);
flush();
$sleepTime = $nextTick - microtime(true);
if ($sleepTime > 0) { usleep((int) ($sleepTime * 1000000)); }
$nextTick += $interval;
}
if (is_resource($fp)) { fclose($fp); }