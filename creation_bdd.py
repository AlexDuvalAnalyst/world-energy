from datetime import datetime
import pandas as pd
import numpy as numpy
import sqlite3 as sq

en = pd.read_csv("energy.csv",sep=',')

en = en[~en['country'].str.contains("\(")] # 

# liste des colonnes a garder
# country, year, iso_code, population, gdp, greenhouse_gas_emissions, biofuel_consumption,  coal_consumption, fossil_fuel_consumption, gas_consumption, hydro_consumption, nuclear_consumption, 
# oil_consumption, solar_consumption, wind_consumption, biofuel_electricity, coal_electricity, fossil_fuel_electricity, gas_electricity, hydro_electricity, nuclear_electricity,
# oil_electricity, solar_electricity, wind_electricity

en = en[['country', 'year', 'iso_code', 'population', 'gdp', 'greenhouse_gas_emissions', 'primary_energy_consumption','biofuel_consumption', 'coal_consumption', 'fossil_fuel_consumption', 'gas_consumption', 'hydro_consumption', 'nuclear_consumption', 'oil_consumption', 'solar_consumption', 'wind_consumption', 'electricity_generation','biofuel_electricity', 'coal_electricity', 'fossil_electricity', 'gas_electricity', 'hydro_electricity', 'nuclear_electricity', 'oil_electricity', 'solar_electricity', 'wind_electricity']]

db = sq.connect('energy.db')
cur = db.cursor()

# insertion des donnees
en.to_sql('energy',db,if_exists='replace',index=False)

# deconnexion de la base de donnees
db.close()




