"""Локальное десктоп-приложение: Starlette + окно Edge/Chrome --app."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import threading
import time
import uuid
import webbrowser
from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from practice_crew.config import (
    OLLAMA_MODEL,
    OUTPUT_DIR,
    PROJECT_ROOT,
    QWEN_API_KEY,
    QWEN_MODEL,
    llm_connection,
    normalize_llm_mode,
    probe_ollama,
)
from practice_crew.logging_setup import setup_logging
from practice_crew.run import run_practice_job

log = logging.getLogger("practice_crew")

WEB_DIR = PROJECT_ROOT / "web"
HOST = "127.0.0.1"
PORT = int(os.getenv("PRACTICE_CREW_PORT", "8765"))
UPLOAD_DIR = OUTPUT_DIR / "uploads"

_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()
_server: uvicorn.Server | None = None


def _health(_request: Request) -> JSONResponse:
    ollama_ok, ollama_detail = probe_ollama()
    return JSONResponse(
        {
            "ok": True,
            "app": "practice-crew",
            "cloud": {"model": QWEN_MODEL, "configured": bool(QWEN_API_KEY)},
            "ollama": {
                "model": OLLAMA_MODEL,
                "reachable": ollama_ok,
                "detail": ollama_detail,
            },
        }
    )


def _index(_request: Request) -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


async def _api_run(request: Request) -> JSONResponse:
    form = await request.form()
    topic = str(form.get("topic") or "").strip()
    upload = form.get("file")
    file_path: Path | None = None
    if upload is not None and getattr(upload, "filename", None):
        name = Path(str(upload.filename)).name
        if Path(name).suffix.lower() not in {".txt", ".md", ".docx"}:
            return JSONResponse({"error": "Нужен файл txt, md или docx"}, status_code=400)
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        dest = UPLOAD_DIR / f"{uuid.uuid4().hex}_{name}"
        data = await upload.read()
        dest.write_bytes(data)
        file_path = dest
    if not topic and file_path is None:
        return JSONResponse({"error": "Укажите тему или приложите файл"}, status_code=400)
    try:
        llm_mode = normalize_llm_mode(str(form.get("llm_mode") or "") or None)
        mode, _key, base, model = llm_connection(llm_mode)
    except (RuntimeError, ValueError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=503)

    job_id = uuid.uuid4().hex
    with _jobs_lock:
        _jobs[job_id] = {"status": "running", "log": f"Режим {mode} ({model})\n"}
    log.info("UI-задача %s режим=%s модель=%s тема=%r файл=%s", job_id, mode, model, topic, file_path)
    threading.Thread(
        target=_run_job,
        args=(job_id, topic, file_path, llm_mode),
        daemon=True,
        name=f"practice-job-{job_id[:8]}",
    ).start()
    return JSONResponse({"job_id": job_id})


def _run_job(job_id: str, topic: str, file_path: Path | None, llm_mode: str | None = None) -> None:
    try:
        result = run_practice_job(topic=topic, file_path=file_path, llm_mode=llm_mode)
        with _jobs_lock:
            _jobs[job_id] = {"status": "done", **result}
        log.info("UI-задача %s готова: %s", job_id, result.get("md_path"))
    except Exception as exc:
        log.exception("UI-задача %s упала", job_id)
        with _jobs_lock:
            _jobs[job_id] = {"status": "error", "error": str(exc)}


def _api_status(request: Request) -> JSONResponse:
    job_id = request.path_params["job_id"]
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "Задача не найдена"}, status_code=404)
    return JSONResponse(job)


async def _api_shutdown(_request: Request) -> JSONResponse:
    log.info("Остановка десктоп-приложения из UI")

    def _stop() -> None:
        time.sleep(0.3)
        if _server is not None:
            _server.should_exit = True

    threading.Thread(target=_stop, daemon=True).start()
    return JSONResponse({"ok": True})


def build_app() -> Starlette:
    routes = [
        Route("/", _index),
        Route("/api/health", _health),
        Route("/api/run", _api_run, methods=["POST"]),
        Route("/api/status/{job_id}", _api_status),
        Route("/api/shutdown", _api_shutdown, methods=["POST"]),
        Mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static"),
    ]
    return Starlette(debug=False, routes=routes)


def _open_app_window(url: str) -> None:
    candidates = [
        (shutil.which("msedge"), ["--app=" + url]),
        (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", ["--app=" + url]),
        (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", ["--app=" + url]),
        (shutil.which("chrome"), ["--app=" + url]),
        (
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            ["--app=" + url],
        ),
    ]
    for exe, extra in candidates:
        if not exe or not Path(exe).is_file():
            continue
        try:
            subprocess.Popen([exe, *extra], close_fds=True)
            log.info("Окно приложения: %s %s", exe, extra)
            return
        except OSError:
            continue
    webbrowser.open(url)
    log.info("Открыт браузер по умолчанию: %s", url)


def main() -> int:
    setup_logging()
    if not WEB_DIR.is_dir():
        log.error("Нет папки web/: %s", WEB_DIR)
        return 1
    global _server
    config = uvicorn.Config(build_app(), host=HOST, port=PORT, log_level="warning")
    _server = uvicorn.Server(config)
    thread = threading.Thread(target=_server.run, daemon=True, name="practice-web")
    thread.start()
    url = f"http://{HOST}:{PORT}/"
    deadline = time.time() + 20
    while time.time() < deadline and not _server.started:
        time.sleep(0.1)
    if not _server.started:
        log.error("Сервер UI не поднялся на %s", url)
        return 1
    log.info("Десктоп UI слушает %s", url)
    _open_app_window(url)
    try:
        while thread.is_alive() and not _server.should_exit:
            time.sleep(0.4)
    except KeyboardInterrupt:
        _server.should_exit = True
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
