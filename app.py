import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="Startup Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv('data/cleaned_file_startup.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Dashboard")
option = st.sidebar.radio("Select", ["Overall", "Startup", "Investor"])

# ---------------- OVERALL ----------------
def overall():
    st.title("📊 Overall Dashboard")

    # KPI (8 cards)
    total = df['amount'].sum()
    avg = df['amount'].mean()
    max_val = df['amount'].max()
    min_val = df['amount'].min()
    startups = df['startup'].nunique()
    investors = len(set(df['investors'].str.split(',').sum()))
    cities = df['city'].nunique()
    sectors = df['vertical'].nunique()

    col1,col2,col3,col4 = st.columns(4)
    col5,col6,col7,col8 = st.columns(4)

    col1.metric("Total 💰", round(total,2))
    col2.metric("Avg 📊", round(avg,2))
    col3.metric("Max 🚀", round(max_val,2))
    col4.metric("Min 🔻", round(min_val,2))

    col5.metric("Startups 🏢", startups)
    col6.metric("Investors 🤝", investors)
    col7.metric("Cities 🌆", cities)
    col8.metric("Sectors 📂", sectors)

    st.markdown("---")

    # Charts (Power BI style)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Yearly Trend")
        st.line_chart(df.groupby('year')['amount'].sum())

    with col2:
        st.subheader("🏆 Top Startups")
        st.bar_chart(df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10))

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📊 Sector Pie")
        sector = df.groupby('vertical')['amount'].sum().head(6)
        fig, ax = plt.subplots()
        ax.pie(sector, labels=sector.index, autopct="%0.1f%%")
        st.pyplot(fig)

    with col4:
        st.subheader("🌆 City Wise")
        st.bar_chart(df.groupby('city')['amount'].sum().head(10))

# ---------------- STARTUP ----------------
def startup():
    st.title("🚀 Startup Analysis")

    startup = st.selectbox("Select Startup", sorted(df['startup'].unique()))
    btn = st.button("Show Startup Analysis")

    if btn:
        temp = df[df['startup'] == startup]

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            city = st.multiselect("Select City", temp['city'].unique(), default=temp['city'].unique())
        with col2:
            year = st.multiselect("Select Year", temp['year'].unique(), default=temp['year'].unique())

        temp = temp[(temp['city'].isin(city)) & (temp['year'].isin(year))]

        # ---------------- KPI ----------------
        total = temp['amount'].sum()
        max_val = temp['amount'].max()
        avg = temp['amount'].mean()
        deals = temp.shape[0]
        cities = temp['city'].nunique()
        startups = temp['startup'].nunique()
        years = temp['year'].nunique()

        col1,col2,col3,col4 = st.columns(4)
        col5,col6,col7 = st.columns(3)

        col1.metric("Total 💰", round(total,2))
        col2.metric("Max 🚀", round(max_val,2))
        col3.metric("Avg 📊", round(avg,2))
        col4.metric("Deals 📄", deals)

        col5.metric("Cities 🌆", cities)
        col6.metric("Startups 🏢", startups)
        col7.metric("Years 📅", years)

        st.markdown("---")

        # ---------------- CHARTS ----------------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Year Trend")
            st.line_chart(temp.groupby('year')['amount'].sum())

        with col2:
            st.subheader("🏆 Top Investors")
            st.bar_chart(temp.groupby('investors')['amount'].sum().sort_values(ascending=False).head())

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("📊 Sector Pie")
            sector = temp.groupby('vertical')['amount'].sum()
            fig, ax = plt.subplots()
            ax.pie(sector, labels=sector.index, autopct="%0.1f%%")
            st.pyplot(fig)

        with col4:
            st.subheader("🌆 City Distribution")
            st.bar_chart(temp.groupby('city')['amount'].sum())

        st.subheader("📄 Data")
        st.dataframe(temp.head(20))
