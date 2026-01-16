# backend/models.py

from pydantic import BaseModel
from typing import Optional, List, Literal

# Modelo para uma opção de múltipla escolha ou botão para o frontend
class Option(BaseModel):
    id: str      # Valor que o frontend deve enviar de volta (ex: "p1", "f2")
    label: str   # Texto que aparece no botão/checkbox

# Modelo para a mensagem que o usuário envia para a API
class UserMessage(BaseModel):
    session_id: str
    text: str

# Modelo para guardar o estado da sessão de um usuário no backend
class SessionState(BaseModel):
    current_question_id: int = 1
    answers: dict = {}
    score: int = 0
    follow_up_needed: list = []
    in_follow_up: bool = False 
    current_follow_up_index: int = 0 
    current_node_id: Optional[str] = None

# Modelo UNIFICADO para a resposta que a API envia para o frontend
class BotResponse(BaseModel):
    session_id: str
    text: str
    question_id: Optional[int] = None
    
    # --- Campos para a interface do app mobile ---
    response_type: Literal["text_only", "single_choice", "multiple_choice"] = "text_only"
    options: List[Option] = []
    
    # --- Campos de controle de fluxo ---
    # Avisa se a entrevista para UM item específico acabou
    is_item_finished: bool = False
    # Avisa se o formulário INTEIRO (incluindo follow-up) acabou
    end_of_form: bool = False
    
    # --- Campos de resultado ---
    # Resultado de um item do follow-up
    outcome: Optional[Literal["PASSOU", "FALHOU"]] = None
    # Pontuação final do M-CHAT-R
    score: Optional[int] = None