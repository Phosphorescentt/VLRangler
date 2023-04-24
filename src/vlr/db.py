from typing import List

from . import model


class PostgresClient:
    def __init__(self, url, auth):
        self.url = url
        self.auth = auth

    def execute(self, command) -> bool:
        raise NotImplementedError()

    def add_team(self, team: model.Team) -> bool:
        if True:  # if db add successful return true
            raise NotImplementedError()
        else:  # otherwise return false
            raise NotImplementedError()

    def add_fixture(self, fixture: model.PastFixture) -> bool:
        raise NotImplementedError()

    def add_fixutres(self, fixtures: List[model.PastFixture]) -> bool:
        raise NotImplementedError()


# Hopefully can have integration with as many different databases as we like.
# Examples include:
#   - Google Sheets
#   - SQLite3
#   - MySQL
#
# For now it's just Postgres tho :)
