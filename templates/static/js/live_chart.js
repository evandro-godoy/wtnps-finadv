/**
 * live_chart.js - Candlestick chart with indicator overlays for WTNPS Trade Demo
 *
 * Fetches historical candles from /api/chart-data (default 1000 bars, WDO$ M5)
 * and renders:
 *   - Candlestick trace
 *   - SMA 21  (Blue   #0000FF)
 *   - SMA 200 (Black  #000000)
 *   - EMA 9   (Red    #FF0000)
 *
 * Also connects to the WebSocket for live signal updates.
 */

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const WS_URL = `ws://${location.host}/ws/live-signals`;
const API_BASE = `${location.origin}`;
const CHART_BARS = 1000;
const MAX_HISTORY_ITEMS = 200;

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let ws = null;
let signalHistory = [];
let signalsCount = 0;
let startTime = null;
let historyScroller = null;
let chartRendered = false;

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing WTNPS Trade Charts...');
    initializeSplitLayout();
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    fetchChartData();
    connectWebSocket();
});

// ---------------------------------------------------------------------------
// Fetch historical chart data and render
// ---------------------------------------------------------------------------
async function fetchChartData() {
    const statusEl = document.getElementById('connection-status');
    if (statusEl) statusEl.textContent = 'Loading data...';

    try {
        const resp = await fetch(`${API_BASE}/api/chart-data?ticker=WDO$&bars=${CHART_BARS}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        console.log(`Received ${data.bars} candles for ${data.ticker}`);
        renderChart(data);

        // Update prediction sidebar if available
        if (data.prediction) {
            updateLatestSignal({
                ai_signal: data.prediction.ai_signal,
                probability: data.prediction.probability,
                price: data.prediction.price,
                timestamp: new Date().toISOString(),
                indicators: {}
            });
        }
    } catch (err) {
        console.error('Failed to fetch chart data:', err);
        renderEmptyChart();
    }
}

// ---------------------------------------------------------------------------
// Render full chart with Plotly
// ---------------------------------------------------------------------------
function renderChart(data) {
    const candles = data.candles;
    if (!candles || candles.length === 0) {
        renderEmptyChart();
        return;
    }

    const times   = candles.map(c => c.time);
    const opens   = candles.map(c => c.open);
    const highs   = candles.map(c => c.high);
    const lows    = candles.map(c => c.low);
    const closes  = candles.map(c => c.close);
    const sma21   = candles.map(c => c.sma_21);
    const sma200  = candles.map(c => c.sma_200);
    const ema9    = candles.map(c => c.ema_9);

    // --- Traces ---
    const candlestickTrace = {
        x: times,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        type: 'candlestick',
        name: 'Price',
        increasing: { line: { color: '#16a34a' } },
        decreasing: { line: { color: '#dc2626' } },
        whiskerwidth: 0.5,
        hoverinfo: 'x+text',
    };

    const sma21Trace = {
        x: times,
        y: sma21,
        type: 'scatter',
        mode: 'lines',
        name: 'SMA 21',
        line: { color: '#0000FF', width: 1.5 },
        hovertemplate: 'SMA 21: %{y:.2f}<extra></extra>',
        connectgaps: false,
    };

    const sma200Trace = {
        x: times,
        y: sma200,
        type: 'scatter',
        mode: 'lines',
        name: 'SMA 200',
        line: { color: '#000000', width: 1.5 },
        hovertemplate: 'SMA 200: %{y:.2f}<extra></extra>',
        connectgaps: false,
    };

    const ema9Trace = {
        x: times,
        y: ema9,
        type: 'scatter',
        mode: 'lines',
        name: 'EMA 9',
        line: { color: '#FF0000', width: 1.5 },
        hovertemplate: 'EMA 9: %{y:.2f}<extra></extra>',
        connectgaps: false,
    };

    // --- Layout ---
    const bg   = '#fffaf3';
    const grid = '#d7cfc1';
    const ink  = '#0b1b2b';

    const layout = {
        title: {
            text: `${data.ticker} — ${data.timeframe}  (${data.bars} barras)`,
            font: { family: 'Space Grotesk, sans-serif', size: 18, color: ink },
        },
        xaxis: {
            type: 'date',
            rangeslider: { visible: false },
            gridcolor: grid,
            linecolor: grid,
        },
        yaxis: {
            title: 'Price',
            gridcolor: grid,
            linecolor: grid,
            side: 'right',
        },
        paper_bgcolor: bg,
        plot_bgcolor: bg,
        font: { color: ink, family: 'IBM Plex Sans, sans-serif' },
        margin: { l: 10, r: 60, t: 50, b: 50 },
        legend: {
            orientation: 'h',
            x: 0, y: 1.08,
            font: { size: 11 },
        },
        hovermode: 'x unified',
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        scrollZoom: true,
    };

    Plotly.newPlot(
        'candlestick-chart',
        [candlestickTrace, sma21Trace, sma200Trace, ema9Trace],
        layout,
        config,
    );

    chartRendered = true;

    // Update info panel
    const countEl = document.getElementById('candle-count');
    if (countEl) countEl.textContent = data.bars;
}

function renderEmptyChart() {
    const bg   = '#fffaf3';
    const grid = '#d7cfc1';
    const ink  = '#0b1b2b';

    Plotly.newPlot(
        'candlestick-chart',
        [{
            x: [], open: [], high: [], low: [], close: [],
            type: 'candlestick', name: 'Price',
        }],
        {
            title: 'Aguardando dados...',
            xaxis: { rangeslider: { visible: false }, gridcolor: grid },
            yaxis: { gridcolor: grid },
            paper_bgcolor: bg, plot_bgcolor: bg,
            font: { color: ink, family: 'IBM Plex Sans, sans-serif' },
            margin: { l: 60, r: 30, t: 60, b: 60 },
        },
        { responsive: true, displaylogo: false },
    );
}

// ---------------------------------------------------------------------------
// Split Layout
// ---------------------------------------------------------------------------
function initializeSplitLayout() {
    if (typeof Split === 'undefined') return;
    Split(['#chart-pane', '#sidebar-pane'], {
        sizes: [72, 28],
        minSize: [320, 260],
        gutterSize: 10,
        gutterAlign: 'center',
        direction: window.innerWidth < 900 ? 'vertical' : 'horizontal',
    });
}

// ---------------------------------------------------------------------------
// WebSocket for live signals
// ---------------------------------------------------------------------------
function connectWebSocket() {
    console.log(`Connecting to WebSocket: ${WS_URL}`);
    updateConnectionStatus('Connecting...', false);

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('Online', true);
        startTime = Date.now();
        setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) ws.send('ping');
        }, 30000);
    };

    ws.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            if (message.type === 'signal') {
                handleLiveSignal(message.data);
            }
        } catch (err) {
            console.error('WS parse error:', err);
        }
    };

    ws.onerror = () => updateConnectionStatus('Error', false);

    ws.onclose = () => {
        updateConnectionStatus('Offline', false);
        setTimeout(connectWebSocket, 5000);
    };
}

// ---------------------------------------------------------------------------
// Live signal handler
// ---------------------------------------------------------------------------
function handleLiveSignal(signal) {
    updateLatestSignal(signal);
    addSignalToHistory(signal);
    signalsCount++;
    updateStats();
}

// ---------------------------------------------------------------------------
// Sidebar updates
// ---------------------------------------------------------------------------
function updateLatestSignal(signal) {
    const setEl = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    };

    setEl('signal-type', signal.ai_signal);
    const sigEl = document.getElementById('signal-type');
    if (sigEl) sigEl.className = `signal-value ${signal.ai_signal.toLowerCase()}`;

    setEl('signal-probability', `${(signal.probability * 100).toFixed(1)}%`);
    setEl('signal-price', signal.price != null ? signal.price.toFixed(2) : '-');

    const ind = signal.indicators || {};
    setEl('signal-trend', ind.trend || '-');
    setEl('signal-rsi', ind.rsi ? ind.rsi.toFixed(1) : '-');

    setEl('last-update', `Atualizado: ${formatTime(new Date(signal.timestamp))}`);
}

function addSignalToHistory(signal) {
    signalHistory.unshift(signal);
    if (signalHistory.length > MAX_HISTORY_ITEMS) signalHistory.pop();
    renderSignalHistory();
}

function renderSignalHistory() {
    const container = document.getElementById('signal-history');
    if (!container) return;

    if (signalHistory.length === 0) {
        container.innerHTML = '<p class="empty-state">Aguardando sinais...</p>';
        return;
    }

    if (!historyScroller && typeof PredictionVirtualScroll !== 'undefined') {
        historyScroller = new PredictionVirtualScroll(container, { rowHeight: 64 });
    }

    if (historyScroller) {
        historyScroller.setItems(signalHistory);
    }
}

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------
function updateConnectionStatus(text, isOnline) {
    const statusText = document.getElementById('connection-status');
    const statusIndicator = document.getElementById('status-indicator');
    if (statusText) statusText.textContent = text;
    if (statusIndicator) statusIndicator.className = `status-indicator ${isOnline ? 'online' : 'offline'}`;
}

function updateCurrentTime() {
    const el = document.getElementById('current-time');
    if (el) el.textContent = formatTime(new Date());
}

function updateStats() {
    const el = document.getElementById('signals-count');
    if (el) el.textContent = signalsCount;
    if (startTime) {
        const uptimeEl = document.getElementById('uptime');
        if (uptimeEl) uptimeEl.textContent = formatUptime(Math.floor((Date.now() - startTime) / 1000));
    }
}

function formatTime(date) {
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function formatUptime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}
