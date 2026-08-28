"""
CashPilot AI – Configuration
=============================
Central configuration for the financial data generator.
All constants used across the project are defined here.
"""

from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Time horizon
# ---------------------------------------------------------------------------
# We generate 365 days of historical data for the PREVIOUS YEAR.
# Date range: 2024-08-28 to 2025-08-27
NUM_DAYS = 365
END_DATE = datetime(2025, 8, 27)
START_DATE = END_DATE - timedelta(days=NUM_DAYS - 1)  # inclusive range → 365 days

# ---------------------------------------------------------------------------
# Company financials (INR)
# ---------------------------------------------------------------------------
CURRENCY = "INR"
STARTING_CASH = 500_000_000      # ₹50 Crore – Tata Motors divisional working capital
MINIMUM_CASH_RESERVE = 50_000_000  # ₹5 Crore – policy floor

# ---------------------------------------------------------------------------
# Entity counts
# ---------------------------------------------------------------------------
NUM_CUSTOMERS_MIN = 20
NUM_CUSTOMERS_MAX = 30
NUM_SUPPLIERS_MIN = 10
NUM_SUPPLIERS_MAX = 15
NUM_INVOICES_MIN = 300
NUM_INVOICES_MAX = 600
NUM_OBLIGATIONS_MIN = 150
NUM_OBLIGATIONS_MAX = 300
NUM_FINANCING_OPTIONS = 5
NUM_EVENTS_MIN = 100
NUM_EVENTS_MAX = 200
NUM_SCENARIOS_MIN = 10
NUM_SCENARIOS_MAX = 20
