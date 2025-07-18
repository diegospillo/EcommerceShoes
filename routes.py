from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Utente, Prodotto, TagliaProdotto, ImmagineProdotto, Carrello, ElementoCarrello, Indirizzo, Ordine, ProdottiOrdine, Recensione, Sale
from datetime import datetime
from dateutil.relativedelta import relativedelta

bp = Blueprint('main', __name__)


def get_or_create_cart(user_id):
    cart = Carrello.query.filter_by(utente_id=user_id).first()
    if not cart:
        cart = Carrello(utente_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart


@bp.route('/')
def index():
    categoria = request.args.get('categoria')
    query = Prodotto.query
    if categoria:
        query = query.filter_by(categoria=categoria)
    prodotti = query.all()
    return render_template('index.html', prodotti=prodotti)


@bp.route('/product/<int:prod_id>')
def product_detail(prod_id):
    prodotto = Prodotto.query.get_or_404(prod_id)
    return render_template('product_detail.html', prodotto=prodotto)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        if Utente.query.filter_by(email=email).first():
            flash('Email già registrata')
            return redirect(url_for('main.register'))
        utente = Utente(
            nome=request.form['nome'],
            cognome=request.form['cognome'],
            email=email,
            telefono=request.form.get('telefono'),
            gender=request.form['gender'],
        )
        utente.set_password(request.form['password'])
        db.session.add(utente)
        db.session.commit()
        flash('Registrazione completata, effettua il login')
        return redirect(url_for('main.login'))
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Utente.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user'] = user.email
            session['ruolo'] = user.ruolo
            session['gender'] = user.gender
            session['source'] = "Google"
            flash('Login effettuato')
            return redirect(url_for('main.index'))
        flash('Credenziali errate')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    session.pop('ruolo', None)
    session.pop('gender', None)
    session.pop('source', None)
    flash('Logout effettuato')
    return redirect(url_for('main.index'))


@bp.route('/cart')
def cart_view():
    if 'user_id' not in session:
        flash('Devi effettuare il login')
        return redirect(url_for('main.login'))
    cart = get_or_create_cart(session['user_id'])
    totale = sum(e.prodotto.prezzo * e.quantita for e in cart.elementi)
    return render_template('cart.html', carrello=cart, totale=totale)



@bp.route('/cart/add/<int:prod_id>', methods=['POST'])
def cart_add(prod_id):
    if 'user_id' not in session:
        flash('Devi effettuare il login')
        return redirect(url_for('main.login'))
    taglia = request.form.get('taglia', type=int)
    quantita = request.form.get('quantita', type=int, default=1)
    cart = get_or_create_cart(session['user_id'])
    elemento = ElementoCarrello.query.filter_by(carrello_id=cart.id, prodotto_id=prod_id, taglia=taglia).first()
    if elemento:
        elemento.quantita += quantita
    else:
        elemento = ElementoCarrello(carrello_id=cart.id, prodotto_id=prod_id, taglia=taglia, quantita=quantita)
        db.session.add(elemento)
    db.session.commit()
    flash('Prodotto aggiunto al carrello')
    return redirect(url_for('main.cart_view'))


@bp.route('/cart/remove/<int:elem_id>')
def cart_remove(elem_id):
    elemento = ElementoCarrello.query.get_or_404(elem_id)
    db.session.delete(elemento)
    db.session.commit()
    flash('Elemento rimosso')
    return redirect(url_for('main.cart_view'))


@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Devi effettuare il login')
        return redirect(url_for('main.login'))
    cart = get_or_create_cart(session['user_id'])
    if request.method == 'POST':
        indirizzo = Indirizzo(
            utente_id=session['user_id'],
            via=request.form['via'],
            civico=request.form['civico'],
            cap=request.form['cap'],
            citta=request.form['citta'],
            provincia=request.form['provincia'],
            nazione=request.form['nazione'],
        )
        db.session.add(indirizzo)
        totale = sum(e.prodotto.prezzo * e.quantita for e in cart.elementi)
        ordine = Ordine(
            utente_id=session['user_id'],
            indirizzo=indirizzo,
            stato='in elaborazione',
            totale=totale,
            metodo_pagamento=request.form['metodo_pagamento'],
        )
        db.session.add(ordine)
        for e in cart.elementi:
            po = ProdottiOrdine(
                ordine=ordine,
                prodotto_id=e.prodotto_id,
                taglia=e.taglia,
                quantita=e.quantita,
                prezzo_unitario=e.prodotto.prezzo,
            )
            for _ in range(e.quantita):
                s = Sale(
                    product_name=e.prodotto.nome,
                    category=e.prodotto.categoria,
                    price=e.prodotto.prezzo,
                    gender=session['gender'],
                    source=session['source'],
                )
                db.session.add(s)
            db.session.add(po)
        ElementoCarrello.query.filter_by(carrello_id=cart.id).delete()
        db.session.commit()
        flash('Ordine completato (pagamento simulato)')
        return redirect(url_for('main.index'))
    return render_template('checkout.html', carrello=cart)


@bp.route('/review/<int:prod_id>', methods=['POST'])
def add_review(prod_id):
    if 'user_id' not in session:
        flash('Devi effettuare il login')
        return redirect(url_for('main.login'))
    recensione = Recensione(
        utente_id=session['user_id'],
        prodotto_id=prod_id,
        voto=request.form['voto'],
        commento=request.form['commento'],
    )
    db.session.add(recensione)
    db.session.commit()
    flash('Recensione aggiunta')
    return redirect(url_for('main.product_detail', prod_id=prod_id))


@bp.route('/admin')
def admin_dashboard():
    if 'user' not in session or session['ruolo'] != "admin":
        flash('Devi effettuare il login')
        return redirect(url_for('main.login'))

    months = [m[0].strftime('%Y-%m') for m in db.session.query(db.func.date_trunc('month', Sale.timestamp)).distinct().all()]
    categories = [c[0] for c in db.session.query(Sale.category).distinct().all()]
    genders = [g[0] for g in db.session.query(Sale.gender).distinct().all()]

    return render_template('admin_dashboard.html', months=months, categories=categories, genders=genders)


@bp.route('/admin/data')
def admin_data():
    if 'user' not in session:
        return {'error': 'unauthorized'}, 401

    month = request.args.get('month')
    category = request.args.get('category')
    gender = request.args.get('gender')

    filters = []
    if month:
        start = datetime.strptime(month, '%Y-%m')
        end = start.replace(day=1) + relativedelta(months=1)
        filters.append(Sale.timestamp >= start)
        filters.append(Sale.timestamp < end)
    if category:
        filters.append(Sale.category == category)
    if gender:
        filters.append(Sale.gender == gender)

    def query_group(field):
        q = db.session.query(field, db.func.count(Sale.id)).filter(*filters).group_by(field).all()
        labels = [str(r[0]) for r in q]
        data = [r[1] for r in q]
        return {'labels': labels, 'data': data}

    category_data = query_group(Sale.category)
    gender_data = query_group(Sale.gender)

    month_q = db.session.query(db.func.to_char(db.func.date_trunc('month', Sale.timestamp), 'YYYY-MM'), db.func.count(Sale.id)).filter(*filters).group_by(db.func.date_trunc('month', Sale.timestamp)).order_by(db.func.date_trunc('month', Sale.timestamp)).all()
    monthly = {'labels': [r[0] for r in month_q], 'data': [r[1] for r in month_q]}

    source_data = query_group(Sale.source)

    heat_q = db.session.query(db.func.extract('dow', Sale.timestamp).label('d'),
                              db.func.extract('hour', Sale.timestamp).label('h'),
                              db.func.count(Sale.id)).filter(*filters).group_by('d', 'h').all()
    heatmap = [{'dow': int(r[0]), 'hour': int(r[1]), 'count': r[2]} for r in heat_q]

    return {
        'category': category_data,
        'gender': gender_data,
        'monthly': monthly,
        'source': source_data,
        'heatmap': heatmap,
    }
