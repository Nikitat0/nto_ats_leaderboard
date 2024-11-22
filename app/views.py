from app import app
from flask import jsonify, render_template
import pandas as pd
import datetime
from typing import Union, Tuple


cache: Union[None, Tuple[datetime.timedelta, list]] = None


def get_task_scores(task: int):
    data = pd.read_html(
        f"https://sim.avt.global/public/{task}")[-1].iloc[:, :4]
    data.fillna("[NAN]", inplace=True)
    teams = [i for i in data["Команда"] if str(i) != "nan"]
    return (
        {team: max(data[data["Команда"] == team]["Очки"]) for team in teams},
        {team: list(data[data["Команда"] == team]["Участник"])
         for team in teams},
    )


def get_leaderboard():
    response = []
    score, teams, teams_tasks = {}, {}, {}
    for task, task_value in ((138, 20), (139, 10), (140, 35), (141, 20), (142, 15)):
        team_scores, members, = get_task_scores(task)
        for team, team_score in team_scores.items():
            teams[team] = teams.get(team, set()) | set(list(members[team]))
            score[team] = score.get(team, 0) + task_value * team_score
            teams_tasks[team] = teams_tasks.get(team, ["0"] * 5)
            teams_tasks[team][task - 138] = task_value * team_score
    response = [
        {
            "task_scores": teams_tasks[team],
            "team": team,
            "members": list(teams[team]),
            "score": score,
        }
        for team, score in score.items()
        if team != "_"
    ]
    return response


def cache_is_invalid():
    return not cache or (datetime.datetime.now() - cache[0]) > datetime.timedelta(
        minutes=5
    )


@app.route("/api/leaderboard")
def leaderboard():
    global cache
    if cache_is_invalid():
        cache = datetime.datetime.now(), get_leaderboard()
    response = jsonify({"data": cache[1]})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/")
def index():
    return render_template("index.html")
