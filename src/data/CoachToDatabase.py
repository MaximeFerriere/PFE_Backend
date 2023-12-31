import json
from neo4j import GraphDatabase
from flask import make_response
from src.data.SportToDatabase import fetch_user_sport
from src.dto.CoachDTO import *
import os
import bcrypt
from dotenv import load_dotenv
from dataclasses import asdict

load_dotenv()
host = os.getenv("HOST")
user = os.getenv("USR")
password = os.getenv("AUTH")

# Connect to the database
graph = GraphDatabase.driver(host, auth=(user, password))


def create_coach(coach_dto: CoachDTO):
    with graph.session() as session:
        # Create the new user in the Neo4j database
        result = session.run(
            'CREATE (co:Coach $coach_properties) RETURN co', coach_properties=asdict(coach_dto))

        coach = result.single().data()['co']
        coach.pop('password', None)

        # Return the result of the query
        return coach


def fetch_coach(id: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (co:Coach) WHERE co.id = $id RETURN co', id=id)

        if (not result.peek()):
            return None

        coach = result.single().data()['co']
        coach.pop('password', None)

        # Return the result of the query
        return coach


def fetch_all_coachs():
    with graph.session() as session:
        result = session.run('MATCH (co:Coach) RETURN co')

        coachs = []

        for coach in result:
            co = coach.data()['co']
            co.pop('password', None)
            #sport = fetch_user_sport("coach", co["email"])
            coachs.append(co)
            # if (len(sport) > 0):
            #    coachs.append(sport[0])

        # Return the result of the query
        return coachs


def apply_for_club_coach(email_coach: str, id_team: str):
    with graph.session() as session:
        session.run(
            'MATCH(u:Coach)-[r:APPLY_FOR_COACH]->(t:Team) WHERE u.email= $email AND t.id = $name DELETE r', email=email_coach, name=id_team)
        session.run(
            'MATCH (u:Coach), (t:Team) WHERE u.email= $email AND t.id = $name CREATE (u)-[r:APPLY_FOR_COACH]->(t) RETURN u,r,t', email=email_coach, name=id_team)


def get_coach_club(email_user: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (p:Coach)-[r:ENTRAINE]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE p.email = $name return c', name=email_user)

        clubs = []

        for club in result:
            u = club.data()['c']
            u.pop('password', None)
            date_str = u["creation_date"].strftime('%Y-%m-%d %H:%M:%S')
            u["creation_date"] = json.dumps(date_str)
            clubs.append(u)

        return clubs


def leave_club(email_coach: str, email_club: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (p:Coach)-[r:ENTRAINE]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE p.email = $name AND c.email = $email DELETE r return p', name=email_coach, email=email_club)

        if (not result.peek()):
            return False
        return True


def is_member(email_coach: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (p:Coach)-[r:ENTRAINE]->(t:Team)-[rel:TEAM_DE]->(c:Club) WHERE p.email = $name RETURN COUNT(r)>0 AS d', name=email_coach)
        data = result.single().data()

        club = data["d"]
        return club


def update_coach(coach_dto: CoachDTO):
    with graph.session() as session:
        result = session.run(
            'MATCH (u:Coach) WHERE u.email = $email SET u.firstname = $firstname, u.lastname = $lastname, u.age = $age,u.number_year_experience = $nYE, u.description = $description, u.picture = $picture, u.picture_banner = $picture_banner RETURN u',
            email=coach_dto.email,
            firstname=coach_dto.firstname,
            lastname=coach_dto.lastname,
            age=coach_dto.age,
            nYE=coach_dto.number_year_experience,
            description=coach_dto.description,
            picture=coach_dto.picture,
            picture_banner=coach_dto.picture_banner)

        if (not result.peek()):
            return None
        coach = result.single().data()['u']
        coach.pop('password', None)

        # Return the result of the query
        return coach
