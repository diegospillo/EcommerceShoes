from app import create_app
from models import db, Utente, Prodotto, TagliaProdotto, ImmagineProdotto

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


def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate()
        print('Database creato e popolato')


if __name__ == '__main__':
    main()
