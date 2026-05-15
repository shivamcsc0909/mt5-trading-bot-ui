import streamlit as st
import datetime
import time
import random
import math
import pandas as pd
import plotly.graph_objects as go

# ----------------------------- Page Config -----------------------------
st.set_page_config(
    page_title="MT5 Trading Bot | Control Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------- Session State Init -----------------------------
if "running" not in st.session_state:
    st.session_state.running = False
    st.session_state.paused = False
    st.session_state.current_price = 2310.0
    st.session_state.chart_points = [st.session_state.current_price + math.sin(i / 3) * 4 for i in range(48)]
    st.session_state.log_lines = []
    st.session_state.symbol = "XAUUSD"
    st.session_state.timeframe = "15 Minutes"
    st.session_state.entry_condition = "Breakout + candle close confirmation"
    st.session_state.exit_condition = "TP, SL, or opposite signal"
    st.session_state.sl = "20"
    st.session_state.tp = "40"
    st.session_state.notes = "Trade only when breakout candle closes above resistance and spread is within limit."
    st.session_state.strategy_type = "Breakout"
    st.session_state.confirmation = "Candle close above/below level"
    st.session_state.invalidation = "Price re-enters range before close"
    st.session_state.one_trade = "Enabled"
    st.session_state.cooldown = "15 minutes"
    st.session_state.session = "London + New York"
    st.session_state.strategy_notes = "Buy only when price breaks resistance and confirmation candle closes above it. Avoid false breakouts."
    st.session_state.risk_trade = "1"
    st.session_state.max_daily_loss = "200"
    st.session_state.max_open = "3"
    st.session_state.trailing_after = "20"
    st.session_state.breakeven_after = "15"
    st.session_state.spread_limit = "3"
    st.session_state.risk_guard = True
    st.session_state.trailing_stop = True
    st.session_state.breakeven_enabled = True
    st.session_state.order_type = "Market Order"
    st.session_state.slippage = "3 pips"
    st.session_state.retries = "2 retries"
    st.session_state.rejection = "Log + safe skip"
    st.session_state.exec_notes = "Use MT5 terminal bridge. Verify symbol constraints before sending any order."
    st.session_state.dummy_server = True
    st.session_state.open_trades_data = [
        {"symbol": "XAUUSD", "type": "BUY", "lot": 0.10, "pl": "+$42"},
        {"symbol": "EURUSD", "type": "SELL", "lot": 0.05, "pl": "-$12"}
    ]
    # Seed logs
    st.session_state.log_lines = [
        "UI loaded successfully.",
        "Dummy server connected.",
        "Strategy inputs are ready for trader review.",
        "Risk guard enabled with max daily loss and max open trade limits.",
        "Monitoring dashboard initialized."
    ]

# ----------------------------- Helper Functions -----------------------------
def add_log(message):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{now}] {message}"
    st.session_state.log_lines.insert(0, line)
    if len(st.session_state.log_lines) > 300:
        st.session_state.log_lines = st.session_state.log_lines[:300]

