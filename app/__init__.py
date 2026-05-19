from flask import Flask
from app.config import Config

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="../templates"
    )

    app.config.from_object(Config)
    
    from app.routes.home import home_bp
    from app.routes.attendance import attendance_bp
    from app.routes.childsetup import children_bp
    from app.routes.household import household_bp
    from app.routes.management import management_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(children_bp)
    app.register_blueprint(household_bp)
    app.register_blueprint(management_bp)

    return app
