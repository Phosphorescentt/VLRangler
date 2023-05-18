import os

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

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
    def get_team_by_id(self, team_id: str) -> model.Team:
        pass

    @abstractmethod
    def get_teams_by_id(self, team_ids: List[str]) -> List[model.Team]:
        pass

    # @abstractmethod
    # def get_fixture_by_id(self, fixture_id: str) -> model.PastFixture:
    #     pass
    #
    # @abstractmethod
    # def get_fixtures_by_id(self, fixture_ids: List[str]) -> List[model.PastFixture]:
    #     pass

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

    @abstractmethod
    def __del__(self):
        """
        This is part of the abstract class to ensure that all implementations
        of of this subclass have safe shutdowns to make sure no data is lost.
        """
        pass


class CSVClient(GenericDatabaseClient):
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

    def __del__(self):
        # Ensure that the most recent version of the database is saved when the
        # script is exited.
        self._read_teams_df()
        self._read_past_fixtures_df()

    def _initialise_teams_file(self):
        with open(self.path / "teams.csv", "w") as f:
            f.write(",display_name")

    def _initialise_past_fixtures_file(self):
        with open(self.path / "past_fixutres.csv", "w") as f:
            f.write(",team1_id,team2_id,series_result,datetime")

    def _read_teams_df(self):
        with open(self.path / "teams.csv", "r") as f:
            self.teams = pd.read_csv(f, index_col=0)

    def _read_past_fixtures_df(self):
        with open(self.path / "past_fixutres.csv", "r") as f:
            self.past_fixutres = pd.read_csv(f, index_col=0)

    def _update_teams_file(self):
        with open(self.path / "teams.csv", "w") as f:
            self.teams.to_csv(f)

    def _update_past_fixtures_file(self):
        with open(self.path / "past_fixtures.csv", "w") as f:
            self.past_fixtures.to_csv(f)

    def get_team_by_id(self, team_id: str) -> model.Team:
        try:
            team_df = self.teams.loc[team_id]
            return model.Team(team_id, *team_df)
        except KeyError:
            # This is kinda a bad solution and really all these functions should
            # return Rust-like result types.
            return model.Team("-1", f"Failed to find team with ID {team_id}")

    def get_teams_by_id(self, team_ids: List[str]) -> List[model.Team]:
        return [self.get_team_by_id(team_id) for team_id in team_ids]

    def add_team(self, team: model.Team) -> bool:
        # Little bug here meaning that you can get multiple duplicate rows
        # in the dataframe/CSV. At least this means it's loading the CSV
        # properly though!
        try:
            self.teams.loc[team.id]
            return False
        except KeyError:
            self.teams.loc[team.id] = [team.display_name]
            self._update_teams_file()
            return True

    def add_teams(self, teams: List[model.Team]) -> List[bool]:
        return [self.add_team(team) for team in teams]

    def add_past_fixture(self, past_fixture: model.PastFixture) -> bool:
        try:
            self.past_fixtures.loc[past_fixture.id]
            return False
        except KeyError:
            self.teams.loc[past_fixture.id]
            return True

    def add_past_fixtures(self, past_fixtures: List[model.PastFixture]) -> List[bool]:
        return [self.add_past_fixture(past_fixture) for past_fixture in past_fixtures]
