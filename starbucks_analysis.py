import pandas as pd

df = pd.read_csv('starbucks_sales.csv')

print(df.shape)
print(df.head())
print(df.info())

df['date'] = pd.to_datetime(df['date'])
df['revenue'] = df['price'] * df['quantity']
df['year'] = df['date'].dt.year
print(df[['date','item','price', 'quantity','revenue','year']].head())

yearly = df.groupby('year').agg(
    revenue=('revenue', 'sum'),
    units=('quantity', 'sum'),
    visits=('transaction_id', 'count')
)
print(yearly)

avg_price = df.groupby('year')['price'].mean()
print(avg_price)

by_store = df.groupby(['store', 'year'])['revenue'].sum().unstack()
print(by_store)

visits_by_store = df.groupby(['store','year'])['transaction_id'].count().unstack()
print(visits_by_store)