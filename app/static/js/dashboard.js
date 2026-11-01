/**
 * DevOps Service Dashboard - Client Logic
 * Handles live health polling, theme toggling, and interactive API calculations.
 */

(function () {
  "use strict";

  // Elements
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const themeIcon = document.getElementById("themeIcon");
  const themeText = document.getElementById("themeText");

  const refreshHealthBtn = document.getElementById("refreshHealthBtn");
  const healthBadge = document.getElementById("healthBadge");
  const healthBadgeText = document.getElementById("healthBadgeText");

  const appNameEl = document.getElementById("appName");
  const appVersionEl = document.getElementById("appVersion");
  const pythonVersionEl = document.getElementById("pythonVersion");
  const appEnvEl = document.getElementById("appEnv");
  const lastCheckEl = document.getElementById("lastCheck");
  const latencyEl = document.getElementById("latency");

  const calcForm = document.getElementById("calcForm");
  const num1Input = document.getElementById("num1");
  const num2Input = document.getElementById("num2");
  const operationSelect = document.getElementById("operation");
  const calcSubmitBtn = document.getElementById("calcSubmitBtn");
  const responseStatusPill = document.getElementById("responseStatusPill");
  const responseCodeBox = document.getElementById("responseCodeBox");
  const copyResponseBtn = document.getElementById("copyResponseBtn");

  // --------------------------------------------------------------------------
  // 1. Theme Management (Dark / Light with LocalStorage & OS preference)
  // --------------------------------------------------------------------------
  function getPreferredTheme() {
    const saved = localStorage.getItem("devops_dashboard_theme");
    if (saved === "dark" || saved === "light") {
      return saved;
    }
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("devops_dashboard_theme", theme);

    if (themeToggleBtn) {
      themeToggleBtn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    }

    if (themeIcon && themeText) {
      if (theme === "dark") {
        themeIcon.textContent = "☀️";
        themeText.textContent = "Light Mode";
      } else {
        themeIcon.textContent = "🌙";
        themeText.textContent = "Dark Mode";
      }
    }
  }

  // Initialize theme
  applyTheme(getPreferredTheme());

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
    });
  }

  // Listen for OS theme preference changes if user hasn't explicitly set a preference
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("devops_dashboard_theme")) {
        applyTheme(e.matches ? "dark" : "light");
      }
    });
  }

  // --------------------------------------------------------------------------
  // 2. Health & Application Info Polling
  // --------------------------------------------------------------------------
  let isFetchingHealth = false;

  async function fetchHealthAndInfo() {
    if (isFetchingHealth) return;
    isFetchingHealth = true;

    if (refreshHealthBtn) {
      refreshHealthBtn.disabled = true;
      refreshHealthBtn.textContent = "Checking...";
    }

    healthBadge.className = "status-badge loading";
    healthBadgeText.textContent = "Checking...";

    const startTime = performance.now();

    try {
      // Fetch /health and /api/v1/info concurrently
      const [healthRes, infoRes] = await Promise.all([
        fetch("/health", { cache: "no-store", headers: { Accept: "application/json" } }),
        fetch("/api/v1/info", { cache: "no-store", headers: { Accept: "application/json" } }),
      ]);

      const durationMs = Math.round(performance.now() - startTime);

      if (!healthRes.ok || !infoRes.ok) {
        throw new Error(`Health HTTP ${healthRes.status}, Info HTTP ${infoRes.status}`);
      }

      const healthData = await healthRes.json();
      const infoData = await infoRes.json();

      // Update UI with real responses
      healthBadge.className = `status-badge ${healthData.status === "healthy" ? "healthy" : "error"}`;
      healthBadgeText.textContent = healthData.status || "Unknown";

      appNameEl.textContent = infoData.app_name || "Unknown";
      appVersionEl.textContent = infoData.version || "1.0.0";
      pythonVersionEl.textContent = infoData.python_version || "Unknown";
      appEnvEl.textContent = infoData.environment || "Unknown";

      const checkDate = new Date();
      lastCheckEl.textContent = checkDate.toLocaleTimeString() + " (" + checkDate.toISOString().slice(0, 10) + ")";
      latencyEl.textContent = `${durationMs} ms`;
    } catch (err) {
      healthBadge.className = "status-badge error";
      healthBadgeText.textContent = "Offline / Error";
      latencyEl.textContent = "N/A";
      lastCheckEl.textContent = new Date().toLocaleTimeString() + " (Failed)";
      console.warn("Failed to reach health endpoints:", err);
    } finally {
      isFetchingHealth = false;
      if (refreshHealthBtn) {
        refreshHealthBtn.disabled = false;
        refreshHealthBtn.textContent = "Refresh Status";
      }
    }
  }

  if (refreshHealthBtn) {
    refreshHealthBtn.addEventListener("click", fetchHealthAndInfo);
  }

  // Periodic polling every 30 seconds
  const POLL_INTERVAL = 30000;
  setInterval(() => {
    if (document.visibilityState === "visible") {
      fetchHealthAndInfo();
    }
  }, POLL_INTERVAL);

  // Initial fetch on page load
  fetchHealthAndInfo();

  // --------------------------------------------------------------------------
  // 3. Interactive API Calculator Form
  // --------------------------------------------------------------------------
  if (calcForm) {
    calcForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const num1Val = num1Input.value.trim();
      const num2Val = num2Input.value.trim();
      const operation = operationSelect.value;

      if (!num1Val || !num2Val) {
        renderResponse(400, {
          error: "Bad Request",
          message: "Please enter both numbers before submitting.",
        });
        return;
      }

      // Convert to float (or retain original string if not float for testing failure validation)
      const num1 = isNaN(Number(num1Val)) ? num1Val : Number(num1Val);
      const num2 = isNaN(Number(num2Val)) ? num2Val : Number(num2Val);

      calcSubmitBtn.disabled = true;
      calcSubmitBtn.textContent = "Calculating...";
      responseStatusPill.textContent = "Sending...";
      responseStatusPill.className = "response-status-pill";

      const startTime = performance.now();

      try {
        const response = await fetch("/api/v1/calculate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            operation: operation,
            num1: num1,
            num2: num2,
          }),
        });

        const duration = Math.round(performance.now() - startTime);
        let resultJson;
        try {
          resultJson = await response.json();
        } catch {
          resultJson = { error: "Parse Error", message: "Response is not valid JSON." };
        }

        renderResponse(response.status, resultJson, duration);
      } catch (networkError) {
        renderResponse(0, {
          error: "Network Error",
          message: networkError.message || "Failed to connect to /api/v1/calculate.",
        });
      } finally {
        calcSubmitBtn.disabled = false;
        calcSubmitBtn.textContent = "Execute Calculation";
      }
    });
  }

  function renderResponse(statusCode, data, durationMs) {
    if (!responseStatusPill || !responseCodeBox) return;

    if (statusCode === 200) {
      responseStatusPill.className = "response-status-pill s200";
      responseStatusPill.textContent = `200 OK (${durationMs}ms)`;
    } else if (statusCode === 0) {
      responseStatusPill.className = "response-status-pill s500";
      responseStatusPill.textContent = "Connection Failed";
    } else {
      responseStatusPill.className = "response-status-pill s400";
      responseStatusPill.textContent = `HTTP ${statusCode} ${durationMs ? `(${durationMs}ms)` : ""}`;
    }

    // Safely write textContent to avoid XSS
    responseCodeBox.textContent = JSON.stringify(data, null, 2);
  }

  if (copyResponseBtn && responseCodeBox) {
    copyResponseBtn.addEventListener("click", () => {
      const text = responseCodeBox.textContent;
      if (!text || text === "No calculation executed yet.") return;

      navigator.clipboard.writeText(text).then(() => {
        const originalText = copyResponseBtn.textContent;
        copyResponseBtn.textContent = "Copied!";
        setTimeout(() => {
          copyResponseBtn.textContent = originalText;
        }, 1500);
      });
    });
  }
})();
