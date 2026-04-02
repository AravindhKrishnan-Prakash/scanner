const state = {
  polling: null,
};

async function fetchDashboard() {
  const response = await fetch("/api/dashboard", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Dashboard request failed: ${response.status}`);
  }
  return response.json();
}

function renderOpportunity(opportunity) {
  const leverageInfo = opportunity.leverage ? `
    <div class="leverage-badge">${opportunity.leverage} Leverage</div>
  ` : '';
  
  const marginInfo = opportunity.margin_required ? `
    <div><span>Margin</span><strong>${opportunity.margin_required}</strong></div>
  ` : '';
  
  const exposureInfo = opportunity.exposure ? `
    <div><span>Exposure</span><strong>${opportunity.exposure}</strong></div>
  ` : '';
  
  return `
    <article class="opportunity-card ${opportunity.action === "BUY" ? "buy" : "sell"}">
      <div class="card-topline">
        <span class="badge">${opportunity.action}</span>
        <span class="confidence">${opportunity.confidence}</span>
      </div>
      ${leverageInfo}
      <h3>${opportunity.asset}</h3>
      <div class="levels">
        <div><span>Entry</span><strong>${opportunity.entry}</strong></div>
        <div><span>Stop</span><strong>${opportunity.stop_loss}</strong></div>
        <div><span>Target</span><strong>${opportunity.target}</strong></div>
      </div>
      <div class="levels compact">
        <div><span>Position</span><strong>${opportunity.position_size}</strong></div>
        ${marginInfo}
        <div><span>Risk</span><strong>${opportunity.risk_amount}</strong></div>
        ${exposureInfo}
        <div><span>Window</span><strong>${opportunity.time_window}</strong></div>
      </div>
      <ul class="reasons">
        ${opportunity.reason.map((item) => `<li>${item}</li>`).join("")}
      </ul>
    </article>
  `;
}

function updateDashboard(snapshot) {
  const modePill = document.getElementById("mode-pill");
  const providerName = document.getElementById("provider-name");
  const tradingMode = document.getElementById("trading-mode");
  const indexTrend = document.getElementById("index-trend");
  const qualifiedCount = document.getElementById("qualified-count");
  const lastScan = document.getElementById("last-scan");
  const opportunityGrid = document.getElementById("opportunity-grid");
  const emptyState = document.getElementById("empty-state");
  const watchlistBody = document.getElementById("watchlist-body");
  const errorPanel = document.getElementById("error-panel");
  const errorList = document.getElementById("error-list");

  const modeText = snapshot.mode === "live" ? "Live Mode" : "Sample Mode";
  const leverageText = snapshot.use_leverage ? ` (${snapshot.leverage_multiplier}x)` : "";
  modePill.textContent = modeText + leverageText;
  
  providerName.textContent = snapshot.provider || "Unknown";
  
  const tradingModeText = snapshot.trading_mode === "intraday" ? "Intraday" : "Swing";
  tradingMode.textContent = tradingModeText;
  
  indexTrend.textContent = snapshot.market?.trend || "Unknown";
  qualifiedCount.textContent = String(snapshot.market?.qualified_trades || 0);
  lastScan.textContent = snapshot.last_scan_at
    ? `Last scan: ${new Date(snapshot.last_scan_at).toLocaleString()}`
    : "Waiting for first scan";

  if (snapshot.opportunities?.length) {
    opportunityGrid.innerHTML = snapshot.opportunities.map(renderOpportunity).join("");
    emptyState.classList.add("hidden");
  } else {
    opportunityGrid.innerHTML = "";
    emptyState.classList.remove("hidden");
  }

  watchlistBody.innerHTML = (snapshot.watchlist || [])
    .map(
      (item) => `
        <tr>
          <td>${item.symbol}</td>
          <td>${item.price}</td>
          <td>${item.vwap || 'N/A'}</td>
          <td>${item.trend}</td>
          <td><span class="st-${item.supertrend || 'neutral'}">${(item.supertrend || 'N/A').substring(0, 3).toUpperCase()}</span></td>
          <td>${item.adx}</td>
          <td>${item.rsi}</td>
          <td>${item.volume_ratio}x</td>
          <td><span class="status-chip">${item.status}</span></td>
        </tr>
      `
    )
    .join("");

  if (snapshot.errors?.length) {
    errorPanel.classList.remove("hidden");
    errorList.innerHTML = snapshot.errors.map((error) => `<li>${error}</li>`).join("");
  } else {
    errorPanel.classList.add("hidden");
    errorList.innerHTML = "";
  }
}

async function refreshDashboard() {
  try {
    const snapshot = await fetchDashboard();
    updateDashboard(snapshot);
  } catch (error) {
    console.error(error);
  }
}

async function triggerScan() {
  const button = document.getElementById("scan-now");
  button.disabled = true;
  button.textContent = "Scanning...";

  try {
    const response = await fetch("/api/scan-now", { method: "POST" });
    if (!response.ok) {
      throw new Error(`Scan failed: ${response.status}`);
    }
    updateDashboard(await response.json());
  } catch (error) {
    console.error(error);
  } finally {
    button.disabled = false;
    button.textContent = "Scan Now";
  }
}

document.getElementById("scan-now").addEventListener("click", triggerScan);
refreshDashboard();
state.polling = setInterval(refreshDashboard, 10000);
