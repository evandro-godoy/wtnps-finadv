/**
 * live_chart.js - WebSocket client and Plotly chart management for WTNPS Trade
 */

// Configuration
const WS_URL = 'ws://localhost:8000/ws/live-signals';
const API_BASE_URL = 'http://localhost:8000';
const MAX_CANDLES = 200; // Maximum number of candles to display
const MAX_HISTORY_ITEMS = 200; // Maximum signal history items to show

// State
let ws = null;
let chartData = {
    x: [],
    open: [],
    high: [],
    low: [],
    close: [],
    signals: []
};
let signalHistory = [];
let signalsCount = 0;
let startTime = null;
let historyScroller = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing WTNPS Trade Live Monitor...');
    initializeChart();
    initializeSplitLayout();
    connectWebSocket();
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    fetchLatestSignals();
});

/**
 * Initialize Plotly candlestick chart
 */
function initializeChart() {
    const ink = '#0b1b2b';
    const grid = '#d7cfc1';
    const bg = '#fffaf3';

    const trace = {
        x: chartData.x,
        close: chartData.close,
        high: chartData.high,
        low: chartData.low,
        open: chartData.open,
        type: 'candlestick',
        name: 'Price',
        increasing: { line: { color: '#16a34a' } },
        decreasing: { line: { color: '#dc2626' } }
    };

    const layout = {
        title: 'Live Candlestick Chart',
        xaxis: {
            title: 'Time',
            type: 'date',
            rangeslider: { visible: false },
            gridcolor: grid
        },
        yaxis: {
            title: 'Price',
            gridcolor: grid
        },
        paper_bgcolor: bg,
        plot_bgcolor: bg,
        font: { color: ink, family: 'IBM Plex Sans, sans-serif' },
        margin: { l: 60, r: 30, t: 60, b: 60 }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
    };

    Plotly.newPlot('candlestick-chart', [trace], layout, config);
}

function initializeSplitLayout() {
    if (typeof Split === 'undefined') {
        return;
    }

    Split(['#chart-pane', '#sidebar-pane'], {
        sizes: [72, 28],
        minSize: [320, 260],
        gutterSize: 10,
        gutterAlign: 'center',
        direction: window.innerWidth < 900 ? 'vertical' : 'horizontal'
    });
}

/**
 * Connect to WebSocket server
 */
function connectWebSocket() {
    console.log(`Connecting to WebSocket: ${WS_URL}`);
    updateConnectionStatus('Connecting...', false);

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('Online', true);
        startTime = Date.now();
        
        // Send ping every 30 seconds to keep connection alive
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send('ping');
            }
        }, 30000);
    };

    ws.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            console.log('Received message:', message);

            if (message.type === 'signal') {
                handleSignal(message.data);
            } else if (message.type === 'connection') {
                console.log('Connection message:', message.message);
            } else if (message.type === 'pong') {
                console.log('Pong received');
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('Error', false);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus('Offline', false);
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
            console.log('Attempting to reconnect...');
            connectWebSocket();
        }, 5000);
    };
}

/**
 * Handle incoming signal data
 */
function handleSignal(signal) {
    console.log('Processing signal:', signal);

    // Add candle data (assuming signal contains OHLC for the current candle)
    const timestamp = new Date(signal.timestamp);
    
    // Update chart data
    chartData.x.push(timestamp);
    chartData.close.push(signal.price);
    // Note: We don't have OHLC data from the signal, so we approximate
    // In production, you'd want to fetch full candle data
    chartData.open.push(signal.price);
    chartData.high.push(signal.price * 1.001);
    chartData.low.push(signal.price * 0.999);
    
    chartData.signals.push({
        time: timestamp,
        signal: signal.ai_signal,
        probability: signal.probability,
        price: signal.price
    });

    // Limit data size
    if (chartData.x.length > MAX_CANDLES) {
        chartData.x.shift();
        chartData.open.shift();
        chartData.high.shift();
        chartData.low.shift();
        chartData.close.shift();
        chartData.signals.shift();
    }

    // Update chart
    updateChart();

    // Update latest signal display
    updateLatestSignal(signal);

    // Add to signal history
    addSignalToHistory(signal);

    // Update stats
    signalsCount++;
    updateStats();
}

