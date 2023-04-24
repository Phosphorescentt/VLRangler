import datetime

from enum import Enum
from typing import List, Optional, Tuple


class Map(Enum):
    BIND = "BIND", "Bind", "bind"
    HAVEN = "HAVEN", "Haven", "haven"
    SPLIT = "SPLIT", "Split", "split"
    ASCENT = "ASCENT", "Ascent", "ascent"
    ICEBOX = "ICEBOX", "Icebox", "icebox"
    BREEZE = "BREEZE", "Breeze", "breeze"
    FRACTURE = "FRACTURE", "Fracture", "fracture"
    PEARL = "PEARL", "Pearl", "pearl"
    LOTUS = "LOTS", "Lotus", "lotus"


class Team:
    def __init__(self, id: int, display_name: str):
        self.id = id
        self.display_name = display_name

    def __repr__(self):
        return f"<Team {self.id} {self.display_name}>"


class MapResult:
    def __init__(self, team1_score: int, team2_score: int, map: Map):
        self.team1_score = team1_score
        self.team2_score = team2_score
        self.map = map

    def __repr__(self, team_names: Optional[Tuple[str, str]]):
        if team_names:
            return f"<MapResult {team_names[0]} {self.team1_score} - {self.team2_score} {team_names[1]}>"
        else:
            return f"<MapResult {self.team1_score} - {self.team2_score}>"


class BOXResult:
    def __init__(
        self, X: int, team1_score: int, team2_score: int, map_results: List[MapResult]
    ):
        self.X = X
        self.team1_score = team1_score
        self.team2_score = team2_score
        if len(map_results) != self.X:
            raise Exception("Length of map_results parameter must be equal to X ")
        else:
            self.map_results = map_results


class PastFixture:
    def __init__(
        self,
        id: int,
        team1_id: Team,
        team2_id: Team,
        series_result: BOXResult,
        datetime: datetime.datetime = datetime.datetime(1, 1, 1),
    ):
        self.id = id
        self.team1_id = team1_id
        self.team2_id = team2_id
        self.series_result = series_result
        self.datetime = datetime
