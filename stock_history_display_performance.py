#!/usr/bin/env python3
import sys
import os
import time
from datetime import datetime, timedelta
import yfinance as yf


# Suppress yfinance verbose error messages
class SuppressStderr:
    """Context manager to suppress stderr output."""

    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._original_stderr


def read_symbols(input_arg):
    """Read stock symbols from file or return single symbol."""
    if os.path.isfile(input_arg):
        symbols_dict = {}
        # Try UTF-8 first, fallback to Big5 encoding for Traditional Chinese Windows files
        try:
            with open(input_arg, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Check if line contains quoted values (StockList.txt format)
                    if line.startswith('"'):
                        # Find first closing quote
                        first_quote_end = line.find('"', 1)
                        if first_quote_end > 0:
                            symbol = line[1:first_quote_end]
                            # Look for second quoted section after comma
                            comma_pos = line.find(",", first_quote_end)
                            if comma_pos > 0:
                                second_quote_start = line.find('"', comma_pos)
                                if second_quote_start > 0:
                                    second_quote_end = line.find(
                                        '"', second_quote_start + 1
                                    )
                                    if second_quote_end > 0:
                                        header = line[
                                            second_quote_start + 1 : second_quote_end
                                        ]
                                        # Look for third parameter (volume multiplier)
                                        third_comma_pos = line.find(
                                            ",", second_quote_end
                                        )
                                        multiplier = 1.0
                                        if third_comma_pos > 0:
                                            third_param = (
                                                line[third_comma_pos + 1 :]
                                                .strip()
                                                .strip('"')
                                            )
                                            try:
                                                multiplier = float(third_param)
                                            except ValueError:
                                                multiplier = 1.0
                                        symbols_dict[symbol] = (header, multiplier)
                                    else:
                                        symbols_dict[symbol] = (None, 1.0)
                                else:
                                    symbols_dict[symbol] = (None, 1.0)
                            else:
                                # Single quoted symbol
                                symbols_dict[symbol] = (None, 1.0)
                        else:
                            # Malformed line, skip
                            continue
                    else:
                        # Plain text format (symbols.txt)
                        symbols_dict[line] = (None, 1.0)
        except UnicodeDecodeError:
            # Fallback to Big5 encoding for Traditional Chinese Windows files
            with open(input_arg, "r", encoding="big5") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('"'):
                        first_quote_end = line.find('"', 1)
                        if first_quote_end > 0:
                            symbol = line[1:first_quote_end]
                            comma_pos = line.find(",", first_quote_end)
                            if comma_pos > 0:
                                second_quote_start = line.find('"', comma_pos)
                                if second_quote_start > 0:
                                    second_quote_end = line.find(
                                        '"', second_quote_start + 1
                                    )
                                    if second_quote_end > 0:
                                        header = line[
                                            second_quote_start + 1 : second_quote_end
                                        ]
                                        third_comma_pos = line.find(
                                            ",", second_quote_end
                                        )
                                        multiplier = 1.0
                                        if third_comma_pos > 0:
                                            third_param = (
                                                line[third_comma_pos + 1 :]
                                                .strip()
                                                .strip('"')
                                            )
                                            try:
                                                multiplier = float(third_param)
                                            except ValueError:
                                                multiplier = 1.0
                                        symbols_dict[symbol] = (header, multiplier)
                                    else:
                                        symbols_dict[symbol] = (None, 1.0)
                                else:
                                    symbols_dict[symbol] = (None, 1.0)
                            else:
                                symbols_dict[symbol] = (None, 1.0)
                        else:
                            continue
                    else:
                        symbols_dict[line] = (None, 1.0)
        return symbols_dict
    else:
        return {input_arg: (None, 1.0)}


def fetch_data(symbol, start_date=None, end_date=None):
    """Fetch stock data from Yahoo Finance."""
    with SuppressStderr():
        try:
            ticker = yf.Ticker(symbol)

            if start_date and end_date:
                # Date range query
                data = ticker.history(start=start_date, end=end_date)
            elif start_date:
                # Single date query
                data = ticker.history(start=start_date, end=start_date)
            else:
                # Latest data query
                data = ticker.history(period="5d")

            if data.empty:
                return "NO_DATA_FOR_DATE"

            return data

        except Exception:
            return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stock_history_display.py <symbol_or_file> [start_date] [end_date]")
        sys.exit(1)

    input_arg = sys.argv[1]
    start_date = sys.argv[2] if len(sys.argv) > 2 else None
    end_date = sys.argv[3] if len(sys.argv) > 3 else None

    print("Connection established\n")

    symbols = read_symbols(input_arg)
    print(f"Processing {len(symbols)} stock symbol(s)\n")

    # Validate date range
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if start_dt > end_dt:
                print("Error: Invalid date range - start date cannot be after end date")
                sys.exit(1)
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

    # Check if single date is a weekend
    if start_date and not end_date:
        try:
            date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            if date_obj.weekday() >= 5:  # 5=Saturday, 6=Sunday
                print(f"Error: {start_date} is a weekend - stock market is closed")
                sys.exit(1)
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

    # Get local date and time when processing starts
    process_start_time = time.time()
    process_time = (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + time.strftime("%Z")
    )

    stock_data = {}
    no_data_stocks = {}
    invalid_stocks = {}

    # Fetch all data using yf.download with threading
    symbol_list = list(symbols.keys())
    
    fetch_start_time = time.time()
    with SuppressStderr():
        if start_date and end_date:
            # Add one day to end_date since yfinance end parameter is exclusive
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt_inclusive = end_dt + timedelta(days=1)
            end_date_str = end_dt_inclusive.strftime("%Y-%m-%d")
            all_data = yf.download(symbol_list, start=start_date, end=end_date_str, threads=True, progress=False)
        elif start_date:
            # For single date, use start + end (start+1day) since start+period doesn't work well with many symbols
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=1)
            end_date_str = end_dt.strftime("%Y-%m-%d")
            all_data = yf.download(symbol_list, start=start_date, end=end_date_str, threads=True, progress=False)
        else:
            all_data = yf.download(symbol_list, period="1d", threads=True, progress=False)
    fetch_elapsed = time.time() - fetch_start_time

    # Process results
    failed_symbols = []
    for symbol, (custom_header, multiplier) in symbols.items():
        try:
            if len(symbol_list) == 1:
                # Single symbol still has MultiIndex columns with yf.download
                data = all_data.xs(symbol, level=1, axis=1) if hasattr(all_data.columns, 'levels') else all_data[['Open', 'High', 'Low', 'Close', 'Volume']]
            else:
                data = all_data.xs(symbol, level=1, axis=1) if len(all_data.columns.levels) > 1 else all_data[symbol]
            
            # Drop rows with all NaN values
            data = data.dropna(how='all')
            
            if data.empty or data.isna().all().all():
                # Mark for individual retry
                failed_symbols.append((symbol, custom_header, multiplier))
            else:
                stock_data[symbol] = (data, custom_header, multiplier)
        except (KeyError, AttributeError):
            invalid_stocks[symbol] = custom_header

    # Retry failed symbols individually
    if failed_symbols:
        for symbol, custom_header, multiplier in failed_symbols:
            with SuppressStderr():
                try:
                    ticker = yf.Ticker(symbol)
                    if start_date and end_date:
                        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                        end_dt_inclusive = end_dt + timedelta(days=1)
                        end_date_str = end_dt_inclusive.strftime("%Y-%m-%d")
                        data = ticker.history(start=start_date, end=end_date_str)
                    elif start_date:
                        data = ticker.history(start=start_date, period="1d")
                    else:
                        data = ticker.history(period="1d")
                    
                    if data.empty:
                        no_data_stocks[symbol] = start_date if start_date else None
                    else:
                        # Select only OHLCV columns
                        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
                        stock_data[symbol] = (data, custom_header, multiplier)
                except Exception:
                    invalid_stocks[symbol] = custom_header

    # Calculate total elapsed time
    total_elapsed = time.time() - process_start_time
    minutes = int(total_elapsed // 60)
    seconds = total_elapsed % 60
    
    # Determine query description
    if start_date and end_date:
        query_desc = f"{input_arg} {start_date} {end_date}"
    elif start_date:
        query_desc = f"{input_arg} {start_date}"
    else:
        query_desc = f"{input_arg} latest_data"
    
    # Print timing report at top
    print(f"; Processed: {process_time}")
    print(f"; Total time: {minutes}m{seconds:.3f}s")
    print(f"; Queried: {query_desc}\n")

    # Find latest date for latest data queries (no start_date)
    latest_date = None
    if not start_date and stock_data:
        for symbol, (data, _, _) in stock_data.items():
            if len(data) == 1:
                current_date = data.index[0]
                if latest_date is None or current_date > latest_date:
                    latest_date = current_date
        if latest_date:
            latest_date = latest_date.strftime("%Y-%m-%d")

    # Display data in original StockList.txt order
    successful = 0
    for symbol, (custom_header, multiplier) in symbols.items():
        if symbol not in stock_data:
            continue
        
        data = stock_data[symbol][0]
        if len(data) == 1:
            row = data.iloc[0]
            date_fmt = data.index[0].strftime("%Y-%m-%d")

            date_flag = latest_date and date_fmt != latest_date
            ohlc_flag = (
                row["Open"] > row["High"]
                or row["Open"] < row["Low"]
                or row["Close"] > row["High"]
                or row["Close"] < row["Low"]
            )

            flag = ""
            if date_flag and ohlc_flag:
                flag = ";*! "
            elif date_flag:
                flag = ";* "
            elif ohlc_flag:
                flag = ";! "

            o = f"{row['Open']:.3f}".rstrip("0").rstrip(".")
            h = f"{row['High']:.3f}".rstrip("0").rstrip(".")
            l = f"{row['Low']:.3f}".rstrip("0").rstrip(".")
            c = f"{row['Close']:.3f}".rstrip("0").rstrip(".")
            try:
                volume = int(row["Volume"] * multiplier)
            except (ValueError, TypeError):
                volume = 0
            print(f"{flag}{date_fmt},{symbol},{o},{h},{l},{c},{volume}")
        else:
            if custom_header:
                print(custom_header)
            for date, row in data.iterrows():
                date_fmt = date.strftime("%Y-%m-%d")
                flag = (
                    "; "
                    if (
                        row["Open"] > row["High"]
                        or row["Open"] < row["Low"]
                        or row["Close"] > row["High"]
                        or row["Close"] < row["Low"]
                    )
                    else ""
                )
                o = f"{row['Open']:.3f}".rstrip("0").rstrip(".")
                h = f"{row['High']:.3f}".rstrip("0").rstrip(".")
                l = f"{row['Low']:.3f}".rstrip("0").rstrip(".")
                c = f"{row['Close']:.3f}".rstrip("0").rstrip(".")
                try:
                    volume = int(row["Volume"] * multiplier)
                except (ValueError, TypeError):
                    volume = 0
                if custom_header:
                    print(f"{flag}{date_fmt},{o},{h},{l},{c},{volume}")
                else:
                    print(f"{flag}{date_fmt},{symbol},{o},{h},{l},{c},{volume}")

        successful += 1

    # Display stocks with no data available
    for symbol in no_data_stocks.keys():
        custom_header, _ = symbols.get(symbol, (None, 1.0))
        if custom_header:
            print(f'; NO_DATA "{symbol}","{custom_header}"')
        else:
            print(f'; NO_DATA "{symbol}"')

    # Display invalid stock symbols
    for symbol, custom_header in invalid_stocks.items():
        if custom_header:
            print(f'; INVALID_SYMBOL "{symbol}","{custom_header}"')
        else:
            print(f'; INVALID_SYMBOL "{symbol}"')
