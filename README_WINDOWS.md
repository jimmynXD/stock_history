# Stock History Windows Executables

Download historical stock data from Yahoo Finance.

## Files

- `stock_history.exe` - Saves data to file
- `stock_history_display.exe` - Displays data in terminal
- `stock_history_performance.exe` - Saves data to file (optimized, 2-5x faster)
- `stock_history_display_performance.exe` - Displays data in terminal (optimized, 2-5x faster)

## Usage

```cmd
stock_history.exe <symbol|file> [start_date] [end_date] [output_path]
stock_history_display.exe <symbol|file> [start_date] [end_date]
```

## Parameters

| Parameter      | Required | Description                                                                | Example                         |
| -------------- | -------- | -------------------------------------------------------------------------- | ------------------------------- |
| `symbol\|file` | Yes      | Stock symbol or file with symbols (one per line)                           | `AAPL` or `symbols.txt`         |
| `start_date`   | No       | Start date (YYYY-MM-DD). Omit for latest data                              | `2024-01-01`                    |
| `end_date`     | No       | End date (YYYY-MM-DD). Omit for single date                                | `2024-12-31`                    |
| `output_path`  | No       | Directory or full file path (.txt, .TXT, .Txt). Default: current directory | `.\data` or `.\data\stocks.txt` |

### Flag Usage Examples

**1. Symbol only (latest data)**

```cmd
stock_history.exe AAPL
```

Downloads most recent trading day data for Apple.

**2. Symbol + start_date (single date)**

```cmd
stock_history.exe AAPL 2024-01-15
```

Downloads data for January 15, 2024 only.

**3. Symbol + start_date + end_date (date range)**

```cmd
stock_history.exe AAPL 2024-01-01 2024-12-31
```

Downloads all trading days from January 1 to December 31, 2024.

**4. Symbol + start_date + end_date + output_path (custom location)**

```cmd
stock_history.exe AAPL 2024-01-01 2024-12-31 C:\StockData
```

Downloads date range and saves to `C:\StockData` directory with auto-generated filename.

**5. Symbol + dates + custom filename**

```cmd
stock_history.exe AAPL 2024-01-01 2024-12-31 C:\StockData\apple_2024.txt
```

Downloads date range and saves to specific file path and name.

**5a. Symbol + start_date + skip end_date + custom filename**

```cmd
stock_history.exe AAPL 2024-01-01 "" C:\StockData\apple_jan.txt
```

Downloads single date and saves to specific file path (use empty string "" to skip end_date parameter).

**6. File (multiple symbols)**

```cmd
stock_history.exe symbols.txt
```

Downloads latest data for all symbols in the file.

**7. File + dates**

```cmd
stock_history.exe symbols.txt 2024-01-01 2024-12-31
```

Downloads date range for all symbols in the file.

**8. Display version (no file saved)**

```cmd
stock_history_display.exe AAPL 2024-01-01 2024-01-31
```

Shows data in terminal instead of saving to file.

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

## Data Validation Flags

**OHLC Anomaly (`;! `):**
Indicates Open or Close price is outside High/Low range:

```
;! 2024-01-01,AAPL,155.00,152.30,149.80,151.50,45678900
```

**Date Mismatch (`;* `):**
When querying latest data for multiple stocks, indicates the stock's date differs from the majority:

```
;* 2024-01-01,AAPL,150.25,152.30,149.80,151.50,45678900
```

**Combined Flags (`;*! `):**
Both date mismatch and OHLC anomaly:

```
;*! 2024-01-01,AAPL,155.00,152.30,149.80,148.00,45678900
```

## Error Messages

Invalid symbols and stocks with no data are written to the output file with special prefixes:

- `; INVALID_SYMBOL "SYMBOL"` - Invalid stock symbol (not found)
- `; INVALID_SYMBOL "SYMBOL","CUSTOM_HEADER"` - Invalid symbol with custom header
- `; NO_DATA "SYMBOL"` - Valid symbol but no trading data for requested date
- `; NO_DATA "SYMBOL","CUSTOM_HEADER"` - No data with custom header

## File Encoding

- Output files are encoded in Big5 (Traditional Chinese) with error replacement for unsupported characters
- Input files support UTF-8 and Big5 encoding

## Output Filenames

Files are saved with different naming conventions based on query type:

- **Latest data (no date specified):** `YYYYMMDD.txt` (e.g., `20260303.txt`)
  - Uses the majority date across all fetched stocks
- **Date range:** `YYYYMMDD-YYYYMMDD.txt` (e.g., `20260226-20260227.txt`)
- **Single date:** `YYYYMMDD.txt` (e.g., `20260226.txt`)
- **Duplicates:** Add `_n` suffix before extension (e.g., `20260227_1.txt`)

## Examples

```cmd
REM Latest data (creates YYYYMMDD.txt)
stock_history.exe AAPL

REM Latest data for multiple stocks (creates YYYYMMDD.txt with majority date)
stock_history.exe symbols.txt

REM Single date (creates YYYYMMDD.txt)
stock_history.exe AAPL 2024-01-15

REM Date range (creates YYYYMMDD-YYYYMMDD.txt)
stock_history.exe AAPL 2024-01-01 2024-12-31

REM Multiple symbols with custom directory
stock_history.exe symbols.txt 2024-01-01 2024-12-31 .\data

REM Custom file path and name
stock_history.exe AAPL 2024-01-01 2024-12-31 .\reports\apple_jan.TXT

REM Skip end_date parameter with empty string to specify output path
stock_history.exe AAPL 2024-01-01 "" .\data\apple_jan.txt

REM Display in terminal
stock_history_display.exe AAPL 2024-01-01 2024-01-31
```

## Input File Formats

**Simple format (symbols.txt):**

```
AAPL
MSFT
GOOG
```

**Advanced format with custom headers:**

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

**Advanced format with volume multipliers:**

```
"^GSPC","CUSTOM_HEADER"
"^DJI","CUSTOM_HEADER"
```

- Format: `"SYMBOL","CUSTOM_HEADER"[,"VOLUME_MULTIPLIER"]`
- Volume multiplier (optional 3rd parameter) scales the volume value
- Examples: "10", "0.001", "100", "0.5"
- If not specified, defaults to 1.0 (no change)
- Applied to both single-date and date-range queries
- Result is truncated to integer

## Error Messages

- `SYMBOL not found` - Invalid stock symbol
- `SYMBOL no data available for DATE` - Valid symbol but no trading data for that date (holiday, weekend, or trading halt)
