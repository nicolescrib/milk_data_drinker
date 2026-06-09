import os
import pytest
import pandas as pd
from milk_data_drinker.timeless.normalizer import read_file


@pytest.fixture
def html_file(tmp_path):
    content = """<table>
        <tr><th>Deposit</th><th>Donor</th><th>Volume</th></tr>
        <tr><td>DEP001</td><td>DON001: Jane Smith</td><td>150.5</td></tr>
        <tr><td>DEP002</td><td>DON002: Mary Jones</td><td>200.0</td></tr>
    </table>"""
    p = tmp_path / "report.xls"
    p.write_text(content)
    return str(p)


@pytest.fixture
def html_file_integer_headers(tmp_path):
    # Timeless sometimes exports with no <th> — pandas assigns integer column indices
    content = """<table>
        <tr><td>Deposit</td><td>Donor</td><td>Volume</td></tr>
        <tr><td>DEP001</td><td>DON001: Jane Smith</td><td>150.5</td></tr>
    </table>"""
    p = tmp_path / "report_no_headers.xls"
    p.write_text(content)
    return str(p)


@pytest.fixture
def csv_file(tmp_path):
    content = "Deposit,Donor,Volume\nDEP001,DON001: Jane Smith,150.5\nDEP002,DON002: Mary Jones,200.0\n"
    p = tmp_path / "report.csv"
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_reads_html_file(html_file):
    df = read_file(html_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


def test_html_columns_cleaned(html_file):
    df = read_file(html_file)
    assert "Deposit" in df.columns or "deposit" in df.columns.str.lower().tolist()


def test_reads_html_with_integer_headers(html_file_integer_headers):
    df = read_file(html_file_integer_headers)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    # first row should have been promoted to headers
    assert "Deposit" in df.columns


def test_reads_csv_file(csv_file):
    df = read_file(csv_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "Deposit" in df.columns


def test_raises_on_missing_file():
    with pytest.raises(Exception):
        read_file("/nonexistent/path/report.xls")


def test_column_names_cleaned(tmp_path):
    content = "<table><tr><th>Date Received</th><th>Expiry Date</th></tr><tr><td>2024-01-01</td><td>2024-06-01</td></tr></table>"
    p = tmp_path / "report.xls"
    p.write_text(content)
    df = read_file(str(p))
    assert "Date_Received" in df.columns
    assert "Expiry_Date" in df.columns
