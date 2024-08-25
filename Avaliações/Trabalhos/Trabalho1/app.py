from flask import Flask, request, render_template, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'minhaChave'

#Login
@app.route("/")
@app.route("/login", methods=['POST','GET'])
def logar():
	#Verificando se usuario está logado
	if 'usuarioLogado' in session:
		return redirect("/inicio")
	#Envio do formulário
	if request.method == 'POST':
		#Obtendo dados enviados pelo formulário
		usuario = request.form.get('usuario')
		senha = request.form.get('senha')
		conexao = sqlite3.connect("medidas.db")
		cursor = conexao.cursor()
		#Vendo se usuário existe
		cursor.execute("SELECT usuario FROM USUARIOS WHERE usuario=?", (usuario,))
		usuarioExiste = cursor.fetchone()
		#Usuário existe
		if usuarioExiste != None:
			#Verificando se senha está correta
			cursor.execute("SELECT senha FROM USUARIOS WHERE usuario=?", (usuario,))
			senhaCerta = cursor.fetchone()[0]
			conexao.close()
			#Senha correta
			if senha == senhaCerta:
				session['usuarioLogado'] = usuario
				return redirect("/inicio")
			#Senha errada
			msgErro = "Usuário ou senha incorreto(os)"
			return render_template("login.html", msgErro=msgErro)
		#Usuário não existe
		conexao.close()
		msgErro = "Usuário ou senha incorreto(os)"
		return render_template("login.html", msgErro=msgErro)
	#Carregando página
	else:
		return (render_template("login.html"))

#Cadastro
@app.route("/cadastro", methods=['POST','GET'])
def cadastrar():
	#Verificando se usuario está logado
	if 'usuarioLogado' in session:
		return redirect("/inicio")
	#Envio do formuláro
	if request.method == 'POST':
		#Obtendo dados enviados pelo formulário	
		usuario = request.form.get('usuario')
		nome = request.form.get('nome')
		senha = request.form.get('senha')
		confirma = request.form.get('confirma')
		#Verificando se senha e confirma senha coincidem
		if confirma != senha:
			msgErro = "Senhas não coincidem"
			return render_template("cadastro.html", msgErro=msgErro)
		conexao = sqlite3.connect("medidas.db")
		cursor = conexao.cursor()
		#Verificando se usuário existe
		cursor.execute("SELECT usuario FROM USUARIOS WHERE usuario=?", (usuario,))
		usuarioExiste = cursor.fetchone()
		#Usuário existe
		if usuarioExiste != None:
			msgErro = "Usuário já existe"
			conexao.close()
			return render_template("cadastro.html", msgErro=msgErro)
		#Usuário não existe
		#Criando usuário
		cursor.execute("INSERT INTO USUARIOS (usuario,nome,senha) VALUES (?,?,?)", (usuario, nome, senha))
		conexao.commit()
		conexao.close()
		return render_template("login.html",sucesso=True)
	#Carregando página
	else:
		return render_template("cadastro.html")

#Início
@app.route("/inicio", methods=['GET'])
def inicio():
	#Verificando se usuario está logado
	if 'usuarioLogado' not in session:
		return redirect("/login")
	#Carregando página
	#Obtendo dados do usuário logado	
	usuarioLogado = session['usuarioLogado']
	conexao = sqlite3.connect("medidas.db")
	cursor = conexao.cursor()
	cursor.execute("SELECT nome FROM usuarios WHERE usuario = ?", (usuarioLogado,))
	nomeLogado = cursor.fetchone()[0]
	cursor.execute("SELECT id, data, peso, ombro, peito, braco, antebraco, cintura, quadril, coxa, panturrilha FROM MEDIDAS WHERE usuario=?", (usuarioLogado,))
	#[(coluna1, coluna2, ...),(coluna1, coluna2, ...), ...]
	medidas = cursor.fetchall()
	conexao.close()
	return render_template("inicio.html", nome=nomeLogado, medidas=medidas)

#Logout
@app.route("/inicio/sair")
def sair():
	session.pop('usuarioLogado', None)
	return redirect("/login")

