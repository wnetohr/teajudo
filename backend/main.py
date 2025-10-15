# backend/main.py

import json
from fastapi import FastAPI
from models import UserMessage, SessionState, BotResponse
from interview_processor import InterviewProcessor # Importa a classe correta

# --- Configuração Inicial ---
app = FastAPI()

try:
    with open("data/questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
except FileNotFoundError:
    print("ERRO: O arquivo 'data/questions.json' não foi encontrado.")
    questions = []

sessions = {}
# Cria uma única instância do processador de entrevistas para ser usada pela API
interview_processor = InterviewProcessor(questions)

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
    
    # 3. Lógica de Follow-up (se aplicável)
    if current_state.in_follow_up:
        # A classe processadora agora cuida de tudo: estado, navegação e construção da resposta.
        return interview_processor.process_interview(session_id, current_state, user_message.text)
        
    # 4. Se não estamos em follow-up, continuamos o questionário principal
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
    
    # 5. Avança para a próxima pergunta ou finaliza
    current_state.current_question_id += 1
    next_question_id = current_state.current_question_id

    if next_question_id > 20:
        # Fim do questionário principal: LÓGICA DE DECISÃO
        score = current_state.score
        disclaimer = "\n\nLembre-se: esta é uma ferramenta de triagem e não um diagnóstico. Os resultados devem ser discutidos com um pediatra ou profissional de saúde qualificado."

        if score <= 2:
            response_text = f"Triagem finalizada. Pontuação: {score} (Baixo Risco). Nenhuma outra avaliação é requerida no momento." + disclaimer
            return BotResponse(session_id=session_id, text=response_text, score=score, end_of_form=True)

        elif score >= 8:
            response_text = f"Triagem finalizada. Pontuação: {score} (Risco Elevado). É recomendado encaminhamento imediato para avaliação diagnóstica." + disclaimer
            return BotResponse(session_id=session_id, text=response_text, score=score, end_of_form=True)

        else: # Risco Médio (3 a 7)
            if not current_state.follow_up_needed:
                 response_text = f"Triagem finalizada. Pontuação: {score} (Risco Médio), mas nenhuma resposta de risco foi identificada para seguimento. Recomenda-se vigilância." + disclaimer
                 return BotResponse(session_id=session_id, text=response_text, score=score, end_of_form=True)

            current_state.in_follow_up = True
            current_state.current_follow_up_index = 0
            
            # Chama o processador para a primeira pergunta da entrevista
            # Passamos uma resposta vazia para sinalizar o início da primeira entrevista
            return interview_processor.process_interview(session_id, current_state, "")
    else:
        # Ainda estamos no questionário principal, envia a próxima pergunta
        next_question_index = next_question_id - 1
        next_question_text = questions[next_question_index]['question']
        
        return BotResponse(
            session_id=session_id,
            text=f"{next_question_id}. {next_question_text}"
        )


