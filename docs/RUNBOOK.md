# Troubleshooting Runbook

| Symptom | Check | Fix |
|---|---|---|
| Camera page loads forever, old image | `curl -I localhost:8080/shot.jpg` hangs | Server handled one connection at a time; switched to `ThreadingHTTPServer` |
| `no configuration file provided: not found` (docker compose) | `ls` – where is docker-compose.yml? | File was inside `snapshots/`; moved it to the project root |
| Board shows `NO DATA` on camera | `cat sim/state/board-01.json` – last update time | Expected: no command for 10 min. Run tests or monitor |
| Board does not answer `PING` | `pgrep -af fake_board`, `systemctl status lab-board@board-01` | Monitor resets it automatically; else `sudo systemctl restart lab-board@board-01` |
| Controller `DOWN ConnectionRefusedError` | `docker ps` | `docker start controller-02` |
| Version test fails | `python -m lab.flash board-02` | Wrong firmware was flashed; flash the version from `firmware/main.py` |
| Dashboard not reachable | `systemctl status lab-dashboard`, `journalctl -u lab-dashboard -n 50` | Check `.env`, certificate files and paths |
| Certificate expires soon | `python -m lab.cert_check` | `sudo bash certs/renew_if_needed.sh` (runs daily via timer) |