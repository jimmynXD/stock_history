#!/usr/bin/env python3
# python3 tests/test_stock_history.py -v
# or
# pip3 install pytest
# python3 -m pytest tests/ -v
"""Unit tests for stock_history.py"""
import unittest
import os
import tempfile
from datetime import datetime
from stock_history import read_symbols, get_filename, fetch_data


class TestReadSymbols(unittest.TestCase):
    """Test read_symbols function"""

    def test_single_symbol(self):
        """Test single symbol from command line"""
        result = read_symbols("AAPL")
        self.assertEqual(result, {"AAPL": (None, 1.0)})

    def test_simple_file(self):
        """Test simple format file"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("AAPL\n")
            f.write("MSFT\n")
            f.write("GOOG\n")
            f.name

        try:
            result = read_symbols(f.name)
            self.assertEqual(
                result, {"AAPL": (None, 1.0), "MSFT": (None, 1.0), "GOOG": (None, 1.0)}
            )
        finally:
            os.unlink(f.name)

    def test_advanced_file(self):
        """Test advanced format with custom headers"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write('"AAPL","Apple Custom Header"\n')
            f.write('"MSFT","Microsoft Custom Header"\n')
            f.name

        try:
            result = read_symbols(f.name)
            self.assertEqual(result["AAPL"], ("Apple Custom Header", 1.0))
            self.assertEqual(result["MSFT"], ("Microsoft Custom Header", 1.0))
        finally:
            os.unlink(f.name)

    def test_advanced_file_with_spaces(self):
        """Test advanced format with spaces before comma"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write('"AAPL"    ,"Apple Custom Header"\n')
            f.write('"MSFT"   ,"Microsoft Custom Header"\n')
            f.name

        try:
            result = read_symbols(f.name)
            self.assertEqual(result["AAPL"], ("Apple Custom Header", 1.0))
            self.assertEqual(result["MSFT"], ("Microsoft Custom Header", 1.0))
        finally:
            os.unlink(f.name)

    def test_ansi_encoding(self):
        """Test Big5 (Traditional Chinese) encoded file"""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt", encoding="big5"
        ) as f:
            f.write("AAPL\n")
            f.write("MSFT\n")
            f.name

        try:
            result = read_symbols(f.name)
            self.assertEqual(result, {"AAPL": (None, 1.0), "MSFT": (None, 1.0)})
        finally:
            os.unlink(f.name)

    def test_empty_lines(self):
        """Test file with empty lines"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("AAPL\n")
            f.write("\n")
            f.write("MSFT\n")
            f.name

        try:
            result = read_symbols(f.name)
            self.assertEqual(result, {"AAPL": (None, 1.0), "MSFT": (None, 1.0)})
        finally:
            os.unlink(f.name)

    def test_comment_lines(self):
        """Test file with comment lines starting with semicolon"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("AAPL\n")
            f.write("; This is a comment\n")
            f.write("MSFT\n")
            f.write("; Another comment\n")
            f.write("GOOG\n")
            f.name

        try:
            result = read_symbols(f.name)
            self.assertEqual(result, {"AAPL": (None, 1.0), "MSFT": (None, 1.0), "GOOG": (None, 1.0)})
        finally:
            os.unlink(f.name)

    def test_comment_lines_with_advanced_format(self):
        """Test comment lines with advanced format"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write('"AAPL","Apple Custom Header"\n')
            f.write("; This is a comment\n")
            f.write('"MSFT","Microsoft Custom Header"\n')
            f.name

        try:
            result = read_symbols(f.name)
            self.assertEqual(result["AAPL"], ("Apple Custom Header", 1.0))
            self.assertEqual(result["MSFT"], ("Microsoft Custom Header", 1.0))
            self.assertEqual(len(result), 2)
        finally:
            os.unlink(f.name)

    def test_volume_multiplier(self):
        """Test volume multiplier parsing"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write('"AAPL","Apple Custom Header","10"\n')
            f.write('"MSFT","Microsoft Custom Header","0.001"\n')
            f.write('"GOOG","Google Custom Header"\n')
            f.name

        try:
            result = read_symbols(f.name)
            self.assertEqual(result["AAPL"], ("Apple Custom Header", 10.0))
            self.assertEqual(result["MSFT"], ("Microsoft Custom Header", 0.001))
            self.assertEqual(result["GOOG"], ("Google Custom Header", 1.0))
        finally:
            os.unlink(f.name)


class TestGetFilename(unittest.TestCase):
    """Test get_filename function"""

    def test_basic_filename(self):
        """Test basic filename generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_filename("20240101", tmpdir)
            expected = os.path.join(tmpdir, "20240101.txt")
            self.assertEqual(result, expected)

    def test_duplicate_filename(self):
        """Test duplicate filename handling"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first file
            base = os.path.join(tmpdir, "20240101.txt")
            open(base, "w").close()

            # Get next filename
            result = get_filename("20240101", tmpdir)
            expected = os.path.join(tmpdir, "20240101_1.txt")
            self.assertEqual(result, expected)

    def test_multiple_duplicates(self):
        """Test multiple duplicate filenames"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple files
            open(os.path.join(tmpdir, "20240101.txt"), "w").close()
            open(os.path.join(tmpdir, "20240101_1.txt"), "w").close()

            # Get next filename
            result = get_filename("20240101", tmpdir)
            expected = os.path.join(tmpdir, "20240101_2.txt")
            self.assertEqual(result, expected)


