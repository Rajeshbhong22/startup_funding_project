import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="Startup Funding Insights Dashboard")

# Constants for Unit Conversion
USD_TO_INR = 83.0 # Approximate exchange rate
CRORE = 10000000.0 # 1 Cr = 10^7

# ---------------- CUSTOM CSS ----------------
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #374151;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        transition: all 0.3s ease;
        border-color: #6366f1;
    }
    h1, h2, h3 {
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #6366f1;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        background-color: #4f46e5;
        border: none;
    }
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
@st.cache_data
def load_data():
    if os.path.exists('data/cleaned_startup_data.csv'):
        df = pd.read_csv('data/cleaned_startup_data.csv')
    else:
        # Fallback to cleaning if not exists
        try:
            from utils.preprocess import preprocess_data
            df = preprocess_data('data/startup_funding.csv', 'data/cleaned_startup_data.csv')
        except:
            st.error("Dataset not found. Please check data/startup_funding.csv")
            return pd.DataFrame()
            
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Funding Insights")
st.sidebar.markdown("---")
option = st.sidebar.selectbox("Navigation", ["Global Overview", "Startup Profile", "Investor Portfolio", "Investment Predictor"])

# ---------------- PAGES ----------------

def overall_dashboard():
    st.title("Global Startup Funding Overview")
    st.markdown("Macro-level analysis of the global venture capital ecosystem (Amount in ₹ Crores).")

    # Top level KPIs
    c1, c2, c3, c4 = st.columns(4)
    
    # Unit conversion from USD to INR Crores
    total_funding_cr = (df['amount'].sum() * USD_TO_INR) / CRORE
    avg_funding_cr = (df['amount'].mean() * USD_TO_INR) / CRORE
    unique_startups = df['startup'].nunique()
    unique_investors = df['investors'].nunique()

    with c1:
        st.metric("Total Funding (₹)", f"₹{total_funding_cr:,.1f} Cr")
    with c2:
        st.metric("Avg Funding (₹)", f"₹{avg_funding_cr:,.2f} Cr")
    with c3:
        st.metric("Startups", f"{unique_startups:,}")
    with c4:
        st.metric("Investors", f"{unique_investors:,}")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Market Trends", "📂 Sector Analysis", "🌍 Geographical Focus"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Historical Funding Trends (₹ Cr)")
            yearly_funding = df.groupby('year')['amount'].sum().reset_index()
            yearly_funding['amount_cr'] = (yearly_funding['amount'] * USD_TO_INR) / CRORE
            fig = px.area(yearly_funding, x='year', y='amount_cr', 
                          title="Year-wise Funding Evolution",
                          labels={'amount_cr': 'Amount (₹ Cr)', 'year': 'Year'},
                          color_discrete_sequence=['#6366f1'])
            fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Cumulative Capital Flow (₹ Cr)")
            yearly_funding['cumulative_cr'] = yearly_funding['amount_cr'].cumsum()
            fig = px.line(yearly_funding, x='year', y='cumulative_cr', 
                          title="Total Capital Growth",
                          labels={'cumulative_cr': 'Cumulative Amount (₹ Cr)'},
                          markers=True, line_shape='spline')
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Investment Type Distribution")
        round_dist = df.groupby('round')['amount'].sum().reset_index().sort_values('amount', ascending=False).head(8)
        fig = px.pie(round_dist, values='amount', names='round', hole=0.5, 
                     title="Breakdown by Funding Stage",
                     color_discrete_sequence=px.colors.sequential.Viridis)
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Leading Industry Verticals (₹ Cr)")
            top_sectors = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10).reset_index()
            top_sectors['amount_cr'] = (top_sectors['amount'] * USD_TO_INR) / CRORE
            fig = px.bar(top_sectors, x='amount_cr', y='vertical', 
                         orientation='h', 
                         title="Top Verticals by Funding",
                         labels={'amount_cr': 'Amount (₹ Cr)'},
                         color='amount_cr',
                         color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Average Ticket Size by Sector (₹ Cr)")
            avg_sector = df.groupby('vertical')['amount'].mean().sort_values(ascending=False).head(10).reset_index()
            avg_sector['avg_cr'] = (avg_sector['amount'] * USD_TO_INR) / CRORE
            fig = px.strip(avg_sector, x='avg_cr', y='vertical', title="Mean Investment per Round", color='vertical')
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Hierarchical Sector Mapping")
        sun_df = df[df['amount'].notna()].groupby(['vertical', 'city', 'startup'])['amount'].sum().reset_index()
        sun_df = sun_df.sort_values('amount', ascending=False).head(50)
        sun_df['amount_cr'] = (sun_df['amount'] * USD_TO_INR) / CRORE
        fig = px.sunburst(sun_df, path=['vertical', 'city', 'startup'], values='amount_cr',
                          title="Multi-Level Funding Relation (Industry -> City -> Startup)")
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Geographical Concentration")
            city_funding = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.pie(city_funding, values='amount', names='city', 
                         title="Top 10 Cities", hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Annual Deal Frequency")
            deal_count = df.groupby('year').size().reset_index(name='count')
            fig2 = px.line(deal_count, x='year', y='count', title="No. of Deals", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

def startup_analysis():
    st.title("Startup Performance Profile")
    
    selected_startup = st.selectbox("Search Startup", sorted(df['startup'].unique()))
    
    if st.button("Analyze"):
        sub_df = df[df['startup'] == selected_startup]
        
        st.subheader(f"Results for {selected_startup}")
        
        c1, c2, c3 = st.columns(3)
        total_cr = (sub_df['amount'].sum() * USD_TO_INR) / CRORE
        c1.metric("Industry", sub_df['vertical'].iloc[0])
        c2.metric("Base City", sub_df['city'].iloc[0])
        c3.metric("Total Funding Received (₹)", f"₹{total_cr:,.1f} Cr")
        
        st.markdown("---")
        
        # Funding Rounds
        st.subheader("Capital Deployment History (₹ Cr)")
        sub_df['amount_cr'] = (sub_df['amount'] * USD_TO_INR) / CRORE
        fig = px.bar(sub_df, x='date', y='amount_cr', color='round', 
                     title="Funding over Time",
                     labels={'amount_cr': 'Amount (₹ Cr)'},
                     hover_data=['investors'])
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Market Benchmarking (₹ Cr)")
        sector = sub_df['vertical'].iloc[0]
        sector_df = df[df['vertical'] == sector].copy()
        sector_df['amount_cr'] = (sector_df['amount'] * USD_TO_INR) / CRORE
        
        fig = px.box(sector_df, y='amount_cr', title=f"Funding Distribution in {sector}", 
                     points="all", color_discrete_sequence=['#6366f1'])
        # Add point for current startup
        fig.add_trace(go.Scatter(x=[0], y=[sub_df['amount_cr'].max()], 
                                 mode='markers', name='Selected Startup Max', 
                                 marker=dict(color='red', size=15, symbol='star')))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Primary Investors")
        st.write(", ".join(sub_df['investors'].astype(str).unique()))
        
        st.subheader("Raw Data")
        st.dataframe(sub_df, use_container_width=True)

def investor_analysis():
    st.title("Investor Portfolio Intelligence")
    
    # Flatten investors if multiple exist
    def get_all_investors():
        all_inv = []
        for i in df['investors'].dropna():
            all_inv.extend([x.strip() for x in i.split(',')])
        return sorted(list(set(all_inv)))
    
    selected_investor = st.selectbox("Search Investor", get_all_investors())
    
    if st.button("Show Portfolio"):
        sub_df = df[df['investors'].str.contains(selected_investor, na=False)]
        
        st.subheader(f"Portfolio of {selected_investor}")
        
        total_cr = (sub_df['amount'].sum() * USD_TO_INR) / CRORE
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Invested (₹)", f"₹{total_cr:,.1f} Cr")
        c2.metric("Companies", sub_df['startup'].nunique())
        c3.metric("Peak Year", int(sub_df.groupby('year')['amount'].sum().idxmax()))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Portfolio Sector Allocation")
            sec_dist = sub_df.groupby('vertical')['amount'].sum().reset_index()
            fig = px.pie(sec_dist, values='amount', names='vertical', hole=0.3)
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Regional Investment Focus")
            city_dist = sub_df.groupby('city')['amount'].sum().reset_index()
            fig = px.bar(city_dist, x='city', y='amount', color='amount')
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Capital Deployment Timeline (₹ Cr)")
        sub_df['amount_cr'] = (sub_df['amount'] * USD_TO_INR) / CRORE
        fig = px.scatter(sub_df, x='date', y='amount_cr', size='amount_cr', color='startup',
                         title="Investment Distribution Over Time",
                         hover_data=['round'])
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Latest 10 Investments")
        st.table(sub_df[['date', 'startup', 'vertical', 'amount']].sort_values('date', ascending=False).head(10))

def funding_predictor():
    st.title("Investment Quantification Engine")
    st.markdown("Predictive analytics for estimating startup valuation and funding potential.")

    # Load Model
    model_path = 'utils/models/funding_model.pkl'
    encoder_path = 'utils/models/encoders.pkl'

    if not os.path.exists(model_path):
        st.warning("Prediction model not found. Training it now... please wait.")
        from utils.train_model import train_model
        train_model('data/cleaned_startup_data.csv')

    model = joblib.load(model_path)
    encoders = joblib.load(encoder_path)

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            industry = st.selectbox("Industry Vertical", sorted(encoders['vertical'].classes_))
            city = st.selectbox("City Location", sorted(encoders['city'].classes_))
        with col2:
            year = st.number_input("Target Year", min_value=2024, max_value=2030, value=2024)
            month = st.slider("Target Month", 1, 12, 6)
        
        submit = st.form_submit_button("Predict Estimated Funding")

    if submit:
        # Prepare Input
        try:
            ind_enc = encoders['vertical'].transform([industry])[0]
            city_enc = encoders['city'].transform([city])[0]
            
            # Create a DataFrame with feature names to avoid UserWarning
            input_df = pd.DataFrame([[ind_enc, city_enc, year, month]], 
                                    columns=['vertical', 'city', 'year', 'month'])
            prediction_usd = model.predict(input_df)[0]
            prediction_cr = (prediction_usd * USD_TO_INR) / CRORE
            
            st.success(f"### Predicted Funding Allocation: **₹{prediction_cr:,.2f} Crore**")
            st.info("Performance estimate based on historical volatility and regional trends.")
            
            # Show feature importance or context
            st.markdown("---")
            st.subheader("Why this amount?")
            st.write(f"Historically, startups in **{industry}** located in **{city}** have shown specific funding patterns. The model uses a Random Forest Regressor to approximate these trends.")
            
        except Exception as e:
            st.error(f"Error in prediction: {e}")

# ROUTING
if option == "Global Overview":
    overall_dashboard()
elif option == "Startup Profile":
    startup_analysis()
elif option == "Investor Portfolio":
    investor_analysis()
elif option == "Investment Predictor":
    funding_predictor()