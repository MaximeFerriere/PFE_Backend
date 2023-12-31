from neo4j import GraphDatabase
from flask import make_response
from src.dto.ClubDTO import *
import os
import bcrypt
import json
from dotenv import load_dotenv
from src.data.SportToDatabase import fetch_user_sport
from dataclasses import asdict

load_dotenv()
host = os.getenv("HOST")
user = os.getenv("USR")
password = os.getenv("AUTH")

# Connect to the database
graph = GraphDatabase.driver(host, auth=(user, password))


def create_club(club_dto: ClubDTO):
    with graph.session() as session:
        # Create the new user in the Neo4j database
        result = session.run(
            'CREATE (c:Club $club_properties) RETURN c', club_properties=asdict(club_dto))

        club = result.single().data()['c']
        date_str = club["creation_date"].strftime('%Y-%m-%d %H:%M:%S')
        club["creation_date"] = json.dumps(date_str)
        club.pop('password', None)

        # Return the result of the query
        return club


def fetch_club(id: str):
    with graph.session() as session:
        result = session.run('MATCH (c:Club) WHERE c.id = $id RETURN c', id=id)

        if (not result.peek()):
            return None

        club = result.single().data()['c']
        date_str = club["creation_date"].strftime('%Y-%m-%d %H:%M:%S')
        club["creation_date"] = json.dumps(date_str)
        club.pop('password', None)

        # Return the result of the query
        return club


def fetch_all_clubs():
    with graph.session() as session:
        result = session.run('MATCH (c:Club) RETURN c')

        clubs = []

        for club in result:
            c = club.data()['c']
            date_str = c["creation_date"].strftime('%Y-%m-%d %H:%M:%S')
            c["creation_date"] = json.dumps(date_str)
            c.pop('password', None)
            #sport = fetch_user_sport("club", c["email"])
            clubs.append(c)
            # if (len(sport) > 0):
            #    clubs.append(sport[0])
        # Return the result of the query
        return clubs


def get_all_request_join_users(email_club: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (p:User)-[r:APPLY_FOR_PLAYER]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE c.email = $name RETURN p,t', name=email_club)
        users = []
        for user in result:
            u = user.data()['p']
            t = user.data()['t']
            u.pop('password', None)
            users.append(u)
            users.append(t)
        return users


def get_all_request_join_coach(email_club: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (p:Coach)-[r:APPLY_FOR_COACH]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE c.email = $name RETURN p,t', name=email_club)

        coachs = []

        for coach in result:
            c = coach.data()['p']
            t = coach.data()['t']
            c.pop('password', None)
            coachs.append(c)
            coachs.append(t)

        return coachs


def accept_new_member(email_club: str, email_member: str, role: str):
    with graph.session() as session:
        if (role == "player"):
            session.run(
                'MATCH (u:User)-[rel:APPLY_FOR_PLAYER]->(t:Team)-[r:TEAM_DE]->(c:Club) WHERE u.email=$email AND c.email = $name DELETE rel SET t.number_players = t.number_players+1 CREATE (u)-[ri:CONSTITUE]->(t) RETURN ri,t,u', email=email_member, name=email_club)
        else:
            session.run(
                'MATCH (u:Coach)-[rel:APPLY_FOR_COACH]->(t:Team)-[r:TEAM_DE]->(c:Club) WHERE u.email=$email AND c.email = $name DELETE rel CREATE (u)-[ri:ENTRAINE]->(t) RETURN ri,t,u', email=email_member, name=email_club)


def refuse_member(email_club: str, email_member: str, role: str):
    with graph.session() as session:
        if (role == "player"):
            session.run(
                'MATCH (u:User)-[rel:APPLY_FOR_PLAYER]->(t:Team)-[r:TEAM_DE]->(c:Club) WHERE u.email=$email AND c.email = $name DELETE rel', email=email_member, name=email_club)
        else:
            session.run(
                'MATCH (u:Coach)-[rel:APPLY_FOR_COACH]->(t:Team)-[r:TEAM_DE]->(c:Club) WHERE u.email=$email AND c.email = $name DELETE rel', email=email_member, name=email_club)


def get_all_players(email_club: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (p:User)-[r:CONSTITUE]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE c.email = $name return p', name=email_club)

        users = []

        for user in result:
            u = user.data()['p']
            u.pop('password', None)
            users.append(u)

        return users


def get_all_coachs(email_club: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (p:Coach)-[r:ENTRAINE]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE c.email = $name return p', name=email_club)

        coachs = []

        for coach in result:
            c = coach.data()['p']
            c.pop('password', None)
            coachs.append(c)

        return coachs


def remove_member(email_club: str, email_member: str, role: str):
    with graph.session() as session:
        if (role == "player"):
            session.run(
                'MATCH (p:User)-[r:CONSTITUE]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE p.email= $email AND c.email = $name t.number_players = t.number_players-1 DELETE r', email=email_member, name=email_club)
        else:
            session.run(
                'MATCH (p:Coach)-[r:ENTRAINE]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE p.email= $email AND c.email = $name DELETE r', email=email_member, name=email_club)


def remove_all_clubs():
    with graph.session() as session:
        session.run('MATCH (n) DETACH DELETE n')


def get_team_clubs(email_club: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (t:Team)-[r:TEAM_DE]->(c:Club) WHERE c.email = $name return t', name=email_club)
        teams = []
        for team in result:
            t = team.data()['t']
            teams.append(t)

        return teams


def update_club(club_dto: ClubDTO):
    with graph.session() as session:
        result = session.run(
            'MATCH (u:Club) WHERE u.email = $email SET u.name = $name, u.description = $description, u.picture = $picture, u.picture_banner = $picture_banner RETURN u',
            email=club_dto.email,
            name=club_dto.name,
            description=club_dto.description,
            picture=club_dto.picture,
            picture_banner=club_dto.picture_banner)

        if (not result.peek()):
            return None
        club = result.single().data()['u']
        date_str = club["creation_date"].strftime('%Y-%m-%d %H:%M:%S')
        club["creation_date"] = json.dumps(date_str)
        club.pop('password', None)

        # Return the result of the query
        return club


def get_club_with_team(id_team: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (t:Team)-[r:TEAM_DE]->(c:Club) WHERE t.id = $name return c', name=id_team)
        if (not result.peek()):
            return None
        club = result.single().data()['c']
        date_str = club["creation_date"].strftime('%Y-%m-%d %H:%M:%S')
        club["creation_date"] = json.dumps(date_str)
        club.pop('password', None)
        return club
