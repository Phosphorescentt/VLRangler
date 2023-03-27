from typing import List, Union

import requests

from bs4 import BeautifulSoup

import model


class VLRSession:
    def __init__(self, url: str = "https://www.vlr.gg"):
        self.url = url
        self.session = requests.session()

    def _request(self, method: str, url: str):
        return requests.request(method, f"{self.url}{url}")

    def _get(self, url: str):
        return self._request("GET", url)

    def get_team_html(self, id: int, name: str = ""):
        r = self._get(f"/team/{id}/{name}")
        if r.status_code == 200:
            return r.content
        else:
            raise requests.HTTPError(f"{r.status_code}")

    def get_team(self, id: int, name: str = "") -> model.Team:
        html = self.get_team_html(id, name)
        s = BeautifulSoup(html, features="html.parser")
        display_name = s.find_all("div", {"class": "team-header-name"})[0]
        return model.Team(id, display_name.h1.string)

    def get_fixtures_for_team(
        self, team: model.Team, paginated: bool = False
    ) -> List[model.PastFixture]:
        if not paginated:
            # do stuff
            return None
        else:
            # implement me
            raise NotImplementedError()
