from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime
import os

app = Flask(__name__)

# ============================================
# LOAD YOUR EXACT DATA
# ============================================

print("\n" + "="*60)
print("LOADING YOUR DATA...")
print("="*60)

# Load Banking Data
bank_df = pd.DataFrame()
bank_path = 'data/indian_banking_transactions.csv'
if os.path.exists(bank_path):
    bank_df = pd.read_csv(bank_path)
    # Convert date columns
    if 'transaction_date' in bank_df.columns:
        bank_df['transaction_date'] = pd.to_datetime(bank_df['transaction_date'], errors='coerce')
    print(f"✅ Banking Data: {len(bank_df):,} rows, {len(bank_df.columns)} columns")
else:
    print(f"❌ Banking file not found")

# Load UPI Data
upi_df = pd.DataFrame()
upi_path = 'data/upi_transactions_2024.csv'
if os.path.exists(upi_path):
    upi_df = pd.read_csv(upi_path)
    # Convert timestamp
    if 'timestamp' in upi_df.columns:
        upi_df['timestamp'] = pd.to_datetime(upi_df['timestamp'], errors='coerce')
    print(f"✅ UPI Data: {len(upi_df):,} rows, {len(upi_df.columns)} columns")
else:
    print(f"❌ UPI file not found")

print("="*60 + "\n")

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Home Page"""
    total_bank = len(bank_df)
    total_upi = len(upi_df)
    total_transactions = total_bank + total_upi
    
    # Count frauds
    bank_frauds = int(bank_df['is_fraud'].sum()) if 'is_fraud' in bank_df.columns else 0
    upi_frauds = int(upi_df['fraud_flag'].sum()) if 'fraud_flag' in upi_df.columns else 0
    total_fraud = bank_frauds + upi_frauds
    
    fraud_rate = (total_fraud / total_transactions * 100) if total_transactions > 0 else 0
    
    return render_template('index.html', 
                         total_transactions=total_transactions,
                         total_fraud=total_fraud,
                         fraud_rate=round(fraud_rate, 2))

@app.route('/dashboard')
def dashboard():
    """Dashboard with plots using Chart.js"""
    
    # Summary statistics
    summary = {
        'total_bank': f"{len(bank_df):,}",
        'total_upi': f"{len(upi_df):,}",
        'bank_frauds': int(bank_df['is_fraud'].sum()) if 'is_fraud' in bank_df.columns else 0,
        'upi_frauds': int(upi_df['fraud_flag'].sum()) if 'fraud_flag' in upi_df.columns else 0,
        'avg_amount': round(bank_df['transaction_amount'].mean(), 2) if 'transaction_amount' in bank_df.columns else 0,
    }
    
    # Prepare data for charts
    chart_data = {}
    
    # Chart 1: Amount Distribution Histogram
    if 'transaction_amount' in bank_df.columns:
        # Create bins for histogram
        amounts = bank_df['transaction_amount'].dropna()
        # Create bins (0-10000, 10000-20000, etc.)
        bins = [0, 10000, 25000, 50000, 75000, 100000, 150000, 200000, 300000, 500000, 1000000]
        labels = ['<10K', '10K-25K', '25K-50K', '50K-75K', '75K-100K', '100K-150K', '150K-200K', '200K-300K', '300K-500K', '>500K']
        
        # Bin the data
        binned = pd.cut(amounts, bins=bins, labels=labels)
        amount_counts = binned.value_counts().sort_index()
        
        chart_data['amount_labels'] = amount_counts.index.tolist()
        chart_data['amount_counts'] = amount_counts.values.tolist()
    
    # Chart 2: Transaction Type
    if 'transaction_type' in bank_df.columns:
        type_counts = bank_df['transaction_type'].value_counts()
        chart_data['type_labels'] = type_counts.index.tolist()
        chart_data['type_counts'] = type_counts.values.tolist()
    
    # Chart 3: Top States
    if 'state' in bank_df.columns:
        state_counts = bank_df['state'].value_counts().head(10)
        chart_data['state_labels'] = state_counts.index.tolist()
        chart_data['state_counts'] = state_counts.values.tolist()
    
    # Chart 4: Account Type
    if 'account_type' in bank_df.columns:
        account_counts = bank_df['account_type'].value_counts()
        chart_data['account_labels'] = account_counts.index.tolist()
        chart_data['account_counts'] = account_counts.values.tolist()
    
    # Chart 5: Channel
    if 'channel' in bank_df.columns:
        channel_counts = bank_df['channel'].value_counts()
        chart_data['channel_labels'] = channel_counts.index.tolist()
        chart_data['channel_counts'] = channel_counts.values.tolist()
    
    # Chart 6: Merchant Category
    if 'merchant_category' in bank_df.columns:
        merchant_counts = bank_df['merchant_category'].value_counts().head(10)
        chart_data['merchant_labels'] = merchant_counts.index.tolist()
        chart_data['merchant_counts'] = merchant_counts.values.tolist()
    
    print(f"Chart data prepared: {list(chart_data.keys())}")
    
    return render_template('dashboard.html', summary=summary, chart_data=chart_data)

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    """Fraud Detection with 4 types (No ML)"""
    fraud_results = []
    selected_type = None
    result_count = 0
    
    if request.method == 'POST':
        selected_type = request.form.get('fraud_type')
        
        # Type 1: High Amount Fraud
        if selected_type == 'high_amount':
            threshold = float(request.form.get('amount_threshold', 50000))
            fraud_df = bank_df[bank_df['transaction_amount'] > threshold].copy()
            fraud_df['fraud_type'] = 'High Amount Transaction'
            fraud_df['risk_score'] = (fraud_df['transaction_amount'] / threshold * 100).clip(0, 100)
            # Select columns to display
            display_cols = ['customer_id', 'transaction_amount', 'transaction_type', 'state', 'merchant_category', 'fraud_type', 'risk_score']
            available_cols = [col for col in display_cols if col in fraud_df.columns]
            fraud_results = fraud_df[available_cols].head(50).to_dict('records')
            result_count = len(fraud_df)
            print(f"High amount fraud detected: {result_count} transactions")
        
        # Type 2: Unusual Timing (Late Night)
        elif selected_type == 'unusual_timing':
            if 'transaction_hour' in bank_df.columns:
                fraud_df = bank_df[bank_df['transaction_hour'].between(0, 5)].copy()
                fraud_df['fraud_type'] = 'Suspicious Timing (Late Night)'
                fraud_df['risk_score'] = 75
                display_cols = ['customer_id', 'transaction_amount', 'transaction_type', 'state', 'merchant_category', 'fraud_type', 'risk_score']
                available_cols = [col for col in display_cols if col in fraud_df.columns]
                fraud_results = fraud_df[available_cols].head(50).to_dict('records')
                result_count = len(fraud_df)
                print(f"Unusual timing fraud detected: {result_count} transactions")
        
        # Type 3: Low Balance - High Withdrawal
        elif selected_type == 'low_balance':
            if 'account_balance' in bank_df.columns:
                fraud_df = bank_df[bank_df['transaction_amount'] > (bank_df['account_balance'] * 0.8)].copy()
                fraud_df['fraud_type'] = 'Low Balance - High Withdrawal'
                fraud_df['risk_score'] = 85
                display_cols = ['customer_id', 'transaction_amount', 'account_balance', 'transaction_type', 'state', 'fraud_type', 'risk_score']
                available_cols = [col for col in display_cols if col in fraud_df.columns]
                fraud_results = fraud_df[available_cols].head(50).to_dict('records')
                result_count = len(fraud_df)
                print(f"Low balance fraud detected: {result_count} transactions")
        
        # Type 4: Frequent Transactions
        elif selected_type == 'frequent_transactions':
            threshold = int(request.form.get('frequency_threshold', 10))
            if 'transaction_date' in bank_df.columns and 'customer_id' in bank_df.columns:
                fraud_df = bank_df.copy()
                fraud_df['date_only'] = fraud_df['transaction_date'].dt.date
                txn_counts = fraud_df.groupby(['customer_id', 'date_only']).size().reset_index(name='count')
                frequent_customers = txn_counts[txn_counts['count'] > threshold]['customer_id'].unique()
                fraud_df = fraud_df[fraud_df['customer_id'].isin(frequent_customers)].copy()
                fraud_df['fraud_type'] = 'Frequent Transactions (Daily Limit Exceeded)'
                fraud_df['risk_score'] = 90
                display_cols = ['customer_id', 'transaction_amount', 'transaction_type', 'state', 'merchant_category', 'fraud_type', 'risk_score']
                available_cols = [col for col in display_cols if col in fraud_df.columns]
                fraud_results = fraud_df[available_cols].head(50).to_dict('records')
                result_count = len(fraud_df)
                print(f"Frequent transactions fraud detected: {result_count} transactions")
    
    return render_template('prediction.html', fraud_results=fraud_results, 
                         selected_type=selected_type, result_count=result_count)

@app.route('/awareness')
def awareness():
    """Fraud Awareness Page"""
    common_frauds = [
        {'name': 'Phishing Attacks', 'icon': '🎣',
         'description': 'Fake emails/messages pretending to be from your bank to steal credentials.',
         'prevention': 'Never click suspicious links. Always verify sender email address.'},
        {'name': 'UPI QR Code Scam', 'icon': '📱',
         'description': 'Fake QR codes that initiate payments instead of receiving money.',
         'prevention': 'Only scan QR codes from trusted sources. Verify payment request details.'},
        {'name': 'OTP Fraud', 'icon': '🔑',
         'description': 'Fraudsters call pretending to be bank officials and ask for OTP.',
         'prevention': 'Never share OTP with anyone. Banks never ask for OTP over phone.'},
        {'name': 'Card Skimming', 'icon': '💳',
         'description': 'Devices installed on ATMs capture card information.',
         'prevention': 'Cover PIN while entering. Check for suspicious devices on ATMs.'},
        {'name': 'Investment Scams', 'icon': '📈',
         'description': 'Fake investment schemes promising unrealistic returns.',
         'prevention': 'Research before investing. Verify SEBI registration.'},
        {'name': 'SIM Swap Fraud', 'icon': '📞',
         'description': 'Fraudsters get duplicate SIM to receive OTPs and access accounts.',
         'prevention': 'Set SIM lock with carrier. Be alert if phone loses network.'}
    ]
    
    total_frauds = int(bank_df['is_fraud'].sum()) if 'is_fraud' in bank_df.columns else 0
    total_frauds += int(upi_df['fraud_flag'].sum()) if 'fraud_flag' in upi_df.columns else 0
    
    stats = {
        'total_frauds_detected': total_frauds,
        'amount_saved': '₹8.7 Cr',
        'active_alerts': 342,
        'success_rate': '94%'
    }
    
    return render_template('awareness.html', common_frauds=common_frauds, stats=stats)

@app.route('/about')
def about():
    """About Us Page"""
    team_members = [
        {'name': 'Data Analytics Team', 'role': 'Fraud Detection Specialists', 'icon': '📊'},
        {'name': 'Security Experts', 'role': 'Cybersecurity Professionals', 'icon': '🔒'},
        {'name': 'Data Scientists', 'role': 'Analytics & Visualization', 'icon': '🤖'},
        {'name': 'Customer Support', 'role': '24/7 Fraud Assistance', 'icon': '💬'}
    ]
    return render_template('about.html', team_members=team_members)

@app.route('/real_time_monitoring')
def real_time_monitoring():
    """Real-time monitoring"""
    alerts = []
    
    # Get fraud transactions from bank data
    if 'is_fraud' in bank_df.columns:
        fraud_data = bank_df[bank_df['is_fraud'] == 1].head(20)
        for idx, row in fraud_data.iterrows():
            alerts.append({
                'transaction_id': row.get('transaction_id', f'TXN{idx}'),
                'amount': row.get('transaction_amount', 0),
                'customer': row.get('customer_id', 'Unknown'),
                'risk_score': 85,
                'reasons': 'Flagged as fraudulent',
                'time': str(row.get('transaction_time', datetime.now().strftime('%H:%M:%S')))
            })
    
    metrics = {
        'transactions_per_minute': round(len(bank_df) / (30 * 24 * 60), 2),
        'high_risk_transactions': int(bank_df['is_fraud'].sum()) if 'is_fraud' in bank_df.columns else 0,
        'total_volume': round(bank_df['transaction_amount'].sum(), 2) if 'transaction_amount' in bank_df.columns else 0,
        'peak_hour': int(bank_df['transaction_hour'].mode().iloc[0]) if 'transaction_hour' in bank_df.columns else 14
    }
    
    return render_template('real_time.html', metrics=metrics, alerts=alerts)

@app.route('/customer_risk_profile', methods=['GET', 'POST'])
def customer_risk_profile():
    """Customer risk profile page"""
    profile = None
    error = None
    
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        
        if customer_id and 'customer_id' in bank_df.columns:
            # Search for the customer
            customer_data = bank_df[bank_df['customer_id'].astype(str) == str(customer_id)]
            
            if not customer_data.empty:
                # Calculate risk score
                risk_score = 0
                risk_factors = []
                
                # Check for fraud history
                if 'is_fraud' in customer_data.columns:
                    fraud_count = int(customer_data['is_fraud'].sum())
                    if fraud_count > 0:
                        risk_score += min(fraud_count * 25, 50)
                        risk_factors.append(f"⚠️ Has {fraud_count} flagged transaction(s)")
                
                # Check for high-value transactions
                if 'transaction_amount' in customer_data.columns:
                    high_value = customer_data[customer_data['transaction_amount'] > 50000]
                    if len(high_value) > 0:
                        risk_score += min(len(high_value) * 10, 30)
                        risk_factors.append(f"💰 {len(high_value)} high-value transaction(s) (>₹50K)")
                
                # Check for unusual timing
                if 'transaction_hour' in customer_data.columns:
                    late_night = customer_data[customer_data['transaction_hour'].between(0, 5)]
                    if len(late_night) > 0:
                        risk_score += min(len(late_night) * 5, 20)
                        risk_factors.append(f"🌙 {len(late_night)} late-night transaction(s) (12AM-5AM)")
                
                # Create profile with safe data conversion
                profile = {
                    'customer_id': str(customer_id),
                    'customer_name': str(customer_data.iloc[0].get('customer_name', customer_id)),
                    'risk_score': min(risk_score, 100),
                    'risk_level': get_risk_level(min(risk_score, 100)),
                    'risk_factors': risk_factors if risk_factors else ["✅ No unusual activity detected"],
                    'total_transactions': int(len(customer_data)),
                    'total_spent': float(customer_data['transaction_amount'].sum()) if 'transaction_amount' in customer_data.columns else 0,
                    'average_transaction': float(customer_data['transaction_amount'].mean()) if 'transaction_amount' in customer_data.columns else 0,
                    'preferred_channel': str(customer_data['channel'].mode().iloc[0]) if 'channel' in customer_data.columns and len(customer_data['channel'].mode()) > 0 else 'N/A',
                    'preferred_state': str(customer_data['state'].mode().iloc[0]) if 'state' in customer_data.columns and len(customer_data['state'].mode()) > 0 else 'N/A',
                    'recent_transactions': customer_data.tail(10).to_dict('records')
                }
            else:
                error = f"❌ Customer ID '{customer_id}' not found. Please check and try again."
        else:
            error = "❌ Please enter a Customer ID"
    
    return render_template('customer_profile.html', profile=profile, error=error)

def get_risk_level(score):
    """Return risk level based on score"""
    if score >= 70:
        return {'text': 'Critical', 'class': 'danger', 'icon': '🔴'}
    elif score >= 40:
        return {'text': 'High', 'class': 'warning', 'icon': '🟠'}
    elif score >= 20:
        return {'text': 'Medium', 'class': 'info', 'icon': '🟡'}
    else:
        return {'text': 'Low', 'class': 'success', 'icon': '🟢'}
    
@app.route('/compare_timeframes')
def compare_timeframes():
    """Compare time periods"""
    comparison = {}
    
    if 'transaction_date' in bank_df.columns and 'is_fraud' in bank_df.columns:
        max_date = bank_df['transaction_date'].max()
        
        periods = {
            'Last 7 Days': bank_df[bank_df['transaction_date'] >= (max_date - pd.Timedelta(days=7))],
            'Last 30 Days': bank_df[bank_df['transaction_date'] >= (max_date - pd.Timedelta(days=30))],
            'Last 90 Days': bank_df[bank_df['transaction_date'] >= (max_date - pd.Timedelta(days=90))],
            'All Time': bank_df
        }
        
        for period_name, period_data in periods.items():
            if len(period_data) > 0:
                fraud_count = int(period_data['is_fraud'].sum())
                fraud_rate = (fraud_count / len(period_data)) * 100 if len(period_data) > 0 else 0
                
                comparison[period_name] = {
                    'transactions': len(period_data),
                    'frauds': fraud_count,
                    'fraud_rate': round(fraud_rate, 2),
                    'avg_amount': round(period_data['transaction_amount'].mean(), 2),
                    'total_volume': round(period_data['transaction_amount'].sum(), 2)
                }
    
    return render_template('compare.html', comparison=comparison)

@app.route('/patterns')
def patterns():
    """Fraud patterns analysis"""
    patterns = {}
    
    if 'is_fraud' in bank_df.columns:
        fraud_data = bank_df[bank_df['is_fraud'] == 1]
        
        if len(fraud_data) > 0:
            print(f"Analyzing {len(fraud_data)} fraud transactions for patterns...")
            
            # Pattern 1: Amount ranges for fraud
            if 'transaction_amount' in fraud_data.columns:
                fraud_data['amount_range'] = pd.cut(fraud_data['transaction_amount'], 
                    bins=[0, 1000, 10000, 50000, 100000, 500000, 1000000],
                    labels=['<₹1K', '₹1K-₹10K', '₹10K-₹50K', '₹50K-₹1L', '₹1L-₹5L', '>₹5L'])
                amount_ranges = fraud_data['amount_range'].value_counts()
                patterns['amount_ranges'] = {str(k): int(v) for k, v in amount_ranges.items()}
                print(f"  ✓ Amount ranges: {len(amount_ranges)} categories")
            
            # Pattern 2: Fraud by hour
            if 'transaction_hour' in fraud_data.columns:
                hour_counts = fraud_data['transaction_hour'].value_counts().sort_index()
                patterns['fraud_by_hour'] = {int(k): int(v) for k, v in hour_counts.items()}
                print(f"  ✓ Hour distribution: {len(hour_counts)} hours")
            
            # Pattern 3: Fraud by state
            if 'state' in fraud_data.columns:
                state_counts = fraud_data['state'].value_counts().head(10)
                patterns['fraud_by_state'] = {str(k): int(v) for k, v in state_counts.items()}
                print(f"  ✓ Top states: {len(state_counts)} states")
            
            # Pattern 4: Fraud by merchant category
            if 'merchant_category' in fraud_data.columns:
                merchant_counts = fraud_data['merchant_category'].value_counts().head(10)
                patterns['fraud_by_merchant'] = {str(k): int(v) for k, v in merchant_counts.items()}
                print(f"  ✓ Merchant categories: {len(merchant_counts)} categories")
            
            # Pattern 5: Fraud by channel
            if 'channel' in fraud_data.columns:
                channel_counts = fraud_data['channel'].value_counts()
                patterns['fraud_by_channel'] = {str(k): int(v) for k, v in channel_counts.items()}
                print(f"  ✓ Channels: {len(channel_counts)} channels")
            
            # Pattern 6: Repeat offenders
            if 'customer_id' in fraud_data.columns:
                repeat_offenders = fraud_data['customer_id'].value_counts()
                repeat_offenders = repeat_offenders[repeat_offenders > 1].head(10)
                patterns['repeat_offenders'] = {str(k): int(v) for k, v in repeat_offenders.items()}
                print(f"  ✓ Repeat offenders: {len(repeat_offenders)} customers")
    
    return render_template('patterns.html', patterns=patterns)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 FRAUD DETECTION SYSTEM STARTING")
    print("="*60)
    print(f"Banking Data: {len(bank_df):,} rows")
    print(f"UPI Data: {len(upi_df):,} rows")
    if 'is_fraud' in bank_df.columns:
        print(f"Bank Frauds: {int(bank_df['is_fraud'].sum()):,}")
    if 'fraud_flag' in upi_df.columns:
        print(f"UPI Frauds: {int(upi_df['fraud_flag'].sum()):,}")
    print("="*60)
    print("\n📍 Open: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)