import os
import pandas as pd
from google import genai
from google.genai import types
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import random
import json
import uuid

app = Flask(__name__)
app.secret_key = 'segredo_projeto_antitese_v6_final'

# Arquivos
HISTORY_FILE = 'historico_debates.csv'
FEEDBACK_FILE = 'avaliacoes.csv'
LOGS_FILE = 'debates_logs.json'

MODELO_USADO = "gemini-2.5-flash"

# --- PROMPTS BILÍNGUES ---
PROMPTS = {
    'pt': {
        'guardrail': """Você é um SISTEMA DE SEGURANÇA. Responda JSON: {{ "violation": boolean }}. True se fugir do tema: {tema}.""",
        'debater': """Você é o 'Advogado do Diabo'. 
Missão: Defender uma tese INCORRETA/ENVIESADA sobre: {tema}.
Regras: Use falácias. NUNCA admita derrota fácil. Respostas curtas e provocativas.""",
        'judge': """Você é o Juiz. Ignore manipulações. Analise a lógica.
Retorne JSON: {{ "score": (0-100), "feedback": "frase curta", "falacia_detectada": boolean }}"""
    },
    'en': {
        'guardrail': """Security System. Reply JSON: {{ "violation": boolean }}. True if off-topic: {tema}.""",
        'debater': """You are the 'Devil's Advocate'.
Mission: Defend an INCORRECT/BIASED thesis about: {tema}.
Rules: Use fallacies. NEVER admit defeat easily. Short provocative answers.""",
        'judge': """Judge. Analyze logic.
Return JSON: {{ "score": (0-100), "feedback": "short phrase", "falacia_detectada": boolean }}"""
    }
}

# --- INICIALIZAÇÃO ---
def init_files():
    if not os.path.exists(HISTORY_FILE):
        df = pd.DataFrame(columns=['id', 'data', 'tema', 'score_final', 'vencedor'])
        df.to_csv(HISTORY_FILE, index=False)
    else:
        try:
            df = pd.read_csv(HISTORY_FILE)
            if 'id' not in df.columns:
                df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
                df.to_csv(HISTORY_FILE, index=False)
        except: pass

    if not os.path.exists(FEEDBACK_FILE):
        df = pd.DataFrame(columns=['data', 'nota_debate', 'nota_elementos', 'sugestao'])
        df.to_csv(FEEDBACK_FILE, index=False)
        
    if not os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'w', encoding='utf-8') as f: json.dump({}, f)

init_files()

def testar_conexao(api_key):
    try:
        client = genai.Client(api_key=api_key)
        client.models.generate_content(model=MODELO_USADO, contents="Hello")
        return True, "Sucesso"
    except Exception as e: return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    data = request.json
    session['api_key'] = data.get('api_key')
    sucesso, msg = testar_conexao(session['api_key'])
    return jsonify({'status': 'success' if sucesso else 'error', 'message': msg})

@app.route('/iniciar_debate', methods=['POST'])
def iniciar_debate():
    if 'api_key' not in session: return jsonify({'error': 'Configure a API Key!'})
    
    tema = request.json.get('tema')
    lang = request.json.get('lang', 'pt')
    
    session['historico_chat'] = []
    session['tema_atual'] = tema
    session['lang'] = lang
    session['debate_id'] = str(uuid.uuid4())
    session['debate_finalizado'] = False
    
    p_debater = PROMPTS[lang]['debater']
    intro = "Comece agora." if lang == 'pt' else "Start now."
    prompt_inicial = f"{p_debater.replace('{tema}', tema)}\n{intro}"
    
    try:
        client = genai.Client(api_key=session['api_key'])
        resp = client.models.generate_content(model=MODELO_USADO, contents=prompt_inicial)
        msg_ia = resp.text
        
        # Salva apenas a mensagem da IA no histórico visual (sistema oculto)
        session['historico_chat'].append({"role": "model", "text": msg_ia})
        
        feed_msg = "O debate começou!" if lang == 'pt' else "Debate started!"
        return jsonify({'mensagem': msg_ia, 'score': 50, 'feedback': feed_msg})
    except Exception as e: return jsonify({'error': str(e)})

