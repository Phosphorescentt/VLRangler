from typing import Any, List, Optional, Type

import requests

from bs4 import BeautifulSoup

from . import db
from . import model


class VLRParser:
    """
    Use this class if you want to parse vlr.gg webpages
    """

    def __init__(self):
        pass

    def parse_team_page(self, id: int, html: bytes) -> model.Team:
        s = BeautifulSoup(html, features="html.parser")
        display_name = s.find_all("div", {"class": "team-header-name"})[0]
        return model.Team(id, display_name.h1.string)

    def parse_team_results_page(self, html: bytes):
        pass


class VLRSession:
    """
    Use this class if you just want data given back to you in a nice format
    """

    def __init__(self, url: str = "https://www.vlr.gg"):
        self.url = url
        self.session = requests.session()
        self.parser = VLRParser()

    def _request(self, method: str, url: str):
        return requests.request(method, f"{self.url}{url}")

    def _get(self, url: str):
        return self._request("GET", url)

    def _get_team_html(self, id: int, name: str = ""):
        r = self._get(f"/team/{id}/{name}")
        if r.status_code == 200:
            return r.content
        else:
            raise requests.HTTPError(f"{r.status_code}")

    def get_team(self, id: int, name: str = "") -> model.Team:
        html = self._get_team_html(id, name)
        team = self.parser.parse_team_page(id, html)
        return team

    def get_fixtures_for_team(
        self, team: model.Team, paginated: bool = False, pages: int = 1
    ) -> List[model.PastFixture]:
        html = self._get(f"/team/matches/{team.id}/{team.display_name}").content
        if paginated:
            results = self.parser.parse_team_results_page(html)
        else:
            raise NotImplementedError()

        return []


class VLRHandler:
    """
    Use this class if you want to be able to give a team's ID/name and get a
    significant amount of data automatically loaded into your database.
    """

    def __init__(
        self,
        database: Type[db.DatabaseClient],
        vlr_session: Optional[VLRSession] = None,
    ):
        self.database = database
        if vlr_session:
            self.session = vlr_session
        else:
            self.session = VLRSession()

    def add_team_from_id(self, team_id: int) -> model.Team:
        raise NotImplementedError()

    def add_teams_from_ids(self, team_ids: List[int]) -> List[model.Team]:
        return [self.add_team_from_id(id) for id in team_ids]

    def add_fixtures_for_team(
        self, teae: model.Team, recursive: bool = False
    ) -> model.PastFixture:
        raise NotImplementedError()

    def add_fixtures_for_teams(
        self, teams: List[model.Team], recursive: bool = False
    ) -> List[model.PastFixture]:
        return [self.add_fixtures_for_team(team) for team in teams]
