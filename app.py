from flask import Flask
from routes.data_routes import data_bp
from routes.calc_routes import calc_bp

app = Flask(__name__)

# On enregistre les blueprints
app.register_blueprint(data_bp, url_prefix="/api/data")
app.register_blueprint(calc_bp, url_prefix="/api/calcul")

if __name__ == "__main__":
    app.run(debug=True)
