from flask import Flask
from config import Config
from datetime import timedelta
from app.extensions import db, login_manager, bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "auth.login"

    # ===== template filters =====
    @app.template_filter('vn_time')
    def vn_time(dt):
        if not dt:
            return ""
        return (dt + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M")

    @app.template_filter('date_vn')
    def date_vn(dt):
        if not dt:
            return ""
        return (dt + timedelta(hours=7)).strftime("%d/%m/%Y")

    @app.template_filter('time_vn')
    def time_vn(dt):
        if not dt:
            return ""
        return (dt + timedelta(hours=7)).strftime("%H:%M")

    # ===== models =====
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ===== register blueprints =====
    from app.routes.dashboard import dashboard_bp
    from app.routes.auth import auth_bp
    from app.routes.purchase import purchase_bp
    from app.routes.sale import sale_bp
    from app.routes.supplier import supplier_bp
    from app.routes.customer import customer_bp
    from app.routes.customer_detail import customer_detail_bp

    app.register_blueprint(customer_bp)
    app.register_blueprint(customer_detail_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(sale_bp)
    app.register_blueprint(supplier_bp)

    return app