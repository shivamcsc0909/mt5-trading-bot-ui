import math
import random
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox


class MT5TradingBotUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MT5 Trading Bot | Strategy Control Center")
        self.geometry("1560x920")
        self.minsize(1280, 780)
        self.configure(bg="#07111f")

        self.running = False
        self.paused = False
        self.current_price = 2310.0
        self.chart_points = [self.current_price + math.sin(i / 3) * 4 for i in range(48)]
        self.log_lines = []
        self.chart_mode = "Candles"

        self._setup_style()
        self._build_ui()
        self._seed_demo_content()
        self._tick()

    # ----------------------------- Theme -----------------------------
    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#07111f", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[16, 10], background="#102136", foreground="#dce8ff")
        style.map("TNotebook.Tab", background=[("selected", "#173055")], foreground=[("selected", "#ffffff")])
        style.configure("TButton", padding=[12, 8], font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", background="#5b8cff", foreground="white")
        style.map("Primary.TButton", background=[("active", "#4a7bea")])
        style.configure("Success.TButton", background="#38d9a9", foreground="#062115")
        style.map("Success.TButton", background=[("active", "#2fb892")])
        style.configure("Danger.TButton", background="#ff6b6b", foreground="white")
        style.map("Danger.TButton", background=[("active", "#ff5252")])
        style.configure("Dark.TButton", background="#13253f", foreground="#e8eefc")
        style.map("Dark.TButton", background=[("active", "#1b355c")])
        style.configure("Treeview", background="#0b1627", fieldbackground="#0b1627", foreground="#e8eefc", rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background="#13253f", foreground="#e8eefc", relief="flat", font=("Segoe UI", 10, "bold"))
        style.map("Treeview.Heading", background=[("active", "#1b355c")])

    def _panel(self, parent, title, subtitle=None):
        outer = tk.Frame(parent, bg="#07111f")
        inner = tk.Frame(outer, bg="#0d1b2e", highlightthickness=1, highlightbackground="#1a3357")
        inner.pack(fill="both", expand=True, padx=4, pady=4)

        head = tk.Frame(inner, bg="#0d1b2e")
        head.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(head, text=title, bg="#0d1b2e", fg="#eff5ff", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(head, text=subtitle, bg="#0d1b2e", fg="#8fa3c2", font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        body = tk.Frame(inner, bg="#0d1b2e")
        body.pack(fill="both", expand=True, padx=0, pady=(0, 12))
        return outer, body

    def _label(self, parent, text, row, col, sticky="w"):
        tk.Label(parent, text=text, bg="#0d1b2e", fg="#8fa3c2", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=col, sticky=sticky, padx=16, pady=(10, 4)
        )

    def _entry(self, parent, row, col, value="", width=28):
        widget = tk.Entry(
            parent,
            width=width,
            bg="#09111d",
            fg="#e8eefc",
            insertbackground="#e8eefc",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#27405f",
        )
        widget.insert(0, value)
        widget.grid(row=row, column=col, sticky="we", padx=16, pady=(0, 6))
        return widget

    def _combo(self, parent, row, col, values, index=0, width=28):
        widget = ttk.Combobox(parent, values=values, state="readonly", width=width)
        widget.grid(row=row, column=col, sticky="we", padx=16, pady=(0, 6))
        if values:
            widget.current(index)
        return widget

    def _text(self, parent, row, col, value="", width=60, height=5, colspan=1):
        widget = tk.Text(
            parent,
            width=width,
            height=height,
            bg="#09111d",
            fg="#e8eefc",
            insertbackground="#e8eefc",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#27405f",
            wrap="word",
        )
        widget.insert("1.0", value)
        widget.grid(row=row, column=col, columnspan=colspan, sticky="we", padx=16, pady=(0, 6))
        return widget
    def _labeled_entry(self, parent, row, col, label, default="", width=28):
        self._label(parent, label, row, col)
        return self._entry(parent, row + 1, col, default, width)

    def _labeled_combo(self, parent, row, col, label, values, index=0, width=28):
        self._label(parent, label, row, col)
        return self._combo(parent, row + 1, col, values, index, width)

    def _labeled_text(self, parent, row, col, label, default="", width=60, height=5, colspan=1):
        self._label(parent, label, row, col)
        return self._text(parent, row + 1, col, default, width, height, colspan)

    def _toggle_row(self, parent, row, title, subtitle, variable):
        frame = tk.Frame(parent, bg="#101a2f", bd=0, highlightthickness=1, highlightbackground="#1b2b49")
        frame.grid(row=row, column=0, columnspan=2, sticky="we", padx=16, pady=8)

        left = tk.Frame(frame, bg="#101a2f")
        left.pack(side="left", padx=14, pady=12)
        tk.Label(left, text=title, bg="#101a2f", fg="#e8eefc", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(left, text=subtitle, bg="#101a2f", fg="#93a4c3", font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        btn = tk.Button(
            frame,
            textvariable=variable,
            bg="#1a2a4a",
            fg="#e8eefc",
            relief="flat",
            command=lambda: self._toggle_state(variable),
            cursor="hand2",
        )
        btn.pack(side="right", padx=14, pady=14)
    def _kpi(self, parent, title, value, subtitle):
        frame = tk.Frame(parent, bg="#0d1b2e", highlightthickness=1, highlightbackground="#1a3357")
        tk.Label(frame, text=title, bg="#0d1b2e", fg="#8fa3c2", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(14, 8))
        label = tk.Label(frame, text=value, bg="#0d1b2e", fg="#eff5ff", font=("Segoe UI", 21, "bold"))
        label.pack(anchor="w", padx=14)
        tk.Label(frame, text=subtitle, bg="#0d1b2e", fg="#8fa3c2", font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(8, 14))
        return frame, label

    def _badge(self, parent, text, fg="#89f0cb", bg="#163a32"):
        return tk.Label(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 9, "bold"), padx=12, pady=5)

    # ----------------------------- Build UI -----------------------------
    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg="#07111f")
        top.pack(fill="x", padx=18, pady=(16, 10))

        left = tk.Frame(top, bg="#07111f")
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="MT5 Trading Bot Control Center", bg="#07111f", fg="#eff5ff", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(left, text="Demo UI to present strategy inputs, risk controls, monitoring, and automated decision flow.", bg="#07111f", fg="#8fa3c2", font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        right = tk.Frame(top, bg="#07111f")
        right.pack(side="right")
        self.clock_label = tk.Label(right, text="--:--:--", bg="#102136", fg="#eff5ff", font=("Segoe UI", 16, "bold"), padx=16, pady=10)
        self.clock_label.pack(anchor="e", pady=(0, 8))
        self.status_badge = self._badge(right, "DEMO SIMULATION ACTIVE")
        self.status_badge.pack(anchor="e")

        # KPI row
        kpi_row = tk.Frame(self, bg="#07111f")
        kpi_row.pack(fill="x", padx=18, pady=(0, 12))
        self.kpi_balance, self.balance_value = self._kpi(kpi_row, "Balance", "$10,250", "Demo account balance")
        self.kpi_equity, self.equity_value = self._kpi(kpi_row, "Equity", "$10,186", "Floating P/L included")
        self.kpi_trades, self.trade_value = self._kpi(kpi_row, "Open Trades", "2", "Max allowed: 3")
        self.kpi_daily, self.daily_value = self._kpi(kpi_row, "Daily P/L", "+$145", "Max loss limit: -$200")
        for i, card in enumerate([self.kpi_balance, self.kpi_equity, self.kpi_trades, self.kpi_daily]):
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            kpi_row.grid_columnconfigure(i, weight=1)

        # Actions row
        actions = tk.Frame(self, bg="#07111f")
        actions.pack(fill="x", padx=18, pady=(0, 12))
        ttk.Button(actions, text="Save Draft", style="Dark.TButton", command=self.save_draft).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Run Backtest", style="Primary.TButton", command=self.run_backtest).pack(side="left", padx=8)
        ttk.Button(actions, text="Start Simulation", style="Success.TButton", command=self.start_bot).pack(side="left", padx=8)
        ttk.Button(actions, text="Emergency Stop", style="Danger.TButton", command=self.emergency_stop).pack(side="left", padx=8)
        ttk.Button(actions, text="Dummy Server", style="Dark.TButton", command=self.toggle_dummy_server).pack(side="left", padx=8)

        # Main grid
        main = tk.Frame(self, bg="#07111f")
        main.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        main.grid_rowconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=0)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_columnconfigure(2, weight=1)

        # Tab notebook across top portion
        notebook_wrap = tk.Frame(main, bg="#07111f")
        notebook_wrap.grid(row=0, column=0, columnspan=3, sticky="nsew")
        notebook_wrap.grid_rowconfigure(0, weight=1)
        notebook_wrap.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(notebook_wrap)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.dashboard_tab = tk.Frame(self.notebook, bg="#07111f")
        self.strategy_tab = tk.Frame(self.notebook, bg="#07111f")
        self.risk_tab = tk.Frame(self.notebook, bg="#07111f")
        self.execution_tab = tk.Frame(self.notebook, bg="#07111f")
        self.logs_tab = tk.Frame(self.notebook, bg="#07111f")

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.strategy_tab, text="Strategy Config")
        self.notebook.add(self.risk_tab, text="Risk Settings")
        self.notebook.add(self.execution_tab, text="Execution")
        self.notebook.add(self.logs_tab, text="Logs")

        self._build_dashboard_tab()
        self._build_strategy_tab()
        self._build_risk_tab()
        self._build_execution_tab()
        self._build_logs_tab()

        # Bottom summary strip
        bottom = tk.Frame(main, bg="#07111f")
        bottom.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_columnconfigure(2, weight=1)

        self.monitor_label = self._bottom_chip(bottom, 0, "Monitor", "Live risk, spread, and trade control indicators")
        self.strategy_label = self._bottom_chip(bottom, 1, "Strategy", "Rules locked after trader input")
        self.deploy_label = self._bottom_chip(bottom, 2, "Deploy", "Ready for dummy server / demo presentation")

    def _bottom_chip(self, parent, col, title, desc):
        frame = tk.Frame(parent, bg="#0d1b2e", highlightthickness=1, highlightbackground="#1a3357")
        frame.grid(row=0, column=col, padx=8, sticky="ew")
        tk.Label(frame, text=title, bg="#0d1b2e", fg="#eff5ff", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(frame, text=desc, bg="#0d1b2e", fg="#8fa3c2", font=("Segoe UI", 9), wraplength=380, justify="left").pack(anchor="w", padx=14, pady=(0, 12))
        return frame

    # ----------------------------- Dashboard tab -----------------------------
    def _build_dashboard_tab(self):
        left_outer, left = self._panel(self.dashboard_tab, "Strategy Inputs & Controls", "Where trader defines what the bot should do.")
        left_outer.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=(10, 0))

        center_outer, center = self._panel(self.dashboard_tab, "Live Market Visualization", "Dummy chart + current price + status loop.")
        center_outer.pack(side="left", fill="both", expand=True, padx=10, pady=(10, 0))

        right_outer, right = self._panel(self.dashboard_tab, "Monitoring & Trade State", "Terms the bot will control and monitor.")
        right_outer.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=(10, 0))

        left.grid_columnconfigure(0, weight=1)
        left.grid_columnconfigure(1, weight=1)
        self.symbol_entry = self._labeled_entry(left, 0, 0, "Symbol", "XAUUSD", width=30)
        self.timeframe_combo = self._labeled_combo(left, 0, 1, "Timeframe", ["5 Minutes", "15 Minutes", "1 Hour", "4 Hours"], 1, 30)
        self.entry_entry = self._labeled_entry(left, 2, 0, "Entry Condition", "Breakout + candle close confirmation", width=34)
        self.exit_entry = self._labeled_entry(left, 2, 1, "Exit Condition", "TP, SL, or opposite signal", width=34)
        self.sl_entry = self._labeled_entry(left, 4, 0, "Stop Loss (pips)", "20", width=30)
        self.tp_entry = self._labeled_entry(left, 4, 1, "Take Profit (pips)", "40", width=30)
        self.notes_text = self._text(left, 6, 0, "Trade only when breakout candle closes above resistance and spread is within limit.", width=70, height=6, colspan=2)

        # Live chart
        center.grid_columnconfigure(0, weight=1)
        self.chart_canvas = tk.Canvas(center, bg="#08101b", highlightthickness=1, highlightbackground="#27405f", height=320)
        self.chart_canvas.pack(fill="both", expand=False, padx=16, pady=(0, 12))

        chart_bar = tk.Frame(center, bg="#0d1b2e")
        chart_bar.pack(fill="x", padx=16, pady=(0, 12))
        self.price_label = tk.Label(chart_bar, text=f"Price: {self.current_price:.2f}", bg="#0d1b2e", fg="#89f0cb", font=("Segoe UI", 14, "bold"))
        self.price_label.pack(side="left")
        self.signal_label = tk.Label(chart_bar, text="Signal: Waiting", bg="#0d1b2e", fg="#ffdf6b", font=("Segoe UI", 12, "bold"))
        self.signal_label.pack(side="right")

        terms = tk.Frame(center, bg="#0d1b2e", highlightthickness=1, highlightbackground="#1a3357")
        terms.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        tk.Label(terms, text="Key Trading Concepts Visualized", bg="#0d1b2e", fg="#eff5ff", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(12, 8))
        self.term_box = tk.Frame(terms, bg="#0d1b2e")
        self.term_box.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        right.grid_columnconfigure(0, weight=1)
        self.pos_tree = ttk.Treeview(right, columns=("symbol", "type", "lot", "pl"), show="headings", height=9)
        for col, text, width in [("symbol", "Symbol", 100), ("type", "Type", 80), ("lot", "Lot", 70), ("pl", "P/L", 80)]:
            self.pos_tree.heading(col, text=text)
            self.pos_tree.column(col, width=width, anchor="center")
        self.pos_tree.pack(fill="both", expand=False, padx=16, pady=(0, 14))

        self.state_card = tk.Frame(right, bg="#0d1b2e", highlightthickness=1, highlightbackground="#1a3357")
        self.state_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        tk.Label(self.state_card, text="Bot State", bg="#0d1b2e", fg="#eff5ff", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
        self.state_text = tk.Label(self.state_card, text="Simulation running on dummy server...", bg="#0d1b2e", fg="#89f0cb", font=("Segoe UI", 10, "bold"), wraplength=360, justify="left")
        self.state_text.pack(anchor="w", padx=14, pady=(0, 10))
        self.control_text = tk.Label(self.state_card, text="Risk Guard: Active | Spread Filter: Active | Cooldown: Active", bg="#0d1b2e", fg="#8fa3c2", font=("Segoe UI", 9), wraplength=360, justify="left")
        self.control_text.pack(anchor="w", padx=14, pady=(0, 12))

    # ----------------------------- Strategy tab -----------------------------
    def _build_strategy_tab(self):
        outer, body = self._panel(self.strategy_tab, "Strategy Logic", "Define how the bot decides entry, confirmation, invalidation, and exit.")
        outer.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        self.strategy_type = self._labeled_combo(body, 0, 0, "Strategy Type", ["Breakout", "Reversal", "Trend Following", "Scalping"], 0, 30)
        self.confirmation_entry = self._labeled_entry(body, 0, 1, "Confirmation Rule", "Candle close above/below level", width=34)
        self.invalidation_entry = self._labeled_entry(body, 2, 0, "Invalidation Rule", "Price re-enters range before close", width=34)
        self.one_trade_combo = self._labeled_combo(body, 2, 1, "One Trade Per Signal", ["Enabled", "Disabled"], 0, 30)
        self.cooldown_entry = self._labeled_entry(body, 4, 0, "Cooldown", "15 minutes", width=30)
        self.session_entry = self._labeled_entry(body, 4, 1, "Session Filter", "London + New York", width=30)
        self.strategy_notes = self._text(body, 6, 0, "Buy only when price breaks resistance and confirmation candle closes above it. Avoid false breakouts.", width=70, height=6, colspan=2)

    # ----------------------------- Risk tab -----------------------------
    def _build_risk_tab(self):
        outer, body = self._panel(self.risk_tab, "Risk & Capital Protection", "These are the guardrails that protect the account.")
        outer.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        self.risk_trade = self._labeled_entry(body, 0, 0, "Risk Per Trade (%)", "1", width=20)
        self.max_daily_loss = self._labeled_entry(body, 0, 1, "Max Daily Loss ($)", "200", width=20)
        self.max_open = self._labeled_entry(body, 2, 0, "Max Open Trades", "3", width=20)
        self.trailing_after = self._labeled_entry(body, 2, 1, "Trailing Stop After (pips)", "20", width=20)
        self.breakeven_after = self._labeled_entry(body, 4, 0, "Breakeven After (pips)", "15", width=20)
        self.spread_limit = self._labeled_entry(body, 4, 1, "Spread Limit (pips)", "3", width=20)
        self.risk_state = tk.StringVar(value="Enabled")
        self.trailing_state = tk.StringVar(value="Enabled")
        self.breakeven_state = tk.StringVar(value="Enabled")
        self._toggle_row(body, 6, "Risk Guard", "Stops trading when max loss is breached", self.risk_state)
        self._toggle_row(body, 7, "Trailing Stop", "Move stop after profit threshold", self.trailing_state)
        self._toggle_row(body, 8, "Breakeven", "Shift SL to entry after profit", self.breakeven_state)

    # ----------------------------- Execution tab -----------------------------
    def _build_execution_tab(self):
        outer, body = self._panel(self.execution_tab, "Execution Controls", "How the bot would route orders through MT5 / dummy server.")
        outer.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        self.order_type = self._labeled_combo(body, 0, 0, "Order Type", ["Market Order", "Pending Order"], 0, 24)
        self.slippage = self._labeled_entry(body, 0, 1, "Slippage Tolerance", "3 pips", width=24)
        self.retries = self._labeled_entry(body, 2, 0, "Retry Logic", "2 retries", width=24)
        self.rejection = self._labeled_entry(body, 2, 1, "Broker Rejection Handling", "Log + safe skip", width=24)
        self.exec_notes = self._text(body, 4, 0, "Use MT5 terminal bridge. Verify symbol constraints before sending any order.", width=70, height=6, colspan=2)

        self.exec_status = tk.Frame(body, bg="#0d1b2e", highlightthickness=1, highlightbackground="#1a3357")
        self.exec_status.grid(row=10, column=0, columnspan=2, sticky="we", padx=16, pady=(8, 14))
        tk.Label(self.exec_status, text="Execution Monitor", bg="#0d1b2e", fg="#eff5ff", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
        self.exec_label = tk.Label(self.exec_status, text="No live order sent — currently in demo showcase mode.", bg="#0d1b2e", fg="#8fa3c2", font=("Segoe UI", 9), wraplength=900, justify="left")
        self.exec_label.pack(anchor="w", padx=14, pady=(0, 12))

    # ----------------------------- Logs tab -----------------------------
    def _build_logs_tab(self):
        outer, body = self._panel(self.logs_tab, "System Logs", "Auto-updating activity feed for strategy, risk, and monitoring.")
        outer.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)
        self.log_box = tk.Text(body, bg="#07101b", fg="#c8d7f5", insertbackground="#c8d7f5",
                               relief="flat", highlightthickness=1, highlightbackground="#27405f",
                               font=("Consolas", 10), wrap="word")
        self.log_box.grid(row=0, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.log_box.configure(state="disabled")

    # ----------------------------- Demo content -----------------------------
    def _seed_demo_content(self):
        self.add_log("UI loaded successfully.")
        self.add_log("Dummy server connected.")
        self.add_log("Strategy inputs are ready for trader review.")
        self.add_log("Risk guard enabled with max daily loss and max open trade limits.")
        self.add_log("Monitoring dashboard initialized.")

        demo_rows = [
            ("XAUUSD", "BUY", "0.10", "+$42"),
            ("EURUSD", "SELL", "0.05", "-$12"),
        ]
        for row in demo_rows:
            self.pos_tree.insert("", tk.END, values=row)

        self._render_terms()

    def _render_terms(self):
        for child in self.term_box.winfo_children():
            child.destroy()

        terms = [
            ("Order", "Broker ko buy/sell instruction"),
            ("Position", "Open trade ki current state"),
            ("SL / TP", "Loss limit aur profit target"),
            ("Spread", "Bid-ask difference"),
            ("Risk Per Trade", "Har trade ka max risk"),
            ("Trailing Stop", "Profit ke saath moving stop"),
            ("Breakeven", "SL ko entry par lana"),
            ("Cooldown", "Next trade se pehle wait"),
            ("Session Filter", "Allowed trading hours"),
            ("Drawdown", "Peak equity se decline"),
            ("Signal", "Entry/exit trigger"),
            ("Execution", "Order ko route karna"),
        ]

        for i, (title, desc) in enumerate(terms):
            row = i // 4
            col = i % 4
            chip = tk.Frame(self.term_box, bg="#102136", highlightthickness=1, highlightbackground="#1a3357")
            chip.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            tk.Label(chip, text=title, bg="#102136", fg="#eff5ff", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
            tk.Label(chip, text=desc, bg="#102136", fg="#8fa3c2", font=("Segoe UI", 9), wraplength=150, justify="left").pack(anchor="w", padx=12, pady=(0, 10))
            self.term_box.grid_columnconfigure(col, weight=1)
            self.term_box.grid_rowconfigure(row, weight=1)

    # ----------------------------- Actions -----------------------------
    def add_log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        line = f"[{now}] {message}\n"
        self.log_lines.insert(0, line)
        if len(self.log_lines) > 300:
            self.log_lines = self.log_lines[:300]
        self._refresh_logs()

    def _refresh_logs(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.insert("1.0", "".join(self.log_lines))
        self.log_box.configure(state="disabled")

    def save_draft(self):
        self.add_log("Strategy draft saved from UI.")
        messagebox.showinfo("Save Draft", "Draft saved successfully.")

    def run_backtest(self):
        self.add_log("Backtest simulation started on selected strategy parameters.")
        self.signal_label.configure(text="Signal: Backtest Running", fg="#ffd66b")
        messagebox.showinfo("Backtest", "Backtest started.")

    def start_bot(self):
        self.running = True
        self.paused = False
        self.status_badge.configure(text="SIMULATION RUNNING", fg="#89f0cb", bg="#163a32")
        self.state_text.configure(text="Dummy server is processing strategy conditions in a controlled demo loop.")
        self.add_log("Simulation started by user.")
        messagebox.showinfo("Start Simulation", "Simulation started.")

    def emergency_stop(self):
        self.running = False
        self.paused = True
        self.status_badge.configure(text="EMERGENCY STOP", fg="#ffb3b3", bg="#5a1f1f")
        self.state_text.configure(text="Trading paused. Review rules before restart.")
        self.exec_label.configure(text="Emergency stop executed. No new order will be sent until manual restart.")
        self.add_log("Emergency stop triggered. Trading paused.")
        messagebox.showwarning("Emergency Stop", "All trading has been paused.")

    def toggle_dummy_server(self):
        if self.running:
            self.running = False
            self.paused = True
            self.add_log("Dummy server disconnected.")
            self.status_badge.configure(text="DUMMY SERVER OFF", fg="#ffdf6b", bg="#4a3c17")
        else:
            self.running = True
            self.paused = False
            self.add_log("Dummy server reconnected.")
            self.status_badge.configure(text="DUMMY SERVER ON", fg="#89f0cb", bg="#163a32")

    # ----------------------------- Live dummy loop -----------------------------
    def _tick(self):
        # clock
        self.clock_label.configure(text=datetime.now().strftime("%I:%M:%S %p"))

        # dummy price movement
        drift = random.uniform(-2.8, 2.8)
        self.current_price = max(2200, self.current_price + drift)
        self.chart_points.append(self.current_price)
        self.chart_points = self.chart_points[-60:]

        # dummy monitor values
        eq = 10180 + random.uniform(-60, 80)
        daily_pl = 145 + random.uniform(-40, 55)
        open_trades = 2 if self.running else 0

        self.balance_value.configure(text="$10,250")
        self.equity_value.configure(text=f"${eq:,.0f}")
        self.trade_value.configure(text=str(open_trades))
        self.daily_value.configure(text=f"{daily_pl:+.0f}$")
        self.price_label.configure(text=f"Price: {self.current_price:,.2f}")

        if self.running and not self.paused:
            # simple signal demo loop
            if random.random() > 0.72:
                self.signal_label.configure(text="Signal: BUY Setup Detected", fg="#89f0cb")
                self.exec_label.configure(text="Rule engine matched breakout + confirmation. Dummy order path shown.")
                self.add_log("Signal detected: breakout + confirmation matched.")
            elif random.random() > 0.72:
                self.signal_label.configure(text="Signal: SELL Setup Detected", fg="#ff9d9d")
                self.exec_label.configure(text="Risk checks passed. Dummy sell execution path displayed.")
                self.add_log("Signal detected: reversal setup matched.")
            else:
                self.signal_label.configure(text="Signal: Waiting", fg="#ffd66b")
        else:
            self.signal_label.configure(text="Signal: Paused", fg="#ff9d9d")

        self._draw_chart()
        self.after(1000, self._tick)

    def _draw_chart(self):
        canvas = self.chart_canvas
        canvas.delete("all")
        w = max(canvas.winfo_width(), 10)
        h = max(canvas.winfo_height(), 10)
        margin = 30

        # grid
        for i in range(6):
            y = margin + i * (h - 2 * margin) / 5
            canvas.create_line(margin, y, w - margin, y, fill="#15304f", width=1)
        for i in range(8):
            x = margin + i * (w - 2 * margin) / 7
            canvas.create_line(x, margin, x, h - margin, fill="#10283f", width=1)

        # current line
        vals = self.chart_points[-48:]
        if len(vals) < 2:
            return
        min_v = min(vals)
        max_v = max(vals)
        span = max(max_v - min_v, 1)
        xs = []
        ys = []
        for idx, v in enumerate(vals):
            x = margin + idx * ((w - 2 * margin) / (len(vals) - 1))
            y = h - margin - ((v - min_v) / span) * (h - 2 * margin)
            xs.append(x)
            ys.append(y)

        # chart line
        for i in range(len(xs) - 1):
            canvas.create_line(xs[i], ys[i], xs[i + 1], ys[i + 1], fill="#5b8cff", width=3)

        # fill area
        area_points = [xs[0], h - margin] + [coord for pair in zip(xs, ys) for coord in pair] + [xs[-1], h - margin]
        canvas.create_polygon(area_points, fill="#173055", outline="")

        # last price marker
        last_x, last_y = xs[-1], ys[-1]
        canvas.create_oval(last_x - 6, last_y - 6, last_x + 6, last_y + 6, fill="#38d9a9", outline="")
        canvas.create_text(last_x, last_y - 18, text=f"{self.current_price:,.2f}", fill="#eff5ff", font=("Segoe UI", 10, "bold"))

    # ----------------------------- Boot -----------------------------
if __name__ == "__main__":
    app = MT5TradingBotUI()
    app.mainloop()
