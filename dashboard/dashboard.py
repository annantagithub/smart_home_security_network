import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import random
from datetime import datetime

# ---------------------------------------
# Load CSS Styles
# ---------------------------------------
with open("dashboard/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------
# Top Navigation Bar
# ---------------------------------------
st.markdown("""
<div class="top-nav">
    🛡️ Smart Home Security Monitoring Center — UEL Cybersecurity
</div>
""", unsafe_allow_html=True)

# ---------------------------------------
# Page Configuration
# ---------------------------------------
st.set_page_config(
    page_title="Smart Home Network Security Dashboard",
    page_icon="🔐",
    layout="wide"
)

# ---------------------------------------
# Additional Inline Styles
# ---------------------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #111827;
        color: #F9FAFB;
    }
    .stButton>button {
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------
# Data Helpers (JSON storage)
# ---------------------------------------
DATA_FILE = "data/network.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"devices": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()
devices = data.get("devices", [])

devices_df = pd.DataFrame(devices)

# ---------------------------------------
# Session State for Alerts
# ---------------------------------------
if "alerts" not in st.session_state:
    st.session_state.alerts = [
        {"time": "10:00", "source": "Guest Phone", "destination": "Admin PC", "type": "Unauthorized Access", "status": "Blocked"},
        {"time": "10:05", "source": "IoT Camera", "destination": "User Laptop", "type": "Cross-VLAN Attempt", "status": "Blocked"},
        {"time": "10:10", "source": "Smart Bulb", "destination": "Admin PC", "type": "ARP Spoofing", "status": "Suspicious"},
        {"time": "10:20", "source": "Guest Phone", "destination": "Admin PC", "type": "Unauthorized Access", "status": "Blocked"},
    ]

alerts = st.session_state.alerts

# ---------------------------------------
# Sidebar Navigation
# ---------------------------------------
with st.sidebar:
    st.header("🔐 Navigation")
    page = st.radio(
        "Go to:",
        ["Dashboard", "Alerts", "Devices", "Quarantine Center", "Network Overview"]
    )

# ---------------------------------------
# Helper Functions (Device Status Updates)
# ---------------------------------------
def update_device_status(name, new_status, new_vlan=None):
    for d in devices:
        if d["name"] == name:
            d["status"] = new_status
            if new_vlan is not None:
                d["vlan"] = new_vlan
            save_data({"devices": devices})
            break

def count_quarantined():
    return sum(1 for d in devices if d["status"] == "Quarantined")

def count_active():
    return len(devices)

# =======================================
# PAGE 1: DASHBOARD
# =======================================
if page == "Dashboard":
    st.title("🏠 Smart Home Network Security Dashboard")
    st.caption("Monitor home IoT devices, VLAN segmentation, alerts and intrusions in real time.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Devices", count_active())
    col2.metric("Blocked Attacks", len(alerts))
    col3.metric("Quarantined Devices", count_quarantined())

    st.markdown("---")
    st.subheader("🖥️ Connected Devices")

    if not devices_df.empty:
        st.table(devices_df)
    else:
        st.info("No device data available yet.")

# =======================================
# PAGE 2: ALERTS
# =======================================
elif page == "Alerts":
    st.title("🚨 Security Alerts")

    if alerts:
        st.table(pd.DataFrame(alerts))
    else:
        st.success("No alerts generated yet.")

    st.markdown("### Simulate Attack 🧪")

    if st.button("🔴 Generate Attack Event"):
        possible_sources = [d["name"] for d in devices] if devices else ["Unknown Device"]

        new_alert = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": random.choice(possible_sources),
            "destination": random.choice(["Admin PC", "User Laptop", "Home Server"]),
            "type": random.choice(["Unauthorized Access", "Cross-VLAN Attempt", "Port Scan", "Brute-Force Login", "Suspicious Traffic"]),
            "status": random.choice(["Blocked", "Quarantined", "Suspicious"])
        }

        st.session_state.alerts.append(new_alert)
        st.success(f"New alert generated: {new_alert}")

    st.markdown("### Live Alert Log")
    st.dataframe(pd.DataFrame(st.session_state.alerts), use_container_width=True)

