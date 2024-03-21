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

class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create test client and add sample data"""
       
        Pet.query.delete()
        User.query.delete()
        

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="password")
        # pet = Pet(
        #     id=1,
        #     nickname="testpet",
        #     user_id=1,
        #     poke_id=1
        # )
        # db.session.add(pet)
        db.session.commit()

    def test_view_home_signup_prompt(self):
        """Does a non-logged in user see the login prompt?"""
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('New here? Sign up to adopt some pets!', html)
    
    def test_view_home_logged_in(self):
        """Does a logged in user see the logged-in view?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

        resp = client.get('/')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('New here? Sign up to adopt some pets!', html)
        self.assertIn('Meet, adopt, and play with some pokemon!', html)

    # User profile/account views
        
    def test_view_user_profile_owner(self):
        """Can user see buttons their own profile?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id


        resp = client.get(f'/users/{self.testuser.id}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('My info', html)

    def test_view_user_profile_not_owner(self):
        """Can a user see buttons on another user's profile?"""
        with app.test_client() as client:
            resp = client.get(f'/users/{self.testuser.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('My info', html)
    def test_user_edit(self):
        """Can a logged in user edit their details"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

        resp = client.get(f'/users/edit')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Edit your account details:', html)

    def test_user_edit_fail(self):
        """Can a non-logged in user edit details"""
        with app.test_client() as client:
            resp = client.get('/users/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn('Edit your account details:', html)
            
    def test_user_delete(self):
        """Can a user access the delete account form?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        
        resp = client.get('/users/delete')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Are you sure you want to delete your account?", html )

    def test_user_delete_fail(self):
        """Can a non-user access delete account form?"""
        with app.test_client() as client:
            resp = client.get('/users/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn('Are you sure you want to delete your account?', html)
# # "Store" views
    def test_adoption_center(self):
        """Can a user view the adoption page?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

        resp = client.get('/pets/adopt')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Adopt a pokepet!', html)
        
    def test_adoption_center_no_login(self):
        """Can a non-logged in user view the adoption page?"""
        with app.test_client() as client:
            resp = client.get('/pets/adopt')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn('Adopt Me!', html)
    def test_forage(self):
        """Can a user see the foraging page?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

        resp = client.get('/foraging')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Berry hunt!', html)


    def test_forage_fail(self):
        """Can a non-user see the foraging page?"""
        with app.test_client() as client:
            resp = client.get('/foraging')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn('Berry hunt!', html)

# pet detail views
    def test_pet_details_owner(self):
        """Can the pet's owner see their details?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

        pet = Pet(
            id= 1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()
        resp = client.get(f'/pets/{pet.id}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Hunger", html)
            
    def test_pet_details_not_owner(self):
        """Can a non-owner see pet details?"""
        pet = Pet(
            id= 1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()
        with app.test_client() as client:
            resp = client.get(f'/pets/{pet.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Hunger", html)

    def test_pet_release(self):
        """Can the owner release a pet?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        
        pet = Pet(
            id= 1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()

        resp = client.post(f'/pets/{pet.id}/release')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 302)
        self.assertIn("Are you sure", html)

        
    def test_pet_release_fail(self):
        """ Can a non-owner release a pet?"""
        pet = Pet(
            id= 1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()

        with app.test_client() as client:
            resp = client.post('/pets/1/release')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn("Are you sure", html)

    def test_pet_feed(self):
        """ Can the pet's owner feed them?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        pet = Pet(
            id= 1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()

        resp = client.post(f'/feed_pet_apple/{pet.id}',  follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("crunches on the apple!", html)
        
    def test_pet_feed_fail(self):
        """Can a non-owner feed a pet?"""
        pet = Pet(
            id= 1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()

        with app.test_client() as client:
            resp = client.post(f'/feed_pet_apple/{pet.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)


    def test_play_pet(self):
        """Can owner play with pet?"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        pet = Pet(
            id= 1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()

        resp = client.post(f'/play_with_pet/{pet.id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'{pet.nickname}', html)

        
    def test_play_pet_fail(self):
        """Can a non-owner play with pet?"""
        pet = Pet(
            id= 1,
            nickname="testpet",
            user_id=self.testuser.id,
            poke_id=1
        )
        db.session.add(pet)
        db.session.commit()

        with app.test_client() as client:
            resp = client.post(f'/play_with_pet/{pet.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)
    