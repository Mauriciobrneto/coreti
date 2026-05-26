from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(username='admin').first()

    if not admin:

        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            tipo='admin',
            ativo=True
        )

        db.session.add(admin)
        db.session.commit()

        print('Usuário admin criado!')

if __name__ == '__main__':
    app.run(debug=True)