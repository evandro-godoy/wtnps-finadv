# src/gui/monitor_ui.py

"""
Interface Gráfica para o Monitor de Trading em Tempo Real.

Utiliza tkinter para criar uma GUI moderna que controla o RealTimeMonitor
e exibe alertas/logs em tempo real de forma thread-safe.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import logging
from collections import deque
from datetime import datetime
from pathlib import Path
import sys
from typing import Deque

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.event_bus import event_bus
from src.events import InferenceSignalEvent, MarketDataCandleEvent
from src.live.monitor_engine import RealTimeMonitor
from src.live.replay_engine import ReplayEngine

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)


class MonitorApp:
    """
    Aplicação GUI para controle e visualização do Monitor em Tempo Real.
    
    Features:
    - Suporte a modo Live e Replay
    - Header com informações do ativo (Ticker, Preço, Timeframe, Status)
    - Gráfico de candlestick integrado
    - Botão Start/Stop para controlar o monitor
    - Notebook com tabs para logs ML e análise técnica
    - Controles de replay (data, hora, velocidade, play/pause/step)
    - Comunicação thread-safe entre monitor e UI via Queue
    """
    
    def __init__(self, root, mode='live', replay_config=None):
        """
        Inicializa a aplicação GUI.
        
        Args:
            root: Janela raiz do tkinter
            mode: 'live' ou 'replay'
            replay_config: dict com {ticker, start_date, start_time, timeframe, speed}
        """
        self.root = root
        self.root.title("WTNPS-TRADE - Monitor em Tempo Real")
        self.root.resizable(True, True)
        
        # Modo de operação
        self.mode = mode
        self.replay_config = replay_config or {}
        
        # Configurações do monitor (editáveis via UI agora)
        self.ticker = self.replay_config.get('ticker', 'WDO$')
        self.timeframe = self.replay_config.get('timeframe', 'M5')
        self.threshold_alert = 0.65
        self.threshold_log = 0.55
        self.buffer_size = 500
        
        # Estado da aplicação
        self.monitor = None
        self.monitor_thread = None
        self.is_running = False
        self.last_candle = {
            'timestamp': None,
            'Open': 0.0,
            'High': 0.0,
            'Low': 0.0,
            'Close': 0.0,
            'Volume': 0
        }
        
        # Queue para comunicação thread-safe
        self.update_queue = queue.Queue()

        # Buffer local de candles para exibição (sem acesso ao buffer interno do monitor)
        self.candle_buffer: Deque[dict] = deque(maxlen=self.buffer_size)
        
        # Janela de buffer (inicialmente None)
        self.buffer_window = None
        
        # Chart widget (será inicializado em _build_ui)
        self.chart_widget = None
        
        # Configura estilos
        self._setup_styles()
        
        # Constrói interface
        self._build_ui()

        # Registra handlers no EventBus
        self._register_event_handlers()
        
        # Inicia polling da queue
        self._poll_queue()
        
        logger.info(f"Interface GUI inicializada em modo {mode.upper()}")
    
    def _setup_styles(self):
        """Configura estilos visuais do ttk."""
        style = ttk.Style()
        style.theme_use('clam')  # Tema moderno
        
        # Estilo para botão Start
        style.configure(
            'Start.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=10,
            background='#28a745',
            foreground='white'
        )
        
        # Estilo para botão Stop
        style.configure(
            'Stop.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=10,
            background='#dc3545',
            foreground='white'
        )
        
        # Estilo para Treeview
        style.configure(
            'Monitor.Treeview',
            font=('Segoe UI', 10),
            rowheight=30
        )
        style.configure(
            'Monitor.Treeview.Heading',
            font=('Segoe UI', 10, 'bold'),
            background='#343a40',
            foreground='white'
        )
    
    def _build_ui(self):
        """Constrói a interface gráfica completa com layout responsivo."""
        # Container principal
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky='nsew')
        
        # Configura grid weights para expansão responsiva
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=3)  # Área principal (75%)
        main_container.columnconfigure(1, weight=1)  # Controles (25%)
        main_container.rowconfigure(1, weight=1)  # Content area expande
        
        # === ROW 0: HEADER + CONTROLS ===
        self._build_header(main_container)       # row=0, col=0
        self._build_controls(main_container)     # row=0, col=1
        
        # === ROW 1: CHART + LOGS (com PanedWindow) ===
        content_pane = ttk.PanedWindow(main_container, orient=tk.VERTICAL)
        content_pane.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=(10, 0))
        
        # Chart (superior)
        self._build_chart_area(content_pane)
        
        # Logs (inferior - Notebook com tabs)
        self._build_logs_area(content_pane)
    
    def _build_header(self, parent):
        """
        Constrói o header com informações do ativo.
        
        Exibe: Ticker, Timeframe, Dados do Último Candle (Hora UTC + OHLC)
        """
        header_frame = ttk.LabelFrame(parent, text="Informações do Ativo", padding="10")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Container para dados do ativo
        info_container = ttk.Frame(header_frame)
        info_container.pack(fill=tk.X)
        
        # === TICKER ===
        ticker_frame = ttk.Frame(info_container)
        ticker_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(
            ticker_frame,
            text="Ticker:",
            font=('Segoe UI', 12)
        ).pack(anchor=tk.W)
        
        self.ticker_label = ttk.Label(
            ticker_frame,
            text=self.ticker,
            font=('Segoe UI', 10, 'bold'),
            foreground='#000000'
        )
        self.ticker_label.pack(anchor=tk.W)
        
        # === TIMEFRAME ===
        tf_frame = ttk.Frame(info_container)
        tf_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(
            tf_frame,
            text="Timeframe:",
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W)
        
        self.timeframe_label = ttk.Label(
            tf_frame,
            text=self.timeframe,
            font=('Segoe UI', 8, 'bold'),
            foreground='#6c757d'
        )
        self.timeframe_label.pack(anchor=tk.W)
        
        # === DADOS DO ÚLTIMO CANDLE ===
        candle_frame = ttk.Frame(info_container)
        candle_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(
            candle_frame,
            text="Último Candle (UTC):",
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W)
        
        # Container horizontal para OHLC
        ohlc_container = ttk.Frame(candle_frame)
        ohlc_container.pack(anchor=tk.W)
        
        # Hora
        self.candle_time_label = ttk.Label(
            ohlc_container,
            text="--:--:--",
            font=('Segoe UI', 14, 'bold'),
            foreground='#28a745'
        )
        self.candle_time_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # OHLC
        ohlc_data_frame = ttk.Frame(ohlc_container)
        ohlc_data_frame.pack(side=tk.LEFT)
        
        self.ohlc_label = ttk.Label(
            ohlc_data_frame,
            text="O: ---- | H: ---- | L: ---- | C: ----",
            font=('Segoe UI', 11),
            foreground='#495057'
        )
        self.ohlc_label.pack()
    
    def _build_controls(self, parent):
        """
        Constrói área de controles.
        
        Botão Iniciar/Parar com indicador de status (semáforo) ao lado.
        Posicionado à direita do header.
        """
        controls_container = ttk.LabelFrame(parent, text="Controles do Monitor", padding="10")
        controls_container.grid(row=0, column=1, sticky=(tk.E, tk.N), pady=(0, 10))
        
        # Botão Iniciar/Parar
        self.start_stop_btn = ttk.Button(
            controls_container,
            text="▶ Iniciar",
            command=self._toggle_monitor,
            style='Start.TButton',
            width=10
        )
        self.start_stop_btn.pack(pady=(0, 8))
        
        # Container para semáforo
        status_frame = ttk.Frame(controls_container)
        status_frame.pack()
        
        ttk.Label(
            status_frame,
            text="Status:",
            font=('Segoe UI', 8)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Canvas para círculo do semáforo
        self.status_canvas = tk.Canvas(
            status_frame,
            width=25,
            height=25,
            bg='#f0f0f0',
            highlightthickness=0
        )
        self.status_canvas.pack(side=tk.LEFT)
        
        # Desenha círculo vermelho (parado)
        self.status_indicator = self.status_canvas.create_oval(
            3, 3, 22, 22,
            fill='#dc3545',
            outline='#6c757d',
            width=2
        )
    
    def _build_chart_area(self, parent):
        """
        Constrói área do gráfico de candlestick.
        
        Args:
            parent: PanedWindow pai
        """
        try:
            from src.gui.chart_widget import CandlestickChartWidget
            
            chart_frame = ttk.LabelFrame(parent, text="Gráfico de Candles", padding="5")
            
            self.chart_widget = CandlestickChartWidget(
                chart_frame,
                max_candles=200
            )
            self.chart_widget.pack(fill=tk.BOTH, expand=True)
            
            parent.add(chart_frame, weight=1)
            
            logger.info("Área de gráfico construída")
        except Exception as e:
            logger.error(f"Erro ao construir chart widget: {e}", exc_info=True)
            # Continua sem chart se houver erro
            pass
    
    def _build_logs_area(self, parent):
        """
        Constrói área de logs/alertas com Notebook (tabs).
        
        Tab 1: Sinais ML (datetime, type, price, prob, message)
        Tab 2: Análise Técnica (datetime, trend, rsi, ema9, sma20, sma50)
        """
        logs_frame = ttk.LabelFrame(parent, text="Logs e Alertas", padding="5")
        
        # Botões de ação (topo)
        btn_frame = ttk.Frame(logs_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(btn_frame, text="🗑 Limpar Logs", command=self._clear_logs, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Ver Buffer", command=self._show_buffer_window, width=12).pack(side=tk.LEFT, padx=5)
        
        # Notebook com 2 tabs
        notebook = ttk.Notebook(logs_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Sinais ML
        self._build_ml_signals_tab(notebook)
        
        # Tab 2: Análise Técnica
        self._build_technical_tab(notebook)
        
        # Adiciona ao PanedWindow
        parent.add(logs_frame, weight=1)
    
    def _build_ml_signals_tab(self, notebook):
        """Constrói tab de sinais ML."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Sinais ML")
        
        # Container com scrollbars
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Scrollbars
        ml_vsb = ttk.Scrollbar(container, orient="vertical")
        ml_hsb = ttk.Scrollbar(container, orient="horizontal")
        
        # Treeview
        self.logs_tree = ttk.Treeview(
            container,
            columns=('datetime', 'type', 'price', 'probability', 'message'),
            show='headings',
            yscrollcommand=ml_vsb.set,
            xscrollcommand=ml_hsb.set,
            style='Monitor.Treeview'
        )
        
        ml_vsb.config(command=self.logs_tree.yview)
        ml_hsb.config(command=self.logs_tree.xview)
        
        self.logs_tree.grid(row=0, column=0, sticky='nsew')
        ml_vsb.grid(row=0, column=1, sticky='ns')
        ml_hsb.grid(row=1, column=0, sticky='ew')
        
        # Configura colunas
        self.logs_tree.heading('datetime', text='Data/Hora (UTC)')
        self.logs_tree.heading('type', text='Tipo')
        self.logs_tree.heading('price', text='Preço')
        self.logs_tree.heading('probability', text='Prob. ML (%)')
        self.logs_tree.heading('message', text='Mensagem')
        
        self.logs_tree.column('datetime', width=180, anchor=tk.W)
        self.logs_tree.column('type', width=80, anchor=tk.CENTER)
        self.logs_tree.column('price', width=120, anchor=tk.E)
        self.logs_tree.column('probability', width=100, anchor=tk.E)
        self.logs_tree.column('message', width=500, anchor=tk.W)
        
        # Tags
        self.logs_tree.tag_configure('ALERT', background='#fff3cd', foreground='#856404')
        self.logs_tree.tag_configure('INFO', background='#d1ecf1', foreground='#0c5460')
        self.logs_tree.tag_configure('TICK', background='#ffffff', foreground='#6c757d')
    
    def _build_technical_tab(self, notebook):
        """Constrói tab de análise técnica."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Análise Técnica")
        
        # Container com scrollbars
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Scrollbars
        tech_vsb = ttk.Scrollbar(container, orient="vertical")
        tech_hsb = ttk.Scrollbar(container, orient="horizontal")
        
        # Treeview
        self.analysis_tree = ttk.Treeview(
            container,
            columns=('datetime', 'trend', 'rsi', 'ema9', 'sma20', 'sma50'),
            show='headings',
            yscrollcommand=tech_vsb.set,
            xscrollcommand=tech_hsb.set,
            style='Monitor.Treeview'
        )
        
        tech_vsb.config(command=self.analysis_tree.yview)
        tech_hsb.config(command=self.analysis_tree.xview)
        
        self.analysis_tree.grid(row=0, column=0, sticky='nsew')
        tech_vsb.grid(row=0, column=1, sticky='ns')
        tech_hsb.grid(row=1, column=0, sticky='ew')
        
        # Configura colunas
        self.analysis_tree.heading('datetime', text='Data/Hora (UTC)')
        self.analysis_tree.heading('trend', text='Tendência')
        self.analysis_tree.heading('rsi', text='RSI')
        self.analysis_tree.heading('ema9', text='EMA9')
        self.analysis_tree.heading('sma20', text='SMA20')
        self.analysis_tree.heading('sma50', text='SMA50')
        
        self.analysis_tree.column('datetime', width=180, anchor=tk.W)
        self.analysis_tree.column('trend', width=120, anchor=tk.CENTER)
        self.analysis_tree.column('rsi', width=100, anchor=tk.CENTER)
        self.analysis_tree.column('ema9', width=100, anchor=tk.E)
        self.analysis_tree.column('sma20', width=100, anchor=tk.E)
        self.analysis_tree.column('sma50', width=100, anchor=tk.E)
        
        # Tags
        self.analysis_tree.tag_configure('ALERT', background='#fff3cd')
        self.analysis_tree.tag_configure('INFO', background='#d1ecf1')
        self.analysis_tree.tag_configure('TICK', background='#ffffff')

    def _register_event_handlers(self) -> None:
        """Registra handlers de eventos no EventBus."""
        event_bus.subscribe("MARKET_DATA_CANDLE", self._on_market_data_event)
        event_bus.subscribe("INFERENCE_SIGNAL", self._on_inference_signal_event)

    def _on_market_data_event(self, event: MarketDataCandleEvent) -> None:
        """Handler para eventos de candle do EventBus."""
        self.update_queue.put({
            'action': 'candle_event',
            'event': event,
        })

    def _on_inference_signal_event(self, event: InferenceSignalEvent) -> None:
        """Handler para eventos de inferência do EventBus."""
        self.update_queue.put({
            'action': 'signal_event',
            'event': event,
        })
    
    def _toggle_analysis_grid(self):
        """Método obsoleto - mantido para compatibilidade."""
        pass
    
    def _toggle_monitor(self):
        """
        Alterna entre iniciar e parar o monitor.
        
        Inicia o monitor em thread separada ou solicita parada.
        """
        if not self.is_running:
            # Iniciar monitor
            self._start_monitor()
        else:
            # Parar monitor
            self._stop_monitor()
    
    def _start_monitor(self):
        """Inicia o monitor em thread separada (Live ou Replay conforme modo)."""
        try:
            logger.info(f"Iniciando monitor em modo {self.mode.upper()}...")
            
            # Atualiza UI
            self.is_running = True
            self.start_stop_btn.config(
                text="■ Parar",
                style='Stop.TButton'
            )
            # Atualiza semáforo para verde
            self.status_canvas.itemconfig(self.status_indicator, fill='#28a745')
            
            # Cria instância do monitor conforme o modo
            if self.mode == 'live':
                # Modo Live - usa RealTimeMonitor
                self.monitor = RealTimeMonitor(
                    ticker=self.ticker,
                    timeframe_str=self.timeframe,
                    threshold_alert=self.threshold_alert,
                    threshold_log=self.threshold_log,
                    buffer_size=self.buffer_size
                )
            else:
                # Modo Replay - usa ReplayEngine
                from datetime import datetime, timedelta
                
                start_date = self.replay_config.get('start_date', '2025-11-20')
                start_time = self.replay_config.get('start_time', '09:00')
                speed = self.replay_config.get('speed', 1.0)
                
                # Calcula end_date (1 dia após start)
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = start_dt + timedelta(days=1)
                
                self.monitor = ReplayEngine(
                    ticker=self.ticker,
                    start_date=start_date,
                    end_date=end_dt.strftime('%Y-%m-%d'),
                    start_time=start_time,
                    timeframe_str=self.timeframe,
                    buffer_size=self.buffer_size,
                    speed_multiplier=speed,
                    config_path="configs/main.yaml",
                    progress_callback=self._on_replay_progress
                )
            
            # Inicia monitor em thread separada
            self.monitor_thread = threading.Thread(
                target=self._run_monitor,
                daemon=True
            )
            self.monitor_thread.start()
            
            logger.info("Monitor iniciado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar monitor: {e}", exc_info=True)
            messagebox.showerror(
                "Erro",
                f"Falha ao iniciar monitor:\n{str(e)}\n\nVerifique se o MT5 está aberto e logado."
            )
            self._reset_ui_state()
    
    def _on_replay_progress(self, current: int, total: int):
        """Callback de progresso do replay (se houver progressbar)."""
        # Por enquanto apenas loga, pode ser expandido com progressbar no futuro
        if total > 0 and current % 50 == 0:
            progress_pct = (current / total) * 100
            logger.info(f"Progresso do replay: {progress_pct:.1f}% ({current}/{total})")
    
    def _run_monitor(self):
        """Executa o loop do monitor (roda em thread separada)."""
        try:
            self.monitor.start()
        except Exception as e:
            logger.error(f"Erro no monitor: {e}", exc_info=True)
            self.update_queue.put({
                'action': 'error',
                'message': str(e)
            })
        finally:
            self.update_queue.put({'action': 'stopped'})
    
    def _stop_monitor(self):
        """Para o monitor."""
        try:
            logger.info("Parando monitor...")
            
            if self.monitor:
                self.monitor.stop()
            
            # Aguarda thread finalizar (com timeout)
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            self._reset_ui_state()
            
            logger.info("Monitor parado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao parar monitor: {e}", exc_info=True)
            messagebox.showerror("Erro", f"Falha ao parar monitor:\n{str(e)}")
    
    def _reset_ui_state(self):
        """Reseta estado da UI para parado."""
        self.is_running = False
        self.start_stop_btn.config(
            text="▶ Iniciar",
            style='Start.TButton'
        )
        # Atualiza semáforo para vermelho
        self.status_canvas.itemconfig(self.status_indicator, fill='#dc3545')
    
    def _poll_queue(self):
        """
        Polling da queue de atualizações.
        
        Processa eventos da queue e atualiza UI (thread-safe).
        Executado periodicamente via root.after.
        """
        try:
            # Processa todos os eventos pendentes na queue
            while True:
                try:
                    event = self.update_queue.get_nowait()
                    
                    if event['action'] == 'candle_event':
                        self._process_candle_update(event['event'])
                    elif event['action'] == 'signal_event':
                        self._process_signal_update(event['event'])
                    elif event['action'] == 'stopped':
                        self._reset_ui_state()
                    elif event['action'] == 'error':
                        messagebox.showerror(
                            "Erro no Monitor",
                            f"Erro durante monitoramento:\n{event['message']}"
                        )
                        self._reset_ui_state()
                    
                except queue.Empty:
                    break
        
        except Exception as e:
            logger.error(f"Erro ao processar queue: {e}", exc_info=True)
        
        finally:
            # Reagenda polling (100ms)
            self.root.after(100, self._poll_queue)

    def _process_candle_update(self, event: MarketDataCandleEvent) -> None:
        """Atualiza header, gráfico e buffer local com dados de candle."""
        try:
            timestamp = event.timestamp
            self.last_candle['Open'] = event.Open
            self.last_candle['High'] = event.High
            self.last_candle['Low'] = event.Low
            self.last_candle['Close'] = event.Close
            self.last_candle['Volume'] = event.Volume
            self.last_candle['timestamp'] = timestamp

            self.candle_buffer.append({
                'timestamp': timestamp,
                'Open': event.Open,
                'High': event.High,
                'Low': event.Low,
                'Close': event.Close,
                'Volume': event.Volume,
            })

            time_str = timestamp.strftime('%H:%M:%S')
            self.candle_time_label.config(text=time_str)

            ohlc_text = (
                f"O: {event.Open:.2f} | H: {event.High:.2f} | "
                f"L: {event.Low:.2f} | C: {event.Close:.2f}"
            )
            self.ohlc_label.config(text=ohlc_text)

            if self.chart_widget:
                candle_dict = {
                    'time': timestamp,
                    'Open': event.Open,
                    'High': event.High,
                    'Low': event.Low,
                    'Close': event.Close,
                    'Volume': event.Volume,
                }
                self.chart_widget.add_candle(candle_dict)
        except Exception as exc:
            logger.error(f"Erro ao processar candle: {exc}", exc_info=True)

    def _process_signal_update(self, event: InferenceSignalEvent) -> None:
        """Atualiza grids de sinais e analise tecnica a partir da inferencia."""
        try:
            indicators = event.indicators or {}
            timestamp = event.timestamp
            datetime_str = timestamp.strftime('%d/%m/%Y %H:%M:%S')

            probability_pct = event.probability * 100
            if probability_pct >= self.threshold_alert * 100:
                event_type = 'ALERT'
            elif probability_pct >= self.threshold_log * 100:
                event_type = 'INFO'
            else:
                event_type = 'TICK'

            direction = 'HOLD'
            if event.ai_signal == 'COMPRA':
                direction = 'CALL'
            elif event.ai_signal == 'VENDA':
                direction = 'PUT'

            trend = indicators.get('trend', 'N/A')
            trend_strength = indicators.get('trend_strength', '')
            pattern = indicators.get('pattern', '')
            support = indicators.get('support', 0.0)
            resistance = indicators.get('resistance', 0.0)
            signal_valid = indicators.get('signal_valid', False)
            validation_reason = indicators.get('validation_reason', '')

            if event_type == 'ALERT':
                target = resistance if direction == 'CALL' else support
                validation_icon = "OK" if signal_valid else "WARN"
                message = (
                    f"{validation_icon} SINAL {direction} ({probability_pct:.1f}%) | "
                    f"Tendencia: {trend} ({trend_strength}) | "
                    f"Padrao: {pattern} | "
                    f"Alvo: {target:.2f}"
                )
            elif event_type == 'INFO':
                rsi = indicators.get('rsi', 0.0)
                rsi_condition = indicators.get('rsi_condition', '')
                message = (
                    f"Prob. moderada ({probability_pct:.1f}%) | "
                    f"Tendencia: {trend} | "
                    f"RSI: {rsi:.0f} ({rsi_condition})"
                )
            else:
                message = f"Candle processado | Tendencia: {trend}"

            price_str = f"R$ {event.price:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
            prob_str = f"{probability_pct:.1f}"

            self.logs_tree.insert(
                '',
                0,
                values=(datetime_str, event_type, price_str, prob_str, message),
                tags=(event_type,)
            )

            trend_str = trend
            if trend_strength and trend != 'N/A':
                trend_str = f"{trend} ({trend_strength[0]})"

            rsi = indicators.get('rsi', 0.0)
            rsi_condition = indicators.get('rsi_condition', '')
            if rsi > 0:
                rsi_str = f"{rsi:.0f}"
                if rsi_condition == 'SOBRECOMPRADO':
                    rsi_str += " 🔺"
                elif rsi_condition == 'SOBREVENDIDO':
                    rsi_str += " 🔻"
            else:
                rsi_str = "N/A"

            ema9 = indicators.get('ema_fast', indicators.get('ema_9', 0.0))
            sma20 = indicators.get('sma_fast', 0.0)
            sma50 = indicators.get('sma_slow', 0.0)

            ema9_str = f"{ema9:.0f}" if ema9 > 0 else "N/A"
            sma20_str = f"{sma20:.0f}" if sma20 > 0 else "N/A"
            sma50_str = f"{sma50:.0f}" if sma50 > 0 else "N/A"

            self.analysis_tree.insert(
                '',
                0,
                values=(datetime_str, trend_str, rsi_str, ema9_str, sma20_str, sma50_str),
                tags=(event_type,)
            )

            for tree in [self.logs_tree, self.analysis_tree]:
                children = tree.get_children()
                if len(children) > 1000:
                    for item in children[1000:]:
                        tree.delete(item)

            if children:
                self.logs_tree.see(children[0])

            if self.chart_widget:
                self.chart_widget.update_indicators(
                    ema9=indicators.get('ema_20', indicators.get('ema_fast')),
                    sma20=indicators.get('sma_20', indicators.get('sma_fast')),
                    sma50=indicators.get('sma_50', indicators.get('sma_slow')),
                    support=indicators.get('support'),
                    resistance=indicators.get('resistance')
                )
        except Exception as exc:
            logger.error(f"Erro ao processar sinal: {exc}", exc_info=True)
    
    def _clear_logs(self):
        """Limpa todos os logs de ambos os Treeviews e o gráfico."""
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
        
        # Limpa gráfico também
        if self.chart_widget:
            self.chart_widget.clear()
        
        logger.info("Logs e gráfico limpos")
    
    def _show_buffer_window(self):
        """Abre janela modal para exibir o buffer de dados."""
        if not self.candle_buffer:
            messagebox.showinfo(
                "Buffer Vazio",
                "Nenhum candle recebido via EventBus."
            )
            return
        
        # Fecha janela anterior se existir
        if self.buffer_window and self.buffer_window.winfo_exists():
            self.buffer_window.destroy()
        
        # Cria nova janela
        self.buffer_window = tk.Toplevel(self.root)
        self.buffer_window.title("Buffer de Dados - Último 500 Candles")
        self.buffer_window.geometry("900x600")
        
        # Frame container
        container = ttk.Frame(self.buffer_window, padding="10")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Label informativo
        info_label = ttk.Label(
            container,
            text=f"Total de registros: {len(self.candle_buffer)}",
            font=('Segoe UI', 10, 'bold')
        )
        info_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para Treeview
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        buffer_tree = ttk.Treeview(
            tree_frame,
            columns=('timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=buffer_tree.yview)
        hsb.config(command=buffer_tree.xview)
        
        # Grid
        buffer_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Configura colunas
        buffer_tree.heading('timestamp', text='Timestamp (UTC)')
        buffer_tree.heading('Open', text='Open')
        buffer_tree.heading('High', text='High')
        buffer_tree.heading('Low', text='Low')
        buffer_tree.heading('Close', text='Close')
        buffer_tree.heading('Volume', text='Volume')
        
        buffer_tree.column('timestamp', width=180, anchor=tk.W)
        buffer_tree.column('Open', width=120, anchor=tk.E)
        buffer_tree.column('High', width=120, anchor=tk.E)
        buffer_tree.column('Low', width=120, anchor=tk.E)
        buffer_tree.column('Close', width=120, anchor=tk.E)
        buffer_tree.column('Volume', width=100, anchor=tk.E)
        
        # Popula dados (ordem reversa - mais recentes primeiro)
        for candle in reversed(self.candle_buffer):
            timestamp = candle.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            buffer_tree.insert(
                '',
                'end',
                values=(
                    timestamp_str,
                    f"{candle.get('Open', 0.0):.2f}",
                    f"{candle.get('High', 0.0):.2f}",
                    f"{candle.get('Low', 0.0):.2f}",
                    f"{candle.get('Close', 0.0):.2f}",
                    int(candle.get('Volume', 0))
                )
            )
        
        # Botão fechar
        close_btn = ttk.Button(
            container,
            text="Fechar",
            command=self.buffer_window.destroy,
            width=15
        )
        close_btn.pack(pady=(10, 0))
    
    def run(self):
        """Inicia o loop principal da GUI."""
        logger.info("Iniciando loop principal da GUI")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Manipula fechamento da janela."""
        if self.is_running:
            if messagebox.askokcancel("Sair", "Monitor está rodando. Deseja parar e sair?"):
                self._stop_monitor()
                # Fecha janela de buffer se existir
                if self.buffer_window and self.buffer_window.winfo_exists():
                    self.buffer_window.destroy()
                self.root.destroy()
        else:
            # Fecha janela de buffer se existir
            if self.buffer_window and self.buffer_window.winfo_exists():
                self.buffer_window.destroy()
            self.root.destroy()


def main(mode='live', replay_config=None):
    """
    Função principal para executar a GUI.
    
    Args:
        mode: 'live' ou 'replay'
        replay_config: dict com configurações de replay
    """
    root = tk.Tk()
    app = MonitorApp(root, mode=mode, replay_config=replay_config)
    app.run()


if __name__ == "__main__":
    main()
