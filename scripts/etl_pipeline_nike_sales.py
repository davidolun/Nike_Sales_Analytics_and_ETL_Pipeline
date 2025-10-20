
#!/usr/bin/env python
# coding: utf-8

"""
Nike Sales Data ETL Pipeline - Production Ready Version

This script performs an end-to-end ETL (Extract, Transform, Load) process
on the synthetic Nike sales dataset with comprehensive logging, error handling,
data validation, and quality metrics.

Author: [Your Name]
Date: 2025-10-10
Version: 2.0
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from pathlib import Path



# Configuration

class ETLConfig:
    """ETL Pipeline Configuration"""
    # Auto-detect project root (works from anywhere!)
    SCRIPT_DIR = Path(__file__).parent
    PROJECT_ROOT = SCRIPT_DIR.parent
    DATA_DIR = PROJECT_ROOT / "data"
    
    RAW_CSV = str(DATA_DIR / "Nike_Sales_Uncleaned.csv")
    CLEANED_CSV = str(DATA_DIR / "Nike_Sales_Cleaned.csv")
    LOG_FILE = str(SCRIPT_DIR / "etl_pipeline.log")
    
    # Data validation rules
    VALID_REGIONS = ['Bangalore', 'Hyderabad', 'Mumbai', 'Pune', 'Delhi', 'Kolkata']
    OUTLIER_THRESHOLD = 1.5
    MIN_UNITS_SOLD = 1
    MIN_MRP = 0



# Logging Setup

def setup_logging():
    """Configure logging for the ETL pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(ETLConfig.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    logging.info("="*70)
    logging.info("Nike Sales ETL Pipeline Started")
    logging.info("="*70)


# --------------------------
# Extraction
# --------------------------
def extract_data(filepath):
    """
    Load raw CSV data into a DataFrame with error handling.
    
    Args:
        filepath (str): Path to the raw CSV file
        
    Returns:
        pd.DataFrame: Raw data
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        pd.errors.EmptyDataError: If the CSV is empty
    """
    logging.info(f"Starting data extraction from: {filepath}")
    
    try:
        # Check if file exists
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Load data
        df = pd.read_csv(filepath)
        
        # Validate data was loaded
        if df.empty:
            raise pd.errors.EmptyDataError("CSV file is empty")
        
        logging.info(f"Successfully extracted {len(df):,} records")
        logging.info(f"   Columns: {list(df.columns)}")
        logging.info(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return df
        
    except FileNotFoundError as e:
        logging.error(f"Extraction failed: {e}")
        raise
    except pd.errors.EmptyDataError as e:
        logging.error(f"Extraction failed: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during extraction: {e}")
        raise


# --------------------------
# Transformation
# --------------------------
def transform_data(df):
    """
    Clean, preprocess, and validate the dataset with detailed tracking.
    
    Args:
        df (pd.DataFrame): Raw dataframe
        
    Returns:
        pd.DataFrame: Cleaned and transformed dataframe
    """
    logging.info("\n" + "="*70)
    logging.info("Starting Data Transformation")
    logging.info("="*70)
    
    initial_count = len(df)
    original_df = df.copy()  # Keep for reporting
    
    try:
        # Step 1: Handle missing values
        logging.info("\n[Step 1/10] Handling missing values...")
        nulls_before = df.isnull().sum().sum()
        
        df["Size"] = df["Size"].fillna(df["Size"].mode()[0])
        df["Units_Sold"] = df["Units_Sold"].fillna(df["Units_Sold"].median())
        df["MRP"] = df["MRP"].fillna(df["MRP"].median())
        df["Discount_Applied"] = df["Discount_Applied"].fillna(0)
        df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
        df["Order_Date"] = df["Order_Date"].fillna(df["Order_Date"].mode()[0])
        
        nulls_after = df.isnull().sum().sum()
        logging.info(f"   Filled {nulls_before - nulls_after} missing values")

        # Step 2: Remove duplicate Order_IDs
        logging.info("\n[Step 2/10] Removing duplicate Order_IDs...")
        duplicates = df.duplicated(subset='Order_ID', keep='first').sum()
        df = df.drop_duplicates(subset='Order_ID', keep='first')
        logging.info(f"   Removed {duplicates} duplicate records")

        # Step 3: Standardize Region names
        logging.info("\n[Step 3/10] Standardizing Region names...")
        regions_before = df['Region'].unique()
        df['Region'] = df['Region'].str.strip().str.title()
        df['Region'] = df['Region'].replace({
            'Bengaluru': 'Bangalore',
            'Hyd': 'Hyderabad',
            'Hyderbad': 'Hyderabad'
        })
        regions_after = df['Region'].unique()
        logging.info(f"   Before: {list(regions_before)}")
        logging.info(f"   After: {list(regions_after)}")

        # Step 4: Handle negative profit
        logging.info("\n[Step 4/10] Flagging negative profit transactions...")
        df['Loss_Flag'] = df['Profit'] < 0
        loss_count = df['Loss_Flag'].sum()
        logging.info(f"   Identified {loss_count} loss-making transactions")

        # Step 5: Validate Units_Sold and recalc Revenue
        logging.info("\n[Step 5/10] Validating Units_Sold and recalculating Revenue...")
        negative_units = (df['Units_Sold'] < 0).sum()
        df['Units_Sold'] = df['Units_Sold'].abs()
        df['Revenue'] = df['Units_Sold'] * df['MRP'] * (1 - df['Discount_Applied'] / 100)
        logging.info(f"   Corrected {negative_units} negative Units_Sold values")
        logging.info(f"   Recalculated Revenue for all records")

        # Step 6: Standardize Product_Line & Gender_Category
        logging.info("\n[Step 6/10] Standardizing Product_Line and Gender_Category...")
        df['Product_Line'] = df['Product_Line'].str.strip().str.title()
        df['Gender_Category'] = df['Gender_Category'].str.strip().str.title()
        logging.info(f"   Product Lines: {df['Product_Line'].unique().tolist()}")
        logging.info(f"   Gender Categories: {df['Gender_Category'].unique().tolist()}")

        # Step 7: Convert columns to correct types
        logging.info("\n[Step 7/10] Converting data types...")
        numeric_cols = ['Units_Sold', 'MRP', 'Discount_Applied', 'Revenue', 'Profit']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        logging.info(f"   Converted {len(numeric_cols)} columns to numeric types")

        # Step 8: Remove revenue outliers using IQR
        logging.info("\n[Step 8/10] Removing revenue outliers (IQR method)...")
        before_outlier_removal = len(df)
        Q1 = df['Revenue'].quantile(0.25)
        Q3 = df['Revenue'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - ETLConfig.OUTLIER_THRESHOLD * IQR
        upper_bound = Q3 + ETLConfig.OUTLIER_THRESHOLD * IQR
        
        df = df[~((df['Revenue'] < lower_bound) | (df['Revenue'] > upper_bound))]
        outliers_removed = before_outlier_removal - len(df)
        logging.info(f"   Q1: ₹{Q1:,.2f}, Q3: ₹{Q3:,.2f}, IQR: ₹{IQR:,.2f}")
        logging.info(f"   Bounds: [₹{lower_bound:,.2f}, ₹{upper_bound:,.2f}]")
        logging.info(f"   Removed {outliers_removed} outlier records")

        # Step 9: Remove any remaining zero Units_Sold
        logging.info("\n[Step 9/10] Removing zero Units_Sold records...")
        zero_units = (df['Units_Sold'] <= 0).sum()
        df = df[df['Units_Sold'] > 0]
        logging.info(f"   Removed {zero_units} records with zero units")

        # Step 10: Add metadata
        logging.info("\n[Step 10/10] Adding ETL metadata...")
        df['etl_timestamp'] = datetime.now()
        df['etl_version'] = '2.0'
        logging.info(f"   Added timestamp and version tracking")

        # Final summary
        final_count = len(df)
        records_removed = initial_count - final_count
        retention_rate = (final_count / initial_count) * 100
        
        logging.info("\n" + "-"*70)
        logging.info(f"Transformation Complete")
        logging.info(f"   Initial records: {initial_count:,}")
        logging.info(f"   Final records: {final_count:,}")
        logging.info(f"   Records removed: {records_removed:,}")
        logging.info(f"   Retention rate: {retention_rate:.2f}%")
        logging.info("-"*70)
        
        return df
        
    except Exception as e:
        logging.error(f"Transformation failed: {e}")
        raise


# --------------------------
# Data Quality Validation
# --------------------------
def validate_data(df):
    """
    Perform comprehensive data quality checks.
    
    Args:
        df (pd.DataFrame): Transformed dataframe
        
    Raises:
        AssertionError: If any validation rule fails
    """
    logging.info("\n" + "="*70)
    logging.info("Running Data Quality Validation")
    logging.info("="*70)
    
    try:
        # Check 1: No nulls in critical columns
        critical_cols = ['Order_ID', 'Order_Date', 'Region', 'Product_Line']
        nulls = df[critical_cols].isnull().sum()
        assert nulls.sum() == 0, f"Found nulls in critical columns: {nulls[nulls > 0]}"
        logging.info("No nulls in critical columns")
        
        # Check 2: Unique Order_IDs
        assert not df['Order_ID'].duplicated().any(), "Duplicate Order_IDs found"
        logging.info("All Order_IDs are unique")
        
        # Check 3: Positive Units_Sold
        assert df['Units_Sold'].min() > 0, f"Invalid Units_Sold: min = {df['Units_Sold'].min()}"
        logging.info(f"Units_Sold range: [{df['Units_Sold'].min()}, {df['Units_Sold'].max()}]")
        
        # Check 4: Positive MRP
        assert df['MRP'].min() > 0, f"Invalid MRP: min = {df['MRP'].min()}"
        logging.info(f"MRP range: [₹{df['MRP'].min():,.2f}, ₹{df['MRP'].max():,.2f}]")
        
        # Check 5: Valid Regions
        invalid_regions = set(df['Region'].unique()) - set(ETLConfig.VALID_REGIONS)
        assert len(invalid_regions) == 0, f"Invalid regions found: {invalid_regions}"
        logging.info(f"All regions are valid: {df['Region'].unique().tolist()}")
        
        # Check 6: Valid discount range
        assert df['Discount_Applied'].between(0, 100).all(), "Discount out of range [0, 100]"
        logging.info(f"Discount range: [{df['Discount_Applied'].min()}%, {df['Discount_Applied'].max()}%]")
        
        # Check 7: Revenue consistency
        calculated_revenue = df['Units_Sold'] * df['MRP'] * (1 - df['Discount_Applied'] / 100)
        revenue_diff = (df['Revenue'] - calculated_revenue).abs().max()
        assert revenue_diff < 0.01, f"Revenue calculation mismatch: max diff = {revenue_diff}"
        logging.info("Revenue calculations are consistent")
        
        logging.info("\n" + "="*70)
        logging.info("All Data Quality Checks Passed!")
        logging.info("="*70)
        
    except AssertionError as e:
        logging.error(f"Data quality validation failed: {e}")
        raise


# --------------------------
# Loading
# --------------------------
def load_data(df, csv_path=None):
    """
    Save the cleaned dataset to CSV file.
    
    Args:
        df (pd.DataFrame): Cleaned dataframe
        csv_path (str, optional): Path to save CSV
    """
    logging.info("\n" + "="*70)
    logging.info("Starting Data Load")
    logging.info("="*70)
    
    try:
        # Load to CSV
        if csv_path:
            logging.info(f"Loading data to CSV: {csv_path}")
            df.to_csv(csv_path, index=False)
            file_size = Path(csv_path).stat().st_size / 1024  # KB
            logging.info(f"Saved {len(df):,} records to CSV ({file_size:.2f} KB)")
        
        logging.info("="*70)
        
    except Exception as e:
        logging.error(f"Load failed: {e}")
        raise


# --------------------------
# Summary Report
# --------------------------
def generate_summary_report(original_df, cleaned_df):
    """
    Generate comprehensive ETL summary statistics.
    
    Args:
        original_df (pd.DataFrame): Original raw dataframe
        cleaned_df (pd.DataFrame): Cleaned dataframe
    """
    logging.info("\n" + "="*70)
    logging.info("ETL PIPELINE SUMMARY REPORT")
    logging.info("="*70)
    
    # Calculate metrics
    records_extracted = len(original_df)
    records_loaded = len(cleaned_df)
    records_removed = records_extracted - records_loaded
    removal_rate = (records_removed / records_extracted) * 100
    
    total_revenue = cleaned_df['Revenue'].sum()
    total_profit = cleaned_df['Profit'].sum()
    avg_profit_margin = (total_profit / total_revenue) * 100
    loss_transactions = (cleaned_df['Profit'] < 0).sum()
    
    # Print report
    logging.info(f"\nData Processing Metrics:")
    logging.info(f"   Records Extracted: {records_extracted:,}")
    logging.info(f"   Records Loaded: {records_loaded:,}")
    logging.info(f"   Records Removed: {records_removed:,} ({removal_rate:.2f}%)")
    
    logging.info(f"\nBusiness Metrics:")
    logging.info(f"   Total Revenue: ₹{total_revenue:,.2f}")
    logging.info(f"   Total Profit: ₹{total_profit:,.2f}")
    logging.info(f"   Avg Profit Margin: {avg_profit_margin:.2f}%")
    logging.info(f"   Loss Transactions: {loss_transactions:,} ({(loss_transactions/records_loaded)*100:.2f}%)")
    
    logging.info(f"\n🏪 Regional Distribution:")
    for region, count in cleaned_df['Region'].value_counts().items():
        pct = (count / records_loaded) * 100
        logging.info(f"   {region}: {count:,} ({pct:.1f}%)")
    
    logging.info(f"\n👕 Product Line Distribution:")
    for product, count in cleaned_df['Product_Line'].value_counts().items():
        pct = (count / records_loaded) * 100
        logging.info(f"   {product}: {count:,} ({pct:.1f}%)")
    
    logging.info("\n" + "="*70)


# --------------------------
# Main ETL Pipeline
# --------------------------
def main():
    """Execute the complete ETL pipeline with error handling"""
    start_time = datetime.now()
    
    try:
        # Setup logging
        setup_logging()
        
        # Extract
        raw_df = extract_data(ETLConfig.RAW_CSV)
        original_df = raw_df.copy()  # Keep for reporting
        
        # Transform
        cleaned_df = transform_data(raw_df)
        
        # Validate
        validate_data(cleaned_df)
        
        # Load
        load_data(
            cleaned_df, 
            csv_path=ETLConfig.CLEANED_CSV
        )
        
        # Generate summary report
        generate_summary_report(original_df, cleaned_df)
        
        # Final message
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logging.info("\n" + "="*70)
        logging.info(f"ETL Pipeline Completed Successfully in {duration:.2f} seconds")
        logging.info("="*70)
        
        return cleaned_df
        
    except Exception as e:
        logging.error(f"\nETL Pipeline Failed: {e}")
        logging.error("="*70)
        raise


# --------------------------
# Entry Point
# --------------------------
if __name__ == "__main__":
    main()
