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

class PetModelTestCase(TestCase):
    """Test pet model"""
    def setUp(self):
        """Create test client"""
        Pet.query.delete()
        User.query.delete()
        Berrydex.query.delete()

        self.client = app.test_client()

    
    def test_pet_model(self):
        """Does the basic model work?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()

        self.assertEqual(len(u.pets), 1)

    def test_pet_repr(self):
        """Does __repr__ method return properly?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()

        self.assertEqual(repr(p), '<Pet #1 testpet, Owner testuser>')

    def test_pet_decrease_happiness(self):
        """Does decrease_happiness work?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()
        p.decrease_happiness(10)

        self.assertEqual(p.happiness, 40)

    def test_pet_increase_happiness(self):
        """Does increase_happiness work?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()
        p.increase_happiness(10)

        self.assertEqual(p.happiness, 60)
    def test_pet_decrease_hunger(self):
        """Does decrease_hunger work?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()
        p.decrease_hunger(10)

        self.assertEqual(p.hunger, 40)

    def test_pet_increase_hunger(self):
        """Does increase_hunger work?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()
        p.increase_hunger(10)

        self.assertEqual(p.hunger, 60)
    
    def test_pet_berrydex(self):
        """Does berrydex record tried berries?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()
        berry = Berry.query.get_or_404(1)
        p.berrydex.append(berry)

        self.assertIn(berry, p.berrydex)

    def test_pet_user(self):
        """Does pet.user record user?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()

        self.assertEqual(p.user, u)

    def test_pet_pokemon(self):
        """Does pet.pokemon record pokemon?"""
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        p = Pet(
            id=1,
            nickname="testpet",
            user_id=1,
            poke_id=1
        )
        db.session.add(p)
        db.session.commit()

        self.assertEqual(p.pokemon, Pokemon.query.get_or_404(1))