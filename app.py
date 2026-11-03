# app.py
from flask import Flask
from clientes.routes import clientes_bp
from dashboard.routes import dashboard_bp
from categorias.routes import categorias_bp
from produtos.routes import produtos_bp  # <-- Nova importação

app = Flask(__name__)
app.secret_key = 'ministore-secret-key-2026'

app.register_blueprint(clientes_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(produtos_bp)      # <-- Novo registro

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=80, debug=True)