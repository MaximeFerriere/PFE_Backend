from neo4j import GraphDatabase
from src.dto.UserDTO import *
import os
import bcrypt
from dotenv import load_dotenv
from dataclasses import asdict

load_dotenv()
host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("AUTH")


# Connect to the database
graph = GraphDatabase.driver(host, auth=(user, password))


def create_user(user_dto: UserDTO):
    with graph.session() as session:
        # Create the new user in the Neo4j database
        result = session.run(
            'CREATE (u:User $user_properties) RETURN u', user_properties=asdict(user_dto))

        user = result.single().data()['u']
        user.pop('password', None)

        print(user)

        # Return the result of the query
        return user


def check_user(password: str, email: str):
    with graph.session() as session:
        result = session.run(
            'MATCH (u:User) WHERE u.email = $email RETURN u.password', email=asdict(email)
        )

        user = result.single().data()['u']['password']
        if bcrypt.checkpw(password, user):
            return True
        else:
            return False