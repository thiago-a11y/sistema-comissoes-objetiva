import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, date
import json

app = Flask(__name__, static_folder='static')
CORS(app)
app.config['SECRET_KEY'] = 'sistema-comissoes-objetiva-2024'

# Configuração do banco de dados SQLite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'comissoes.db')

def get_db_connection():
    """Conecta ao banco SQLite"""
    try:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def init_db():
    """Inicializa as tabelas do banco de dados"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Tabela de usuários
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL DEFAULT 'vendedor',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de vendedores
        cur.execute('''
            CREATE TABLE IF NOT EXISTS vendedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefone TEXT,
                data_admissao DATE,
                observacoes TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de oportunidades
        cur.execute('''
            CREATE TABLE IF NOT EXISTS oportunidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                vendedor TEXT NOT NULL,
                tipo_conta TEXT NOT NULL,
                mensalidade REAL DEFAULT 0,
                servicos REAL DEFAULT 0,
                valor_total REAL NOT NULL,
                valor_liquido REAL NOT NULL,
                comissao REAL NOT NULL,
                data_fechamento DATE,
                descricao TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de parcelas
        cur.execute('''
            CREATE TABLE IF NOT EXISTS parcelas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oportunidade_id INTEGER,
                cliente TEXT NOT NULL,
                vendedor TEXT NOT NULL,
                numero TEXT NOT NULL,
                valor REAL NOT NULL,
                valor_liquido REAL NOT NULL,
                vencimento DATE NOT NULL,
                pagamento_comissao DATE NOT NULL,
                comissao REAL NOT NULL,
                observacoes TEXT,
                primeira_mensalidade BOOLEAN DEFAULT 0,
                recebida_pelo_cliente BOOLEAN DEFAULT 0,
                comissao_paga BOOLEAN DEFAULT 0,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (oportunidade_id) REFERENCES oportunidades (id)
            )
        ''')
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")
        return False
    finally:
        conn.close()

# Inicializar banco na inicialização da aplicação
init_db()

def format_date_br(date_str):
    """Converte data para formato brasileiro DD/MM/YYYY"""
    if not date_str:
        return ''
    try:
        if isinstance(date_str, str):
            # Se já está no formato ISO, converte
            if '-' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', ''))
                return date_obj.strftime('%d/%m/%Y')
            return date_str
        elif isinstance(date_str, (date, datetime)):
            return date_str.strftime('%d/%m/%Y')
        return str(date_str)
    except:
        return str(date_str)

def parse_date_br(date_str):
    """Converte data do formato brasileiro DD/MM/YYYY para ISO"""
    if not date_str:
        return None
    try:
        if '/' in date_str:
            # Formato brasileiro DD/MM/YYYY
            day, month, year = date_str.split('/')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return date_str
    except:
        return None

# Rota principal
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Rota de login
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        senha = data.get('senha', '')
        
        # Verificar usuários fixos primeiro
        usuarios_fixos = {
            'thiago@objetivasolucao.com.br': {
                'senha': 'vendas123',
                'nome': 'Thiago Teles Xavier',
                'tipo': 'master'
            },
            'dalzia.reis@objetivasolucao.com.br': {
                'senha': 'dalzia123',
                'nome': 'Dalzia Reis',
                'tipo': 'visualizador'
            }
        }
        
        if email in usuarios_fixos and usuarios_fixos[email]['senha'] == senha:
            return jsonify({
                'success': True,
                'user': {
                    'email': email,
                    'nome': usuarios_fixos[email]['nome'],
                    'tipo': usuarios_fixos[email]['tipo']
                }
            })
        
        # Verificar vendedores cadastrados
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM vendedores WHERE email = ?', (email,))
            vendedor = cur.fetchone()
            conn.close()
            
            if vendedor and senha == 'vendas123':
                return jsonify({
                    'success': True,
                    'user': {
                        'email': email,
                        'nome': vendedor['nome'],
                        'tipo': 'vendedor'
                    }
                })
        
        return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Rotas para vendedores
@app.route('/api/vendedores', methods=['GET'])
def get_vendedores():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
            
        cur = conn.cursor()
        cur.execute('SELECT * FROM vendedores ORDER BY nome')
        vendedores = cur.fetchall()
        conn.close()
        
        result = []
        for v in vendedores:
            result.append({
                'id': str(v['id']),
                'nome': v['nome'],
                'email': v['email'],
                'telefone': v['telefone'] or '',
                'dataAdmissao': format_date_br(v['data_admissao']),
                'observacoes': v['observacoes'] or '',
                'dataCadastro': format_date_br(v['data_cadastro'])
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vendedores', methods=['POST'])
def create_vendedor():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cur = conn.cursor()
        data_admissao = parse_date_br(data.get('dataAdmissao', ''))
        
        cur.execute('''
            INSERT INTO vendedores (nome, email, telefone, data_admissao, observacoes)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['nome'],
            data['email'],
            data.get('telefone', ''),
            data_admissao,
            data.get('observacoes', '')
        ))
        
        vendedor_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': str(vendedor_id),
            'nome': data['nome'],
            'email': data['email'],
            'telefone': data.get('telefone', ''),
            'dataAdmissao': format_date_br(data_admissao),
            'observacoes': data.get('observacoes', ''),
            'dataCadastro': format_date_br(datetime.now())
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vendedores/<int:vendedor_id>', methods=['DELETE'])
def delete_vendedor(vendedor_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cur = conn.cursor()
        cur.execute('DELETE FROM vendedores WHERE id = ?', (vendedor_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rotas para oportunidades
@app.route('/api/oportunidades', methods=['GET'])
def get_oportunidades():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
            
        cur = conn.cursor()
        cur.execute('SELECT * FROM oportunidades ORDER BY data_cadastro DESC')
        oportunidades = cur.fetchall()
        conn.close()
        
        result = []
        for o in oportunidades:
            result.append({
                'id': str(o['id']),
                'cliente': o['cliente'],
                'vendedor': o['vendedor'],
                'tipoConta': o['tipo_conta'],
                'mensalidade': o['mensalidade'],
                'servicos': o['servicos'],
                'valorTotal': o['valor_total'],
                'valorLiquido': o['valor_liquido'],
                'comissao': o['comissao'],
                'dataFechamento': format_date_br(o['data_fechamento']),
                'descricao': o['descricao'] or '',
                'dataCadastro': format_date_br(o['data_cadastro'])
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/oportunidades', methods=['POST'])
def create_oportunidade():
    try:
        data = request.get_json()
        
        # Calcular valores com 15% de desconto
        valor_total = float(data['valorTotal'])
        valor_liquido = valor_total * 0.85  # 15% de desconto
        comissao = valor_liquido * 0.10  # 10% de comissão sobre valor líquido
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cur = conn.cursor()
        data_fechamento = parse_date_br(data.get('dataFechamento', ''))
        
        cur.execute('''
            INSERT INTO oportunidades (cliente, vendedor, tipo_conta, mensalidade, servicos, 
                                     valor_total, valor_liquido, comissao, data_fechamento, descricao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['cliente'],
            data['vendedor'],
            data['tipoConta'],
            float(data.get('mensalidade', 0)),
            float(data.get('servicos', 0)),
            valor_total,
            valor_liquido,
            comissao,
            data_fechamento,
            data.get('descricao', '')
        ))
        
        oportunidade_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': str(oportunidade_id),
            'cliente': data['cliente'],
            'vendedor': data['vendedor'],
            'tipoConta': data['tipoConta'],
            'mensalidade': float(data.get('mensalidade', 0)),
            'servicos': float(data.get('servicos', 0)),
            'valorTotal': valor_total,
            'valorLiquido': valor_liquido,
            'comissao': comissao,
            'dataFechamento': format_date_br(data_fechamento),
            'descricao': data.get('descricao', ''),
            'dataCadastro': format_date_br(datetime.now())
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/oportunidades/<int:oportunidade_id>', methods=['DELETE'])
def delete_oportunidade(oportunidade_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cur = conn.cursor()
        # Deletar parcelas relacionadas primeiro
        cur.execute('DELETE FROM parcelas WHERE oportunidade_id = ?', (oportunidade_id,))
        # Deletar oportunidade
        cur.execute('DELETE FROM oportunidades WHERE id = ?', (oportunidade_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rotas para parcelas
@app.route('/api/parcelas', methods=['GET'])
def get_parcelas():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
            
        cur = conn.cursor()
        cur.execute('SELECT * FROM parcelas ORDER BY vencimento')
        parcelas = cur.fetchall()
        conn.close()
        
        result = []
        for p in parcelas:
            result.append({
                'id': str(p['id']),
                'oportunidadeId': str(p['oportunidade_id']) if p['oportunidade_id'] else '',
                'cliente': p['cliente'],
                'vendedor': p['vendedor'],
                'numero': p['numero'],
                'valor': p['valor'],
                'valorLiquido': p['valor_liquido'],
                'vencimento': format_date_br(p['vencimento']),
                'pagamentoComissao': format_date_br(p['pagamento_comissao']),
                'comissao': p['comissao'],
                'observacoes': p['observacoes'] or '',
                'primeiraMensalidade': bool(p['primeira_mensalidade']),
                'recebidaPeloCliente': bool(p['recebida_pelo_cliente']),
                'comissaoPaga': bool(p['comissao_paga']),
                'dataCadastro': format_date_br(p['data_cadastro'])
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas', methods=['POST'])
def create_parcela():
    try:
        data = request.get_json()
        
        # Calcular valores com 15% de desconto
        valor = float(data['valor'])
        valor_liquido = valor * 0.85  # 15% de desconto
        comissao = valor_liquido * 0.10  # 10% de comissão sobre valor líquido
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cur = conn.cursor()
        vencimento = parse_date_br(data.get('vencimento', ''))
        pagamento_comissao = parse_date_br(data.get('pagamentoComissao', ''))
        
        cur.execute('''
            INSERT INTO parcelas (oportunidade_id, cliente, vendedor, numero, valor, valor_liquido,
                                vencimento, pagamento_comissao, comissao, observacoes, primeira_mensalidade,
                                recebida_pelo_cliente, comissao_paga)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(data['oportunidadeId']) if data.get('oportunidadeId') else None,
            data['cliente'],
            data['vendedor'],
            data['numero'],
            valor,
            valor_liquido,
            vencimento,
            pagamento_comissao,
            comissao,
            data.get('observacoes', ''),
            bool(data.get('primeiraMensalidade', False)),
            bool(data.get('recebidaPeloCliente', False)),
            bool(data.get('comissaoPaga', False))
        ))
        
        parcela_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': str(parcela_id),
            'oportunidadeId': data.get('oportunidadeId', ''),
            'cliente': data['cliente'],
            'vendedor': data['vendedor'],
            'numero': data['numero'],
            'valor': valor,
            'valorLiquido': valor_liquido,
            'vencimento': format_date_br(vencimento),
            'pagamentoComissao': format_date_br(pagamento_comissao),
            'comissao': comissao,
            'observacoes': data.get('observacoes', ''),
            'primeiraMensalidade': bool(data.get('primeiraMensalidade', False)),
            'recebidaPeloCliente': bool(data.get('recebidaPeloCliente', False)),
            'comissaoPaga': bool(data.get('comissaoPaga', False)),
            'dataCadastro': format_date_br(datetime.now())
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas/<int:parcela_id>', methods=['PUT'])
def update_parcela(parcela_id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cur = conn.cursor()
        cur.execute('''
            UPDATE parcelas 
            SET recebida_pelo_cliente = ?, comissao_paga = ?
            WHERE id = ?
        ''', (
            bool(data.get('recebidaPeloCliente', False)),
            bool(data.get('comissaoPaga', False)),
            parcela_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas/<int:parcela_id>', methods=['DELETE'])
def delete_parcela(parcela_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cur = conn.cursor()
        cur.execute('DELETE FROM parcelas WHERE id = ?', (parcela_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para estatísticas do dashboard
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cur = conn.cursor()
        
        # Total de oportunidades
        cur.execute('SELECT COUNT(*) as total FROM oportunidades')
        total_oportunidades = cur.fetchone()['total']
        
        # Total de vendedores
        cur.execute('SELECT COUNT(*) as total FROM vendedores')
        total_vendedores = cur.fetchone()['total']
        
        # Total de parcelas
        cur.execute('SELECT COUNT(*) as total FROM parcelas')
        total_parcelas = cur.fetchone()['total']
        
        # Parcelas pagas
        cur.execute('SELECT COUNT(*) as total FROM parcelas WHERE comissao_paga = 1')
        parcelas_pagas = cur.fetchone()['total']
        
        # Valor total de comissões
        cur.execute('SELECT SUM(comissao) as total FROM parcelas')
        total_comissoes = cur.fetchone()['total'] or 0
        
        # Comissões pagas
        cur.execute('SELECT SUM(comissao) as total FROM parcelas WHERE comissao_paga = 1')
        comissoes_pagas = cur.fetchone()['total'] or 0
        
        conn.close()
        
        return jsonify({
            'totalOportunidades': total_oportunidades,
            'totalVendedores': total_vendedores,
            'totalParcelas': total_parcelas,
            'parcelasPagas': parcelas_pagas,
            'totalComissoes': round(total_comissoes, 2),
            'comissoesPagas': round(comissoes_pagas, 2),
            'comissoesPendentes': round(total_comissoes - comissoes_pagas, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

