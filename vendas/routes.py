from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection
import mysql.connector

vendas_bp = Blueprint('vendas', __name__, template_folder='templates')

@vendas_bp.route('/vendas')
def listar():
    conn = None
    cursor = None
    vendas = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = '''
            SELECT v.*, c.nome AS cliente_nome 
            FROM vendas v
            JOIN clientes c ON v.id_cliente = c.id
            ORDER BY v.data_venda DESC
        '''
        cursor.execute(sql)
        vendas = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'Erro ao buscar vendas: {e}', 'danger')
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        
    return render_template('vendas_lista.html', vendas=vendas)

@vendas_bp.route('/vendas/nova', methods=['GET', 'POST'])
def nova():
    conn = None
    cursor = None
    clientes = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            id_cliente = request.form['id_cliente']
            total = request.form.get('total') or 0
            
            sql = 'INSERT INTO vendas (id_cliente, total) VALUES (%s, %s)'
            cursor.execute(sql, (id_cliente, total))
            conn.commit()
            nova_venda_id = cursor.lastrowid
            
            flash('Venda criada! Adicione os produtos abaixo.', 'success')
            return redirect(url_for('vendas.detalhes', id=nova_venda_id))
        
        cursor.execute('SELECT id, nome FROM clientes ORDER BY nome')
        clientes = cursor.fetchall()
        
    except mysql.connector.Error as e:
        flash(f'Erro ao registrar venda: {e}', 'danger')
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        
    return render_template('vendas_form.html', clientes=clientes)

@vendas_bp.route('/vendas/<int:id>', methods=['GET', 'POST'])
def detalhes(id):
    conn = None
    cursor = None
    venda = None
    itens = []
    produtos = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            id_produto = request.form['id_produto']
            quantidade = int(request.form['quantidade'])

            cursor.execute('SELECT preco FROM produtos WHERE id = %s', (id_produto,))
            produto_bd = cursor.fetchone()

            if produto_bd:
                preco_unitario = produto_bd['preco']
                cursor.execute('''
                    INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario)
                    VALUES (%s, %s, %s, %s)
                ''', (id, id_produto, quantidade, preco_unitario))

                cursor.execute('''
                    UPDATE vendas 
                    SET total = (SELECT COALESCE(SUM(quantidade * preco_unitario), 0) FROM itens_venda WHERE id_venda = %s)
                    WHERE id = %s
                ''', (id, id))
                conn.commit()
                flash('Item adicionado à venda!', 'success')
                return redirect(url_for('vendas.detalhes', id=id))

        cursor.execute('''
            SELECT v.*, c.nome AS cliente_nome 
            FROM vendas v
            JOIN clientes c ON v.id_cliente = c.id
            WHERE v.id = %s
        ''', (id,))
        venda = cursor.fetchone()

        if not venda:
            flash('Venda não encontrada.', 'danger')
            return redirect(url_for('vendas.listar'))

        cursor.execute('''
            SELECT iv.*, p.nome AS produto_nome, (iv.quantidade * iv.preco_unitario) AS subtotal
            FROM itens_venda iv
            JOIN produtos p ON iv.id_produto = p.id
            WHERE iv.id_venda = %s
        ''', (id,))
        itens = cursor.fetchall()

        cursor.execute('SELECT id, nome, preco FROM produtos ORDER BY nome')
        produtos = cursor.fetchall()

    except mysql.connector.Error as e:
        flash(f'Erro ao carregar detalhes da venda: {e}', 'danger')
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return render_template('vendas_detalhes.html', venda=venda, itens=itens, produtos=produtos)

@vendas_bp.route('/vendas/<int:id>/excluir', methods=['POST'])
def excluir(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM itens_venda WHERE id_venda = %s', (id,))
        cursor.execute('DELETE FROM vendas WHERE id = %s', (id,))
        conn.commit()
        flash('Venda excluída com sucesso!', 'success')
    except mysql.connector.Error as e:
        flash(f'Erro ao excluir venda: {e}', 'danger')
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    return redirect(url_for('vendas.listar'))
