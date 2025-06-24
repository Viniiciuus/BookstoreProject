from flask import Blueprint, render_template, redirect, url_for, session, flash
from flask_login import login_required
from models import Livro, db

# Cria um blueprint para o carrinho
carrinho_bp = Blueprint('carrinho', __name__)

@carrinho_bp.route('/adicionar_carrinho/<int:id>')
@login_required
def adicionar_carrinho(id):
    if 'carrinho' not in session:
        session['carrinho'] = []
    if id not in session['carrinho']:
        session['carrinho'].append(id)
    flash('Livro adicionado ao carrinho!', 'success')
    return redirect(url_for('index'))

@carrinho_bp.route('/carrinho')
@login_required
def carrinho():
    carrinho_ids = session.get('carrinho', [])
    livros = Livro.query.filter(Livro.id.in_(carrinho_ids)).all()
    total = sum(livro.preco for livro in livros)
    return render_template('carrinho.html', livros=livros, total=total)

@carrinho_bp.route('/limpar_carrinho')
@login_required
def limpar_carrinho():
    session.pop('carrinho', None)
    return redirect(url_for('carrinho.carrinho'))

@carrinho_bp.route('/finalizar')
@login_required
def finalizar():
    session.pop('carrinho', None)
    flash('Compra finalizada com sucesso!', 'success')
    return render_template('finalizar.html')