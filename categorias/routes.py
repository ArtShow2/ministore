# categorias/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection
import mysql.connector

categorias_bp = Blueprint('categorias', __name__, template_folder='templates')


@categorias_bp.route('/categorias')
def listar():
    conn = None
    cursor = None
    categorias = []

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM categorias ORDER BY nome')
        categorias = cursor.fetchall()

    except mysql.connector.Error as e:
        flash(f'Erro ao buscar categorias: {e}', 'danger')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('lista_categoria.html', categorias=categorias)


@categorias_bp.route('/categorias/nova', methods=['GET', 'POST'])
def nova():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form.get('descricao', '')

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = '''
                INSERT INTO categorias (nome, descricao)
                VALUES (%s, %s)
            '''

            cursor.execute(sql, (nome, descricao))
            conn.commit()

            flash('Categoria cadastrada com sucesso!', 'success')
            return redirect(url_for('categorias.listar'))

        except mysql.connector.Error as e:
            flash(f'Erro ao cadastrar categoria: {e}', 'danger')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('form_categoria.html', categoria=None)


@categorias_bp.route('/categorias/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form['nome']
            descricao = request.form.get('descricao', '')

            sql = '''
                UPDATE categorias
                SET nome=%s, descricao=%s
                WHERE id=%s
            '''

            cursor.execute(sql, (nome, descricao, id))
            conn.commit()

            flash('Categoria atualizada com sucesso!', 'success')
            return redirect(url_for('categorias.listar'))

        cursor.execute(
            'SELECT * FROM categorias WHERE id = %s',
            (id,)
        )

        categoria = cursor.fetchone()

        if not categoria:
            flash('Categoria não encontrada.', 'danger')
            return redirect(url_for('categorias.listar'))

    except mysql.connector.Error as e:
        flash(f'Erro: {e}', 'danger')
        return redirect(url_for('categorias.listar'))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('form_categoria.html', categoria=categoria)


@categorias_bp.route('/categorias/<int:id>/excluir', methods=['POST'])
def excluir(id):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'DELETE FROM categorias WHERE id = %s',
            (id,)
        )

        conn.commit()

        flash('Categoria excluída com sucesso!', 'success')

    except mysql.connector.Error as e:
        flash(f'Erro ao excluir categoria: {e}', 'danger')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('categorias.listar'))