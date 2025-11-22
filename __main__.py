import pandas as pd
from src.fortnite_api import *
from src.azure_db import *
from sqlalchemy import text 

#Connect to Azure DB
engine = azure_db_connect()

#Identify existing players in DB
players_df = pd.read_sql("SELECT * FROM fortnite_player", con=engine)
#Player stats from the latest update (before new date is added)
players_stats_hist = pd.read_sql("SELECT * FROM fortnite_player_stats", con=engine)

#Get today's stats from Fortnite API
players_stats_current = get_stats(players_df)
#Clean the data retrieved
players_stats_current = clean_current_stats(players_stats_current)

#final clean before upload
players_stats_current_update = clean_upload_stats(players_stats_hist, players_stats_current)

#Purge existing rows before loading the new snapshot
with engine.begin() as conn:
    #Reliable fallback that respects FK constraints:
    conn.execute(text("DELETE FROM fortnite_player_stats"))

#Update Current Stats to players_stats
players_stats_current_update.to_sql('fortnite_player_stats', con=engine, if_exists='append', index=False)
#Update same Stats to players_stats_hist --> Place a security to check if stats were already inserted for the day
players_stats_current_update.to_sql('fortnite_player_stats_hist', con=engine, if_exists='append', index=False)

#Dispose engine after all DB operations are complete
engine.dispose()





