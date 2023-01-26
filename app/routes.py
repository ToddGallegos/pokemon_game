from app import app
from flask import render_template, request, redirect, url_for, flash
from .forms import PokemonCatcherForm, SignUpForm, SignInForm, AttackForm
from .models import User, Pokemon
import requests
from flask_login import login_user, logout_user, current_user

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/pokemon', methods=["GET", "POST"])
def pokemon():
    form = PokemonCatcherForm()
    if request.method == "POST":
        if form.validate():
            pokemon_name = form.pokemon_name.data
            
            def pokemon_info(p_name):
                response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{p_name.lower()}')
                if response.ok:
                    my_pokemon = {'pokemon_name': response.json()['forms'][0]['name'], 
                                'base_hp': response.json()['stats'][0]['base_stat'], 
                                'base_attack': response.json()['stats'][1]['base_stat'], 
                                'base_defense': response.json()['stats'][2]['base_stat'], 
                                'base_experience': response.json()['base_experience'], 
                                'ability_name': response.json()['abilities'][0]['ability']['name'], 
                                'front_shiny_sprite': response.json()['sprites']['front_default']}
                    return my_pokemon

            the_pokemon = pokemon_info(pokemon_name)
            
            
            if current_user.is_authenticated:
            
                form.pokemon_name.data = ''
                
                if the_pokemon:
                    pokemon_name = the_pokemon['pokemon_name'].capitalize()
                    base_hp = the_pokemon['base_hp']
                    base_attack = the_pokemon['base_attack']
                    base_defense = the_pokemon['base_defense']
                    base_experience = the_pokemon['base_experience']
                    ability_name = the_pokemon['ability_name'].capitalize()
                    front_shiny_sprite = the_pokemon['front_shiny_sprite']
                    user_id = current_user.id
                    
                    dblist = Pokemon.query.filter_by(pokemon_name = pokemon_name).all()
                    if dblist == []:
                        if len(Pokemon.query.filter_by(user_id = current_user.id).all()) < 5:
                            pokemon = Pokemon(pokemon_name, base_hp, base_attack, base_defense, base_experience, ability_name, front_shiny_sprite, user_id)
                            pokemon.save_to_db()
                        else:
                            flash("You already have the maximum number of Pokemon.")
                            return redirect(url_for('pokemon'))
                    else:
                        flash("That Pokemon already has a trainer.")
                        return redirect(url_for('pokemon'))
            return render_template('pokemon.html', form = form, the_pokemon = the_pokemon)
            
            
        
    elif request.method == "GET":
        return render_template('pokemon.html', form = form)
    
@app.route('/mypokemon')
def mypokemon():
    pokemons = Pokemon.query.filter_by(user_id = current_user.id)
    return render_template('mypokemon.html', pokemons = pokemons)

@app.route('/battle')
def battle():
    form = AttackForm()
    pokemons = Pokemon.query.filter_by(user_id = current_user.id)
    if request.method == "POST":
        if form.validate():
            attacker = form.attacker.data.capitalize()
            defender = form.defender.data.capitalize()
            
            pokemon1 = Pokemon.query.filter_by(pokemon_name = attacker)
            pokemon2 = Pokemon.query.filter_by(pokemon_name = defender)
        
    return render_template('battle.html', pokemons = pokemons, form = form)
    

@app.route('/mypokemon/<pokemon_id>/delete')
def delete_pokemon(pokemon_id):
    pokemon = Pokemon.query.get(pokemon_id)
    if current_user.id != pokemon.user_id:
        flash("That Pokemon doesn't belong to you.")
        redirect(url_for('mypokemon'))
    pokemon.delete_pokemon()
    flash("Pokemon deleted.")
    return redirect(url_for('mypokemon'))

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == "POST":
        if form.validate():
            user_name = form.user_name.data
            email = form.email.data
            password = form.password.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            
            user = User(user_name, email, password, first_name, last_name)
            user.save_to_db()
            
            flash("You created an account. Please log in.")
            return redirect(url_for('signin'))
        else:
            flash("Invalid input. Please try again.")
            return render_template('signup.html', form = form)
    
    elif request.method == "GET":
        return render_template('signup.html', form = form)

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    form = SignInForm()
    if request.method == "POST":
        if form.validate():
            user_name = form.user_name.data
            password = form.password.data
            
            user = User.query.filter_by(user_name = user_name).first()
            
            if user:
                if user.password == password:
                    login_user(user)
                    flash("Successful Login. Welcome back!")
                    return redirect(url_for('homepage'))
                else:
                    flash("Incorrect Username or Password.")
                    return redirect(url_for('signin'))
            else:
                flash("User does not exist")
                return redirect(url_for('signin'))
            
        return render_template('signin.html', form = form)
    
    elif request.method == 'GET':
        return render_template('signin.html', form = form)
    
@app.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out.")
    return redirect(url_for('signin'))

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    user = current_user
    form = SignUpForm()
    if request.method == "POST":
        if form.validate():
            user_name = form.user_name.data
            email = form.email.data
            password = form.password.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            user.user_name = user_name
            user.email = email
            user.password = password
            user.first_name = first_name
            user.last_name = last_name
            user.save_changes()
            
            flash("Successfully updated profile.")
            return redirect(url_for('profile'))
        else:
            flash("Invalid input. Please try again.")
            return render_template('profile.html', form = form)
    
    elif request.method == "GET":
        return render_template('profile.html', form = form)