import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import psycopg2
from PIL import Image
from streamlit_option_menu import option_menu
from contextlib import contextmanager

#PAGE CONFIGURATION
st.set_page_config(
    page_title="PhonePe Pulse",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 0 !important;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F0F0F0;
        border-radius: 10px;
        padding: 10px 15px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Database connection context manager
@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="AI@Guvi12345",
            database="phone_pay",
            port="5432"
        )
        yield conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        yield None
    finally:
        if conn is not None:
            conn.close()

# Data loading functions with caching
@st.cache_data(ttl=600)
def load_data(table_name):
    query = f"SELECT * FROM {table_name}"
    try:
        with get_db_connection() as conn:
            if conn:
                return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error loading {table_name} data: {e}")
    return pd.DataFrame()

# Helper functions
def format_currency(amount):
    if amount >= 1e7:
        return f"₹{amount/1e7:.2f} Cr"
    elif amount >= 1e5:
        return f"₹{amount/1e5:.2f} L"
    return f"₹{amount:,.2f}"

def create_geo_visualization(df, value_column, title):
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(url)
    data = json.loads(response.content)
    
    fig = px.choropleth(
        df,
        geojson=data,
        locations='states',
        featureidkey="properties.ST_NM",
        color=value_column,
        color_continuous_scale="Viridis",
        title=title
    )
    fig.update_geos(fitbounds="locations", visible=False)
    return fig

def show_transaction_analysis():
    st.header("Transaction Analysis")

def show_transaction_analysis():
    st.header("Transaction Analysis")
    
    # Load data
    df = load_data("aggregated_transaction")
    if df.empty:
        st.warning("No transaction data available")
        return
    
    # Year and Quarter selection
    col1, col2 = st.columns([1,2])
    with col1:
        years = sorted(df['years'].unique(), reverse=True)
        year = st.selectbox("Select Year", years)
        quarters = sorted(df['quarter'].unique())
        quarter = st.selectbox("Select Quarter", quarters)
    
    filtered_df = df[(df['years'] == year) & (df['quarter'] == quarter)]
    
    # Transaction Metrics
    total_amount = filtered_df['transaction_amount'].sum()
    total_count = filtered_df['transaction_count'].sum()
    avg_amount = total_amount / total_count if total_count > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transaction Amount", format_currency(total_amount))
    col2.metric("Total Transactions", f"{total_count:,}")
    col3.metric("Average Transaction Value", format_currency(avg_amount))
    
    # State Selection and Transaction Type Distribution
    selected_state = st.selectbox("Select State", sorted(filtered_df['states'].unique()))
    state_df = filtered_df[filtered_df['states'] == selected_state]
    
    # Two pie charts side by side
    col1, col2 = st.columns(2)
    with col1:
        # Transaction amount pie chart
        type_df_amount = state_df.groupby('transaction_type').agg({
            'transaction_amount': 'sum'
        }).reset_index()
        fig_amount = px.pie(type_df_amount, 
                    values='transaction_amount', 
                    names='transaction_type',
                    title=f'{selected_state} Transaction Amount Distribution')
        st.plotly_chart(fig_amount)

    with col2:
        # Transaction count pie chart
        type_df_count = state_df.groupby('transaction_type').agg({
            'transaction_count': 'sum'
        }).reset_index()
        fig_count = px.pie(type_df_count, 
                    values='transaction_count', 
                    names='transaction_type',
                    title=f'{selected_state} Transaction Count Distribution')
        st.plotly_chart(fig_count)
    
    # State metrics and detailed breakdown
    st.subheader(f"{selected_state} Transaction Summary")
    state_total = state_df['transaction_amount'].sum()
    state_count = state_df['transaction_count'].sum()
    st.write(f"Total Amount: {format_currency(state_total)}")
    st.write(f"Transaction Count: {state_count:,}")
    
    if st.button("View More Details"):
        st.write("Transaction Type Breakdown:")
        state_breakdown = state_df.groupby('transaction_type').agg({
            'transaction_amount': 'sum',
            'transaction_count': 'sum'
        }).reset_index()
        st.dataframe(state_breakdown)
    
    # State-wise bar charts
    st.subheader("State-wise Transaction Analysis")
    state_totals = filtered_df.groupby('states').agg({
        'transaction_count': 'sum',
        'transaction_amount': 'sum'
    }).reset_index()
    
    # Transaction Amount by State
    fig_bar_amount = px.bar(state_totals,
                           x='transaction_amount',
                           y='states',
                           orientation='h',
                           title='Transaction Amount by State')
    st.plotly_chart(fig_bar_amount, use_container_width=True)
    
    # Transaction Count by State
    fig_bar_count = px.bar(state_totals,
                          x='transaction_count',
                          y='states',
                          orientation='h',
                          title='Transaction Count by State')
    st.plotly_chart(fig_bar_count, use_container_width=True)

