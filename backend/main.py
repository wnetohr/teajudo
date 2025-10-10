# backend/main.py

import json
from fastapi import FastAPI
# Lembre-se de garantir que o models.py tem os campos para o follow-up
from models import UserMessage, SessionState, BotResponse 

# --- Configuração Inicial ---
app = FastAPI()

try:
    with open("data/questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
except FileNotFoundError:
    print("ERRO: O arquivo 'data/questions.json' não foi encontrado.")
    questions = []

sessions = {}

# --- Endpoints da API ---

@app.get("/")
def read_root():
    return {"status": "API do Chatbot M-CHAT-R está online"}

@app.post("/chat", response_model=BotResponse)
def handle_chat(user_message: UserMessage):
    session_id = user_message.session_id

    # 1. Obter ou Criar a Sessão do Usuário
    if session_id not in sessions:
        sessions[session_id] = SessionState()
        
        first_question_text = questions[0]['question']
        intro_text = "Olá! Este é um chatbot para preencher o formulário M-CHAT-R. Responda com 'Sim' ou 'Não'. Se tiver dúvida sobre uma pergunta, digite 'dúvida'. Vamos começar."
        
        return BotResponse(
            session_id=session_id,
            text=f"{intro_text}\n\n1. {first_question_text}"
        )

    # 2. Se a sessão já existe, processamos a resposta
    current_state = sessions[session_id]
    
    # --- LÓGICA PRINCIPAL ---
    # Primeiro, verificamos se estamos na fase de follow-up
    if current_state.in_follow_up:
        # AQUI VAI ENTRAR A LÓGICA DE NAVEGAÇÃO DOS NÓS DO FOLLOW-UP
        # (Nosso próximo passo será construir isso)
        
        response_text = f"Recebi '{user_message.text}'. O fluxo da entrevista de seguimento será construído aqui."
        
        return BotResponse(session_id=session_id, text=response_text)

    # Se não estamos em follow-up, continuamos o questionário principal
    current_question_index = current_state.current_question_id - 1
    
    # Bloco de lógica de pontuação
    question_just_answered = questions[current_question_index]
    user_answer = user_message.text
    
    previous_question_id_str = str(current_state.current_question_id)
    current_state.answers[previous_question_id_str] = user_answer

    if user_answer.lower() == question_just_answered["scoring_risk_on"].lower():
        current_state.score += 1
        if current_state.current_question_id not in current_state.follow_up_needed:
            current_state.follow_up_needed.append(current_state.current_question_id)
    
    # 3. Avança para a próxima pergunta
    current_state.current_question_id += 1
    next_question_id = current_state.current_question_id

    if next_question_id > 20:
        # Fim do questionário principal: AGORA A LÓGICA DE DECISÃO É EXECUTADA
        score = current_state.score
        response_text = ""
        disclaimer = "\n\nLembre-se: esta é uma ferramenta de triagem e não um diagnóstico. Os resultados devem ser discutidos com um pediatra ou profissional de saúde qualificado."

        if score <= 2:
            response_text = (f"Triagem finalizada. Pontuação: {score} (Baixo Risco). "
                           f"Nenhuma outra avaliação é requerida no momento, a menos que a evolução clínica indique algum risco de TEA.")
            response_text += disclaimer
        elif score >= 8:
            response_text = (f"Triagem finalizada. Pontuação: {score} (Risco Elevado). "
                           f"É recomendado que a criança seja encaminhada imediatamente para uma avaliação diagnóstica e intervenção precoce.")
            response_text += disclaimer
        else: # Risco Médio (3 a 7)
            current_state.in_follow_up = True
            current_state.current_follow_up_index = 0
            
            first_follow_up_question_id = current_state.follow_up_needed[0]
            question_data = questions[first_follow_up_question_id - 1]

            response_text = (f"Triagem inicial finalizada. Pontuação: {score} (Risco Médio). "
                           f"Agora, vamos iniciar uma pequena entrevista para obter mais informações sobre as respostas de risco.\n\n"
                           f"Vamos começar pela pergunta {first_follow_up_question_id}: '{question_data['question']}'")
            
        return BotResponse(
            session_id=session_id,
            text=response_text,
            end_of_form=(not current_state.in_follow_up),
            score=score
        )
    else:
        # Ainda estamos no questionário principal, envia a próxima pergunta
        next_question_index = next_question_id - 1
        next_question_text = questions[next_question_index]['question']
        
        return BotResponse(
            session_id=session_id,
            text=f"{next_question_id}. {next_question_text}"
        )