from app import app
from flask import render_template, request, redirect, url_for, flash, jsonify
from .forms import PokemonCatcherForm, SignUpForm, SignInForm, AttackForm, UserAttackForm
from .models import User, Pokemon
import requests
from flask_login import login_user, logout_user, current_user
from random import randint

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
                response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{p_name}')
                if response.ok:
                    my_pokemon = {'pokemon_name': response.json()['forms'][0]['name'], 
                                'base_hp': response.json()['stats'][0]['base_stat'], 
                                'base_attack': response.json()['stats'][1]['base_stat'], 
                                'base_defense': response.json()['stats'][2]['base_stat'], 
                                'front_shiny_sprite': response.json()['sprites']['front_default'],
                                'other_sprite': response.json()['sprites']['other']['official-artwork']['front_default'],
                                'questionmark': url_for('static', filename = 'questionmark.jpg')}
                    return my_pokemon
                
            if pokemon_name.lower() == "random":
                a = randint(1, 1008)
                b = randint(10001, 10271)
                c = randint(1,1279)
                if c < 1009:
                    pokemon_index = a
                elif c > 1008:
                    pokemon_index = b
                the_pokemon = pokemon_info(pokemon_index)
            else:    
                the_pokemon = pokemon_info(pokemon_name.lower())
            
            if current_user.is_authenticated:
            
                form.pokemon_name.data = ''
                
                if the_pokemon:
                    pokemon_name = the_pokemon['pokemon_name'].capitalize()
                    base_hp = the_pokemon['base_hp']
                    base_attack = the_pokemon['base_attack']
                    base_defense = the_pokemon['base_defense']
                    if the_pokemon['front_shiny_sprite']:
                        front_shiny_sprite = the_pokemon['front_shiny_sprite']
                    elif the_pokemon['other_sprite']:
                        front_shiny_sprite = the_pokemon['other_sprite']
                    else:
                        front_shiny_sprite = url_for('static', filename = 'questionmark.jpg')
                    user_id = current_user.id
                    
                    dblist = Pokemon.query.filter_by(pokemon_name = pokemon_name).all()
                    if dblist == []:
                        if len(Pokemon.query.filter_by(user_id = current_user.id).all()) < 5:
                            pokemon = Pokemon(pokemon_name, base_hp, base_attack, base_defense, front_shiny_sprite, user_id)
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

@app.route('/battle', methods = ["GET", "POST"])
def battle():
    form = AttackForm()
    opponentform = UserAttackForm()
    pokemons = Pokemon.query.filter_by(user_id = current_user.id)
    
    if request.method == "POST":
        if opponentform.validate():
            opponent_user_name = opponentform.opponent.data
            if opponent_user_name.lower() == "random":
                opponents = User.query.all()
                randomindex = randint(0, len(opponents) - 1)
                opponent_user_name = opponents[randomindex].user_name
                while opponent_user_name == current_user.user_name:
                    randomindex = randint(0, len(opponents) - 1)
                    opponent_user_name = opponents[randomindex].user_name
                opp = User.query.filter_by(user_name = opponent_user_name).first()
                enemy_pokemons = Pokemon.query.join(User).filter(User.user_name == opponent_user_name).all()
                return render_template('battle.html', pokemons = pokemons, form = form, opponentform = opponentform, enemy_pokemons = enemy_pokemons, opponent_user_name = opponent_user_name, opp = opp)
            else:
                opp = User.query.filter_by(user_name = opponent_user_name).first()
                kills = opp.kills
                deaths = opp.deaths
                
                if opp:
                    enemy_pokemons = Pokemon.query.join(User).filter(User.user_name == opponent_user_name).all()
                    if form.validate():
                        attacker = form.attacker.data.capitalize()
                        defender = form.defender.data.capitalize()
                        
                        pokemon1 = Pokemon.query.filter_by(pokemon_name = attacker).first()
                        pokemon2 = Pokemon.query.filter_by(pokemon_name = defender).first()
                        return redirect(url_for('fight'))
                    return render_template('battle.html', pokemons = pokemons, form = form, opponentform = opponentform, enemy_pokemons = enemy_pokemons, opponent_user_name = opponent_user_name, opp = opp, kills = kills, deaths = deaths)
                else:
                    flash("User does not exist.")
                    return redirect(url_for('battle'))
    return render_template('battle.html', pokemons = pokemons, form = form, opponentform = opponentform)

@app.route('/battle/<opponent_user_name>/fight', methods = ["GET", "POST"])
def fight(opponent_user_name):
    form = AttackForm()
    opponentform = UserAttackForm()
    opponentform.opponent.data = opponent_user_name
    pokemons = Pokemon.query.filter_by(user_id = current_user.id).all()
    enemy_pokemons = Pokemon.query.join(User).filter(User.user_name == opponent_user_name).all()
    if request.method == "POST":
        # if opponentform.validate():
        #     redirect(url_for(battle))
        if form.validate():
            attacker = form.attacker.data.capitalize()
            defender = form.defender.data.capitalize()
            
            pokemon1 = Pokemon.query.filter_by(pokemon_name = attacker).first()
            pokemon2 = Pokemon.query.filter_by(pokemon_name = defender).first()
            if pokemon1 not in pokemons:
                form.attacker.data = ''
            if pokemon2 not in enemy_pokemons:
                form.defender.data = ''
            if pokemon2 in enemy_pokemons and pokemon1 in pokemons:
                pokemon1.attack(pokemon2)
                enemy_pokemons = Pokemon.query.join(User).filter(User.user_name == opponent_user_name).all()
                pokemons = Pokemon.query.filter_by(user_id = current_user.id).all()
                if not pokemon2:
                    form.defender.data = ''
                
                if enemy_pokemons:
                    if len(enemy_pokemons) > 1:
                        enemy_pokemons[randint(0, len(enemy_pokemons) - 1)].attack(pokemon1)
                        pokemons = Pokemon.query.filter_by(user_id = current_user.id).all()
                        if not pokemon1:
                            form.attacker.data = ''
                        
                    else:
                        enemy_pokemons[0].attack(pokemon1)
                        pokemons = Pokemon.query.filter_by(user_id = current_user.id).all()
                else:
                    flash("You won!")
                    return redirect(url_for('homepage'))
                if not pokemons:
                    flash("You lost!")
                    return redirect(url_for('homepage'))
            if not pokemon1:
                form.attacker.data = ''
            if not pokemon2:
                form.defender.data = ''
            opp = User.query.filter_by(user_name = opponent_user_name).first()
            return render_template('battle.html', pokemons = pokemons, form = form, opponentform = opponentform, enemy_pokemons = enemy_pokemons, opponent_user_name = opponent_user_name, opp = opp)
        return render_template('battle.html', pokemons = pokemons, form = form, opponentform = opponentform, enemy_pokemons = enemy_pokemons, opponent_user_name = opponent_user_name, opp = opp)
        
    return render_template('battle.html', pokemons = pokemons, form = form, opponentform = opponentform, enemy_pokemons = enemy_pokemons, opponent_user_name = opponent_user_name, opp = opp)

@app.route('/mypokemon/<pokemon_id>/delete')
def delete_pokemon(pokemon_id):
    pokemon = Pokemon.query.get(pokemon_id)
    if current_user.id != pokemon.user_id:
        flash("That Pokemon doesn't belong to you.")
        return redirect(url_for('mypokemon'))
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
    
@app.route('/pokemonapi')
def pokemonapi():
    pokemons = Pokemon.query.all()
    return jsonify([p.to_dict() for p in pokemons])