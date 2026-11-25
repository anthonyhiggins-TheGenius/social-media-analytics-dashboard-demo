
import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Social Media Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Social Media Analytics Dashboard")
st.caption("CEO DEMO | Synthetic data only — not actual company results")
# Load data from Google Sheets
@st.cache_data(ttl=0)
def load_data():
    import gspread
    from google.oauth2.service_account import Credentials

    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets.readonly"
        ]
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(st.secrets["google_sheets"]["spreadsheet_id"])
    worksheet = spreadsheet.worksheet("Synthetic Dataset")

    df = pd.DataFrame(worksheet.get_all_records())
    df = df.rename(columns={
        "Content Type": "Post Type",
        "Engagement Rate (by Reach)": "Engagement Rate"
    })
    return df
    random.seed(42)
    records = []

    for i in range(1, 61):
        platform = random.choice(["Instagram", "Facebook"])
        post_type = random.choice(
            ["Reel", "Image", "Carousel", "Story"]
        )
        reach = random.randint(500, 5000)
        likes = random.randint(30, 450)
        comments = random.randint(5, 80)
        shares = random.randint(2, 100)
        saves = random.randint(0, 120)

        records.append({
            "Post": f"Post {i}",
            "Date": datetime(2026, 10, 1) + timedelta(days=i % 45),
            "Platform": platform,
            "Post Type": post_type,
            "Reach": reach,
            "Likes": likes,
            "Comments": comments,
            "Shares": shares,
            "Saves": saves
        })

    df = pd.DataFrame(records)
    df["Engagements"] = (
        df["Likes"] + df["Comments"] +
        df["Shares"] + df["Saves"]
    )
    df["Engagement Rate"] = (
        df["Engagements"] / df["Reach"] * 100
    )
    return df

df = pd.read_excel("Synthetic_Social_Media_Dataset.xlsx")
df = df.rename(columns={
    "Post ID": "Post",
    "Content Type": "Post Type",
    "Total Engagements": "Engagements",
    "Engagement Rate (by Reach)": "Engagement Rate"
})

df["Date"] = pd.to_datetime(df["Date"])

# Interactive filters
st.sidebar.header("Dashboard Filters")

platforms = st.sidebar.multiselect(
    "Select Platform",
    sorted(df["Platform"].unique()),
    default=sorted(df["Platform"].unique())
)

post_types = st.sidebar.multiselect(
    "Select Post Type",
    sorted(df["Post Type"].unique()),
    default=sorted(df["Post Type"].unique())
)

filtered = df[
    df["Platform"].isin(platforms) &
    df["Post Type"].isin(post_types)
].copy()

if filtered.empty:
    st.warning("No posts match your selected filters.")
    st.stop()

# Performance indicators
total_reach = filtered["Reach"].sum()
total_engagements = filtered["Engagements"].sum()
engagement_rate = total_engagements / total_reach * 100
total_saves = filtered["Saves"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Reach", f"{total_reach:,}")
c2.metric("Total Engagements", f"{total_engagements:,}")
c3.metric("Engagement Rate", f"{engagement_rate:.2f}%")
c4.metric("Total Saves", f"{total_saves:,}")

st.divider()

# Engagement over time
st.subheader("Engagement Performance Over Time")

daily = filtered.groupby(
    "Date", as_index=False
)["Engagements"].sum()

fig_time = px.line(
    daily,
    x="Date",
    y="Engagements",
    markers=True
)
st.plotly_chart(fig_time, use_container_width=True)

# Platform and post type comparison
left, right = st.columns(2)

with left:
    st.subheader("Engagement by Platform")
    platform_data = filtered.groupby(
        "Platform", as_index=False
    )["Engagements"].sum()

    fig_platform = px.bar(
        platform_data,
        x="Platform",
        y="Engagements",
        color="Platform"
    )
    st.plotly_chart(fig_platform, use_container_width=True)

with right:
    st.subheader("Engagement Rate by Post Type")
    type_data = filtered.groupby(
        "Post Type", as_index=False
    ).agg(
        Engagements=("Engagements", "sum"),
        Reach=("Reach", "sum")
    )
    type_data["Engagement Rate"] = (
        type_data["Engagements"] /
        type_data["Reach"] * 100
    )

    fig_types = px.bar(
        type_data,
        x="Post Type",
        y="Engagement Rate",
        color="Post Type"
    )
    st.plotly_chart(fig_types, use_container_width=True)

# Top-performing posts
st.subheader("🏆 Top 10 Performing Posts")

top_posts = filtered.sort_values(
    "Engagements", ascending=False
).head(10)

st.dataframe(
    top_posts,
    use_container_width=True,
    hide_index=True
)

# Download results
st.subheader("Download Report")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Filtered Data",
    data=csv,
    file_name="social_media_analytics_demo.csv",
    mime="text/csv"
)

st.caption(
    "All figures are fictional and intended solely "
    "to demonstrate dashboard functionality."
)