def show_user_analysis():
    st.header("User Analysis")
    
    # Load data
    user_df = load_data("map_user")
    agg_user_df = load_data("aggregated_user")  # For brand analysis
    
    if user_df.empty or agg_user_df.empty:
        st.warning("No user data available")
        return
    
    # Year and Quarter selection
    col1, col2 = st.columns([1,2])
    with col1:
        years = sorted(user_df['years'].unique(), reverse=True)
        year = st.selectbox("Select Year", years, key='user_year')
        quarters = sorted(user_df['quarter'].unique())
        quarter = st.selectbox("Select Quarter", quarters, key='user_quarter')
    
    # Filter data based on selection
    filtered_user_df = user_df[(user_df['years'] == year) & (user_df['quarter'] == quarter)]
    filtered_agg_user_df = agg_user_df[(agg_user_df['years'] == year) & (agg_user_df['quarter'] == quarter)]
    
    # Transaction Type Distribution Pie Chart
    st.subheader("Transaction Type Distribution")
    type_df = filtered_agg_user_df.groupby('brands').agg({
        'transaction_count': 'sum'
    }).reset_index()
    
    fig_pie = px.pie(type_df,
                     values='transaction_count',
                     names='brands',
                     title=f'Transaction Distribution by Brand ({year} Q{quarter})')
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Brand Transaction Count Bar Chart
    st.subheader("Brand-wise Transaction Analysis")
    fig_bar = px.bar(type_df,
                     x='transaction_count',
                     y='brands',
                     orientation='h',
                     title=f'Transaction Count by Brand ({year} Q{quarter})')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Registered Users and App Opens Analysis
    st.subheader("State-wise User Metrics")
    state_metrics = filtered_user_df.groupby('states').agg({
        'registereduser': 'sum',
        'appopens': 'sum'
    }).reset_index()
    
    fig_metrics = go.Figure()
    fig_metrics.add_trace(go.Bar(
        name='Registered Users',
        x=state_metrics['registereduser'],
        y=state_metrics['states'],
        orientation='h',
        marker_color='#ff7f0e'  # Orange color for registered users
    ))
    fig_metrics.add_trace(go.Bar(
        name='App Opens',
        x=state_metrics['appopens'],
        y=state_metrics['states'],
        orientation='h',
        marker_color='#1f77b4'  # Blue color for app opens
    ))
    
    fig_metrics.update_layout(
        barmode='group',
        title=f'Registered Users and App Opens by State ({year} Q{quarter})',
        xaxis_title='Count',
        yaxis_title='State'
    )
    st.plotly_chart(fig_metrics, use_container_width=True)
    
    # State-wise Detailed Analysis
    st.subheader("State-wise Detailed Analysis")
    selected_state = st.selectbox("Select State", sorted(filtered_user_df['states'].unique()))
    state_df = filtered_user_df[filtered_user_df['states'] == selected_state]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Registered Users by District
        fig_reg_users = px.bar(state_df,
                              x='registereduser',
                              y='districts', 
                              orientation='h',
                              title=f'Registered Users by District in {selected_state}',
                              color_discrete_sequence=['#ff7f0e'])  # Orange color
        st.plotly_chart(fig_reg_users, use_container_width=True)
    
    with col2:
        # App Opens by District
        fig_app_opens = px.bar(state_df,
                              x='appopens',
                              y='districts',  
                              orientation='h',
                              title=f'App Opens by District in {selected_state}',
                              color_discrete_sequence=['#1f77b4'])  # Blue color
        st.plotly_chart(fig_app_opens, use_container_width=True)

