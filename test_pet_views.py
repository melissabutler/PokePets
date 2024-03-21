import os
from unittest import TestCase

from models import db, User, Pokemon, Pet, Berry, Pokedex, Berrydex, UserBerry
from functions import create_berry_db, create_pokemon_db, create_type_db, berries, types

os.environ['DATABASE_URL'] = "postgresql:///poke-test"

from app import app, CURR_USER_KEY

db.drop_all()
db.create_all()

create_berry_db(db, berries)
create_type_db(db, types)
create_pokemon_db(15, db)

app.config['WTF_CSRF_ENABLED'] = False

class PetViewsTestCase(TestCase):
    """Test pet views"""
    def setUp(self):
        """Create test client and add sample data"""
       
        Pet.query.delete()
        User.query.delete()
        

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="password")
    
        db.session.commit()

    def test_user_adopt(self):
        """Can user adopt a pet?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

        resp = client.post('/pets/adopt/1', data={"nickname": "testpet"})

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(self.testuser.pets), 1)

    def test_user_release(self):
        """Can user remove a pet?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        pet = Pet(
            id=1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()

        resp = client.post(f'/pets/{pet.id}/release')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(self.testuser.pets), 0)
    
    def test_user_add_other(self):
        """Can user add a pet to another account?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

        user2 = User(
            id= 2,
            username= "testuser2",
            password= "password",
            email = "test2@test.com"
        )
    

        resp = client.post('/pets/adopt/1', data={"nickname": "testpet", "user_id": "2"})

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(user2.pets), 0)

    def test_user_release_other(self):
        """Can a user release another account's pet?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        user2 = User(
            id= 2,
            username= "testuser2",
            password= "password",
            email = "test2@test.com"
        )
        pet = Pet(
            id = 1,
            nickname= "testpet",
            user_id = user2.id,
            poke_id = 1,
        )
        db.session.add_all([user2, pet])
        db.session.commit()

        resp = client.post(f'/pets/{pet.id}/release')

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(user2.pets), 1)

    def test_feed_pet_stats(self):
        """Does feeding pet alter stats?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

        pet = Pet(
            id = 1,
            nickname= "testpet",
            user_id = self.testuser.id,
            poke_id = 1,
        )
        db.session.add(pet)
        db.session.commit()

        resp = client.post(f'/feed_pet_apple/1', follow_redirects=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(pet.hunger, 60)

    def test_play_pet_stats(self):
        """Does playing with pet alter stats?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        pet = Pet(
                id = 1,
                nickname= "testpet",
                user_id = self.testuser.id,
                poke_id = 1,
            )
        db.session.add(pet)
        db.session.commit()

        resp = client.post(f'/play_with_pet/1', follow_redirects=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(pet.happiness, 60)

    def test_forage_stats(self):
        """Does foraging alter stats?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        pet = Pet(
            id = 1,
            nickname= "testpet",
            user_id = self.testuser.id,
            poke_id = 1,
        )
        db.session.add(pet)
        db.session.commit()

        resp = client.post(f'/foraging/1', follow_redirects=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(pet.happiness, 50)
