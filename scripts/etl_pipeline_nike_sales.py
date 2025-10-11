#!/usr/bin/env python
# coding: utf-8

"""
👟 Nike Sales Data ETL Pipeline

This script performs an end-to-end ETL (Extract, Transform, Load) process
on the synthetic Nike sales dataset. It extracts raw CSV data, cleans
and transforms it, and then loads the cleaned dataset into CSV or SQLite DB.
"""

import pandas as pd
import numpy as np
import sqlite3


# --------------------------
# Extraction
# --------------------------
def extract_data(filepath):
    """Load raw CSV data into a DataFrame."""
    df = pd.read_csv(filepath)
    return df


# --------------------------
# Transformation
# --------------------------
def transform_data(df):
    """Clean, preprocess, and validate the dataset."""

    # Step 1: Handle missing values
    df["Size"] = df["Size"].fillna(df["Size"].mode()[0])
    df["Units_Sold"] = df["Units_Sold"].fillna(df["Units_Sold"].median())
    df["MRP"] = df["MRP"].fillna(df["MRP"].median())
    df["Discount_Applied"] = df["Discount_Applied"].fillna(0)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Order_Date"] = df["Order_Date"].fillna(df["Order_Date"].mode()[0])

    # Step 2: Remove duplicate Order_IDs
    df = df.drop_duplicates(subset='Order_ID', keep='first')

    # Step 3: Standardize Region names
    df['Region'] = df['Region'].str.strip().str.title()
    df['Region'] = df['Region'].replace({
        'Bengaluru': 'Bangalore',
        'Hyd': 'Hyderabad',
        'Hyderbad': 'Hyderabad'
    })

    # Step 4: Handle negative profit
    df['Loss_Flag'] = df['Profit'] < 0

    # Step 5: Validate Units_Sold and recalc Revenue
    df['Units_Sold'] = df['Units_Sold'].abs()
    df['Revenue'] = df['Units_Sold'] * df['MRP'] * (1 - df['Discount_Applied'] / 100)

    # Step 6: Standardize Product_Line & Gender_Category
    df['Product_Line'] = df['Product_Line'].str.strip().str.title()
    df['Gender_Category'] = df['Gender_Category'].str.strip().str.title()

    # Step 7: Convert columns to correct types
    numeric_cols = ['Units_Sold', 'MRP', 'Discount_Applied', 'Revenue', 'Profit']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Step 8: Remove revenue outliers using IQR
    Q1 = df['Revenue'].quantile(0.25)
    Q3 = df['Revenue'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df['Revenue'] < (Q1 - 1.5 * IQR)) | (df['Revenue'] > (Q3 + 1.5 * IQR)))]

    # Step 9: Remove any remaining zero Units_Sold
    df = df[df['Units_Sold'] > 0]

    return df


# --------------------------
# Loading
# --------------------------
def load_data(df, csv_path=None,):
    """Save the cleaned dataset to CSV and/or SQLite database."""
    if csv_path:
        df.to_csv(csv_path, index=False)
        print(f"✅ Data saved to CSV: {csv_path}")
    


# --------------------------
# Main ETL pipeline
# --------------------------
def main():
    # File paths
    raw_csv = "../data/Nike_Sales_Uncleaned.csv"
    cleaned_csv = "../data/Nike_Sales_Cleaned.csv"
    

    # Run ETL
    df = extract_data(raw_csv)
    df = transform_data(df)
    load_data(df, csv_path=cleaned_csv,)

    # Final validation
    print("---- Final Data Validation ----")
    print("Nulls per column:\n", df.isnull().sum())
    print("Duplicate Order_IDs:", df.duplicated(subset='Order_ID').sum())
    print("Unique Regions:", df['Region'].unique())
    print("Unique Product Lines:", df['Product_Line'].unique())
    print("Unique Gender Categories:", df['Gender_Category'].unique())
    print("Number of transactions with negative profit:", (df['Profit'] < 0).sum())
    print("ETL pipeline completed successfully!")


# Run the ETL pipeline
if __name__ == "__main__":
    main()
