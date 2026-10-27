# dashboard/routes.py
from flask import Blueprint, render_template, flash
from database import get_connection
import mysql.connector

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')

@dashboard_bp.route('/')
def index():
    conn = None
    cursor = None
    totais = {
        'clientes': 0,
        'categorias': 0,
        'produtos': 0,
        'vendas': 0
    }
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clientes')
        totais['clientes'] = cursor.fetchone()[0]
        
    except mysql.connector.Error as e:
        flash(f'Erro ao carregar dashboard: {e}', 'danger')

    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        
    return render_template('index.html', totais=totais)