import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import datetime
import random
import time

# -----------------------------
# PATH SETUP (robust)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent          # /dashboard
ROOT_DIR = BASE_DIR.parent                         # project root
DATA_DIR = ROOT_DIR / "data"                       # /data
CSS_PATH = BASE_DIR / "styles.css"
ALERTS_PATH = DATA_DIR / "alerts.json"
NETWORK_PATH = DATA_DIR / "network.json"

# -----------------------------
# LOAD CSS
# -----------------------------
if CSS_PATH.exists():
   st.markdown(f"<style>{CSS_PATH.read_text()}</style>", unsafe_allow_html=True)
with open("dashboard/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Smart Home Network Security Dashboard",
    page_icon="🏠",
    layout="wide"
)

# -----------------------------
# TOP NAV BAR (Premium)
# -----------------------------
st.markdown(
    """
    <div class="top-nav">
        <div class="top-nav-left">
            <span class="brand-dot"></span>
            <span class="brand-title">Smart Home Security Monitoring Center</span>
        </div>
        <div class="top-nav-right">
            <span class="pill">UEL Cybersecurity</span>
            <span class="pill glow">Live</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HELPERS
# -----------------------------
def load_json(path: Path, fallback):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return fallback
    return fallback


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2))


def get_devices():
    data = load_json(NETWORK_PATH, {"devices": []})
    return data.get("devices", [])


def save_devices(devices):
    save_json(NETWORK_PATH, {"devices": devices})


def get_alerts():
    data = load_json(ALERTS_PATH, {"alerts": []})
    return data.get("alerts", [])


def save_alerts(alerts):
    save_json(ALERTS_PATH, {"alerts": alerts})


def push_fake_alert(devices):
    """Simulate a live alert every refresh"""
    if not devices:
        return
    suspects = [d for d in devices if d.get("status") != "Safe"]
    device = random.choice(suspects if suspects else devices)
    new_alert = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "device": device.get("name"),
        "ip": device.get("ip"),
        "type": random.choice(["Port Scan", "Malware Beacon", "Unauthorized Access", "Brute Force"]),
        "severity": random.choice(["Low", "Medium", "High"]),
        "vlan": device.get("vlan"),
        "status": "Blocked" if random.random() > 0.4 else "Detected"
    }
    alerts = get_alerts()
    alerts.append(new_alert)
    save_alerts(alerts)


def update_device_status(name, new_status, new_vlan=None):
    devices = get_devices()
    for d in devices:
        if d.get("name") == name:
            d["status"] = new_status
            if new_vlan is not None:
                d["vlan"] = new_vlan
    save_devices(devices)


# -----------------------------
# SIDEBAR NAV
# -----------------------------
with st.sidebar:
    st.markdown("<div class='side-title'>🧭 Navigation</div>", unsafe_allow_html=True)
    page = st.radio(
        "Go to:",
        ["Dashboard", "Alerts", "Devices", "Quarantine Center", "Network Overview"],
        label_visibility="collapsed"
    )

# Always load latest data
devices = get_devices()
alerts = get_alerts()

devices_df = pd.DataFrame(devices) if devices else pd.DataFrame(columns=["name","ip","vlan","status"])
alerts_df = pd.DataFrame(alerts) if alerts else pd.DataFrame(columns=["timestamp","device","ip","type","severity","vlan","status"])

# -----------------------------
# PAGE 1: DASHBOARD
# -----------------------------
if page == "Dashboard":
    st.markdown("<div class='page-header'>🏠 Smart Home Network Security Dashboard</div>", unsafe_allow_html=True)
    st.caption("Monitor IoT devices, VLAN segmentation, alerts and intrusions in real-time.")

    # KPI counts
    active_count = len(devices)
    blocked_count = len(alerts_df[alerts_df["status"] == "Blocked"]) if not alerts_df.empty else 0
    quarantined_count = len(devices_df[devices_df["status"] == "Quarantined"]) if not devices_df.empty else 0

    # KPI Tiles (responsive)
    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card glow-blue">
                <div class="kpi-title">Active Devices</div>
                <div class="kpi-value">{active_count}</div>
                <div class="kpi-foot">Connected right now</div>
            </div>

            <div class="kpi-card glow-cyan">
                <div class="kpi-title">Blocked Attacks</div>
                <div class="kpi-value">{blocked_count}</div>
                <div class="kpi-foot">Auto-blocked by ACL</div>
            </div>

            <div class="kpi-card glow-purple">
                <div class="kpi-title">Quarantined</div>
                <div class="kpi-value">{quarantined_count}</div>
                <div class="kpi-foot">Isolated to VLAN 99</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title'>🖥️ Connected Devices</div>", unsafe_allow_html=True)

    if devices_df.empty:
        st.info("No devices found.")
    else:
        # Device cards (mobile-friendly)
        for d in devices:
            status = d.get("status", "Unknown")
            vlan = d.get("vlan", "-")
            ip = d.get("ip", "-")
            name = d.get("name", "Device")

            status_class = {
                "Safe": "status-safe",
                "Suspicious": "status-suspicious",
                "Quarantined": "status-quarantine"
            }.get(status, "status-neutral")

            st.markdown(
                f"""
                <div class="device-card">
                    <div class="device-row">
                        <div class="device-name">📌 {name}</div>
                        <div class="device-status {status_class}">{status}</div>
                    </div>
                    <div class="device-meta">
                        <span>IP: {ip}</span>
                        <span>VLAN: {vlan}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# -----------------------------
# PAGE 2: ALERTS
# -----------------------------
elif page == "Alerts":
    st.markdown("<div class='page-header'>🚨 Alerts</div>", unsafe_allow_html=True)
    st.caption("Simulated real-time threat events.")

    # push 1 new alert each page refresh to simulate live behavior
    push_fake_alert(devices)
    alerts_df = pd.DataFrame(get_alerts())

    if alerts_df.empty:
        st.info("No alerts yet.")
    else:
        # Latest first
        alerts_df = alerts_df.sort_values("timestamp", ascending=False)

        # Show as nice list on mobile
        st.markdown("<div class='section-title'>Recent Alerts</div>", unsafe_allow_html=True)

        for _, a in alerts_df.head(20).iterrows():
            sev = a.get("severity","Low")
            sev_class = {
                "Low": "sev-low",
                "Medium": "sev-med",
                "High": "sev-high"
            }.get(sev, "sev-low")

            st.markdown(
                f"""
                <div class="alert-card">
                    <div class="alert-top">
                        <div class="alert-type">⚠️ {a.get("type")}</div>
                        <div class="alert-sev {sev_class}">{sev}</div>
                    </div>
                    <div class="alert-body">
                        <div><b>Device:</b> {a.get("device")}</div>
                        <div><b>IP:</b> {a.get("ip")}</div>
                        <div><b>VLAN:</b> {a.get("vlan")}</div>
                        <div class="alert-time">{a.get("timestamp")}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div class='section-title'>Alerts Over Time</div>", unsafe_allow_html=True)
        alerts_df["timestamp"] = pd.to_datetime(alerts_df["timestamp"], errors="coerce")
        alerts_df = alerts_df.dropna(subset=["timestamp"])
        if not alerts_df.empty:
            line_df = alerts_df.groupby(alerts_df["timestamp"].dt.floor("min")).size().reset_index(name="count")
            fig = px.line(line_df, x="timestamp", y="count", markers=True, title="Alert Activity Over Time")
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# PAGE 3: DEVICES
# -----------------------------
elif page == "Devices":
    st.markdown("<div class='page-header'>📡 Devices</div>", unsafe_allow_html=True)
    st.caption("Inspect and take actions per device.")

    if not devices:
        st.info("No devices available.")
    else:
        for d in devices:
            with st.expander(f"{d.get('name')} — {d.get('ip')} (VLAN {d.get('vlan')})", expanded=False):
                st.write(f"**Status:** {d.get('status')}")
                st.write(f"**IP Address:** {d.get('ip')}")
                st.write(f"**VLAN:** {d.get('vlan')}")

                c1, c2, c3 = st.columns(3)

                with c1:
                    if st.button(f"Mark Safe ✅", key=f"safe_{d.get('name')}"):
                        update_device_status(d.get("name"), "Safe")
                        st.success("Device marked safe.")

                with c2:
                    if st.button(f"Block 🚫", key=f"block_{d.get('name')}"):
                        update_device_status(d.get("name"), "Suspicious")
                        st.warning("Device blocked (Suspicious).")

                with c3:
                    if st.button(f"Quarantine 🧪", key=f"iso_{d.get('name')}"):
                        update_device_status(d.get("name"), "Quarantined", new_vlan=99)
                        st.error("Device quarantined to VLAN 99.")

# -----------------------------
# PAGE 4: QUARANTINE CENTER
# -----------------------------
elif page == "Quarantine Center":
    st.markdown("<div class='page-header'>🧪 Quarantine Center</div>", unsafe_allow_html=True)
    quarantined = [d for d in devices if d.get("status") == "Quarantined"]

    if not quarantined:
        st.success("No quarantined devices. Network is clean.")
    else:
        st.markdown("<div class='section-title'>Isolated Devices (VLAN 99)</div>", unsafe_allow_html=True)

        for d in quarantined:
            st.markdown(
                f"""
                <div class="device-card quarantine">
                    <div class="device-row">
                        <div class="device-name">🛑 {d.get("name")}</div>
                        <div class="device-status status-quarantine">Quarantined</div>
                    </div>
                    <div class="device-meta">
                        <span>IP: {d.get("ip")}</span>
                        <span>VLAN: {d.get("vlan")}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(f"Release {d.get('name')} 🔓", key=f"release_{d.get('name')}"):
                update_device_status(d.get("name"), "Safe", new_vlan=40)
                st.success(f"{d.get('name')} released back to VLAN 40.")

# -----------------------------
# PAGE 5: NETWORK OVERVIEW
# -----------------------------
elif page == "Network Overview":
    st.markdown("<div class='page-header'>🗺️ Network Overview</div>", unsafe_allow_html=True)

    st.markdown(
        """
        **VLAN Segments (Simulation):**
        - VLAN 10 → Admin  
        - VLAN 20 → Users  
        - VLAN 30 → Guest  
        - VLAN 40 → IoT  
        - VLAN 99 → Quarantine  
        """
    )

    if devices_df.empty:
        st.info("No data available for charts.")
    else:
        st.markdown("<div class='section-title'>Device Distribution by VLAN</div>", unsafe_allow_html=True)
        vlan_counts = devices_df["vlan"].value_counts().reset_index()
        vlan_counts.columns = ["vlan", "count"]
        fig1 = px.bar(vlan_counts, x="vlan", y="count", title="Devices per VLAN")
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("<div class='section-title'>Security Status of Devices</div>", unsafe_allow_html=True)
        status_counts = devices_df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig2 = px.pie(status_counts, names="status", values="count", title="Security Status of Devices")
        st.plotly_chart(fig2, use_container_width=True)
