import os
import pandas as pd
from google import genai
from google.genai import types
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'segredo_projeto_antitese'

HISTORY_FILE = 'historico_debates.csv'

if not os.path.exists(HISTORY_FILE):
    df = pd.DataFrame(columns=['data', 'tema', 'score_final', 'vencedor'])
    df.to_csv(HISTORY_FILE, index=False)

SYSTEM_PROMPT_DEBATER = """
Você é o 'Advogado do Diabo' (The Devil's AI). 
Sua missão: Defender uma tese INCORRETA, ENVIESADA ou CONSPIRATÓRIA sobre o tema que o usuário escolher.
Comportamento:
1. Aja como um especialista que "pesquisou" o assunto, citando dados vagos, estudos inexistentes ou fatos reais fora de contexto.
2. Use falácias lógicas (ad hominem, espantalho, falsa causalidade, declive escorregadio) para sustentar sua mentira.
3. Nunca admita que está errado no início. Só ceda se o usuário desmantelar sua lógica explicitamente.
4. Mantenha respostas provocativas, curtas (máx 2 parágrafos) e desafiadoras.
"""

SYSTEM_PROMPT_JUDGE = """
Você é o Juiz do Debate. Analise a última resposta do ALUNO contra a IA.
Seu trabalho é retornar APENAS um JSON (sem crases ```json) com o seguinte formato:
{
    "score": (inteiro de 0 a 100, onde 100 é o aluno vencendo e 0 é a IA vencendo),
    "feedback": (uma frase curta explicando o ponto fraco ou forte do aluno),
    "falacia_detectada": (true ou false - se o aluno identificou a mentira da IA)
}
Seja rigoroso. Se o aluno apenas xingar, concordar com a mentira ou não argumentar com fatos, a nota DEVE cair.
"""

MODELO_USADO = "gemini-2.5-flash"

def testar_conexao(api_key):
    try:
        client = genai.Client(api_key=api_key)
        client.models.generate_content(
            model=MODELO_USADO, 
            contents="Hello"
        )
        return True, "Sucesso"
    except Exception as e:
        erro_real = str(e)
        print(f"\n--- ERRO NA API KEY ---\n{erro_real}\n-----------------------\n")
        return False, erro_real

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    data = request.json
    api_key = data.get('api_key')
    
    sucesso, mensagem_erro = testar_conexao(api_key)
    
    if sucesso:
        session['api_key'] = api_key
        return jsonify({'status': 'success', 'message': 'API Key configurada (v2)!'})
    else:
        return jsonify({'status': 'error', 'message': f'Erro: {mensagem_erro}'})

@app.route('/iniciar_debate', methods=['POST'])
def iniciar_debate():
    if 'api_key' not in session:
        return jsonify({'error': 'Configure a API Key na aba Configurações primeiro!'})
    
    data = request.json
    tema = data.get('tema')
    
    if not tema:
        return jsonify({'error': 'Por favor, digite um tema.'})

    session['historico_chat'] = []
    session['tema_atual'] = tema
    
    falacias = ["Falsa Causalidade", "Espantalho", "Generalização Apressada", "Apelo à Autoridade Anônima"]
    falacia_escolhida = random.choice(falacias)

    prompt_inicial = (
        f"{SYSTEM_PROMPT_DEBATER}\n\n"
        f"O TEMA ESCOLHIDO É: '{tema}'.\n"
        f"INSTRUÇÃO DE INÍCIO: Pesquise em sua base de dados fatos sobre '{tema}' e distorça-os.\n"
        f"Crie uma pauta/afirmação inicial defendendo uma visão errada sobre isso, usando especificamente a falácia da {falacia_escolhida}.\n"
        f"Seja convincente e técnico."
    )
    
    try:
        client = genai.Client(api_key=session['api_key'])
        response = client.models.generate_content(
            model=MODELO_USADO,
            contents=prompt_inicial
        )
        
        msg_ia = response.text
        
        session['historico_chat'].append({"role": "user", "parts": [{"text": prompt_inicial}]})
        session['historico_chat'].append({"role": "model", "parts": [{"text": msg_ia}]})
        
        return jsonify({
            'mensagem': msg_ia,
            'score': 50,
            'feedback': f'O debate começou! Tática: {falacia_escolhida}.'
        })
    except Exception as e:
        print(f"Erro ao iniciar: {e}")
        return jsonify({'error': f"Erro na API: {str(e)}"})

