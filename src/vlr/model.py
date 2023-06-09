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
    # Deprecated temporarily to get an MVP.
    def __init__(self, team0_score: int, team1_score: int, map: Map):
        self.team0_score = team0_score
        self.team1_score = team1_score
        self.map = map

    def __repr__(self, team_names: Optional[Tuple[str, str]]):
        if team_names:
            return f"<MapResult {team_names[0]} {self.team0_score} - {self.team1_score} {team_names[1]}>"
        else:
            return f"<MapResult {self.team0_score} - {self.team1_score}>"


class BOXResult:
    # Deprecated temporarily to get an MVP.
    def __init__(
        self, X: int, team0_score: int, team1_score: int, map_results: List[MapResult]
    ):
        self.X = X
        self.team0_score = team0_score
        self.team1_score = team1_score
        if len(map_results) != self.X:
            raise Exception("Length of map_results parameter must be equal to X ")
        else:
            self.map_results = map_results


class PastFixture:
    def __init__(
        self,
        id: int,
        team0_id: int,
        team1_id: int,
        # series_result: BOXResult,
        series_result: Tuple[int, int],
        datetime: datetime.datetime = datetime.datetime(1, 1, 1),
    ):
        self.id = id
        self.team0_id = team0_id
        self.team1_id = team1_id
        self.series_result = series_result
        self.datetime = datetime

    def __repr__(self):
        return f"<PastFixture {self.team0_id} {self.series_result[0]}-{self.series_result[1]} {self.team1_id}>"
