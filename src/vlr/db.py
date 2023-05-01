import os

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
# For now it's just CSV tho :)


class GenericDatabaseClient:
    def __init__(self):
        pass

    def add_team(self, team: model.Team):
        raise NotImplementedError()

    def add_teams(self, teams: List[model.Team]):
        raise NotImplementedError()

    def add_past_fixture(self, past_fixture: model.PastFixture):
        raise NotImplementedError()

    def add_past_fixtures(self, past_fixture: List[model.PastFixture]):
        raise NotImplementedError()


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
                self._update_teams_df()

                self._initialise_past_fixtures_file()
                self._update_past_fixutres_df()
            case (False, True):
                self._initialise_teams_file()
                self._update_teams_df()

                self._update_past_fixutres_df()
            case (True, False):
                self._update_teams_df()

                self._initialise_past_fixtures_file()
                self._update_past_fixutres_df()
            case (True, True):
                self._update_teams_df()
                self._update_past_fixutres_df()

    def _update_teams_df(self):
        with open(self.path / "teams.csv", "r") as f:
            self.teams = pd.read_csv(f)

    def _update_past_fixutres_df(self):
        with open(self.path / "past_fixutres.csv", "r") as f:
            self.past_fixutres = pd.read_csv(f)

    def _initialise_teams_file(self):
        with open(self.path / "teams.csv", "w") as f:
            f.write("id, display_name")

    def _initialise_past_fixtures_file(self):
        with open(self.path / "past_fixutres.csv", "w") as f:
            f.write("id, team1_id, team2_id, series_result, datetime")