# ---------------- INVESTOR ----------------
def investor():
    st.title("💰 Investor Analysis")

    investors = sorted(set(df['investors'].str.split(',').sum()))
    investor = st.selectbox("Select Investor", investors)

    btn = st.button("Show Investor Analysis")

    if btn:
        temp = df[df['investors'].str.contains(investor)]

        # Filters AFTER button
        col1, col2, col3 = st.columns(3)

        with col1:
            startup = st.multiselect("Startup", temp['startup'].unique(), default=temp['startup'].unique())

        with col2:
            city = st.multiselect("City", temp['city'].unique(), default=temp['city'].unique())

        with col3:
            year = st.multiselect("Year", temp['year'].unique(), default=temp['year'].unique())

        temp = temp[
            (temp['startup'].isin(startup)) &
            (temp['city'].isin(city)) &
            (temp['year'].isin(year))
        ]

        # ---------------- KPI ----------------
        total = temp['amount'].sum()
        max_val = temp['amount'].max()
        avg = temp['amount'].mean()
        deals = temp.shape[0]
        cities = temp['city'].nunique()
        startups = temp['startup'].nunique()
        years = temp['year'].nunique()

        col1,col2,col3,col4 = st.columns(4)
        col5,col6,col7 = st.columns(3)

        col1.metric("Total 💰", round(total,2))
        col2.metric("Max 🚀", round(max_val,2))
        col3.metric("Avg 📊", round(avg,2))
        col4.metric("Deals 📄", deals)

        col5.metric("Cities 🌆", cities)
        col6.metric("Startups 🏢", startups)
        col7.metric("Years 📅", years)

        st.markdown("---")

        # ---------------- CHARTS ----------------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Year Trend")
            st.line_chart(temp.groupby('year')['amount'].sum())

        with col2:
            st.subheader("🏆 Top Startups")
            st.bar_chart(temp.groupby('startup')['amount'].sum().sort_values(ascending=False).head())

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("📊 Sector Pie")
            sector = temp.groupby('vertical')['amount'].sum()
            fig, ax = plt.subplots()
            ax.pie(sector, labels=sector.index, autopct="%0.1f%%")
            st.pyplot(fig)

        with col4:
            st.subheader("🌆 City Distribution")
            st.bar_chart(temp.groupby('city')['amount'].sum())

        st.subheader("📄 Data")
        st.dataframe(temp.head(20))
def investor():
    st.title("💰 Investor Analysis")

    investors = sorted(set(df['investors'].str.split(',').sum()))
    investor = st.selectbox("Select Investor", investors)

    btn = st.button("Show Investor Analysis")

    if btn:
        temp = df[df['investors'].str.contains(investor)]

        # Filters AFTER button
        col1, col2, col3 = st.columns(3)

        with col1:
            startup = st.multiselect("Startup", temp['startup'].unique(), default=temp['startup'].unique())

        with col2:
            city = st.multiselect("City", temp['city'].unique(), default=temp['city'].unique())

        with col3:
            year = st.multiselect("Year", temp['year'].unique(), default=temp['year'].unique())

        temp = temp[
            (temp['startup'].isin(startup)) &
            (temp['city'].isin(city)) &
            (temp['year'].isin(year))
        ]

        # ---------------- KPI ----------------
        total = temp['amount'].sum()
        max_val = temp['amount'].max()
        avg = temp['amount'].mean()
        deals = temp.shape[0]
        cities = temp['city'].nunique()
        startups = temp['startup'].nunique()
        years = temp['year'].nunique()

        col1,col2,col3,col4 = st.columns(4)
        col5,col6,col7 = st.columns(3)

        col1.metric("Total 💰", round(total,2))
        col2.metric("Max 🚀", round(max_val,2))
        col3.metric("Avg 📊", round(avg,2))
        col4.metric("Deals 📄", deals)

        col5.metric("Cities 🌆", cities)
        col6.metric("Startups 🏢", startups)
        col7.metric("Years 📅", years)

        st.markdown("---")

        # ---------------- CHARTS ----------------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Year Trend")
            st.line_chart(temp.groupby('year')['amount'].sum())

        with col2:
            st.subheader("🏆 Top Startups")
            st.bar_chart(temp.groupby('startup')['amount'].sum().sort_values(ascending=False).head())

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("📊 Sector Pie")
            sector = temp.groupby('vertical')['amount'].sum()
            fig, ax = plt.subplots()
            ax.pie(sector, labels=sector.index, autopct="%0.1f%%")
            st.pyplot(fig)

        with col4:
            st.subheader("🌆 City Distribution")
            st.bar_chart(temp.groupby('city')['amount'].sum())

        st.subheader("📄 Data")
        st.dataframe(temp.head(20))
# ---------------- ROUTING ----------------
if option == "Overall":
    overall()
elif option == "Startup":
    startup()
else:
    investor()