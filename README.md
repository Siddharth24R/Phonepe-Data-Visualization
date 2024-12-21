# PhonePe Pulse Data Visualization Dashboard 📊

## Overview
This Streamlit application provides a comprehensive visualization dashboard for PhonePe's transaction and user data across India. It offers insights into transaction patterns, user behavior, and geographical distribution of PhonePe usage.

## Features 🌟

### 1. Transaction Analysis
- Detailed visualization of transaction patterns
- State-wise transaction distribution
- Transaction type breakdown
- Amount and count analysis
- Quarter-wise trend analysis

### 2. User Analysis
- User registration patterns
- App usage statistics
- Brand preferences
- State and district-wise user distribution
- Device usage analytics

### 3. Geographical Insights
- Interactive choropleth maps
- State-wise distribution visualization
- Regional usage patterns
- District-level analysis

### 4. Facts & Insights
- Top performing states and districts
- Mobile brand usage statistics
- Growth trends
- Transaction patterns
- User behavior insights

## Prerequisites 📋

### Required Dependencies
```python
streamlit
pandas
numpy
plotly.express
plotly.graph_objects
requests
psycopg2-binary
Pillow
streamlit-option-menu
```

### Database Setup
The application requires a PostgreSQL database with the following tables:
- aggregated_transaction
- map_user
- aggregated_user
- map_transaction

## Installation & Setup 🛠️

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure the database connection:
Update the following parameters in the code:
```python
host="localhost"
user="your_username"
password="your_password"
database="your_database"
port="5432"
```

4. Run the application:
```bash
streamlit run app.py
```

## Project Structure 📁
```
project/
│
├── app.py                  # Main application file
├── requirements.txt        # Dependencies
├── README.md              # Documentation
└── assets/                # Static assets
```

## Features Deep Dive 🔍

### Transaction Analysis
- Year and quarter-wise analysis
- State-specific transaction patterns
- Transaction type distribution
- Amount and count visualizations

### User Analysis
- Registration trends
- App opens statistics
- Brand usage patterns
- Geographical distribution

### Geographical Insights
- Interactive state maps
- District-level analysis
- Regional comparison tools
- Trend visualization

## Data Visualization Components 📈

The dashboard includes:
- Choropleth maps
- Pie charts
- Bar graphs
- Line plots
- Sunburst diagrams
- Interactive filters

## Performance Optimization 🚀

- Data caching implementation
- Efficient database queries
- Optimized visualization rendering
- Context managers for database connections

## Security Features 🔒

- Secure database connection handling
- Error handling and logging
- Input validation
- Safe data processing

## Contributing 🤝

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments 🙏

- PhonePe Pulse for the dataset
- Streamlit for the framework
- Contributors and maintainers
