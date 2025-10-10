from pydantic import BaseModel
from typing import Optional

# Modelo para a mensagem que o usuário envia
class UserMessage(BaseModel):
    session_id: str
    text: str

# Modelo para guardar o estado da sessão de um usuário
class SessionState(BaseModel):
    current_question_id: int = 1
    answers: dict = {}
    score: int = 0
    follow_up_needed: list = []
    in_follow_up: bool = False 
    current_follow_up_index: int = 0 
    current_node_id: Optional[str] = None

# Modelo para a resposta que o bot envia
class BotResponse(BaseModel):
    session_id: str
    text: str
    end_of_form: bool = False
    score: Optional[int] = None