from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(45), nullable = False, unique = True)
    email = db.Column(db.String(150), nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    first_name = db.Column(db.String(45), nullable = False)
    last_name = db.Column(db.String(45), nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default=datetime.utcnow())
    pokemon = db.relationship("Pokemon", backref='owner', lazy=True)
    kills = db.Column(db.Integer, default=0)
    deaths = db.Column(db.Integer, default=0)
    
    def __init__(self, user_name, email, password, first_name, last_name):
        self.user_name = user_name
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def save_changes(self):
        db.session.commit()

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    pokemon_name = db.Column(db.String, nullable = False, unique = True)
    base_hp = db.Column(db.Integer, nullable = False)
    base_attack = db.Column(db.Integer, nullable = False)
    base_defense = db.Column(db.Integer, nullable = False)
    front_shiny_sprite = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    def __init__(self, pokemon_name, base_hp, base_attack, base_defense, front_shiny_sprite, user_id):
        self.pokemon_name = pokemon_name
        self.base_hp = base_hp
        self.base_attack = base_attack
        self.base_defense = base_defense
        self.front_shiny_sprite = front_shiny_sprite
        self.user_id = user_id
        
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_pokemon(self):
        db.session.delete(self)
        db.session.commit()
        
    def attack(self, pokemon):
        if self.base_attack > pokemon.base_defense:
            pokemon.base_hp -= self.base_attack - pokemon.base_defense
            db.session.commit()
            if pokemon.base_hp < 1:
                owner = User.query.get(pokemon.user_id)
                owner.deaths += 1
                owner2 = User.query.get(self.user_id)
                owner2.kills += 1
                db.session.commit()
                pokemon.delete_pokemon()
                
    def to_dict(self):
        return {
            'id': self.id,
            'pokemon_name': self.pokemon_name,
            'front_shiny_sprite': self.front_shiny_sprite,
            'base_attack': self.base_attack,
            'base_defense': self.base_defense,
            'base_hp': self.base_hp
        }