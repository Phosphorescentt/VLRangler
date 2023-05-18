import re
import datetime

from pprint import pprint

from typing import Any, List, Optional, Tuple, Type

import requests

from bs4 import BeautifulSoup

from . import db
from . import model


class VLRParser:
    """
    Use this class if you want to parse raw vlr.gg web page html.
    """

    def __init__(self):
        pass

    def clean_string(self, s: str) -> str:
        return s.replace("\t", "").replace("\n", "")

    def parse_team_page(self, id: str, html: bytes) -> model.Team:
        # TODO: Refactor this to not take an ID and instead just return the
        # display name of the team.
        s = BeautifulSoup(html, features="html.parser")
        display_name = s.find_all("div", {"class": "team-header-name"})[0]
        return model.Team(id, display_name.h1.string)

    def parse_team_id_from_url(self, url: str) -> str:
        return url.split("/")[2]

    def parse_match_id_from_url(self, url: str) -> str:
        return url.split("/")[0]

    def parse_match_results_page(
        self, html: bytes
    ) -> Tuple[Tuple[str, str], Tuple[str, str], datetime.datetime]:
        s = BeautifulSoup(html, features="html.parser")
        # Get left team
        left_team_div = s.find_all(
            "a", {"class": "match-header-link wf-link-hover mod-1"}
        )[0]
        left_team_id = self.parse_team_id_from_url(left_team_div["href"])

        # Get right team
        right_team_div = s.find_all(
            "a", {"class": "match-header-link wf-link-hover mod-2"}
        )[0]
        right_team_id = self.parse_team_id_from_url(right_team_div["href"])

        team_ids = (left_team_id, right_team_id)

        # Get scores
        scores_div = s.find_all("div", {"class": "js-spoiler"})[0]
        scores_div_spans = scores_div.find_all("span")
        result = (
            self.clean_string(scores_div_spans[0].text),
            self.clean_string(scores_div_spans[2].text),
        )

        # Get datetime
        match_header_date = s.find_all("div", {"class": "match-header-date"})[0]
        infos = match_header_date.findChildren("div", recursive=False)
        dt_string = (
            infos[0]["data-utc-ts"].split(" ")[0]
            + " "
            + infos[1].text.replace("\t", "").replace("\n", "")
        )
        dt = datetime.datetime.strptime(
            dt_string,
            "%Y-%m-%d %I:%M %p %Z",
        )

        return (team_ids, result, dt)

    def parse_team_results_page(self, html: bytes) -> List[str]:
        """Get a list of all urls for matches on the page"""
        s = BeautifulSoup(html, features="html.parser")
        results_container = s.find_all("div", {"class": "mod-dark"})[0]
        results_divs = results_container.findChildren("div", recursive=False)
        urls = [div.find_all("a")[0]["href"] for div in results_divs]
        return urls


class VLRSession:
    """
    Use this class if you just want data given back to you from vlr.gg in a nice format.
    """

    def __init__(self, url: str = "https://www.vlr.gg"):
        self.url = url
        self.session = requests.session()
        self.parser = VLRParser()

    def _request(self, method: str, url: str):
        return requests.request(method, f"{self.url}{url}")

    def _get(self, url: str):
        return self._request("GET", url)

    def _get_team_html(self, id: str, name: str = ""):
        r = self._get(f"/team/{id}/{name}")
        if r.status_code == 200:
            return r.content
        else:
            raise requests.HTTPError(f"{r.status_code}")

    def get_team(self, id: str, name: str = "") -> model.Team:
        html = self._get_team_html(id, name)
        team = self.parser.parse_team_page(id, html)
        return team

    def get_past_fixtures_for_team(
        self,
        team: model.Team,
        pages: Optional[int] = None,
        max_fixtures: Optional[int] = None,
    ) -> List[model.PastFixture]:
        html = self._get(f"/team/matches/{team.id}/{team.display_name}").content
        if pages:
            # Iterate and combine all urls into one list
            raise NotImplementedError()
        else:
            urls = self.parser.parse_team_results_page(html)

        if max_fixtures:
            urls = urls[:max_fixtures]

        fixtures = []
        for url in urls:
            html = self._get(url).content
            id = self.parser.parse_match_id_from_url(url)
            team_ids, result, dt = self.parser.parse_match_results_page(html)

            fixture = model.PastFixture(id, team_ids[0], team_ids[1], result, dt)
            fixtures.append(fixture)

        return fixtures


class VLRHandler:
    """
    Use this class if you want to be able to give a team's ID/name and get a
    significant amount of data automatically loaded into your database.
    """

    def __init__(
        self,
        database: Type[db.GenericDatabaseClient],
        vlr_session: Optional[VLRSession] = None,
    ):
        self.database = database
        if vlr_session:
            self.session = vlr_session
        else:
            self.session = VLRSession()

    def get_team_from_id(self, team_id: str) -> model.Team:
        # TODO: check if something is in the db before going off to vlr to get
        # the data.
        return self.session.get_team(team_id)

    def get_teams_from_ids(self, team_ids: List[str]) -> List[model.Team]:
        return [self.get_team_from_id(id) for id in team_ids]

    def add_team_from_id(self, team_id: str) -> model.Team:
        team = self.get_team_from_id(team_id)
        s = self.database.add_team(team)
        if s:
            return team
        else:
            raise Exception("Something went wrong!")

    def add_teams_from_ids(self, team_ids: List[str]) -> List[model.Team]:
        return [self.add_team_from_id(id) for id in team_ids]

    def get_past_fixtures_for_team(
        self,
        team: model.Team,
        pages: Optional[int] = None,
        max_fixtures: Optional[int] = None,
        recursive: bool = False,
    ) -> List[model.PastFixture]:
        if recursive:
            raise NotImplementedError()
        else:
            return self.session.get_past_fixtures_for_team(team, pages, max_fixtures)

    def add_past_fixtures_for_team(
        self, team: model.Team, recursive: bool = False
    ) -> model.PastFixture:
        raise NotImplementedError()

    def add_past_fixtures_for_teams(
        self, teams: List[model.Team], recursive: bool = False
    ) -> List[model.PastFixture]:
        # If `recursive == true` then every time we come across a team that is
        # not already in the database, we shouold add it.
        return [self.add_past_fixtures_for_team(team) for team in teams]
