from app import create_app

app = create_app()
import logging

logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    app.run(debug=True)
