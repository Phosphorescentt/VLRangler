import datetime
from typing import Tuple, List


class Team:
    def __init__(self, id: int, display_name: str):
        self.id = id
        self.display_name = display_name

    def __repr__(self):
        return f"<Team {self.id} {self.display_name}>"


class BOXResult:
    def __init__(self, X: int, team1_score: int, team2_score: int):
        self.X = X
        self.team1_score = team1_score
        self.team2_score = team2_score


class PastFixture:
    def __init__(
        self,
        id: int,
        team1: Team,
        team2: Team,
        series_result: Tuple[int, int],
        map_results: List[Tuple[int, int]] = [],
        datetime: datetime.datetime = datetime.datetime(1, 1, 1),
    ):
        self.id = id
        self.team1 = team1
        self.team2 = team2
        self.series_result = series_result
        self.map_results = map_results
        self.datetime = datetime
