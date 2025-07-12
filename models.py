from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy instance (will be bound to app in app.py)
db = SQLAlchemy()


class Utente(db.Model):
    __tablename__ = 'utenti'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    cognome = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(30))
    data_registrazione = db.Column(db.DateTime, default=datetime.utcnow)
    ruolo = db.Column(db.String(20), default='cliente')

    indirizzi = db.relationship('Indirizzo', backref='utente', lazy=True)
    carrello = db.relationship('Carrello', backref='utente', uselist=False)
    ordini = db.relationship('Ordine', backref='utente', lazy=True)
    recensioni = db.relationship('Recensione', backref='utente', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Indirizzo(db.Model):
    __tablename__ = 'indirizzi'
    id = db.Column(db.Integer, primary_key=True)
    utente_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    via = db.Column(db.String(120))
    civico = db.Column(db.String(10))
    cap = db.Column(db.String(10))
    citta = db.Column(db.String(64))
    provincia = db.Column(db.String(64))
    nazione = db.Column(db.String(64))


class Prodotto(db.Model):
    __tablename__ = 'prodotti'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120))
    marca = db.Column(db.String(64))
    modello = db.Column(db.String(64))
    categoria = db.Column(db.String(64))
    prezzo = db.Column(db.Float)
    descrizione = db.Column(db.Text)
    disponibilita = db.Column(db.Boolean, default=True)

    taglie = db.relationship('TagliaProdotto', backref='prodotto', lazy=True)
    immagini = db.relationship('ImmagineProdotto', backref='prodotto', lazy=True)
    recensioni = db.relationship('Recensione', backref='prodotto', lazy=True)


class TagliaProdotto(db.Model):
    __tablename__ = 'taglie_prodotto'
    id = db.Column(db.Integer, primary_key=True)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotti.id'), nullable=False)
    taglia = db.Column(db.Integer)
    quantita = db.Column(db.Integer)


class ImmagineProdotto(db.Model):
    __tablename__ = 'immagini_prodotto'
    id = db.Column(db.Integer, primary_key=True)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotti.id'), nullable=False)
    url = db.Column(db.String(250))


class Carrello(db.Model):
    __tablename__ = 'carrelli'
    id = db.Column(db.Integer, primary_key=True)
    utente_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)

    elementi = db.relationship('ElementoCarrello', backref='carrello', lazy=True)


class ElementoCarrello(db.Model):
    __tablename__ = 'elementi_carrello'
    id = db.Column(db.Integer, primary_key=True)
    carrello_id = db.Column(db.Integer, db.ForeignKey('carrelli.id'), nullable=False)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotti.id'), nullable=False)
    taglia = db.Column(db.Integer)
    quantita = db.Column(db.Integer)

    prodotto = db.relationship('Prodotto')


class Ordine(db.Model):
    __tablename__ = 'ordini'
    id = db.Column(db.Integer, primary_key=True)
    utente_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    indirizzo_id = db.Column(db.Integer, db.ForeignKey('indirizzi.id'), nullable=False)
    data_ordine = db.Column(db.DateTime, default=datetime.utcnow)
    stato = db.Column(db.String(64))
    totale = db.Column(db.Float)
    metodo_pagamento = db.Column(db.String(64))

    indirizzo = db.relationship('Indirizzo')
    prodotti = db.relationship('ProdottiOrdine', backref='ordine', lazy=True)


class ProdottiOrdine(db.Model):
    __tablename__ = 'prodotti_ordine'
    id = db.Column(db.Integer, primary_key=True)
    ordine_id = db.Column(db.Integer, db.ForeignKey('ordini.id'), nullable=False)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotti.id'), nullable=False)
    taglia = db.Column(db.Integer)
    quantita = db.Column(db.Integer)
    prezzo_unitario = db.Column(db.Float)

    prodotto = db.relationship('Prodotto')


class Recensione(db.Model):
    __tablename__ = 'recensioni'
    id = db.Column(db.Integer, primary_key=True)
    utente_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotti.id'), nullable=False)
    voto = db.Column(db.Integer)
    commento = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.utcnow)
