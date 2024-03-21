import os

from flask import Flask, render_template, redirect, flash, session, g
import random
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from flask_debugtoolbar import DebugToolbarExtension


from models import db, connect_db, User, Pokemon, Pet, Type, Berry, UserBerry
from forms import UserAddForm, LoginForm, UserEditForm, PetForm, ReleasePet, ForageForm, DeleteUser
from functions import create_pokemon_db, get_random_ids, create_type_db, create_berry_db, berries, types, roll_dice, forage, play_phrases

CURR_USER_KEY = "curr_user"

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///pokepets'))

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "password")

debug = DebugToolbarExtension(app)
connect_db(app)



BASE_URL = 'https://pokeapi.co/api/v2/pokemon/'

# ###################### login/logout setup

@app.before_request
def add_user_to_g():
    """IF we're logged in, add current user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """ Log out user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if len(Type.query.all()) == 0:
    create_type_db(db, types)


if len(Berry.query.all()) == 0:
    create_berry_db(db, berries)

if len(Pokemon.query.all()) == 0:
    create_pokemon_db(150, db)



############# SETUP ROUTES, login/logout/signup ##########################
    
@app.route('/')
def home():
    """Shows home page if logged in or signup page if not logged in"""
    if g.user:
        return render_template('home.html')
    else:
        return render_template('home-anon.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handles user signup
    
    Create new user and add to DB, redirect to home page
    
    If form not valid, re-present form.
    
    If username already in use, flash error and re-present form."""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "DANGER")
            return render_template('users/signup.html', form=form)
        
        do_login(user)

        return redirect('/')

    else:
        return render_template('users/signup.html', form=form)
    
@app.route('/login', methods=["GET", "POST"])
def login():
    """ Handles user login"""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(username=form.username.data, password=form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back {user.username}!", "SUCCESS")
            return redirect('/')
        flash("Invalid credentials.", "DANGER")

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handles user logout"""
    do_logout()
    flash("Logged out", "SUCCESS")

    return redirect('/login')

########################## USER ROUTES #######################
@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    """Shows user's profile details"""
    
    user = User.query.get_or_404(user_id)

    return render_template('users/profile.html', user=user)

@app.route('/users/details')
def show_user_details():
    """Shows a user's private details and allows for edit. Unavailable if not logged in user."""
    user = User.query.get_or_404(g.user.id)
    if not g.user:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')

    return render_template('users/details.html', user=user)

@app.route('/users/edit', methods=['GET', 'POST'])
def edit_user():
    """ If logged in as user, edit that user's details"""
    if not g.user:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    form = UserEditForm(obj=g.user)
    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.email = form.email.data

        db.session.add(g.user)
        db.session.commit()
        flash("User successfully edited.", "SUCCESS")
        return redirect(f'/users/{g.user.id}')
    return render_template('users/edit.html', form=form)


@app.route('/users/delete', methods=['GET', 'POST'])
def delete_user():
    """ If logged in as user, delete that user"""
    if not g.user:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    form = DeleteUser()
    if form.validate_on_submit():
        do_logout()
        flash(f"Account deleted.", "DANGER")
        db.session.delete(g.user)
        db.session.commit()
        return redirect('/signup')

    return render_template('/users/delete.html', form=form)



################### ADOPTION ROUTES ##################

@app.route('/pets/adopt')
def adoption_center():
    """Shows adoptable pets"""
    if not g.user:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    ids = get_random_ids(3)
    pokemon = Pokemon.query.filter(Pokemon.id.in_(ids))
    return render_template('adoption.html', pokemon=pokemon)

@app.route('/pets/adopt/<int:poke_id>', methods=['GET', 'POST'])
def adopt_pet(poke_id):
    """Shows adoption form for a particular pet"""
    if not g.user:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    poke = Pokemon.query.get_or_404(poke_id)
    form = PetForm()
    pets = Pet.query.all()
    nicknames = []

    if len(g.user.pets) == 12:
        flash("Max amount of pets reached. In order to adopt a new pet, you must release one of your old pets.", "DANGER")
        return redirect(f'/users/{g.user.id}')

    for pet in pets:
        nicknames.append(pet.nickname)

    if form.validate_on_submit():
        if form.nickname.data in nicknames:
            flash(f'Nickname "{form.nickname.data} already taken, please pick another!', "DANGER")
            return render_template('pets/adopt.html', pokemon=poke, form=form)
        else:
            pet = Pet(
                nickname = form.nickname.data,
                user_id= g.user.id,
                poke_id = poke.id
                )
            if (poke not in g.user.pokedex):
                g.user.pokedex.append(poke)
                db.session.commit()
            db.session.add(pet)
            db.session.commit()

            flash(f"{pet.nickname} the {poke.name[0].upper()}{poke.name[1:]} has been adopted! Congrats!", "SUCCESS")

            return redirect(f'/users/{g.user.id}')
    
    else: 
        return render_template('pets/adopt.html', pokemon=poke, form=form)
    

###### PET ROUTES ##########
@app.route('/pets/<int:pet_id>')
def show_pet(pet_id):
    """ Shows a pet's details"""
    pet = Pet.query.get_or_404(pet_id)
    type = Type.query.get_or_404(pet.pokemon.type)

    return render_template('pets/details.html', pet=pet, type=type)

@app.route('/pets/<int:pet_id>/release-check', methods=["GET", "POST"])
def release_pet_check(pet_id):
    """Show release form"""
    pet = Pet.query.get_or_404(pet_id)
    if not g.user or pet.user_id is not g.user.id:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    form = ReleasePet()
    if form.validate_on_submit():
        return redirect(f'/pets/{pet.id}/release')
    return render_template('pets/release.html', form=form, pet=pet)

@app.route('/pets/<int:pet_id>/release', methods=["POST"])
def release_pet(pet_id):
    """Delete Pet"""
    pet= Pet.query.get_or_404(pet_id)
    if not g.user or pet.user_id is not g.user.id:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')

    flash(f"{pet.nickname} has been released.")
    db.session.delete(pet)
    db.session.commit()

    return redirect(f'/users/{g.user.id}')

@app.route('/feed_pet_apple/<int:pet_id>/', methods=['POST'])
def feed_pet(pet_id):
    """Feeds pet an apple"""
    pet = Pet.query.get_or_404(pet_id)
    if not g.user or pet.user_id is not g.user.id:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    

    if pet.hunger == 100:
        flash(f"{pet.nickname} isn't hungry right now!", "DANGER")
    
    else:
        flash(f"{pet.nickname} crunches on the apple!", "SUCCESS")
   
        pet.increase_hunger(10)
        pet.decrease_happiness(5)
    
        db.session.commit()


    return redirect(f'/pets/{pet.id}')
@app.route('/feed_pet_berry/<int:pet_id>/<int:item_id>', methods=["POST"])
def feed_pet_berry(pet_id, item_id):
    """Feeds pet a berry"""
    pet = Pet.query.get_or_404(pet_id)
    if not g.user or pet.user_id is not g.user.id:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    
    item = UserBerry.query.get_or_404(item_id)
    berry = Berry.query.get_or_404(item.berry_id)

    type = Type.query.get_or_404(pet.pokemon.type)

    if pet.hunger == 100:
        flash(f"{pet.nickname} isn't hungry!")
        return redirect(f'/pets/{pet.id}')

    if item.berry_id == type.fav_berry_id:
        pet.increase_hunger(50)
        pet.increase_happiness(50)
        if berry not in pet.berrydex:
            pet.berrydex.append(berry)
            db.session.commit()
        db.session.delete(item)
        flash(f"{pet.nickname} gobbles up the berry! Delicious!", "SUCCESS")
       


    elif item.berry_id == type.least_fav_berry_id:
        flash(f"{pet.nickname} spits out the berry! Yuck!", "DANGER")
        pet.decrease_happiness(20)
        if berry not in pet.berrydex:
            pet.berrydex.append(berry)
            db.session.commit()

    else:
        flash(f"{pet.nickname} eats the berry. Yum!", "SUCCESS")
        pet.increase_hunger(15)
        db.session.delete(item)

    db.session.commit()
        

    return redirect(f'/pets/{pet.id}')


@app.route('/play_with_pet/<int:pet_id>', methods=['POST'])
def play_with_pet(pet_id):
    """Alters pet stats based on play action """
    pet = Pet.query.get_or_404(pet_id)
    if not g.user or pet.user_id is not g.user.id:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    

    if pet.happiness == 100:
        flash(f'{pet.nickname} is as happy as can be!', "SUCCESS")

    if pet.hunger <= 30:
        flash(f"{pet.nickname} is too hungry to play!", "DANGER")
        return redirect(f'/pets/{pet.id}')
    pet.increase_happiness(10)
    pet.decrease_hunger(10)
    flash(f"{pet.nickname}" + f"{random.choice(play_phrases)}", "SUCCESS" )

    db.session.add(pet)
    db.session.commit()

    return redirect(f'/pets/{pet.id}')
    

#########
@app.route('/foraging')
def show_forage():
    """Show form for picking a pet to go foraging"""
    if not g.user:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
   
    return render_template('forage.html', user=g.user)

@app.route('/foraging/<int:pet_id>', methods=['GET','POST'])
def go_forage(pet_id):
    """Sends chosen pet foraging"""

    pet = Pet.query.get_or_404(pet_id)
   
    if not g.user or pet.user_id is not g.user.id:
        flash("Access unauthorized.", "DANGER")
        return redirect('/')
    
    if pet.hunger <= 10:
        flash(f"{pet.nickname} is too tired to go foraging!", "DANGER")
        pet.decrease_happiness(5)
        return redirect('/foraging')


    result = forage()

    if result:
        flash(f"{pet.nickname} found a berry!", "SUCCESS")
        new_berry = UserBerry(
            user_id= g.user.id,
            berry_id = result.id
        )
        db.session.add(new_berry)
        flash(f"{result.name} berry added to inventory", "SUCCESS")
        pet.increase_happiness(50)
        db.session.commit()
    else:
        flash(f"{pet.nickname} didn't find anything!", "DANGER")
        pet.decrease_happiness(10)


    pet.decrease_hunger(30)
    db.session.commit()


    return redirect(f'/foraging')


@app.route('/pokedex')
def pokedex():
    """Shows list of all potential pets"""
    pokemon = Pokemon.query.all()

    return render_template('pokedex.html', pokemon=pokemon)
    

@app.route('/pets')
def random_pets():
    """ Show a random assortment of existing user pets"""
    pets = Pet.query.limit(15).all()
    return render_template('pets/random.html', pets=pets)