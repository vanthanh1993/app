from app import create_app, db
from flask_bcrypt import Bcrypt

from app.models import *

app = create_app()
bcrypt = Bcrypt(app)

with app.app_context():
    print("🔄 Reset database...")

    db.drop_all()
    db.create_all()

    print("✅ Tables created!")

    # 👤 tạo admin
    password = bcrypt.generate_password_hash("123456").decode("utf-8")

    admin = User(
        username="admin",
        password_hash=password,
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()

    print("👤 Admin created!")