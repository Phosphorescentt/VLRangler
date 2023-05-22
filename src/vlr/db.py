import os
import logging
import datetime

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from . import model


# Hopefully can have integration with as many different databases as we like.
# Or at the very least we can make it easy for other people to bolt on their
# own database client by giving them the GenericDatabaseClient class to
# inherit.
# Examples for other database types include:
#   - Google Sheets
#   - SQLite3
#   - Postgres
#   - MySQL
#
# For now it's just Pandas and CSVs :)


# Abstract base class for a database client so that we can ensure that all
# of the daatabase clients have the right amount of functionality.
class GenericDatabaseClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_team_by_id(self, team_id: int) -> model.Team:
        pass

    @abstractmethod
    def get_teams_by_id(self, team_ids: List[int]) -> List[model.Team]:
        pass

    @abstractmethod
    def get_past_fixture_by_id(self, fixture_id: str) -> model.PastFixture:
        pass

    @abstractmethod
    def get_past_fixtures_by_id(
        self, fixture_ids: List[str]
    ) -> List[model.PastFixture]:
        pass

    @abstractmethod
    def add_team(self, team: model.Team) -> bool:
        pass

    @abstractmethod
    def add_teams(self, teams: List[model.Team]) -> List[bool]:
        pass

    @abstractmethod
    def add_past_fixture(self, past_fixture: model.PastFixture) -> bool:
        pass

    @abstractmethod
    def add_past_fixtures(self, past_fixture: List[model.PastFixture]) -> List[bool]:
        pass


class CSVClient(GenericDatabaseClient):
    class helpers:
        @staticmethod
        def split_results_string(x: str) -> Tuple[int, int]:
            x.replace(" ", "")
            x.replace("(", "")
            x.replace(")", "")
            x = x.split(",")
            return (int(x[0]), int(x[1]))

    def __init__(self, root_filepath):
        self.path = Path(root_filepath)
        self.teams = pd.DataFrame()
        self.past_fixtures = pd.DataFrame()

        # Handle all the cases for existence/nonexistence of the database files.
        match (
            os.path.isfile(self.path / "teams.csv"),
            os.path.isfile(self.path / "past_fixutres.csv"),
        ):
            case (False, False):
                self._initialise_teams_file()
                self._read_teams_df()

                self._initialise_past_fixtures_file()
                self._read_past_fixtures_df()
            case (False, True):
                self._initialise_teams_file()
                self._read_teams_df()

                self._read_past_fixtures_df()
            case (True, False):
                self._read_teams_df()

                self._initialise_past_fixtures_file()
                self._read_past_fixtures_df()
            case (True, True):
                self._read_teams_df()
                self._read_past_fixtures_df()

    def _initialise_teams_file(self):
        with open(self.path / "teams.csv", "w") as f:
            f.write(",display_name")

    def _initialise_past_fixtures_file(self):
        with open(self.path / "past_fixtures.csv", "w") as f:
            f.write(",team0_id,team1_id,series_result,datetime")

    def _read_teams_df(self):
        with open(self.path / "teams.csv", "r") as f:
            # Might have to do some processing here to move from an easily
            # stored format to a Pandas dataframe to allow for storing tuples
            # or other objects in the .csv file
            self.teams = pd.read_csv(f, index_col=0, dtype={"display_name": str})

    def _read_past_fixtures_df(self):
        with open(self.path / "past_fixtures.csv", "r") as f:
            # Might have to do some processing here to move from an easily
            # stored format to a Pandas dataframe to allow for storing tuples
            # or other objects in the .csv file
            self.past_fixtures = pd.read_csv(
                f,
                index_col=0,
                converters={
                    "team0_id": int,
                    "team1_id": int,
                    "series_result": self.helpers.split_results_string,
                    "datetime": datetime.datetime,
                },
            )

            # For example, currently series results are stored in the format
            # "(team0_score, team1_score)" in the CSV but in memory this
            # will need to be treated as a tuple. To that end, we have to map
            # everything in the series_result column to a tuple. Likewise
            # datetimes are unlikely to be stored in a good format as everything
            # in the CSV is treated as a string unless it's easy to parse
            # into somthing else (i.e. an integer or a float).

            self.past_fixtures["series_result"].apply(self.helpers.split_results_string)

    def _update_teams_file(self):
        with open(self.path / "teams.csv", "w") as f:
            self.teams.to_csv(f)

    def _update_past_fixtures_file(self):
        with open(self.path / "past_fixtures.csv", "w") as f:
            self.past_fixtures.to_csv(f)

    def get_team_by_id(self, team_id: int) -> model.Team:
        try:
            team_df = self.teams.loc[team_id]
            return model.Team(team_id, *team_df)
        except KeyError:
            # This is kinda a bad solution and really all these functions should
            # return Rust-like result types instead of just an errored team model.
            return model.Team(
                -1, f"Failed to find team with (type, ID): ({type(team_id)}, {team_id})"
            )

    def get_teams_by_id(self, team_ids: List[int]) -> List[model.Team]:
        return [self.get_team_by_id(team_id) for team_id in team_ids]

    def add_team(self, team: model.Team) -> bool:
        try:
            t = self.get_team_by_id(team.id)
            if t.id == -1:
                raise KeyError()

            return False
        except KeyError:
            self.teams.loc[team.id] = [team.display_name]
            self._update_teams_file()
            return True

    def add_teams(self, teams: List[model.Team]) -> List[bool]:
        return [self.add_team(team) for team in teams]

    def get_past_fixture_by_id(self, past_fixture_id: int) -> model.PastFixture:
        try:
            past_fixture_df = self.past_fixtures.loc[past_fixture_id]
            return model.PastFixture(past_fixture_id, *past_fixture_df)
        except KeyError:
            # This is kinda a bad solution and really all these functions should
            # return Rust-like result types instead of just an errored team model.
            return model.PastFixture(-1, -1, -1, (-1, -1), datetime.datetime(1, 1, 1))

    def get_past_fixtures_by_id(
        self, past_fixture_ids: List[int]
    ) -> List[model.PastFixture]:
        return [
            self.get_past_fixture_by_id(past_fixture_id)
            for past_fixture_id in past_fixture_ids
        ]

    def add_past_fixture(self, past_fixture: model.PastFixture) -> bool:
        try:
            f = self.get_past_fixture_by_id(past_fixture.id)
            if f.id == -1:
                raise KeyError()

            return False
        except KeyError:
            self.past_fixtures.loc[past_fixture.id] = [
                past_fixture.team0_id,
                past_fixture.team1_id,
                past_fixture.series_result,
                past_fixture.datetime,
            ]
            self._update_past_fixtures_file()
            return True

    def add_past_fixtures(self, past_fixtures: List[model.PastFixture]) -> List[bool]:
        return [self.add_past_fixture(past_fixture) for past_fixture in past_fixtures]
