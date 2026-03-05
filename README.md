# UAC Care Pipeline Analytics

A production-ready Python analytics dashboard for tracking the care pipeline efficiency for Unaccompanied Alien Children (UAC) through **CBP Custody → HHS Care → Sponsor Placement**.

## 📊 Overview

This dashboard provides comprehensive analytics for:
- **Pipeline flow visualization** through care stages
- **Transition efficiency metrics** (transfer, discharge, throughput)
- **Bottleneck detection** and backlog identification
- **Temporal pattern analysis** (weekday/weekend trends, stagnation detection)
- **Outcome stability scoring** with trend analysis

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd uac-care-pipeline-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard

```bash
# Navigate to src directory
cd src

# Launch Streamlit app
streamlit run uac_dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

## 📁 Project Structure

```
uac-care-pipeline-analytics/
├── src/
│   └── uac_dashboard/
│       ├── __init__.py
│       ├── data.py              # Data models and sample data
│       ├── metrics.py           # KPI computations and analysis
│       ├── visualization.py     # Plotly chart generation
│       └── app.py               # Streamlit web application
├── tests/
│   ├── test_data.py             # Unit tests for data module
│   └── test_metrics.py          # Unit tests for metrics module
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 📈 Key Performance Indicators (KPIs)

### 1. Transfer Efficiency Ratio
**Formula:** `Transfers ÷ (CBP Custody at start + Apprehensions)`

**Interpretation:**
- **> 90%**: Efficient transfer operations
- **70-90%**: Acceptable performance
- **< 70%**: Significant delays or capacity constraints

### 2. Discharge Effectiveness Index
**Formula:** `Discharges ÷ (HHS Care at start + Transfers In)`

**Interpretation:**
- **> 80%**: Effective placement operations
- **50-80%**: Moderate performance
- **< 50%**: Prolonged stays or sponsor matching challenges

### 3. Pipeline Throughput Rate
**Formula:** `(Total Transfers + Total Discharges) ÷ Total Apprehensions`

**Interpretation:**
- **> 85%**: Healthy flowing pipeline
- **60-85%**: Moderate flow
- **< 60%**: Systemic bottlenecks causing accumulation

### 4. Backlog Accumulation Rate
**Formula:** `(Ending Load - Starting Load) ÷ Total Apprehensions`

**Interpretation:**
- **Negative**: System is draining backlog ✓
- **0-20%**: Mild accumulation
- **> 20%**: Rapid accumulation requiring intervention ⚠️

### 5. Outcome Stability Score
**Formula:** `1 - (Standard Deviation of Daily Discharge Rate ÷ Mean Discharge Rate)`

**Interpretation:**
- **> 85%**: Stable operations ✓
- **60-85%**: Moderate variability
- **< 60%**: Erratic performance requiring process review ⚠️

## 🔍 Dashboard Features

### Pipeline Flow Visualization
Interactive Sankey diagram showing the flow of children through care stages:
- Intake (Apprehensions)
- CBP Custody
- HHS Care
- Sponsor Placement
- Remaining loads

### Efficiency Metrics Panel
Real-time gauge charts displaying:
- Transfer Efficiency Ratio
- Discharge Effectiveness Index
- Pipeline Throughput Rate

### Bottleneck Detection
Automated detection of:
- Backlog conditions (mild/moderate/severe)
- Sustained imbalances (consecutive days with inflow > outflow)
- Peak load identification
- Inflow/outflow ratio analysis

### Temporal Analysis
Pattern detection including:
- Weekday vs weekend transfer speed comparison
- Monthly discharge rate trends
- Stagnation period identification (prolonged periods of minimal activity)

### Outcome Stability
Statistical analysis of:
- Discharge rate variability
- Placement consistency scores
- Sudden performance drop detection
- Trend direction (improving/stable/declining)

## 🛠️ Development

### Running Tests

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_metrics
```

### Data Model

The system uses the following data structure:

```python
DailyMetrics(
    date: datetime              # Reporting date
    children_apprehended: int   # Daily intake
    children_in_cbp_custody: int   # Active CBP load
    children_transferred_out: int  # Flow to HHS
    children_in_hhs_care: int      # Active HHS load
    children_discharged: int       # Sponsor placements
)
```

### Extending the Dashboard

To add new metrics:
1. Add KPI definition to `KPI_REGISTRY` in `metrics.py`
2. Implement calculation function in `metrics.py`
3. Add visualization in `visualization.py`
4. Update dashboard layout in `app.py`

## 📝 Sample Data

The dashboard includes a built-in sample data generator that creates realistic synthetic data for demonstration purposes:

```python
from uac_dashboard.data import create_sample_datastore

# Generate 365 days of sample data
data_store = create_sample_datastore(days=365)
```

Sample data features:
- Seasonal variation (quarterly patterns)
- Weekend effects (reduced activity)
- Realistic load balancing
- Configurable random seed for reproducibility

## 🎯 Use Cases

This dashboard is designed for:
- **Operations Managers**: Monitor daily pipeline efficiency
- **Policy Analysts**: Identify systemic bottlenecks and trends
- **Stakeholders**: Track outcome stability and performance
- **Report Generation**: Export visualizations and metrics

## ⚙️ Configuration

### Dashboard Controls

The sidebar provides:
- **Date Range Selection**: Filter data by custom date ranges
- **Display Options**: Toggle ratio-based metrics
- **Alert Thresholds**: Set custom efficiency alert levels

### Alerts

The dashboard automatically generates visual alerts for:
- Efficiency metrics below threshold
- Backlog conditions (moderate/severe)
- Declining performance trends
- Sudden performance drops

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📧 Support

For questions or support:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Maintained by:** UAC Analytics Team
