import pandas as pd
import numpy as np
import re

def clean_amount(value):
    if pd.isna(value) or value == 'undisclosed' or value == 'unknown' or value == 'N/A' or value == 'nan':
        return np.nan
    # Remove commas and other non-numeric chars except '.'
    clean_val = re.sub(r'[^\d.]', '', str(value))
    try:
        return float(clean_val)
    except:
        return np.nan

def clean_date(date_str):
    if pd.isna(date_str):
        return pd.NaT
    # Replace dots and special chars with forward slash
    date_str = str(date_str).replace('.', '/').replace('//', '/')
    # Handle some common typos
    date_str = date_str.replace('05/072018', '05/07/2018')
    date_str = date_str.replace('01/07/015', '01/07/2015')
    
    try:
        return pd.to_datetime(date_str, format='%d/%m/%Y', errors='coerce')
    except:
        return pd.NaT

def clean_city(city):
    if pd.isna(city):
        return "Unknown"
    city = str(city).split('/')[0].strip() # Take first city if multiple
    mapping = {
        'Bengaluru': 'Bangalore',
        'Gurugram': 'Gurgaon',
        'New Delhi': 'Delhi',
        'San Francisco': 'International',
        'Palo Alto': 'International',
        'Menlo Park': 'International',
        'San Jose': 'International',
        'New York': 'International',
        'Singapore': 'International',
        'California': 'International',
        'Santa Monica': 'International'
    }
    return mapping.get(city, city)

def clean_industry(industry):
    if pd.isna(industry):
        return "Unknown"
    industry = str(industry).lower()
    if 'ecommerce' in industry or 'e-commerce' in industry:
        return 'E-Commerce'
    if 'fintech' in industry or 'finance' in industry:
        return 'FinTech'
    if 'edtech' in industry or 'education' in industry:
        return 'EdTech'
    if 'healthcare' in industry or 'health' in industry:
        return 'Healthcare'
    if 'food' in industry or 'beverage' in industry:
        return 'Food & Beverage'
    if 'transport' in industry or 'logistics' in industry:
        return 'Logistics'
    if 'tech' in industry:
        return 'Technology'
    return industry.capitalize()

def preprocess_data(input_path, output_path):
    df = pd.read_csv(input_path)
    
    # Clean Column Names
    df.columns = [col.strip() for col in df.columns]
    
    # Rename columns for ease of use
    df.rename(columns={
        'Startup Name': 'startup',
        'Industry Vertical': 'vertical',
        'City  Location': 'city',
        'Investors Name': 'investors',
        'InvestmentnType': 'round',
        'Amount in USD': 'amount',
        'Date dd/mm/yyyy': 'date'
    }, inplace=True)
    
    # Apply Cleaning
    df['amount'] = df['amount'].apply(clean_amount)
    df['date'] = df['date'].apply(clean_date)
    df['city'] = df['city'].apply(clean_city)
    df['vertical'] = df['vertical'].apply(clean_industry)
    df['startup'] = df['startup'].str.replace('"', '').str.strip()
    
    # Dropping Sr No and Remarks as they aren't useful for most analyses
    df.drop(columns=['Sr No', 'Remarks', 'SubVertical'], inplace=True, errors='ignore')
    
    # Drop rows with no dates or startup names
    df.dropna(subset=['date', 'startup'], inplace=True)
    
    # Extract year/month
    df['year'] = df['date'].dt.year.astype(int)
    df['month'] = df['date'].dt.month.astype(int)
    
    # Save Cleaned Data
    df.to_csv(output_path, index=False)
    print(f"✅ Data cleaned and saved to {output_path}")
    return df

if __name__ == "__main__":
    preprocess_data('data/startup_funding.csv', 'data/cleaned_startup_data.csv')
