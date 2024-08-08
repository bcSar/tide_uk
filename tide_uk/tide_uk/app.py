# -*- coding: utf-8 -*-
import sqlite3, os 
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app)

scheduler = BackgroundScheduler()



def get_db_connection():
    conn = sqlite3.connect("D:\\my_apps\\sqlite\\main.db")
    conn.row_factory = sqlite3.Row
    return conn




@app.route("/api/markers")
def get_markers():
    conn = get_db_connection()

    first_half = conn.execute("SELECT * FROM tide LIMIT 42").fetchall()
    second_half = conn.execute("SELECT * FROM tide LIMIT 42 OFFSET 42").fetchall()

    conn.close()

    markers = []

    for i in range(len(first_half)):
        markers.append(
            {
                "place": first_half[i]["place"],
                "lat": first_half[i]["lat"],
                "long": first_half[i]["long"],
                "station1": first_half[i]["station"],
                "station2": second_half[i]["station"],
                "datetime1": first_half[i]["datetime"],
                "datetime2": second_half[i]["datetime"],
                "parametername": first_half[i]["parameter name"],
                "value1": first_half[i]["value"],
                "value2": second_half[i]["value"],
                "unit1": first_half[i]["unit"],
                "unit2": second_half[i]["unit"],
                "period": first_half[i]["period"],
            }
        )
    return markers

def run_parser():
    with open(os.path.join(os.path.dirname(__file__), 'parser.py')) as f:
        code = f.read()
        exec(code)
    socketio.emit('update_markers', get_markers())


run_parser()

scheduler.add_job(run_parser, "interval", minutes=15)
scheduler.start()


@app.route("/")
@app.route("/main")
def main():
    return render_template("main.html")


if __name__ == "__main__":
    socketio.run(app, "localhost")
