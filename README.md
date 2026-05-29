# 🔍 FraudShield - Advanced Fraud Detection System

## 📌 Project Overview

**FraudShield** is a comprehensive web-based fraud detection and analytics system built with Flask. It analyzes banking and UPI transaction data to identify suspicious activities using rule-based detection algorithms (No Machine Learning required). The system provides real-time monitoring, interactive dashboards, customer risk profiling, and fraud pattern analysis.

### 🎯 Key Features

- **4 Types of Fraud Detection** (No ML):
  - High Amount Transaction Fraud
  - Unusual Timing Fraud (Late Night Transactions)
  - Low Balance - High Withdrawal Fraud
  - Frequent Transactions Fraud

- **Interactive Dashboard** with 6 Analytical Plots:
  - Transaction Amount Distribution
  - Transaction Type Distribution
  - Geographic (State-wise) Analysis
  - Account Type Distribution
  - Channel Distribution
  - Merchant Category Analysis

- **Real-Time Monitoring** - Live transaction alerts and metrics
- **Fraud Pattern Analysis** - Historical pattern detection
- **Customer Risk Profiling** - Individual customer risk assessment
- **Time Period Comparison** - Compare fraud metrics across periods
- **Fraud Awareness Page** - Educational content about common frauds
- **Dark Theme UI** - Modern, eye-friendly interface

## 📁 Project Structure
fraud_detection_project/
│
├── app.py # Main Flask application
├── requirements.txt # Python dependencies
├── README.md # Project documentation
│
├── data/ # Data directory
│ ├── indian_banking_transactions.csv # Banking transactions data
│ └── upi_transactions_2024.csv # UPI transactions data
│
├── static/ # Static files
│ ├── css/
│ │ └── style.css # Custom CSS styles
│ └── js/
│ └── dashboard.js # Dashboard JavaScript
│
└── templates/ # HTML templates
├── base.html # Base template
├── index.html # Home page
├── dashboard.html # Analytics dashboard
├── prediction.html # Fraud detection page
├── real_time.html # Live monitoring
├── patterns.html # Fraud patterns analysis
├── customer_profile.html # Customer risk profile
├── compare.html # Time comparison
├── awareness.html # Fraud awareness
└── about.html # About us page


## 🛠️ Requirements

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Python Packages

```txt
Flask==2.3.3          # Web framework
pandas==2.0.3         # Data processing and analysis
numpy==1.24.3         # Numerical operations
plotly==5.15.0        # Interactive visualizations


git clone <your-repo-url>
cd fraud_detection_project


# for windows

python -m venv venv
venv\Scripts\activate


# for mac

python3 -m venv venv
source venv/bin/activate

#  Install Dependencies

pip install -r requirements.txt

Or install manually:


pip install Flask==2.3.3 pandas==2.0.3 numpy==1.24.3 plotly==5.15.0


 # Run the Application

python app.py

http://localhost:5000

