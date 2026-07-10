<?php
/* ============================================================
   naštimaj — lead endpoint
   Prima JSON {ime, email, telefon, web (honeypot), zelja, sazetak},
   šalje mail na info@shtimung.hr + kopiju sažetka korisniku.

   Plus Hosting ima mail() u disable_functions, pa se šalje
   autenticiranim SMTP-om (kredencijali u smtp-config.php).
   ============================================================ */

declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');

const PRIMA = 'info@shtimung.hr';

function fail(int $kod, string $poruka): void
{
    http_response_code($kod);
    echo json_encode(['ok' => false, 'greska' => $poruka]);
    exit;
}

/* ---------- minimalni SMTP klijent (SSL, AUTH LOGIN) ---------- */
function smtpPosalji(array $cfg, string $za, string $subjekt, string $telo, string $replyTo): bool
{
    $fp = @stream_socket_client('ssl://' . $cfg['host'] . ':465', $errno, $errstr, 15);
    if ($fp === false) {
        return false;
    }
    stream_set_timeout($fp, 15);

    $ocekuj = static function (string $kod) use ($fp): bool {
        while (($linija = fgets($fp, 515)) !== false) {
            if (strlen($linija) < 4) {
                return false;
            }
            if ($linija[3] === ' ') { // zadnja linija (moguće višelinijskog) odgovora
                return strncmp($linija, $kod, strlen($kod)) === 0;
            }
        }
        return false;
    };
    $cmd = static function (string $c) use ($fp): void {
        fwrite($fp, $c . "\r\n");
    };

    $od = $cfg['user'];
    $zaglavlja = 'From: shtimung <' . $od . ">\r\n"
        . 'To: <' . $za . ">\r\n"
        . 'Reply-To: ' . $replyTo . "\r\n"
        . 'Subject: =?UTF-8?B?' . base64_encode($subjekt) . "?=\r\n"
        . 'Date: ' . date('r') . "\r\n"
        . 'Message-ID: <' . bin2hex(random_bytes(12)) . '@shtimung.hr>' . "\r\n"
        . "MIME-Version: 1.0\r\n"
        . "Content-Type: text/plain; charset=utf-8\r\n"
        . 'Content-Transfer-Encoding: 8bit';

    // normaliziraj prijelome + dot-stuffing po RFC 5321
    $telo = preg_replace('/\r\n|\r|\n/', "\r\n", $telo);
    $telo = preg_replace('/^\./m', '..', $telo);

    $ok = $ocekuj('220');
    if ($ok) { $cmd('EHLO shtimung.hr'); $ok = $ocekuj('250'); }
    if ($ok) { $cmd('AUTH LOGIN'); $ok = $ocekuj('334'); }
    if ($ok) { $cmd(base64_encode($cfg['user'])); $ok = $ocekuj('334'); }
    if ($ok) { $cmd(base64_encode($cfg['pass'])); $ok = $ocekuj('235'); }
    if ($ok) { $cmd('MAIL FROM:<' . $od . '>'); $ok = $ocekuj('250'); }
    if ($ok) { $cmd('RCPT TO:<' . $za . '>'); $ok = $ocekuj('250'); }
    if ($ok) { $cmd('DATA'); $ok = $ocekuj('354'); }
    if ($ok) {
        fwrite($fp, $zaglavlja . "\r\n\r\n" . $telo . "\r\n.\r\n");
        $ok = $ocekuj('250');
    }
    $cmd('QUIT');
    fclose($fp);
    return $ok;
}

/* ---------- ulaz ---------- */
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    fail(405, 'Samo POST.');
}

$raw = file_get_contents('php://input');
if ($raw === false || strlen($raw) > 20000) {
    fail(400, 'Neispravan zahtjev.');
}
$d = json_decode($raw, true);
if (!is_array($d)) {
    fail(400, 'Neispravan zahtjev.');
}

// honeypot: ljudi polje ne vide, botovima kažemo "ok" i ništa ne šaljemo
if (!empty($d['web'])) {
    echo json_encode(['ok' => true]);
    exit;
}

$ime = trim((string)($d['ime'] ?? ''));
$email = trim((string)($d['email'] ?? ''));
$telefon = trim((string)($d['telefon'] ?? ''));
$zelja = ($d['zelja'] ?? '') === 'showroom' ? 'showroom' : 'mail';
$sazetak = trim((string)($d['sazetak'] ?? ''));

if ($ime === '' || mb_strlen($ime) > 100) {
    fail(422, 'Upiši ime.');
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 200) {
    fail(422, 'Upiši ispravan mail.');
}
if (mb_strlen($telefon) > 40 || mb_strlen($sazetak) > 5000) {
    fail(422, 'Neispravan zahtjev.');
}
foreach ([$ime, $email, $telefon] as $polje) {
    if (preg_match('/[\r\n]/', $polje)) {
        fail(422, 'Neispravan zahtjev.');
    }
}

$cfg = @include __DIR__ . '/smtp-config.php';
if (!is_array($cfg) || empty($cfg['host']) || empty($cfg['user']) || empty($cfg['pass'])) {
    fail(500, 'Slanje trenutno nije dostupno. Piši nam direktno na info@shtimung.hr.');
}

$zeljaTekst = $zelja === 'showroom'
    ? 'Želi doći vidjeti uživo u showroom'
    : 'Želi detaljan prijedlog na mail';

/* ---------- mail nama: lead sa specifikacijom ---------- */
$telo = "=== nashtimaj lead ===\n\n"
    . "Ime: {$ime}\n"
    . "Mail: {$email}\n"
    . 'Telefon: ' . ($telefon !== '' ? $telefon : '-') . "\n"
    . "{$zeljaTekst}\n\n"
    . "{$sazetak}\n";

if (!smtpPosalji($cfg, PRIMA, "nashtimaj lead: {$ime}", $telo, $email)) {
    fail(500, 'Slanje nije uspjelo. Piši nam direktno na info@shtimung.hr.');
}

/* ---------- kopija korisniku (ako ne prođe, lead je ipak zaprimljen) ---------- */
$kopija = "Bok {$ime},\n\n"
    . "ovo je tvoj shtimung, onako kako si ga naštimao:\n\n"
    . "{$sazetak}\n\n"
    . ($zelja === 'showroom'
        ? "Javljamo ti se s terminom: sve što si upalio radi uživo u našem showroomu u Zagrebu.\n"
        : "Javljamo ti se s konkretnim prijedlogom u roku dan-dva.\n")
    . "\nshtimung | pametan dom po mjeri\nhttps://shtimung.hr\n";

smtpPosalji($cfg, $email, 'tvoj shtimung', $kopija, PRIMA);

echo json_encode(['ok' => true]);
