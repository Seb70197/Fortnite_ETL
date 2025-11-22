import os
import urllib
from sqlalchemy import create_engine


def azure_db_connect():
    """Connect to Azure DB. The connection is using credential stored in created environment

    Returns:
        variable : connection engine
    """
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
    print("Connected to Azure SQL Database")
    
    return engine