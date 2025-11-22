import os
import urllib
from sqlalchemy import create_engine, text
from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def azure_db_connect():
    """Connect to Azure DB. The connection is using credential stored in created environment

    Returns:
        variable : connection engine
    """
    print('Starting connection to Azure SQL Database...')
    db_server = os.environ['DB_SERVER']
    db_name = os.environ['DB_DATABASE']
    db_uid = os.environ['DB_UID']
    db_pwd = os.environ['DB_PWD']

    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={db_server};"
        f"Database={db_name};"
        f"Uid={db_uid};"
        f"Pwd={db_pwd};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;")
    
    params = urllib.parse.quote_plus(conn_str)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    # Test connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        
    print("Connected to Azure SQL Database")
    
    return engine