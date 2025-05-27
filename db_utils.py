import pyodbc
import pandas as pd
import warnings

def establish_connection(server: str, database: str):
    drivers = pyodbc.drivers()
    driver = "ODBC Driver 18 for SQL Server" if "ODBC Driver 18 for SQL Server" in drivers else "ODBC Driver 17 for SQL Server"
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def run_query(server: str, database: str, query: str):
    conn = establish_connection(server, database)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error executing query:\n{e}")
        return None
    finally:
        conn.close()