# =======================================
# PAGE 3: DEVICE EXPLORER
# =======================================
elif page == "Devices":

    device_icons = {
        "Admin PC": "🖥️",
        "User Laptop": "💻",
        "IoT Camera": "📷",
        "Guest Phone": "📱",
        "Smart Bulb": "💡"
    }

    if not devices_df.empty:
        devices_df["icon"] = devices_df["name"].apply(lambda x: device_icons.get(x, "🔧"))
        devices_df["name"] = devices_df["icon"] + " " + devices_df["name"]

    st.title("💻 Device Explorer")
    st.caption("View device details and take actions.")

    if not devices:
        st.info("No devices available.")
    else:
        for d in devices:
            with st.expander(f"{d['name']} — {d['ip']} (VLAN {d['vlan']})"):

                st.write(f"**Status:** {d['status']}")
                st.write(f"**VLAN:** {d['vlan']}")

                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    if st.button(f"Mark Safe ({d['name']})", key=f"safe_{d['name']}"):
                        update_device_status(d["name"], "Safe")
                        st.success("Device marked safe.")

                with col_b:
                    if st.button(f"Block ({d['name']})", key=f"block_{d['name']}"):
                        update_device_status(d["name"], "Suspicious")
                        st.warning("Device blocked.")

                with col_c:
                    if st.button(f"Isolate ({d['name']})", key=f"iso_{d['name']}"):
                        update_device_status(d["name"], "Quarantined", new_vlan=99)
                        st.error("Device quarantined.")

# =======================================
# PAGE 4: QUARANTINE CENTER
# =======================================
elif page == "Quarantine Center":
    st.title("🚫 Quarantine Center")

    quarantined = [d for d in devices if d["status"] == "Quarantined"]

    if quarantined:
        st.table(pd.DataFrame(quarantined))

        for d in quarantined:
            if st.button(f"Release {d['name']}", key=f"rel_{d['name']}"):
                update_device_status(d["name"], "Safe", new_vlan=40)
                st.success(f"{d['name']} released from quarantine.")
    else:
        st.success("No devices in quarantine.")

# =======================================
# PAGE 5: NETWORK OVERVIEW
# =======================================
elif page == "Network Overview":
    st.title("🌐 Network Overview")

    st.write("""
    - VLAN 10 ➜ Admin  
    - VLAN 20 ➜ Users  
    - VLAN 30 ➜ Guest  
    - VLAN 40 ➜ IoT  
    - VLAN 99 ➜ Quarantine  
    """)

    df = pd.DataFrame(devices)

    if not df.empty:
        # VLAN distribution
        st.subheader("📊 Device Distribution by VLAN")
        st.bar_chart(df["vlan"].value_counts())

        # Status chart
        st.subheader("🛡️ Device Security Status")
        fig = px.pie(values=df["status"].value_counts().values,
                     names=df["status"].value_counts().index)
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    st.subheader("🔥 VLAN Traffic Heatmap (Simulated)")
    heatmap_data = pd.DataFrame(
        [[10, 30, 20],
         [15, 40, 10],
         [5, 10, 50]],
        columns=["Admin VLAN 10", "User VLAN 20", "IoT VLAN 40"],
        index=["Morning", "Afternoon", "Night"]
    )
    fig3 = px.imshow(heatmap_data, aspect="auto", color_continuous_scale="teal")
    st.plotly_chart(fig3, use_container_width=True)

    # Topology Map
    st.subheader("🌐 IoT Network Topology Map")
    nodes = ["Router", "Admin PC", "User Laptop", "IoT Camera", "Guest Phone", "Smart Bulb"]
    edges = [("Router", "Admin PC"), ("Router", "User Laptop"), ("Router", "IoT Camera"),
             ("Router", "Guest Phone"), ("Router", "Smart Bulb")]

    topology_df = pd.DataFrame(edges, columns=["source", "target"])
    fig4 = px.scatter(
        topology_df,
        x=[1, 2, 2, 2, 2, 2],
        y=[3, 5, 4, 3, 2, 1],
        text=nodes,
        size=[20] * 6,
        color=nodes,
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig4.update_traces(textposition="top center")
    st.plotly_chart(fig4, use_container_width=True)