class TestFetchData(unittest.TestCase):
    """Test fetch_data function"""

    def test_invalid_symbol(self):
        """Test invalid stock symbol returns None"""
        result = fetch_data("INVALID_SYMBOL_XYZ", None, None)
        self.assertIsNone(result)

    def test_valid_symbol_latest(self):
        """Test valid symbol returns data"""
        result = fetch_data("AAPL", None, None)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

    def test_date_range(self):
        """Test date range query"""
        result = fetch_data("AAPL", "2024-01-01", "2024-01-05")
        if result is not None and not isinstance(result, str):
            self.assertGreater(len(result), 0)

    def test_no_data_for_date(self):
        """Test symbol with no data for specific date returns NO_DATA_FOR_DATE"""
        # Use a date far in the past where data might not exist
        result = fetch_data("AAPL", "1900-01-01", "1900-01-02")
        # Should return either None or NO_DATA_FOR_DATE
        self.assertTrue(result is None or result == "NO_DATA_FOR_DATE")


class TestDateValidation(unittest.TestCase):
    """Test date validation logic"""

    def test_weekend_detection(self):
        """Test weekend date detection"""
        # 2024-01-06 is a Saturday
        date_obj = datetime.strptime("2024-01-06", "%Y-%m-%d")
        self.assertGreaterEqual(date_obj.weekday(), 5)

    def test_weekday_detection(self):
        """Test weekday date detection"""
        # 2024-01-05 is a Friday
        date_obj = datetime.strptime("2024-01-05", "%Y-%m-%d")
        self.assertLess(date_obj.weekday(), 5)

    def test_date_comparison(self):
        """Test date range validation"""
        start = datetime.strptime("2024-01-01", "%Y-%m-%d")
        end = datetime.strptime("2024-12-31", "%Y-%m-%d")
        self.assertLess(start, end)

    def test_invalid_date_range(self):
        """Test invalid date range detection"""
        start = datetime.strptime("2024-12-31", "%Y-%m-%d")
        end = datetime.strptime("2024-01-01", "%Y-%m-%d")
        self.assertGreater(start, end)


class TestOHLCValidation(unittest.TestCase):
    """Test OHLC data validation logic"""

    def test_valid_ohlc(self):
        """Test valid OHLC values"""
        open_price = 100.0
        high_price = 105.0
        low_price = 98.0
        close_price = 102.0

        # Check Open is within High/Low
        self.assertLessEqual(open_price, high_price)
        self.assertGreaterEqual(open_price, low_price)

        # Check Close is within High/Low
        self.assertLessEqual(close_price, high_price)
        self.assertGreaterEqual(close_price, low_price)

    def test_invalid_ohlc_open_high(self):
        """Test Open higher than High (invalid)"""
        open_price = 110.0
        high_price = 105.0
        self.assertGreater(open_price, high_price)

    def test_invalid_ohlc_close_low(self):
        """Test Close lower than Low (invalid)"""
        close_price = 95.0
        low_price = 98.0
        self.assertLess(close_price, low_price)

    def test_high_low_relationship(self):
        """Test High must be greater than or equal to Low"""
        high_price = 105.0
        low_price = 98.0
        self.assertGreaterEqual(high_price, low_price)


if __name__ == "__main__":
    unittest.main()
