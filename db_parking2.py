from config import load_config
import mysql.connector
import pandas as pd
import streamlit as st
import os

class ParkingDatabase:

    def __init__(self):
        self.config=load_config()
        self.create_db_table()
    def create_db_table(self):
        init_cfg=self.config.copy()
        init_cfg.pop("database",None)
        with mysql.connector.connect(**init_cfg) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE DATABASE IF NOT EXISTS parking_db ")
                cur.execute("USE parking_db")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS parking_info(
                    id  INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    address VARCHAR(200),
                    x VARCHAR(30),
                    y VARCHAR(30),
                    distance INT,
                    url TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP )
                """
            )
            conn.commit()
    def clear_parking_data(self) -> None:
        with mysql.connector.connect(**self.config) as conn:
            cur.execute("DELETE FROM parking_info")
            conn.commit()
        print("parking data cleared")

    def save_to_db(self,parking_data:list[dict]) ->None:
        with mysql.connector.connect(**self.config) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM parking_info")

                for lot in parking_data:
                    cur.execute(
                        """
                        INSERT INTO parking_info
                        (name,address,x,y,distance,url)
                        VALUES(%s,%s,%s,%s,%s,%s)
                        """,
                        (lot["place_name"],
                         lot.get("road_address_name") or lot.get("address_name"),
                         lot["x"],
                         lot["y"],
                         lot['distance'],
                         lot["place_url"],
                         ),
                    )
                conn.commit()
            print("parkin data saved")
    def get_parking_data(self) -> pd.DataFrame:
        with mysql.connector.connect(**self.config) as conn:
            df=pd.read_sql(
                "SELECT * FROM parking_info ORDER BY distance ASC ",conn
            )
        return df
