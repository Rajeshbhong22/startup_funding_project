def top_startups(df):
    return df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)

def city_analysis(df):
    return df.groupby('city')['amount'].sum().sort_values(ascending=False)

def year_analysis(df):
    return df.groupby('year')['amount'].sum()

def investor_analysis(df):
    return df['investors'].value_counts().head(10)