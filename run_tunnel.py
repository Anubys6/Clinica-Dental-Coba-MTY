import subprocess
import re
import time
import sys
import os

CLOUDFLARED = r"C:\Program Files (x86)\cloudflared\cloudflared.exe"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL_FILE = os.path.join(BASE_DIR, "tunnel_url.txt")
LOG_FILE = os.path.join(BASE_DIR, "tunnel.log")

def run():
    cmd = [CLOUDFLARED, "tunnel", "--protocol", "http2", "--url", "http://localhost:8090"]
    while True:
        print("[Tunnel Manager] Starting fresh cloudflared tunnel...", flush=True)
        with open(LOG_FILE, "a", encoding="utf-8") as log_out:
            log_out.write(f"\n--- Starting at {time.ctime()} ---\n")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            found_url = False
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                log_out.write(line)
                log_out.flush()
                
                # Check for active URL
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if match:
                    url = match.group(0)
                    with open(URL_FILE, "w", encoding="utf-8") as f:
                        f.write(url)
                    print(f"\n>>> ACTIVE_TUNNEL_URL: {url} <<<\n", flush=True)
                    found_url = True

                # If Cloudflare expired the quick tunnel, force restart
                if "Tunnel not found" in line or "Unauthorized" in line:
                    print(f"[Tunnel Manager] Detected expired quick tunnel ({line.strip()}). Terminating and refreshing...", flush=True)
                    proc.kill()
                    break

            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

            print(f"[Tunnel Manager] cloudflared exited. Restarting fresh in 2s...", flush=True)
            time.sleep(2)

if __name__ == "__main__":
    run()
