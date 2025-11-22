import pandas as pd
from src.fortnite_api import *
from src.azure_db import *

#Connect to Azure DB
engine = azure_db_connect()

#Identify existing players in DB
players_df = pd.read_sql("SELECT * FROM fortnite_player", con=engine)
#Player stats from the latest update (before new date is added)
players_stats_hist = pd.read_sql("SELECT * FROM fortnite_player_stats", con=engine)

#Print test for validation of connection
print(players_df.head())
print(players_stats_hist.head())



