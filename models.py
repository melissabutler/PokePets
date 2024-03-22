from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

class Pokedex(db.Model):
    """Connection of a user to Seen Pokemon"""
    __tablename__ = "pokedex"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        primary_key=True
    )

    pokemon_seen_id = db.Column(
        db.Integer,
        db.ForeignKey('pokemons.id', ondelete="CASCADE"),
        primary_key=True
    )

class Berrydex(db.Model):
    """Connection of a pet to tried berry"""
    __tablename__= "berrydex"

    pet_id = db.Column(
        db.Integer,
        db.ForeignKey('pets.id', ondelete="CASCADE"),
        primary_key=True
    )

    berry_tried_id = db.Column(
        db.Integer,
        db.ForeignKey('berries.id', ondelete="CASCADE"),
        primary_key=True
    )


class UserBerry(db.Model):
    """Berries owned by user"""
    __tablename__ = "user_berries"

    id= db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )
    berry_id = db.Column(
        db.Integer,
        db.ForeignKey('berries.id'),
        nullable=False
    )
    
    user = db.relationship('User')
    berry = db.relationship('Berry')


class User(db.Model):
    """User"""
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
        )
    
    username = db.Column(
        db.String(20),
        unique=True,
        nullable=False
        )
    
    password = db.Column(
        db.Text,
        nullable=False
        )
    
    email = db.Column(
        db.String(50),
        unique=True,
        nullable=False
        )
    
    pets = db.relationship('Pet')

    berries = db.relationship('UserBerry')

    pokedex = db.relationship(
        "Pokemon",
        secondary="pokedex",
        primaryjoin=(Pokedex.user_id == id)
    )
    
    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"
    
    
    
    @classmethod
    def signup(cls, username, password, email):
        """Signs up new user with an encrypted password"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'. 
        If cannot find matching user or wrong password, return false."""
        
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            
        return False
    

class Pet(db.Model):
    """Pet"""

    __tablename__ = "pets"

    id= db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
        )
    nickname = db.Column(
        db.String(20),
        nullable=False,
        unique=True
        )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False,
    )
    poke_id = db.Column(
        db.Integer,
        db.ForeignKey('pokemons.id'),
        nullable=False
    )
    
    hunger = db.Column(
        db.Integer(),
        nullable=False,
        default=50
    )
    
    happiness = db.Column(
        db.Integer(),
        nullable=False,
        default=50
    )

    user = db.relationship('User', overlaps="pets")
    pokemon = db.relationship('Pokemon')

    berrydex = db.relationship(
        "Berry",
        secondary="berrydex",
        primaryjoin=(Berrydex.pet_id == id)
    )


    def __repr__(self):
        return f"<Pet #{self.id} {self.nickname}, Owner {self.user.username}>"


    def decrease_happiness(self, amt):
        """Decreases pet happiness by inputted amount"""
        pet = Pet.query.filter_by(id=self.id).first()

        if (pet.happiness - amt) < 0:
            pet.happiness = 0
            return pet
        else:
            pet.happiness -= amt
            return pet

    def increase_happiness(self, amt):
        """Increases pet happiness by inputted amount"""
        pet = Pet.query.filter_by(id=self.id).first()

        if (pet.happiness + amt) > 100:
            pet.happiness = 100
            return pet
        else:
            pet.happiness += amt
            return pet
   
    def decrease_hunger(self, amt):
        """Decreases pet hunger by inputted amount"""
        pet = Pet.query.filter_by(id=self.id).first()

        if (pet.hunger - amt) < 0:
            pet.hunger = 0
            return pet
        else:
            pet.hunger -= amt
            return pet

    def increase_hunger(self, amt):
        """Increases pet hunger by inputted amount"""
        pet = Pet.query.filter_by(id=self.id).first()

        if (pet.hunger + amt) > 100:
            pet.hunger = 100
            return pet
        else:
            pet.hunger += amt
            return pet
    

class Pokemon(db.Model):
    """Pokemon details"""
    __tablename__= "pokemons"
    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False
    )
    name = db.Column(
        db.String(),
        nullable=False
    )
    sprite_url = db.Column(
        db.String(),
        nullable=False
    )
    type = db.Column(
        db.String(),
        db.ForeignKey('types.name', ondelete="CASCADE"),
        nullable=False
    )
    def pokedex_id(self):
        return (f"{self.id:03d}")

class Type(db.Model):
    """Pokemon Type Details"""
    __tablename__ = "types"

    name= db.Column(
        db.String,
        primary_key=True,
        nullable=False
    )

    fav_berry_id= db.Column(
        db.Integer,
        db.ForeignKey('berries.id', ondelete="CASCADE"),
        nullable=False
    )
    least_fav_berry_id= db.Column(
        db.Integer,
        db.ForeignKey('berries.id', ondelete="CASCADE"),
        nullable=False
    )
    
class Berry(db.Model):
    """Berry details"""
    __tablename__ = "berries"
    id= db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True
    )
    name= db.Column(
        db.String,
        nullable=False
    )
    img_url = db.Column(
        db.String,
        nullable=False
    )


    
def connect_db(app):
    """Connect to database"""
    with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()