/**
 * Update Plotly chart with new data
 */
function updateChart() {
    const update = {
        x: [chartData.x],
        close: [chartData.close],
        high: [chartData.high],
        low: [chartData.low],
        open: [chartData.open]
    };

    Plotly.restyle('candlestick-chart', update, [0]);

    // Add signal markers (arrows)
    const annotations = chartData.signals
        .filter(s => s.signal !== 'HOLD')
        .map(s => ({
            x: s.time,
            y: s.price,
            text: s.signal === 'COMPRA' ? '▲' : '▼',
            showarrow: false,
            font: {
                size: 20,
                color: s.signal === 'COMPRA' ? '#16a34a' : '#dc2626'
            },
            yshift: s.signal === 'COMPRA' ? -20 : 20
        }));

    Plotly.relayout('candlestick-chart', { annotations });
}

/**
 * Update latest signal display in sidebar
 */
function updateLatestSignal(signal) {
    document.getElementById('signal-type').textContent = signal.ai_signal;
    document.getElementById('signal-type').className = `signal-value ${signal.ai_signal.toLowerCase()}`;
    
    document.getElementById('signal-probability').textContent = `${(signal.probability * 100).toFixed(1)}%`;
    document.getElementById('signal-price').textContent = signal.price.toFixed(2);
    
    const indicators = signal.indicators || {};
    document.getElementById('signal-trend').textContent = indicators.trend || '-';
    document.getElementById('signal-rsi').textContent = indicators.rsi ? indicators.rsi.toFixed(1) : '-';
    
    document.getElementById('last-update').textContent = `Atualizado: ${formatTime(new Date(signal.timestamp))}`;
}

/**
 * Add signal to history list
 */
function addSignalToHistory(signal) {
    signalHistory.unshift(signal);
    
    // Limit history size
    if (signalHistory.length > MAX_HISTORY_ITEMS) {
        signalHistory.pop();
    }

    renderSignalHistory();
}

/**
 * Render signal history list
 */
function renderSignalHistory() {
    const historyContainer = document.getElementById('signal-history');
    
    if (signalHistory.length === 0) {
        historyContainer.innerHTML = '<p class="empty-state">Aguardando sinais...</p>';
        return;
    }

    if (!historyScroller) {
        historyScroller = new PredictionVirtualScroll(historyContainer, { rowHeight: 64 });
    }

    historyScroller.setItems(signalHistory);
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(text, isOnline) {
    const statusText = document.getElementById('connection-status');
    const statusIndicator = document.getElementById('status-indicator');
    
    statusText.textContent = text;
    statusIndicator.className = `status-indicator ${isOnline ? 'online' : 'offline'}`;
}

/**
 * Update current time display
 */
function updateCurrentTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = formatTime(now);
}

/**
 * Update stats (candles, signals, uptime)
 */
function updateStats() {
    document.getElementById('candle-count').textContent = chartData.x.length;
    document.getElementById('signals-count').textContent = signalsCount;
    
    if (startTime) {
        const uptime = Math.floor((Date.now() - startTime) / 1000);
        document.getElementById('uptime').textContent = formatUptime(uptime);
    }
}

/**
 * Fetch latest signals from REST API (on page load)
 */
async function fetchLatestSignals() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/signals/latest?limit=200`);
        
        if (!response.ok) {
            console.warn('Failed to fetch latest signals');
            return;
        }

        const signals = await response.json();
        console.log(`Fetched ${signals.length} historical signals`);

        // Process historical signals
        signals.forEach(signal => {
            handleSignal(signal);
        });
    } catch (error) {
        console.error('Error fetching latest signals:', error);
    }
}

/**
 * Format timestamp for display
 */
function formatTime(date) {
    return date.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * Format uptime in human-readable format
 */
function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}
