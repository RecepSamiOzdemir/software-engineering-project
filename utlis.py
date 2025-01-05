import pandas as pd
import numpy as np

def arrange_df(df):
    cars = df
    cars = cars.drop_duplicates()
    # cars.to_csv(cars, index=False)
    cars_new = cars

    cars_new = cars_new.drop(columns=['Date', 'Brand', 'Province/District'])
    cars_new['Brand'] = cars['Brand'].str.split(' ').str[0]
    cars_new['Sherry'] = cars['Brand'].str.split(' ').str[1]
    # cars_new['Model'] = cars['Brand'].str.split(' ').str[2]
    cars_new['Model'] = cars['Brand'].apply(lambda x: ' '.join(x.split()[2:]))
    cars_new['Province'] = cars['Province/District'].str.split(' ').str[0]
    cars_new['District'] = cars['Province/District'].str.split(' ').str[1]

    cars_new['Price'] = cars_new['Price'].str.split(' ').str[0]
    cars_new['Price'] = cars_new['Price'].str.replace('.', '').astype(int)

    cars_new['Year'] = cars_new['Year'].astype(str).str.slice(start=0, stop=4, step=None)
    cars_new['Year'] = pd.to_numeric(cars_new['Year']).astype('Int64')

    cars_new['Kilometer'] = cars_new['Kilometer'].str.split(' ').str[0]
    cars_new['Kilometer'] = cars_new['Kilometer'].str.replace('.', '')
    cars_new['Kilometer'] = pd.to_numeric(cars_new['Kilometer'],  errors='coerce')


    cars_new['Color'] = cars_new['Color'].str.split(' ').str[0]

    cars_new = cars_new[['Brand', 'Sherry', 'Model', 'Price', 'Year', 'Kilometer', 'Color', 'Province', 'District',
                         'Damage Information']]

    cars_new = cars_new.drop_duplicates()
    cars_new = cars_new.dropna()
    return cars_new





