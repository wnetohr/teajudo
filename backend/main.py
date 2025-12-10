import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Lembre-se de garantir que o models.py tem os campos para o follow-up
from models import UserMessage, SessionState, BotResponse 
from interview_processor import InterviewProcessor # Importa a nova classe

# --- Configuração Inicial ---
app = FastAPI()

# Durante desenvolvimento é útil habilitar CORS para que o frontend (web/emulador)
# consiga se conectar sem bloqueios. Em produção restrinja `allow_origins`.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- mudar para lista de origens específicas em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    with open("data/questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
except FileNotFoundError:
    print("ERRO: O arquivo 'data/questions.json' não foi encontrado.")
    questions = []

sessions = {}
# Cria uma única instância do nosso processador de entrevistas
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
        
        return BotResponse(
            session_id=session_id,
            text=f"{first_question_text}"
        )

    # 2. Se a sessão já existe, processamos a resposta
    current_state = sessions[session_id]
    
    # 3. Lógica de Follow-up (se aplicável)
    if current_state.in_follow_up:
        
        # --- CORREÇÃO IMPORTANTE ---
        # Verifica se a entrevista de seguimento JÁ terminou.
        if current_state.current_follow_up_index >= len(current_state.follow_up_needed):
            # Calcula a recomendação final baseada na pontuação total
            score = current_state.score
            disclaimer = "\n\nLembre-se: esta é uma ferramenta de triagem e não um diagnóstico. Os resultados devem ser discutidos com um pediatra ou profissional de saúde qualificado."

            if score <= 2:
                response_text = (f"Entrevista de seguimento concluída! Pontuação final: {score} (Baixo Risco). "
                                f"Não é necessário procurar um neuropediatra neste momento.")
            elif score >= 8:
                response_text = (f"Entrevista de seguimento concluída! Pontuação final: {score} (Risco Elevado). "
                                f"Recomenda-se procurar um neuropediatra/serviço de avaliação especializada o quanto antes.")
            else:
                response_text = (f"Entrevista de seguimento concluída! Pontuação final: {score} (Risco Médio). "
                                f"Recomenda-se discutir os resultados com o pediatra; considerar encaminhamento para neuropediatra se houver preocupação clínica.")

            response_text += disclaimer
            return BotResponse(
                session_id=session_id,
                text=response_text,
                end_of_form=True,
                score=score
            )
        # --- FIM DA CORREÇÃO ---

        # --- LÓGICA DO DESPACHANTE ---
        
        # Delega todo o trabalho para a classe processadora
        # (Esta chamada agora é segura, pois verificámos o índice acima)
        return interview_processor.process_interview(session_id, current_state, user_message.text)
        
    # 4. Se não estamos em follow-up, continuamos o questionário principal
    
    # Proteção para caso o formulário principal já tenha terminado
    if current_state.current_question_id > 20:
        return BotResponse(
            session_id=session_id,
            text=f"O questionário já foi concluído. Pontuação: {current_state.score}.",
            end_of_form=True
        )

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
        # Fim do questionário principal: AGORA A LÓGICA DE DECISÃO É EXECUTADA
        score = current_state.score
        disclaimer = "\n\nLembre-se: esta é uma ferramenta de triagem e não um diagnóstico. Os resultados devem ser discutidos com um pediatra ou profissional de saúde qualificado."

        if score <= 2:
            response_text = (f"Triagem finalizada. Pontuação: {score} (Baixo Risco). "
                           f"Nenhuma outra avaliação é requerida no momento, a menos que a evolução clínica indique algum risco de TEA.")
            response_text += disclaimer
            return BotResponse(session_id=session_id, text=response_text, end_of_form=True, score=score)
            
        elif score >= 8:
            response_text = (f"Triagem finalizada. Pontuação: {score} (Risco Elevado). "
                           f"É recomendado que a criança seja encaminhada imediatamente para uma avaliação diagnóstica e intervenção precoce.")
            response_text += disclaimer
            return BotResponse(session_id=session_id, text=response_text, end_of_form=True, score=score)
            
        else: # Risco Médio (3 a 7)
            if not current_state.follow_up_needed:
                 # Se o score é médio mas nenhuma pergunta DE FATO precisa de follow-up (raro, mas possível)
                 response_text = (f"Triagem finalizada. Pontuação: {score} (Risco Médio). "
                                f"Nenhuma das respostas se qualifica para a entrevista de seguimento. Recomenda-se vigilância.")
                 response_text += disclaimer
                 return BotResponse(session_id=session_id, text=response_text, end_of_form=True, score=score)
            
            # ATIVA O ESTADO DE FOLLOW-UP
            current_state.in_follow_up = True
            current_state.current_follow_up_index = 0
            
            # Chama o processador de entrevista PELA PRIMEIRA VEZ (com resposta vazia)
            return interview_processor.process_interview(session_id, current_state, "")
            
    else:
        # Ainda estamos no questionário principal, envia a próxima pergunta
        next_question_index = next_question_id - 1
        next_question_text = questions[next_question_index]['question']
        
        return BotResponse(
            session_id=session_id,
            text=f"{next_question_id}. {next_question_text}"
        )

