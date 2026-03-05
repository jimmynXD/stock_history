# Stock OHLCV History Downloader

Download historical OHLCV (Open, High, Low, Close, Volume) data for stocks using Yahoo Finance.

## Requirements

- Python 3.8 (this version will work for windows 7)
- yfinance library

## Installation

```bash
pip install -r requirements.txt
```

## Scripts

- **stock_history.py** - Save data to file
- **stock_history_display.py** - Display data to console (no file output)
- **stock_history_performance.py** - Save data to file (optimized, 2-5x faster)
- **stock_history_display_performance.py** - Display data to console (optimized, 2-5x faster)

## Usage

### Mac/Linux

```bash
# Single stock symbol - latest data
python3 stock_history.py AAPL

# Multiple stocks from file
python3 stock_history.py symbols.txt

# Single date
python3 stock_history.py AAPL 2024-01-01

# Date range
python3 stock_history.py AAPL 2024-01-01 2024-12-31

# Specify output directory
python3 stock_history.py AAPL 2024-01-01 2024-12-31 ./data

# Specify custom output file path and name
python3 stock_history.py AAPL 2024-01-01 2024-12-31 ./data/my_stocks.txt

# Skip end_date parameter with empty string to specify output path
python3 stock_history.py AAPL 2024-01-01 "" ./data/my_stocks.txt

# Display to console (no file)
python3 stock_history_display.py AAPL 2024-01-01
```

### Windows

```cmd
# Build self executable compilers
pyinstaller --onefile --name stock_history_win7 stock_history.py
pyinstaller --onefile --name stock_history_display_win7 stock_history_display.py
pyinstaller --onefile --name stock_history_performance stock_history_performance.py
pyinstaller --onefile --name stock_history_display_performance stock_history_display_performance.py

stock_history.exe AAPL
```

## Input Format

**Single symbol:** Pass the stock symbol directly (e.g., `AAPL`)

**Multiple symbols:** Create a text file with one symbol per line

Simple format (symbols.txt):

```
AAPL
MSFT
GOOG
```

Advanced format with custom headers:

```
"AAPL","CUSTOM_HEADER"
"MSFT","CUSTOM_HEADER"
```

**Comments:** Lines starting with `;` are treated as comments and skipped

```
AAPL
; This is a comment
MSFT
```

- Format: `"SYMBOL","CUSTOM_HEADER"[,"VOLUME_MULTIPLIER"]` (flexible whitespace before comma)
- Custom headers are used for date range queries only
- Single date queries use standard format regardless of custom header
- Volume multiplier (optional 3rd parameter) scales the volume value (e.g., "10", "0.001", "100")
  - If not specified, defaults to 1.0 (no change)
  - Applied to both single-date and date-range queries
  - Result is truncated to integer
- Supports both UTF-8 and Big5 encoding

**Date formats:**

- No date = latest available data
- Single date = data for that day (YYYY-MM-DD)
- Two dates = date range (start and end, both inclusive)
- Dates must be weekdays (not Saturday/Sunday)

**Output directory:** Optional 4th parameter to specify where to save the file (default: current directory)

- Can be a directory path (e.g., `./data`) - auto-generates filename
- Can be a full file path (e.g., `./data/my_stocks.txt`) - uses exact filename

## Output Format

**Single date:**

```
2024-01-01,AAPL,150.25,152.30,149.80,151.50,45678900
2024-01-01,MSFT,380.50,382.75,379.20,381.90,23456789
```

**Multiple dates (with custom header):**

```
CUSTOM_HEADER
2024-01-01,150.25,152.30,149.80,151.50,45678900
2024-01-02,151.60,153.20,151.00,152.80,46789012
CUSTOM_HEADER
2024-01-01,380.50,382.75,379.20,381.90,23456789
2024-01-02,382.00,384.50,381.50,383.75,24567890
```

**Multiple dates (without custom header):**

```
2024-01-01,AAPL,150.25,152.30,149.80,151.50,45678900
2024-01-02,AAPL,151.60,153.20,151.00,152.80,46789012
2024-01-01,MSFT,380.50,382.75,379.20,381.90,23456789
2024-01-02,MSFT,382.00,384.50,381.50,383.75,24567890
```

**Data validation flag:**
Lines prefixed with `;! ` indicate OHLC anomalies (Open or Close outside High/Low range):

```
;! 2024-01-01,AAPL,155.00,152.30,149.80,151.50,45678900
```

**Date mismatch flag (latest data only):**
When querying latest data for multiple stocks, lines prefixed with `;* ` indicate the stock's date differs from the majority date:

```
;* 2024-01-01,AAPL,150.25,152.30,149.80,151.50,45678900
```

**Combined flags:**
Both issues present are indicated with `;*! `:

```
;*! 2024-01-01,AAPL,155.00,152.30,149.80,148.00,45678900
```

**Notes:**

- Dates in multiple date queries are displayed in ascending order (earliest first)
- OHLC values are rounded to 2 decimal places
- Volume is displayed as an integer

## Output Files

Files are saved with different naming conventions based on query type:

- **Latest data (no date specified):** `YYYYMMDD.txt` (e.g., `20260303.txt`)
  - Uses the majority date across all fetched stocks
- **Date range:** `YYYYMMDD-YYYYMMDD.txt` (e.g., `20260226-20260227.txt`)
- **Single date:** `YYYYMMDD.txt` (e.g., `20260226.txt`)
- **Duplicates:** Add `_n` suffix before extension (e.g., `20260227_1.txt`)
- **File encoding:** Big5 (Traditional Chinese) with error replacement for unsupported characters

## Error Messages

Invalid symbols and stocks with no data are written to the output file with special prefixes:

- `; INVALID_SYMBOL "SYMBOL"` - Invalid stock symbol (not found)
- `; INVALID_SYMBOL "SYMBOL","CUSTOM_HEADER"` - Invalid symbol with custom header
- `; NO_DATA "SYMBOL"` - Valid symbol but no trading data for requested date
- `; NO_DATA "SYMBOL","CUSTOM_HEADER"` - No data with custom header

## Testing

Run tests with:

```bash
cd /Users/jamnxpbj/repos/pyth
PYTHONPATH=. python3 tests/test_stock_history.py -v
```

See `tests/README.md` for detailed test documentation.

## Examples

```bash
# Get latest data for Apple (creates YYYYMMDD.txt)
python3 stock_history.py AAPL

# Get latest data for multiple stocks (creates YYYYMMDD.txt with majority date)
python3 stock_history.py StockList.txt

# Get data for specific date (creates YYYYMMDD.txt)
python3 stock_history.py AAPL 2024-01-15

# Get date range for multiple stocks (creates YYYYMMDD-YYYYMMDD.txt)
python3 stock_history.py StockList.txt 2024-01-01 2024-01-31

# Save to custom directory
python3 stock_history.py AAPL 2024-01-01 2024-01-31 ./data

# Save to custom file path and name
python3 stock_history.py AAPL 2024-01-01 2024-01-31 ./reports/apple_jan2024.txt

# Skip end_date parameter with empty string to specify output path
python3 stock_history.py AAPL 2024-01-01 "" ./data/my_stocks.txt

# Display to console without saving
python3 stock_history_display.py AAPL 2024-01-01 2024-01-31
```