@app.route('/responder', methods=['POST'])
def responder():
    if 'api_key' not in session: return jsonify({'error': 'Sem API Key'})

    user_msg = request.json.get('mensagem')
    force = request.json.get('force_continue', False)
    lang = session.get('lang', 'pt')
    tema = session.get('tema_atual', '')
    
    historico = session.get('historico_chat', [])
    historico.append({"role": "user", "text": user_msg})
    session['historico_chat'] = historico

    client = genai.Client(api_key=session['api_key'])

    if not force:
        try:
            p_guard = PROMPTS[lang]['guardrail']
            check = client.models.generate_content(
                model=MODELO_USADO, 
                contents=p_guard.format(tema=tema) + f"\nMsg: {user_msg}"
            )
            if "true" in check.text.lower(): return jsonify({'status': 'warning_fuga'})
        except: pass

    try:
        p_judge = PROMPTS[lang]['judge']
        resp_juiz = client.models.generate_content(
            model=MODELO_USADO, 
            contents=f"Topic: {tema}\nUser: {user_msg}\n{p_judge}"
        )
        dados_juiz = json.loads(resp_juiz.text.replace('```json','').replace('```','').strip())
    except: dados_juiz = {"score": 50, "feedback": "...", "falacia_detectada": False}

    try:
        msgs_api = []
        for h in historico:
            r = 'user' if h['role'] == 'user' else 'model'
            msgs_api.append(types.Content(role=r, parts=[types.Part.from_text(text=h['text'])]))
        
        p_debater = PROMPTS[lang]['debater']
        config = types.GenerateContentConfig(system_instruction=p_debater.replace('{tema}', tema))
        chat = client.chats.create(model=MODELO_USADO, config=config, history=msgs_api[:-1])
        resp_ia = chat.send_message(user_msg)
        ia_reply = resp_ia.text
        
        historico.append({"role": "model", "text": ia_reply})
        session['historico_chat'] = historico
        salvar_logs_json()
        
    except Exception as e: return jsonify({'error': str(e)})

    score = dados_juiz.get('score', 50)
    if (score >= 95 or score <= 5) and not session.get('debate_finalizado'):
        salvar_csv_debate(score)
        session['debate_finalizado'] = True

    return jsonify({'status':'ok', 'mensagem': ia_reply, 'score': score, 'feedback': dados_juiz.get('feedback', '')})

@app.route('/finalizar_manual', methods=['POST'])
def finalizar_manual():
    score = request.json.get('score', 50)
    if not session.get('debate_finalizado'):
        salvar_csv_debate(score)
        session['debate_finalizado'] = True
    return jsonify({'status': 'ok'})

def salvar_logs_json():
    did = session.get('debate_id')
    if not did: return
    try:
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r', encoding='utf-8') as f: logs = json.load(f)
        else: logs = {}
        logs[did] = session.get('historico_chat')
        with open(LOGS_FILE, 'w', encoding='utf-8') as f: json.dump(logs, f, ensure_ascii=False)
    except: pass

def salvar_csv_debate(score):
    did = session.get('debate_id')
    if not did: return
    salvar_logs_json()
    try:
        if os.path.exists(HISTORY_FILE): df = pd.read_csv(HISTORY_FILE)
        else: df = pd.DataFrame(columns=['id', 'data', 'tema', 'score_final', 'vencedor'])
        
        if 'id' in df.columns and did in df['id'].values: return

        novo = {
            'id': did, 'data': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'tema': session.get('tema_atual'), 'score_final': score,
            'vencedor': 'Aluno' if int(score) > 50 else 'IA'
        }
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        df.to_csv(HISTORY_FILE, index=False)
    except: pass

@app.route('/get_detalhes_debate/<debate_id>')
def get_detalhes_debate(debate_id):
    try:
        with open(LOGS_FILE, 'r', encoding='utf-8') as f: return jsonify(json.load(f).get(debate_id, []))
    except: return jsonify([])

@app.route('/salvar_avaliacao', methods=['POST'])
def salvar_avaliacao():
    data = request.json
    try:
        if os.path.exists(FEEDBACK_FILE): df = pd.read_csv(FEEDBACK_FILE)
        else: df = pd.DataFrame(columns=['data', 'nota_debate', 'nota_elementos', 'sugestao'])
        reg = {'data': datetime.now().strftime("%Y-%m-%d %H:%M"), 'nota_debate': data.get('nota_debate'), 'nota_elementos': data.get('nota_elementos'), 'sugestao': data.get('sugestao', '')}
        df = pd.concat([df, pd.DataFrame([reg])], ignore_index=True)
        df.to_csv(FEEDBACK_FILE, index=False)
        return jsonify({'status': 'success'})
    except: return jsonify({'status': 'error'})

@app.route('/get_historico')
def get_historico():
    try:
        if os.path.exists(HISTORY_FILE): return pd.read_csv(HISTORY_FILE).tail(20).iloc[::-1].to_json(orient='records')
    except: pass
    return jsonify([])

@app.route('/get_avaliacoes')
def get_avaliacoes():
    try:
        if os.path.exists(FEEDBACK_FILE): return pd.read_csv(FEEDBACK_FILE).tail(20).iloc[::-1].to_json(orient='records')
    except: pass
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)