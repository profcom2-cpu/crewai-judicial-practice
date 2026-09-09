const form = document.getElementById("form");
const runBtn = document.getElementById("run");
const quitBtn = document.getElementById("quit");
const statusEl = document.getElementById("status");
const resultWrap = document.getElementById("result-wrap");
const resultEl = document.getElementById("result");
const pathsEl = document.getElementById("paths");

function showStatus(text, isError) {
  statusEl.hidden = false;
  statusEl.textContent = text;
  statusEl.classList.toggle("err", Boolean(isError));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  runBtn.disabled = true;
  resultWrap.hidden = true;
  showStatus("Экипаж работает. Обычно 1–3 минуты…");
  const data = new FormData(form);
  try {
    const started = await fetch("/api/run", { method: "POST", body: data });
    const body = await started.json();
    if (!started.ok) {
      throw new Error(body.error || "Не удалось запустить");
    }
    await poll(body.job_id);
  } catch (err) {
    showStatus(err.message || String(err), true);
    runBtn.disabled = false;
  }
});

async function poll(jobId) {
  for (;;) {
    const res = await fetch("/api/status/" + jobId);
    const job = await res.json();
    if (!res.ok) {
      throw new Error(job.error || "Нет статуса задачи");
    }
    if (job.status === "running") {
      showStatus("Экипаж работает…");
      await new Promise((r) => setTimeout(r, 2000));
      continue;
    }
    if (job.status === "error") {
      throw new Error(job.error || "Ошибка прогона");
    }
    showStatus("Готово.");
    pathsEl.textContent = [job.md_path, job.json_path].filter(Boolean).join(" · ");
    resultEl.textContent = job.diary_md || "";
    resultWrap.hidden = false;
    runBtn.disabled = false;
    return;
  }
}

quitBtn.addEventListener("click", async () => {
  try {
    await fetch("/api/shutdown", { method: "POST" });
  } finally {
    window.close();
  }
});
