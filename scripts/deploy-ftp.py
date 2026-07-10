#!/usr/bin/env python3
"""Deploy shtimung weba preko FTPS-a (fallback dok Plus Hosting ne uključi shell).

Kredencijali se čitaju iz scripts/deploy.env (FTP_HOST, FTP_USER, FTP_PASS).
FTP račun je ograničen na public_html, pa je remote root = web root.

Korištenje:
  python3 scripts/deploy-ftp.py          # dry-run (ispiše što bi uploadao)
  python3 scripts/deploy-ftp.py --go     # stvarni deploy
"""

import ftplib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# što se shipa (isti skup kao u deploy.sh)
INCLUDE = ["index.html", ".htaccess"]
INCLUDE_DIRS = ["css", "js", "brand", "nashtimaj"]
EXCLUDE_PARTS = {"_src", ".DS_Store"}


def load_env():
    env = {}
    for line in (ROOT / "scripts" / "deploy.env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip().strip('"')
    return env


def collect_files():
    files = [ROOT / f for f in INCLUDE if (ROOT / f).exists()]
    for d in INCLUDE_DIRS:
        for p in sorted((ROOT / d).rglob("*")):
            if p.is_file() and not (set(p.parts) & EXCLUDE_PARTS):
                files.append(p)
    return files


def ensure_dir(ftp, remote_dir):
    parts = [p for p in remote_dir.split("/") if p]
    path = ""
    for part in parts:
        path += "/" + part
        try:
            ftp.mkd(path)
        except ftplib.error_perm:
            pass  # već postoji


def main():
    go = "--go" in sys.argv
    env = load_env()
    files = collect_files()

    total = sum(f.stat().st_size for f in files)
    print(f"{len(files)} datoteka, {total / 1024:.0f} KB")

    if not go:
        for f in files:
            print("  →", f.relative_to(ROOT))
        print("\nDRY RUN. Dodaj --go za stvarni deploy.")
        return

    ftp = ftplib.FTP_TLS(env["FTP_HOST"], timeout=30)
    ftp.login(env["FTP_USER"], env["FTP_PASS"])
    ftp.prot_p()  # kriptiraj i data kanal
    print("✓ spojen (FTPS):", ftp.getwelcome()[:60])

    made_dirs = set()
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        rdir = "/".join(rel.split("/")[:-1])
        if rdir and rdir not in made_dirs:
            ensure_dir(ftp, rdir)
            made_dirs.add(rdir)
        with open(f, "rb") as fh:
            ftp.storbinary(f"STOR /{rel}", fh)
        print("  ↑", rel)

    ftp.quit()
    print("\n✓ Deploy gotov → https://shtimung.hr")


if __name__ == "__main__":
    main()
