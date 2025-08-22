import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# 📂 CSV Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # -----------------------------
    # 1) Read CSV
    # -----------------------------
    df = pd.read_csv(uploaded_file)

    # -----------------------------
    # 2) Convert timestamp
    # -----------------------------
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp_naive"] = df["timestamp"].dt.tz_convert(None)

    # -----------------------------
    # 3) Calculate volume
    # -----------------------------
    df["volume"] = df["price"] * df["quantity"]

    # -----------------------------
    # 4) Token selection
    # -----------------------------
    if "symbol" in df.columns:
        available_tokens = df["symbol"].unique().tolist()
        selected_token = st.selectbox("Select Token for analysis", ["All"] + available_tokens)
        if selected_token != "All":
            df = df[df["symbol"] == selected_token]
    else:
        st.warning("⚠️ Column 'symbol' not found. Token filtering will not be applied.")
        selected_token = "All"

    # -----------------------------
    # 5) Adjust to Thursday 9PM start of week
    # -----------------------------
    df["week"] = (df["timestamp_naive"] - pd.Timedelta(hours=21)).dt.to_period("W-THU").dt.start_time + pd.Timedelta(hours=21)

    # -----------------------------
    # 6) Weekly Aggregation
    # -----------------------------
    weekly_volume = df.groupby("week")["volume"].sum().reset_index()
    weekly_trades = df.groupby("week")["volume"].count().reset_index().rename(columns={"volume": "num_trades"})
    weekly_summary = pd.merge(weekly_volume, weekly_trades, on="week")

    # -----------------------------
    # 7) Show Table
    # -----------------------------
    st.subheader("📊 Weekly Summary")
    st.dataframe(weekly_summary)

    st.metric(label="🔹 Total Accumulated Volume", value=f"{weekly_summary['volume'].sum():,.2f}")

    # -----------------------------
    # 8) Combined Chart (Side-by-side Bars, Dual Axis)
    # -----------------------------
    fig = go.Figure()

    # Volume - Left Axis
    fig.add_trace(go.Bar(
        x=weekly_summary["week"],
        y=weekly_summary["volume"],
        name="Volume",
        marker_color="skyblue",
        offsetgroup=0,
        yaxis="y"
    ))

    # Trades - Right Axis
    fig.add_trace(go.Bar(
        x=weekly_summary["week"],
        y=weekly_summary["num_trades"],
        name="Number of Trades",
        marker_color="orange",
        offsetgroup=1,
        yaxis="y2"
    ))

    fig.update_layout(
        title=dict(
            text=f"📊 Weekly Volume and Number of Trades (Starting Thursday 9PM) - {selected_token}",
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(title="Week"),
        yaxis=dict(
            title=dict(text="Volume", font=dict(color="skyblue")),
            tickfont=dict(color="skyblue")
        ),
        yaxis2=dict(
            title=dict(text="Number of Trades", font=dict(color="orange")),
            tickfont=dict(color="orange"),
            overlaying="y",
            side="right"
        ),
        barmode="group",
        legend=dict(x=0.5, xanchor="center", orientation="h"),
        width=950,
        height=500,
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, use_container_width=False)

else:
    st.info("📥 Please upload a CSV file to begin analysis.")
