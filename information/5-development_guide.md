# Development & Deployment Guide

This document explains how KrishiMitra is built, run locally in development, and finally deployed to the Raspberry Pi.

## Developer Environment (Local PC)

The development environment consists of the FastAPI backend and the React Vite frontend running in tandem.

### Starting the Backend
1. Open a terminal.
2. Navigate to `/backend`.
3. Activate the virtual environment (if using one).
4. Identify that all ML `.pkl` and `.json` files are properly stored in `/backend/model/`.
5. Run: `python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
   - Test endpoints by heading to `http://localhost:8000/docs` to see the native FastAPI SwaggerUI documentation.

### Starting the Frontend
1. Open a second terminal.
2. Navigate to `/frontend`.
3. Run `npm install` (first time only).
4. Run: `npm run dev`
5. Open your browser to `http://localhost:3000` or whatever address Vite provides. The frontend is configured via `vite.config.js` to proxy `/api/*` traffic automatically to `localhost:8000`.

### Simulation mode
When running on your laptop/PC, the `sensor_hub.py` (which targets Raspberry Pi GPIOs and I2C lines) won't run natively. However, the architecture is decoupled. You can use the `POST /api/sensors/manual` endpoint via standard Swagger UI or the Dashboard's manual control panel to inject "fake" sensor data directly into the system state and test ML prediction reactions visually.

---

## Deployment Environment (Raspberry Pi Edge Device)

Production deployment targets the Raspberry Pi physical hub.

### File Transport & Remote SSH Credentials
The system code is cloned over Git to the Pi workspace `/home/ess/.openclaw/workspace/smart-agriculture-advisory-system`.

To remotely invoke Git, SSH, or push configurations to the Pi over the network via bridging scripts, your system must use these exact credentials:
- **Hostname**: `ess` (or IP resolution `ess.local`)
- **Username**: `ess`
- **Password**: `2026`

**Windows Helper Scripts**: If deploying from a Windows environment where interactive SSH passwords fail for automation, two Python bridge scripts have been added locally:
- `clone_on_pi.py`: Uses `paramiko` to log into the Pi via SSH to clone the repository remotely.
- `exec_on_pi.py`: A reusable script to execute shell commands securely over SSH. It also supports transferring files using an `UPLOAD:local_path->remote_path` syntax.

### Quick Setup (`setup.sh` and `quick_deploy.sh`)
Included in `/deployment` are bash scripts. They automate:
1. `pip3` dependency installs (using `--ignore-installed typing_extensions` to seamlessly bypass Debian package locks, along with `--break-system-packages` for edge deployment).
2. The `npm install` and Node `npm run build` static compilation of the React app into pure HTML/CSS/JS files in the `/dist` directory.
3. Movement of `openclaw/*.md` files containing natural language knowledge over to the agent's memory banks.

### Systemd Services 
KrishiMitra includes native Ubuntu/Debian background process management, ensuring it reboots securely without human interaction.
There are 3 distinct services deployed to `/etc/systemd/system/`:
1. `krishimitra-backend.service`: Runs `uvicorn` on port 8000, and natively serves the React frontend `dist/` directory from `/`.
2. `krishimitra-sensors.service`: Runs the continuous `sensor_hub.py` sensing loop.
3. `krishimitra-tft.service`: Controls the ST7735 screen draw operations independent of the backend load.
