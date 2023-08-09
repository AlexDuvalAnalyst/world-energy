from datetime import datetime
import pandas as pd
import numpy as numpy
import sqlite3 as sq

en = pd.read_csv("energy.csv",sep=',')

# retirer tous les pays qui on une ( ) dans leur nom car ca correspond a des regions
en = en[~en['country'].str.contains("\(")] # ~ signifie not, ce qui permet de retirer les lignes qui contiennent ( dans le nom du pays

# liste des colonnes a garder
# country, year, iso_code, population, gdp, greenhouse_gas_emissions, biofuel_consumption,  coal_consumption, fossil_fuel_consumption, gas_consumption, hydro_consumption, nuclear_consumption, 
# oil_consumption, solar_consumption, wind_consumption, biofuel_electricity, coal_electricity, fossil_fuel_electricity, gas_electricity, hydro_electricity, nuclear_electricity,
# oil_electricity, solar_electricity, wind_electricity

# premiere page generale sur les pays et les energies consommees et produites, avec gaz a effet de serre
# deuxieme page sur les tailles de populations et les energies en lien
# troisieme page sur le gdp et les energies en lien

en = en[['country', 'year', 'iso_code', 'population', 'gdp', 'greenhouse_gas_emissions', 'primary_energy_consumption','biofuel_consumption', 'coal_consumption', 'fossil_fuel_consumption', 'gas_consumption', 'hydro_consumption', 'nuclear_consumption', 'oil_consumption', 'solar_consumption', 'wind_consumption', 'electricity_generation','biofuel_electricity', 'coal_electricity', 'fossil_electricity', 'gas_electricity', 'hydro_electricity', 'nuclear_electricity', 'oil_electricity', 'solar_electricity', 'wind_electricity']]

db = sq.connect('energy.db')
cur = db.cursor()

# insertion des donnees
en.to_sql('energy',db,if_exists='replace',index=False)

# deconnexion de la base de donnees
db.close()