def show_geographical_insights():
    st.header("Geographical Insights")
    
    # Load all required data
    trans_df = load_data("aggregated_transaction")
    user_df = load_data("map_user")
    
    if trans_df.empty or user_df.empty:
        st.warning("No data available")
        return
    
    # Year and Quarter selection
    col1, col2 = st.columns([1,2])
    with col1:
        years = sorted(trans_df['years'].unique(), reverse=True)
        year = st.selectbox("Select Year", years, key='geo_year')
        quarters = sorted(trans_df['quarter'].unique())
        quarter = st.selectbox("Select Quarter", quarters, key='geo_quarter')
    
    # Visualization type selection
    viz_type = st.radio(
        "Select Visualization",
        ["Transaction Amount", "Transaction Count", "Registered Users"]
    )
    
    # Filter data based on selection
    filtered_trans_df = trans_df[(trans_df['years'] == year) & (trans_df['quarter'] == quarter)]
    filtered_user_df = user_df[(user_df['years'] == year) & (user_df['quarter'] == quarter)]
    
    if viz_type == "Transaction Amount":
        state_totals = filtered_trans_df.groupby('states')['transaction_amount'].sum().reset_index()
        fig = create_geo_visualization(
            state_totals,
            'transaction_amount',
            f'Transaction Amount by State ({year} Q{quarter})'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Transaction Count":
        state_totals = filtered_trans_df.groupby('states')['transaction_count'].sum().reset_index()
        fig = create_geo_visualization(
            state_totals,
            'transaction_count',
            f'Transaction Count by State ({year} Q{quarter})'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Registered Users
        state_totals = filtered_user_df.groupby('states')['registereduser'].sum().reset_index()
        fig = create_geo_visualization(
            state_totals,
            'registereduser',
            f'Registered Users by State ({year} Q{quarter})'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_facts_analysis():
    st.header("PhonePe Facts and Insights")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="AI@Guvi12345",
            database="phone_pay",
            port="5432"
        )
        cursor = conn.cursor()
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return
    
    options = st.selectbox(
        "Select Fact to Explore",
        (
            "Select Facts",
            "Top Brands of Mobile Used",
            "Top 10 Districts - Lowest Transaction Amount",
            "Top 10 Districts - Highest Transaction Amount",
            "PhonePe Users Growth Trend",
            "Top 10 States - Highest PhonePe Usage",
            "Top 10 States - Lowest PhonePe Usage",
            "Top 10 Districts - Highest PhonePe Usage",
            "Top 10 Districts - Lowest PhonePe Usage",
            "Top 10 Districts - Highest Transaction Count",
            "Top 10 Districts - Lowest Transaction Count"
        )
    )
    
    try:
        if options == "Top Brands of Mobile Used":
            year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022])
            
            query = f"""
            SELECT brands, SUM(transaction_count) as count 
            FROM aggregated_user 
            WHERE years = {year} 
            GROUP BY brands 
            ORDER BY count DESC
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Brand', 'Count'])
            
            fig = px.bar(df, x='Brand', y='Count', 
                        title=f'Mobile Brand Usage in {year}',
                        color_discrete_sequence=['#ff4b4b'])
            st.plotly_chart(fig, use_container_width=True)
            
        elif options == "Top 10 Districts - Lowest Transaction Amount":
            year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022])
            
            query = f"""
            SELECT district, SUM(transaction_amount) as amount 
            FROM map_transaction 
            WHERE years = {year} 
            GROUP BY district 
            ORDER BY amount ASC 
            LIMIT 10
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['District', 'Amount'])
            
            fig = px.pie(df, values='Amount', names='District', 
                        title=f'Top 10 Districts with Lowest Transactions ({year})')
            st.plotly_chart(fig, use_container_width=True)
            
        elif options == "Top 10 Districts - Highest Transaction Amount":
            year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022])
            
            query = f"""
            SELECT district, SUM(transaction_amount) as amount 
            FROM map_transaction 
            WHERE years = {year} 
            GROUP BY district 
            ORDER BY amount DESC 
            LIMIT 10
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['District', 'Amount'])
            
            fig = px.pie(df, values='Amount', names='District', 
                        title=f'Top 10 Districts with Highest Transactions ({year})')
            st.plotly_chart(fig, use_container_width=True)
            
        elif options == "PhonePe Users Growth Trend":
            query = """
            SELECT years, SUM(registereduser) as users 
            FROM map_user 
            GROUP BY years 
            ORDER BY years
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['Years', 'Users'])
            
            fig = px.line(df, x='Years', y='Users', 
                         title='PhonePe Users Growth Over Years',
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
        elif options in ["Top 10 States - Highest PhonePe Usage", "Top 10 States - Lowest PhonePe Usage"]:
            year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022])
            order = "DESC" if "Highest" in options else "ASC"
            
            query = f"""
            SELECT states, SUM(registereduser) as users 
            FROM map_user 
            WHERE years = {year} 
            GROUP BY states 
            ORDER BY users {order}
            LIMIT 10
            """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['States', 'Users'])
            
            fig = px.pie(df, 
                        values='Users', 
                        names='States',
                        title=f'{"Top" if "Highest" in options else "Bottom"} 10 States by PhonePe Usage ({year})')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
            
        elif options in ["Top 10 Districts - Highest PhonePe Usage", "Top 10 Districts - Lowest PhonePe Usage"]:
            year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022])
            order = "DESC" if "Highest" in options else "ASC"
            
            query = f"""
            SELECT districts, states, SUM(registereduser) as users 
            FROM map_user 
            WHERE years = {year} 
            GROUP BY districts, states 
            ORDER BY users {order}
            LIMIT 10
            """
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['District', 'State', 'Users'])
            
            fig = px.pie(df, 
                        values='Users', 
                        names='District',
                        title=f'{"Top" if "Highest" in options else "Bottom"} 10 Districts by PhonePe Usage ({year})',
                        hover_data=['State'])
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
            
        elif options in ["Top 10 Districts - Highest Transaction Count", "Top 10 Districts - Lowest Transaction Count"]:
            year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022])
            order = "DESC" if "Highest" in options else "ASC"
            
            query = f"""
            SELECT states, district, SUM(transaction_count) as count 
            FROM map_transaction 
            WHERE years = {year} 
            GROUP BY states, district 
            ORDER BY count {order}
            LIMIT 10
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['States', 'District', 'Count'])
            
            fig = px.sunburst(df, path=['States', 'District'], values='Count',
                             title=f'{"Top" if "Highest" in options else "Bottom"} 10 Districts by Transaction Count ({year})')
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error processing request: {e}")
        st.error("Please check your database schema and column names")
    
    finally:
        cursor.close()
        conn.close()
#  main() 
def main():
    with st.sidebar:
        selected = option_menu(
            "Navigation",
            ["Home", "Transaction Analysis", "User Analysis", 
             "Geographical Insights", "Facts & Insights"],
            icons=['house', 'graph-up', 'people', 'geo-alt', 'info-circle'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#262730"},
                "icon": {"color": "white", "font-size": "30px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
                "nav-link-selected": {"background-color": "#ff4b4b"},
            }
        )
    
    if selected == "Home":
        # Title Section
        st.title("PhonePe Pulse Data Visualization")
        
        # Header and Introduction
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("_India's Best Transaction App_")
            st.write("""
            _PhonePe is a digital wallet and mobile payment platform in India. 
            It uses the Unified Payment Interface (UPI) system to allow users to:_
            """)
            
            # Features Section
            st.markdown("""
            **Key Features:**
            - 💸 Send and receive money
            - 📱 Recharge mobile, DTH, data cards
            - 🧾 Make utility payments
            - 🏪 Pay at shops
            - 💰 Invest in tax saving funds
            - 🛡️ Buy insurance
            - 📈 Invest in mutual funds
            - 🏆 Digital gold
            """)
            
            st.write("""
            _In recent years, PhonePe has expanded its services to include insurance, lending, and wealth management. Additional features include:_
            """)
            features = ["""
                - Fund Transfer
                - Payment to Merchant
                - Recharge and Bill payments
                - Autopay of Bills
                - Cashback and Rewards
            """]
            for feature in features:
                st.write(feature)
            
            # Download Button
            st.markdown("### Get Started")
            st.link_button(
                "**🔥 DOWNLOAD THE APP NOW**",
                "https://www.phonepe.com/app-download/",
                use_container_width=True
            )
        
        with col2:
            # Video Section
            st.subheader("Discover PhonePe")
            video_url = "https://youtu.be/aXnNA4mv1dU?si=HnSu_ETm4X29Lrvf"
            st.video(video_url)
            
            # Additional Links
            st.write("***To know more about PhonePe:***")
            st.link_button(
                "**🌐 Visit PhonePe Website**",
                "https://www.phonepe.com/",
                use_container_width=True
            )
        
        # Analytics Section
        st.markdown("---")
        st.header("Explore Our Analytics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            - 📊 **Transaction Analysis**
                - Track payment patterns
                - Monitor transaction volumes
                        
            - 📱 **User Behavior Analytics**
                - Understand user preferences
                - Analyze app usage patterns
            """)
        
        with col2:
            st.markdown("""
            - 🗺️ **Geographical Insights**
                - Regional transaction patterns
                - State-wise analysis
                        
            - ℹ️ **Facts & Insights**
                - Key statistics
                - Trending patterns
            """)
        
    elif selected == "Transaction Analysis":
        show_transaction_analysis()
    elif selected == "User Analysis":
        show_user_analysis()
    elif selected == "Geographical Insights":
        show_geographical_insights()
    elif selected == "Facts & Insights":
        show_facts_analysis()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