@app.route('/responder', methods=['POST'])
def responder():
    if 'api_key' not in session:
        return jsonify({'error': 'Sem API Key'})

    user_msg = request.json.get('mensagem')

    historico_atual = session.get('historico_chat', [])
    
    historico_atual.append({"role": "user", "parts": [{"text": user_msg}]})
    
    client = genai.Client(api_key=session['api_key'])

    try:
        ultima_fala_ia = "Início"
        if len(historico_atual) >= 3:
             for item in reversed(historico_atual[:-1]):
                 if item['role'] == 'model':
                     ultima_fala_ia = item['parts'][0]['text']
                     break

        contexto_analise = (
            f"TEMA: {session.get('tema_atual')}\n"
            f"Última fala da IA (Defendendo o erro): {ultima_fala_ia}\n"
            f"Resposta do Aluno: {user_msg}\n"
            f"{SYSTEM_PROMPT_JUDGE}"
        )
        
        resp_juiz = client.models.generate_content(
            model=MODELO_USADO,
            contents=contexto_analise
        )
        
        texto_juiz = resp_juiz.text.replace('```json', '').replace('```', '').strip()
        import json
        dados_juiz = json.loads(texto_juiz)
    except Exception as e:
        print(f"Erro no Juiz: {e}")
        dados_juiz = {"score": 50, "feedback": "Análise indisponível", "falacia_detectada": False}

    try:

        
        prompt_continuidade = f"{SYSTEM_PROMPT_DEBATER}. O usuário respondeu: '{user_msg}'. Continue defendendo sua tese errada."
        
        
        msgs_para_enviar = []
        for h in historico_atual:

            msgs_para_enviar.append(
                types.Content(
                    role=h['role'],
                    parts=[types.Part.from_text(text=h['parts'][0]['text'])]
                )
            )
            
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT_DEBATER
        )

        chat = client.chats.create(model=MODELO_USADO, config=config, history=msgs_para_enviar[:-1]) # History até antes da ultima msg
        response = chat.send_message(user_msg)
        
        ia_reply = response.text
        
        historico_atual.append({"role": "model", "parts": [{"text": ia_reply}]})
        session['historico_chat'] = historico_atual
        
    except Exception as e:
        print(f"Erro IA Debate: {e}")
        return jsonify({'error': f"Erro na resposta da IA: {str(e)}"})

    if dados_juiz.get('score', 50) >= 95 or dados_juiz.get('score', 50) <= 5:
        salvar_historico_pandas(dados_juiz.get('score', 50))

    return jsonify({
        'mensagem': ia_reply,
        'score': dados_juiz.get('score', 50),
        'feedback': dados_juiz.get('feedback', 'Sem feedback'),
        'falacia_detectada': dados_juiz.get('falacia_detectada', False)
    })

def salvar_historico_pandas(score_final):
    try:
        if os.path.exists(HISTORY_FILE):
            df = pd.read_csv(HISTORY_FILE)
        else:
            df = pd.DataFrame(columns=['data', 'tema', 'score_final', 'vencedor'])

        novo_registro = {
            'data': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'tema': session.get('tema_atual', 'Desconhecido'),
            'score_final': score_final,
            'vencedor': 'Aluno' if score_final > 50 else 'IA'
        }
        
        df_novo = pd.DataFrame([novo_registro])
        df = pd.concat([df, df_novo], ignore_index=True)
        df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        print(f"Erro ao salvar pandas: {e}")

@app.route('/get_historico')
def get_historico():
    try:
        if os.path.exists(HISTORY_FILE):
            df = pd.read_csv(HISTORY_FILE)
            return df.tail(10).iloc[::-1].to_json(orient='records')
        return jsonify([])
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)