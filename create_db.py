from app import create_app
from models import db, Utente, Prodotto, TagliaProdotto, ImmagineProdotto, Sale

def populate():
    # Crea alcuni prodotti di esempio
    p1 = Prodotto(nome='Runner', marca='Nike', modello='Air Zoom', categoria='running', prezzo=120.0, descrizione='Scarpe da running leggere.')
    p2 = Prodotto(nome='Classic', marca='Adidas', modello='Stan Smith', categoria='casual', prezzo=90.0, descrizione='Scarpe casual classiche.')
    db.session.add_all([p1, p2])
    db.session.commit()

    taglie = [38, 39, 40, 41, 42, 43]
    for p in [p1, p2]:
        for t in taglie:
            db.session.add(TagliaProdotto(prodotto_id=p.id, taglia=t, quantita=10))
        db.session.add(ImmagineProdotto(prodotto_id=p.id, url='https://martinvalen.com/27402-mv_large_default/uomo-coronate-suola-alta-sneakers-scarpe-bianco-nero.jpg'))
    db.session.commit()

    # crea admin
    admin = Utente(nome='Admin', cognome='User', email='admin@example.com')
    admin.set_password('admin')
    admin.ruolo = 'admin'
    db.session.add(admin)
    db.session.commit()

    # dati di vendita fittizi
    import random
    from datetime import datetime, timedelta

    categories = ['running', 'casual', 'eleganti']
    genders = ['uomo', 'donna']
    sources = ['Instagram', 'Newsletter', 'Facebook', 'Google']
    start_date = datetime.now() - timedelta(days=120)
    sales_entries = []
    for _ in range(100):
        delta = random.randint(0, 120)
        ts = start_date + timedelta(days=delta, hours=random.randint(0, 23))
        sales_entries.append(
            Sale(
                product_name=random.choice(['Runner', 'Classic']),
                category=random.choice(categories),
                price=random.uniform(70, 150),
                gender=random.choice(genders),
                timestamp=ts,
                source=random.choice(sources),
            )
        )
    db.session.add_all(sales_entries)
    db.session.commit()


def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate()
        print('Database creato e popolato')


if __name__ == '__main__':
    main()
