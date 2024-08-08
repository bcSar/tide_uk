# -*- coding: utf-8 -*-
import sqlite3

import pandas as pd
import requests

# чтение данных
stations = "https://environment.data.gov.uk/flood-monitoring/id/stations?type=TideGauge"
r_stations = requests.get(stations)
r_stations = r_stations.json()

# создание датасета
stations = {
    "place": [],
    "lat": [],
    "long": [],
    "station": [],
    "datetime": [],
    "parameter name": [],
    "value": [],
    "unit": [],
    "period": [],
}

for i in range(len(r_stations["items"])):
    try:
        stations["place"].append(r_stations["items"][i]["label"])
    except Exception:
        stations["place"].append(None)
    try:
        stations["lat"].append(r_stations["items"][i]["lat"])
    except Exception:
        stations["lat"].append(None)
    try:
        stations["long"].append(r_stations["items"][i]["long"])
    except Exception:
        stations["long"].append(None)
    try:
        stations["station"].append(r_stations["items"][i]["stationReference"])
    except Exception:
        stations["station"].append(None)

    r_measures = requests.get(r_stations["items"][i]["measures"][0]["@id"]).json()
    try:
        stations["datetime"].append(r_measures["items"]["latestReading"]["dateTime"])
    except Exception:
        stations["datetime"].append(None)
    try:
        stations["value"].append(r_measures["items"]["latestReading"]["value"])
    except Exception:
        stations["value"].append(None)
    try:
        stations["parameter name"].append(r_measures["items"]["parameterName"])
    except Exception:
        stations["parameter name"].append(None)
    try:
        stations["unit"].append(r_measures["items"]["unitName"])
    except Exception:
        stations["unit"].append(None)
    try:
        stations["period"].append(str(r_measures["items"]["period"] / 60) + " minutes")
    except Exception:
        stations["period"].append(None)

df = pd.DataFrame(stations)
if "mm" in df.unit.value_counts().index.tolist():
    df.drop(list(df.loc[df["unit"] == "mm"].index), inplace=True)
df = df.sort_values(by=["unit", "place"]).reset_index(drop=True)
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce").dt.strftime(
    "%Y-%m-%d %H:%M"
)

# обновление баз  данных
conn = sqlite3.connect("D:\\my_apps\\sqlite\\main.db")
existing_df = pd.read_sql_query("SELECT * FROM tide", conn)


if existing_df.equals(df):
    print("The data hasn't changed. The database update is not required.")
    conn.close()
else:
    print("The data has changed. The database is updating...")
    try:
        df.to_sql("tide", conn, if_exists="replace", index=False)
    except Exception as e:
        print(f"An error occurred: {e}")

    conn.commit()
    conn.close()

    print("Database is updated.")
