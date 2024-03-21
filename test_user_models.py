import os
from unittest import TestCase

from models import db, User, Pokemon, Pet, Berry, Pokedex, Berrydex, UserBerry
from functions import create_berry_db, create_pokemon_db, create_type_db, berries, types

os.environ['DATABASE_URL'] = "postgresql:///poke-test"

from app import app 

db.drop_all()
db.create_all()

create_berry_db(db, berries)
create_type_db(db, types)
create_pokemon_db(15, db)

class UserModelTestCase(TestCase):
    """Test user model."""
    def setUp(self):
        """Create test client, add sample data."""
        Pet.query.delete()
        UserBerry.query.delete()
        User.query.delete()
        Pokedex.query.delete()
        

        self.client = app.test_client()

    def test_user_model(self):
        """Does the basic model work?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.pets), 0)
    
    def test_user_repr(self):
        """Does __repr__ method return properly?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.assertEqual(repr(u), '<User #1: testuser>')
    
    def test_user_signup(self):
        """Does user.create return a user from valid credentials"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.assertIsInstance(u, User)

    def test_user_signup_fail(self):
        """ Does user.create fail if given non-valid credentials?"""
        u = User.signup(
            email="bademail",
            username="testuser",
            password="HASHED_PASSWORD"
        ) 

        self.assertIsNot(u, User)

    def test_user_auth(self):
        """Does user.authenticate return a user when given valid username and pass?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u_auth = User.authenticate(username="testuser", password="HASHED_PASSWORD")

        self.assertIsInstance(u_auth, User)
    
    def test_user_auth_invalid_username(self):
        """Does user auth fail with an invalid username?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u_auth = User.authenticate(username="wronguser", password="HASHED_PASSWORD")

        self.assertIsNot(u_auth, User)

    def test_user_auth_invalid_password(self):
        """Does userauth fail with an invalid password"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u_auth = User.authenticate(username="testuser", password="WRONG_PASSWORD")

        self.assertIsNot(u_auth, User)

    def test_user_pet(self):
        """Does pets detect user pets?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        pet = Pet(
            nickname= "testpet",
            user_id= 1,
            poke_id = 1
        )
        db.session.add_all([u, pet])
        db.session.commit()

        self.assertIn(pet, u.pets)

    def test_user_berry(self):
        """Does userberry track user inventory?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        berry = UserBerry(
            user_id= 1,
            berry_id= 1,
        )

        db.session.add_all([u, berry])
        db.session.commit()
        
        self.assertIn(berry, u.berries)


    def test_user_pokedex(self):
        """Does user.pokedex track user seen pokemon?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        seen = Pokedex(
            user_id=1,
            pokemon_seen_id=1
        )
        db.session.add(seen)
        db.session.commit()
        poke = Pokemon.query.get_or_404(seen.pokemon_seen_id)

        self.assertIn(poke, u.pokedex)

    

