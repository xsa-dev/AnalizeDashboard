# Backtest Dashboard

A Streamlit application for visualizing backtest results from JSON files.

**Русская версия: [README.md](README.md)**

## Features

- 📊 **Interactive Charts** - Visualization of PNL, cumulative PNL, distributions, and time series
- 🔍 **Data Filtering** - Select coins, strategies, and time periods for analysis
- 📅 **Time Filters** - Analyze data for specific periods with quick selection options
- 📈 **Strategy Analysis** - Comparative analysis of strategy performance
- 💰 **Metrics** - Detailed statistics for strategies and symbols
- 📋 **Data Tables** - View and export data to CSV
- ⚙️ **Settings Management** - Save and load filter configurations with automatic default settings loading. [Guide](docs/SETTINGS_GUIDE.md)

## Data Structure

The application works with JSON files containing backtest results in the following format:

```json
{
  "trades": [
    {
      "id": "...",
      "strategy_name": "CloudScalper2024",
      "symbol": "UNI-USDT",
      "exchange": "Bybit Spot",
      "type": "long",
      "entry_price": 6.37,
      "exit_price": 6.24,
      "qty": 778.2,
      "fee": 9.81,
      "size": 4957.18,
      "PNL": -109.21,
      "PNL_percentage": -2.20,
      "holding_period": 24300.0,
      "opened_at": 1749335400000.0,
      "closed_at": 1749359700000.0
    }
  ],
  "considering_timeframes": ["4h", "1m", "30m"]
}
```

## Installation

1. Clone the repository or download the files
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place JSON files with backtest results in the `input/batch-backtest-09-2025/` folder

## Running

```bash
streamlit run app.py
```

The application will be available at: http://localhost:8501

## Project Structure

```
AnalizeDashboard/
├── app.py                 # Main Streamlit application
├── data_loader.py         # Module for data loading and processing
├── visualizations.py      # Module for creating charts
├── requirements.txt       # Python dependencies
├── README.md             # Documentation (Russian)
├── README_EN.md          # Documentation (English)
├── example_settings.json  # Example settings file
├── docs/
│   └── SETTINGS_GUIDE.md  # Settings management guide
└── input/
    └── batch-backtest-09-2025/  # Folder with JSON files
        ├── *.json
        └── ...
```

## Usage

### Data Filtering

In the sidebar you can select:
- **Coins** - One or more cryptocurrencies for analysis
- **Strategies** - One or more trading strategies
- **Time Period** - Analysis of data for specific dates:
  - Select start and end dates
  - Quick buttons: last month, 3 months, 6 months, entire period
  - Automatic validation of range correctness

### Chart Types

1. **PNL by Trades** - Bar chart of profits and losses
2. **Cumulative PNL** - Line chart of accumulated profit
3. **PNL Timeline** - Time series with trade points
4. **PNL Distribution** - Boxplot by strategies

### Metrics

- **Total PNL** - Total profit/loss
- **Average PNL** - Average profit per trade
- **Win Rate** - Percentage of profitable trades
- **Trade Count** - Total number of trades
- **Holding Period** - Average position holding time
- **Profit Factor** - Ratio of gross profit to gross loss
- **Expected Value** - Expected profit per trade
- **Sharpe Ratio** - Ratio of average profit to standard deviation

### Data Export

In the "Data Tables" section you can:
- Select columns for display
- Configure number of rows
- Download data in CSV format

### Settings Management

In the "Settings" section you can:
- **Auto-load** - On first run, settings are automatically loaded from example_settings.json
- **Export Settings** - Save current filters and display settings to JSON file
- **Import Settings** - Load previously saved settings from file
- **Preset Settings** - Quickly apply popular combinations:
  - Top strategies (best 3 by PNL)
  - Top coins (best 5 by PNL)
  - Last month
  - Default settings (example_settings.json)
- **Reset Settings** - Clear all imported settings

**What is saved in settings:**
- Selected symbols (coins)
- Selected strategies
- Time period (start and end dates)
- Chart type for display
- Columns for table display
- Maximum number of rows in table

## Key Metrics

### Profit Factor
- **Formula**: Gross Profit / Gross Loss
- **Interpretation**: 
  - > 1.0 - strategy is profitable
  - > 1.5 - good strategy
  - > 2.0 - excellent strategy
- **Example**: 1.22 means that for every dollar of loss, there is $1.22 of profit

### Expected Value
- **Formula**: Average PNL per trade
- **Interpretation**:
  - > 0 - strategy is profitable in the long term
  - < 0 - strategy is unprofitable
- **Example**: 9.24 USDT means that on average each trade brings 9.24 USDT

### Sharpe Ratio
- **Formula**: Average Profit / Standard Deviation
- **Interpretation**:
  - > 1.0 - good return with acceptable risk
  - > 2.0 - excellent return with low risk
- **Example**: 0.0717 means relatively low return per unit of risk

## Technical Details

- **Streamlit** - Web framework for creating interactive applications
- **Plotly** - Library for creating interactive charts
- **Pandas** - Data processing and analysis
- **Caching** - Uses `@st.cache_data` for performance optimization

## Extending Functionality

The application is easily extensible:

1. **New Charts** - Add methods to the `BacktestVisualizer` class
2. **Additional Metrics** - Extend methods in `BacktestDataLoader`
3. **New Filters** - Add widgets to the sidebar
4. **Database Connection** - Replace JSON loading with database connection

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Plotly 5.17.0+
- Pandas 2.0.0+
- NumPy 1.24.0+

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

## Changelog

### v1.0.0
- Initial release
- Basic backtest visualization functionality
- Interactive filtering and analysis
- Settings management system
- CSV export capability
