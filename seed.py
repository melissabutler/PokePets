from app import db, create_pokemon_db, create_berry_db, create_type_db, get_random_ids
from models import User, Pokemon, Pet, Berry, Type, UserBerry
from functions import berries, types

db.drop_all()
db.create_all()

create_berry_db(db, berries)
create_type_db(db, types)
create_pokemon_db(150, db)

user1 = User.signup(username="user1", password="password", email="test@test.com")
user2 = User.signup(username="user2", password="password", email="test2@test.com")


db.session.add_all([user1, user2])
db.session.commit()

pet1 = Pet(nickname="Bob", user_id=1, poke_id=1)
pet2= Pet(nickname="Bobby", user_id=2, poke_id=2)

db.session.add_all([pet1, pet2])
db.session.commit()

berry = UserBerry(user_id=1, berry_id=1)

berry2 = UserBerry(user_id=1, berry_id=1)

db.session.add_all([berry, berry2])
db.session.commit()