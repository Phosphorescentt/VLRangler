from typing import Any, List

import requests

from bs4 import BeautifulSoup

from . import model


class VLRSession:
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
        self, team: model.Team, paginated: bool = False
    ) -> List[model.PastFixture]:
        html = self._get(f"/team/matches/{team.id}/{team.display_name}").content
        if paginated:
            results = self.parser.parse_team_results_page(html)
        else:
            raise NotImplementedError()

        return []


class VLRParser:
    def __init__(self):
        pass

    def parse_team_page(self, id: int, html: bytes) -> model.Team:
        s = BeautifulSoup(html, features="html.parser")
        display_name = s.find_all("div", {"class": "team-header-name"})[0]
        return model.Team(id, display_name.h1.string)

    def parse_team_results_page(self, html: bytes):
        pass