#Adição de medidas
@app.route("/inicio/adicionar", methods=['GET','POST'])
def adicionar():
	#Verificando se usuario está logado
	if 'usuarioLogado' not in session:
		return redirect("/login")
	#Envio do formulário
	if request.method == 'POST':
		logado = session['usuarioLogado']
		#Obtendo dados enviados pelo formulário
		peso = request.form.get('peso')
		ombro = request.form.get('ombro')
		peito = request.form.get('peito')
		braco = request.form.get('braco')
		antebraco = request.form.get('antebraco')
		cintura = request.form.get('cintura')
		quadril = request.form.get('quadril')
		coxa = request.form.get('coxa')
		panturrilha = request.form.get('panturrilha')
		#Calculando e formatando data atual
		dataAtual = datetime.now()
		ano = str(dataAtual.year)
		mes = str(dataAtual.month)
		dia = str(dataAtual.day)
		data = f"{dia}/{mes}/{ano}"
		#Inserindo dados
		conexao = sqlite3.connect("medidas.db")
		cursor = conexao.cursor()
		cursor.execute("INSERT INTO MEDIDAS (data, peso, ombro, peito, braco, antebraco, cintura, quadril, coxa, panturrilha, usuario) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data, peso, ombro, peito, braco, antebraco, cintura, quadril, coxa, panturrilha, logado))
		conexao.commit()
		conexao.close()
		return render_template("adicionar.html",sucesso=True)
	#Carregando página
	else:
		return render_template("adicionar.html")

#Exclusão de medidas
@app.route("/inicio/<id>", methods=['POST'])
def apagar(id):
	#Verificando se usuario está logado
	if 'usuarioLogado' not in session:
		return redirect("/login")
	id = int(id)
	conexao = sqlite3.connect("medidas.db")
	cursor = conexao.cursor()
	#Vendo se é o dono das medidas que está excluindo
	cursor.execute("SELECT usuario FROM MEDIDAS WHERE id=?", (id,))
	dono = cursor.fetchone()[0]
	if dono == session['usuarioLogado']:
		cursor.execute("DELETE FROM MEDIDAS WHERE id=?", (id,))
		conexao.commit()
	conexao.close()
	return(redirect("/inicio"))


@app.route("/inicio/editar/<id>", methods=['POST', 'GET'])
def editar(id):
	#Verificando se usuario está logado
	if 'usuarioLogado' not in session:
		return redirect("/login")
	#Envio do formulário
	if request.method == 'POST':
		#Obtendo dados enviados pelo formulário
		peso = request.form.get('peso')
		ombro = request.form.get('ombro')
		peito = request.form.get('peito')
		braco = request.form.get('braco')
		antebraco = request.form.get('antebraco')
		cintura = request.form.get('cintura')
		quadril = request.form.get('quadril')
		coxa = request.form.get('coxa')
		panturrilha = request.form.get('panturrilha')
		conexao = sqlite3.connect("medidas.db")
		cursor = conexao.cursor()
		cursor.execute("UPDATE MEDIDAS SET peso=?, ombro=?, peito=?, braco=?, antebraco=?, cintura=?, quadril=?, coxa=?, panturrilha=? WHERE id=?", (peso, ombro, peito, braco, antebraco, cintura, quadril, coxa, panturrilha, id))
		conexao.commit()
		conexao.close()
		return render_template("editar.html",sucesso=True)
	#Carregando página
	else:
		conexao = sqlite3.connect("medidas.db")
		cursor = conexao.cursor()
		#Vendo se é o dono das medidas que está editando
		cursor.execute("SELECT usuario FROM MEDIDAS WHERE id=?", (id,))
		dono = cursor.fetchone()[0]
		if dono == session['usuarioLogado']:
			cursor.execute("SELECT id, peso, ombro, peito, braco, antebraco, cintura, quadril, coxa, panturrilha FROM MEDIDAS WHERE id=?", (id,))
			editadas = cursor.fetchone()
			conexao.close()
			return(render_template("editar.html", editado = editadas))
		else:
			return redirect("/inicio")

if __name__ == "__main__":
	app.run(debug=True)