def draw_chart():
    vals = st.session_state.chart_points[-48:]
    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=list(range(len(vals))),
        y=vals,
        mode='lines',
        line=dict(color='#5b8cff', width=3),
        fill='tozeroy',
        fillcolor='rgba(23,48,85,0.4)',
        name='Price'
    ))

    # Latest price marker
    if vals:
        fig.add_trace(go.Scatter(
            x=[len(vals)-1],
            y=[vals[-1]],
            mode='markers+text',
            marker=dict(color='#38d9a9', size=12),
            text=[f"{vals[-1]:,.2f}"],
            textposition="top center",
            textfont=dict(color='white'),
            showlegend=False
        ))

    fig.update_layout(
        plot_bgcolor='#08101b',
        paper_bgcolor='#0d1b2e',
        font_color='#eff5ff',
        margin=dict(l=30, r=30, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor='#15304f', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#15304f', zeroline=False),
        height=320
    )
    return fig

def update_dummy_data():
    # Price drift
    drift = random.uniform(-2.8, 2.8)
    st.session_state.current_price = max(2200, st.session_state.current_price + drift)
    st.session_state.chart_points.append(st.session_state.current_price)
    st.session_state.chart_points = st.session_state.chart_points[-60:]
    # Equity & daily P/L
    eq = 10180 + random.uniform(-60, 80)
    daily_pl = 145 + random.uniform(-40, 55)
    open_trades = 2 if st.session_state.running else 0
    return eq, daily_pl, open_trades

# ----------------------------- UI Layout -----------------------------
# ---- Header ----
col_title, col_clock = st.columns([4, 1])
with col_title:
    st.markdown("<h1 style='color:#eff5ff;'>MT5 Trading Bot Control Center</h1>", unsafe_allow_html=True)
    st.caption("Demo UI to present strategy inputs, risk controls, monitoring, and automated decision flow.")

with col_clock:
    st.markdown(
        f"<div style='background:#102136; padding:10px; border-radius:5px; text-align:center;'>"
        f"<span style='color:#eff5ff; font-size:20px; font-weight:bold;'>{datetime.datetime.now().strftime('%I:%M:%S %p')}</span>"
        f"</div>",
        unsafe_allow_html=True
    )
    # Status badge
    if st.session_state.running and not st.session_state.paused:
        badge_color = "#89f0cb"
        badge_bg = "#163a32"
        status_text = "SIMULATION RUNNING"
    elif st.session_state.running and st.session_state.paused:
        badge_color = "#ffb3b3"
        badge_bg = "#5a1f1f"
        status_text = "EMERGENCY STOP"
    else:
        badge_color = "#ffdf6b"
        badge_bg = "#4a3c17"
        status_text = "DUMMY SERVER ON" if st.session_state.dummy_server else "DUMMY SERVER OFF"
    st.markdown(
        f"<div style='background:{badge_bg}; padding:6px; border-radius:4px; text-align:center; margin-top:5px;'>"
        f"<span style='color:{badge_color}; font-weight:bold; font-size:14px;'>{status_text}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

# ---- KPI Row ----
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Balance", value="$10,250")
with col2:
    eq_val, daily, trades = update_dummy_data() if st.session_state.running else (10186, 145, 2 if st.session_state.dummy_server else 0)
    st.metric(label="Equity", value=f"${eq_val:,.0f}")
with col3:
    st.metric(label="Open Trades", value=str(trades))
with col4:
    st.metric(label="Daily P/L", value=f"{daily:+.0f}$")

# ---- Action Buttons ----
btn_cols = st.columns(5)
with btn_cols[0]:
    if st.button("Save Draft", use_container_width=True):
        add_log("Strategy draft saved from UI.")
        st.toast("Draft saved successfully.")
with btn_cols[1]:
    if st.button("Run Backtest", use_container_width=True):
        add_log("Backtest simulation started on selected strategy parameters.")
        st.toast("Backtest started.")
with btn_cols[2]:
    if st.button("Start Simulation", use_container_width=True):
        st.session_state.running = True
        st.session_state.paused = False
        add_log("Simulation started by user.")
        st.toast("Simulation started.")
with btn_cols[3]:
    if st.button("Emergency Stop", use_container_width=True):
        st.session_state.running = False
        st.session_state.paused = True
        add_log("Emergency stop triggered. Trading paused.")
        st.toast("All trading has been paused.")
with btn_cols[4]:
    if st.button("Toggle Dummy Server", use_container_width=True):
        st.session_state.dummy_server = not st.session_state.dummy_server
        st.session_state.running = st.session_state.dummy_server
        st.session_state.paused = not st.session_state.dummy_server
        add_log("Dummy server " + ("reconnected" if st.session_state.dummy_server else "disconnected"))
        st.toast("Dummy server toggled.")

# ---- Main Tabs ----
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Strategy Config", "Risk Settings", "Execution", "Logs"])

# ================= Dashboard Tab =================
with tab1:
    left, center, right = st.columns([1, 1.2, 1])

    with left:
        st.subheader("Strategy Inputs & Controls")
        st.caption("Where trader defines what the bot should do.")
        st.session_state.symbol = st.text_input("Symbol", value=st.session_state.symbol, key="sym")
        st.session_state.timeframe = st.selectbox("Timeframe", ["5 Minutes", "15 Minutes", "1 Hour", "4 Hours"], 
                                                  index=["5 Minutes", "15 Minutes", "1 Hour", "4 Hours"].index(st.session_state.timeframe))
        st.session_state.entry_condition = st.text_input("Entry Condition", value=st.session_state.entry_condition)
        st.session_state.exit_condition = st.text_input("Exit Condition", value=st.session_state.exit_condition)
        st.session_state.sl = st.text_input("Stop Loss (pips)", value=st.session_state.sl)
        st.session_state.tp = st.text_input("Take Profit (pips)", value=st.session_state.tp)
        st.session_state.notes = st.text_area("Notes", value=st.session_state.notes, height=130)

    with center:
        st.subheader("Live Market Visualization")
        st.plotly_chart(draw_chart(), use_container_width=True, config={'displayModeBar': False})
        # Signal and price
        col_price, col_signal = st.columns(2)
        with col_price:
            st.metric("Current Price", f"{st.session_state.current_price:,.2f}")
        with col_signal:
            if st.session_state.running and not st.session_state.paused:
                r = random.random()
                if r > 0.72:
                    sig = "BUY Setup Detected"
                    color = "#89f0cb"
                    add_log("Signal detected: breakout + confirmation matched.")
                elif r > 0.72:
                    sig = "SELL Setup Detected"
                    color = "#ff9d9d"
                    add_log("Signal detected: reversal setup matched.")
                else:
                    sig = "Waiting"
                    color = "#ffd66b"
            else:
                sig = "Paused"
                color = "#ff9d9d"
            st.markdown(f"<span style='color:{color}; font-weight:bold; font-size:18px;'>Signal: {sig}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Key Trading Concepts Visualized")
        terms_data = [
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
        # Display in 4 columns grid
        terms_cols = st.columns(4)
        for i, (title, desc) in enumerate(terms_data):
            col_idx = i % 4
            with terms_cols[col_idx]:
                st.markdown(
                    f"<div style='background:#102136; padding:8px; border-radius:6px; margin-bottom:8px;'>"
                    f"<b style='color:#eff5ff;'>{title}</b><br>"
                    f"<span style='color:#8fa3c2; font-size:13px;'>{desc}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    with right:
        st.subheader("Monitoring & Trade State")
        # Positions table
        st.caption("Open Positions")
        positions_df = pd.DataFrame(st.session_state.open_trades_data)
        st.dataframe(positions_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        # Bot state card
        st.subheader("Bot State")
        if st.session_state.running and not st.session_state.paused:
            state_msg = "Simulation running on dummy server..."
        elif st.session_state.running and st.session_state.paused:
            state_msg = "Trading paused. Review rules before restart."
        else:
            state_msg = "Dummy server connected but simulation stopped."
        st.markdown(f"<div style='background:#0d1b2e; padding:10px; border-radius:5px; border:1px solid #1a3357; margin-bottom:10px;'>"
                    f"<span style='color:#89f0cb;'>{state_msg}</span></div>", unsafe_allow_html=True)
        st.markdown("<span style='color:#8fa3c2;'>Risk Guard: Active | Spread Filter: Active | Cooldown: Active</span>", unsafe_allow_html=True)

# ================= Strategy Tab =================
with tab2:
    st.subheader("Strategy Logic")
    st.caption("Define how the bot decides entry, confirmation, invalidation, and exit.")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.strategy_type = st.selectbox("Strategy Type", ["Breakout", "Reversal", "Trend Following", "Scalping"],
                                                      index=["Breakout", "Reversal", "Trend Following", "Scalping"].index(st.session_state.strategy_type))
        st.session_state.confirmation = st.text_input("Confirmation Rule", value=st.session_state.confirmation)
        st.session_state.invalidation = st.text_input("Invalidation Rule", value=st.session_state.invalidation)
    with col2:
        st.session_state.one_trade = st.selectbox("One Trade Per Signal", ["Enabled", "Disabled"],
                                                 index=["Enabled", "Disabled"].index(st.session_state.one_trade))
        st.session_state.cooldown = st.text_input("Cooldown", value=st.session_state.cooldown)
        st.session_state.session = st.text_input("Session Filter", value=st.session_state.session)
    st.session_state.strategy_notes = st.text_area("Strategy Notes", value=st.session_state.strategy_notes, height=120)

# ================= Risk Tab =================
with tab3:
    st.subheader("Risk & Capital Protection")
    st.caption("These are the guardrails that protect the account.")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.risk_trade = st.text_input("Risk Per Trade (%)", value=st.session_state.risk_trade)
        st.session_state.max_daily_loss = st.text_input("Max Daily Loss ($)", value=st.session_state.max_daily_loss)
        st.session_state.max_open = st.text_input("Max Open Trades", value=st.session_state.max_open)
        st.session_state.trailing_after = st.text_input("Trailing Stop After (pips)", value=st.session_state.trailing_after)
    with col2:
        st.session_state.breakeven_after = st.text_input("Breakeven After (pips)", value=st.session_state.breakeven_after)
        st.session_state.spread_limit = st.text_input("Spread Limit (pips)", value=st.session_state.spread_limit)

    # Toggle rows
    st.markdown("---")
    st.session_state.risk_guard = st.toggle("Risk Guard (Stops trading when max loss is breached)", value=st.session_state.risk_guard)
    st.session_state.trailing_stop = st.toggle("Trailing Stop (Move stop after profit threshold)", value=st.session_state.trailing_stop)
    st.session_state.breakeven_enabled = st.toggle("Breakeven (Shift SL to entry after profit)", value=st.session_state.breakeven_enabled)

# ================= Execution Tab =================
with tab4:
    st.subheader("Execution Controls")
    st.caption("How the bot would route orders through MT5 / dummy server.")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.order_type = st.selectbox("Order Type", ["Market Order", "Pending Order"],
                                                   index=["Market Order", "Pending Order"].index(st.session_state.order_type))
        st.session_state.slippage = st.text_input("Slippage Tolerance", value=st.session_state.slippage)
    with col2:
        st.session_state.retries = st.text_input("Retry Logic", value=st.session_state.retries)
        st.session_state.rejection = st.text_input("Broker Rejection Handling", value=st.session_state.rejection)
    st.session_state.exec_notes = st.text_area("Execution Notes", value=st.session_state.exec_notes, height=120)

    st.markdown("---")
    st.subheader("Execution Monitor")
    if st.session_state.running:
        if random.random() > 0.8:
            msg = "Rule engine matched breakout + confirmation. Dummy order path shown."
        else:
            msg = "Risk checks passed. Dummy execution path displayed."
    else:
        msg = "No live order sent — currently in demo showcase mode."
    st.info(msg)

# ================= Logs Tab =================
with tab5:
    st.subheader("System Logs")
    # Display logs newest first
    log_text = "\n".join(st.session_state.log_lines)
    st.code(log_text, language=None, line_numbers=False)

# ---- Bottom Summary Strip ----
st.markdown("---")
bot_col1, bot_col2, bot_col3 = st.columns(3)
with bot_col1:
    st.markdown("**Monitor**")
    st.caption("Live risk, spread, and trade control indicators")
with bot_col2:
    st.markdown("**Strategy**")
    st.caption("Rules locked after trader input")
with bot_col3:
    st.markdown("**Deploy**")
    st.caption("Ready for dummy server / demo presentation")

# ----------------------------- Live Update Loop -----------------------------
# This block simulates continuous updating by rerunning the script every second when simulation is active.
if st.session_state.running and not st.session_state.paused:
    # Wait 1 second to mimic tick interval
    time.sleep(1)
    st.rerun()
