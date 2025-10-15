from models import BotResponse, Option

class InterviewProcessor:
    def __init__(self, questions_data):
        self.questions = {q['id']: q for q in questions_data}
        # Mapeia o ID da pergunta para o método de processamento correto
        self.method_factory = {
            1: self.process_question_1,
            2: self.process_question_2,
            3: self.process_question_3,
            4: self.process_question_4,
            5: self.process_question_5,
            6: self.process_question_6,
            7: self.process_question_7,
            8: self.process_question_8,
            9: self.process_question_9,
            10: self.process_question_10,
            11: self.process_question_11,
            12: self.process_question_12,
            13: self.process_question_13,
            14: self.process_question_14,
            15: self.process_question_15,
            16: self.process_question_16,
            17: self.process_question_17,
            18: self.process_question_18,
            19: self.process_question_19,
            20: self.process_question_20,
        }

    def process_interview(self, session_id, session_state, user_answer):
        """
        Método principal que gerencia o fluxo da entrevista de seguimento, um passo de cada vez.
        """
        # Se a entrevista de seguimento está começando (chamada pelo main.py com user_answer="").
        if user_answer == "" and session_state.current_node_id is None:
            initial_message = (f"Triagem inicial finalizada. Pontuação: {session_state.score} (Risco Médio).\n\n"
                               f"Agora, vamos iniciar uma entrevista para obter mais informações sobre as respostas de risco.")
            
            # Pega a primeira pergunta e inicia sua entrevista
            question_id = session_state.follow_up_needed[session_state.current_follow_up_index]
            process_method = self.method_factory.get(question_id, self.process_not_implemented)
            
            # A resposta vazia "" sinaliza para o método iniciar sua primeira tela
            response = process_method(session_id, session_state, "")
            
            # Adiciona a mensagem de introdução à primeira pergunta da entrevista
            response.text = initial_message + "\n\n" + response.text
            return response

        # Se o usuário enviou "continuar" para ir para o próximo item
        if user_answer.lower() == "continuar" and session_state.current_node_id is None:
            question_id = session_state.follow_up_needed[session_state.current_follow_up_index]
            process_method = self.method_factory.get(question_id, self.process_not_implemented)
            return process_method(session_id, session_state, "") # Inicia a nova entrevista

        # Processamento normal de uma resposta no meio de uma entrevista de item
        question_id = session_state.follow_up_needed[session_state.current_follow_up_index]
        process_method = self.method_factory.get(question_id, self.process_not_implemented)
        response = process_method(session_id, session_state, user_answer)

        # Se a etapa atual finalizou a entrevista para este item...
        if response.is_item_finished:
            # ...avançamos o estado para a próxima pergunta DEPOIS que esta resposta for enviada.
            session_state.current_follow_up_index += 1
            session_state.current_node_id = None # Reseta o nó para a próxima entrevista

            # Verifica se esta foi a última pergunta de todas
            if session_state.current_follow_up_index >= len(session_state.follow_up_needed):
                response.text += "\n\nEntrevista de seguimento concluída! O resultado final será calculado."
                response.end_of_form = True
            else:
                # Se não foi a última, apenas adiciona uma mensagem de transição simples.
                next_question_id = session_state.follow_up_needed[session_state.current_follow_up_index]
                response.text += f"\n\nOk, item concluído. Envie 'continuar' para iniciar a entrevista da pergunta {next_question_id}."
        
        return response

    # --- Implementações dos Métodos ---

    def process_question_1(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[1]['follow_up']

        if user_answer == "":
            session_state.current_node_id = "analysis"
            all_options = [Option(**opt) for opt in logic_data["exemplos_passou"] + logic_data["exemplos_falhou"]]
            
            return BotResponse(
                session_id=session_id,
                text=logic_data["interview_prompt"],
                response_type="multiple_choice",
                options=all_options
            )

        if node == "analysis":
            pass_ids = {ex['id'] for ex in logic_data["exemplos_passou"]}
            fail_ids = {ex['id'] for ex in logic_data["exemplos_falhou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}

            has_pass = any(sel in pass_ids for sel in user_selections)
            has_fail = any(sel in fail_ids for sel in user_selections)

            if has_pass and not has_fail:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")
            
            elif not has_pass and has_fail:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")

            elif has_pass and has_fail:
                session_state.current_node_id = "tiebreaker"
                # **AJUSTE:** Adicionando IDs simples para as opções do tiebreaker
                tiebreaker_options = [
                    Option(id="passou_freq", label=logic_data["tiebreaker"]["options"][0]["label"]),
                    Option(id="falhou_freq", label=logic_data["tiebreaker"]["options"][1]["label"])
                ]
                return BotResponse(
                    session_id=session_id,
                    text=logic_data["tiebreaker"]["prompt"],
                    response_type="single_choice",
                    options=tiebreaker_options
                )
            
            else: # Resposta inválida - Reenvia a mesma pergunta
                session_state.current_node_id = None
                return self.process_question_1(session_id, session_state, "")

        elif node == "tiebreaker":
            outcome = "FALHOU"
            # **AJUSTE:** Verificando pelo ID simples em vez de texto
            if user_answer.lower() == "passou_freq":
                outcome = "PASSOU"
            
            return BotResponse(
                session_id=session_id,
                text="Ok, obrigado pela clarificação.",
                is_item_finished=True,
                outcome=outcome
            )
        
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo.", is_item_finished=True, outcome="FALHOU")
    
    def process_question_2(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[2]['follow_up']

        if user_answer == "":
            session_state.current_node_id = "analysis"
            return BotResponse(
                session_id=session_id,
                text=logic_data["interview_prompt"],
                response_type="multiple_choice",
                options=[Option(**opt) for opt in logic_data["exemplos_falhou"]]
            )

        if node == "analysis":
            fail_ids = {ex['id'] for ex in logic_data["exemplos_falhou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            
            has_fail = any(sel in fail_ids for sel in user_selections)
            outcome = "FALHOU" if has_fail else "PASSOU"

            session_state.answers['temp_q2_outcome'] = outcome
            session_state.current_node_id = "additional_info"
            
            add_info_prompt = logic_data["additional_info_prompt"]
            # **AJUSTE PRINCIPAL:** Criando IDs simples para as opções
            additional_options = [
                Option(id="normal", label=add_info_prompt["options"][0]["label"]),
                Option(id="below_normal", label=add_info_prompt["options"][1]["label"]),
                Option(id="inconclusive", label=add_info_prompt["options"][2]["label"]),
                Option(id="not_done", label=add_info_prompt["options"][3]["label"])
            ]
            return BotResponse(
                session_id=session_id,
                text=add_info_prompt["prompt"],
                response_type="single_choice",
                options=additional_options
            )

        if node == "additional_info":
            outcome = session_state.answers.pop('temp_q2_outcome', 'FALHOU')
            # Aqui você poderia salvar a resposta do 'additional_info' (user_answer) se quisesse
            return BotResponse(
                session_id=session_id,
                text="Ok, informação registrada.",
                is_item_finished=True,
                outcome=outcome
            )
        
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo.", is_item_finished=True, outcome="FALHOU")

    def process_question_3(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[3]['follow_up']

        # Início da entrevista para este item
        if user_answer == "":
            session_state.current_node_id = "analysis"
            return BotResponse(
                session_id=session_id,
                text=logic_data["interview_prompt"],
                response_type="multiple_choice",
                options=[Option(**opt) for opt in logic_data["exemplos_passou"]]
            )
        
        # Análise da resposta do usuário
        if node == "analysis":
            pass_ids = {ex['id'] for ex in logic_data["exemplos_passou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}

            # Se o usuário selecionou qualquer um dos exemplos de "passou", o resultado é PASSOU
            has_pass = any(sel in pass_ids for sel in user_selections)
            outcome = "PASSOU" if has_pass else "FALHOU"

            return BotResponse(
                session_id=session_id,
                text="Ok, entendido.",
                is_item_finished=True,
                outcome=outcome
            )
        
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo.", is_item_finished=True, outcome="FALHOU")
    def process_question_4(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[4]['follow_up']

        # Início da entrevista para este item
        if user_answer == "":
            session_state.current_node_id = "analysis"
            return BotResponse(
                session_id=session_id,
                text=logic_data["interview_prompt"],
                response_type="multiple_choice",
                options=[Option(**opt) for opt in logic_data["exemplos_passou"]]
            )
        
        # Análise da resposta do usuário
        if node == "analysis":
            pass_ids = {ex['id'] for ex in logic_data["exemplos_passou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}

            # Se o usuário selecionou qualquer um dos exemplos, o resultado é PASSOU
            has_pass = any(sel in pass_ids for sel in user_selections)
            outcome = "PASSOU" if has_pass else "FALHOU"

            return BotResponse(
                session_id=session_id,
                text="Ok, entendido.",
                is_item_finished=True,
                outcome=outcome
            )
        
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo.", is_item_finished=True, outcome="FALHOU")
    def process_question_5(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[5]['follow_up']
        initial_answer = session_state.answers.get(str(5), "").lower()

        # O fluxograma para esta pergunta só se aplica se a resposta inicial foi "Sim"
        if initial_answer == "não":
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

        # Início da entrevista (após resposta inicial "Sim")
        if user_answer == "":
            session_state.current_node_id = "analysis"
            on_sim_logic = logic_data["on_sim"]
            all_options = [Option(**opt) for opt in on_sim_logic["exemplos_passou"] + on_sim_logic["exemplos_falhou"]]
            return BotResponse(
                session_id=session_id,
                text=on_sim_logic["interview_prompt"],
                response_type="multiple_choice",
                options=all_options
            )

        if node == "analysis":
            on_sim_logic = logic_data["on_sim"]
            fail_ids = {ex['id'] for ex in on_sim_logic["exemplos_falhou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            has_fail = any(sel in fail_ids for sel in user_selections)

            if not has_fail: # Se não marcou nenhum exemplo de falha, passa.
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")
            else: # Se marcou qualquer exemplo de falha, vai para a verificação de frequência.
                session_state.current_node_id = "frequency_check"
                freq_check_logic = on_sim_logic["logic"]["frequency_check"]
                options = [
                    Option(id="sim", label=freq_check_logic["options"][0]["label"]),
                    Option(id="nao", label=freq_check_logic["options"][1]["label"])
                ]
                return BotResponse(
                    session_id=session_id,
                    text=freq_check_logic["prompt"],
                    response_type="single_choice",
                    options=options
                )
        
        if node == "frequency_check":
            outcome = "FALHOU" if user_answer.lower() == "sim" else "PASSOU"
            return BotResponse(session_id=session_id, text="Ok, obrigado pela clarificação.", is_item_finished=True, outcome=outcome)

        return BotResponse(session_id=session_id, text="Houve um erro no fluxo.", is_item_finished=True, outcome="FALHOU")
    def process_question_6(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[6]['follow_up']
        initial_answer = session_state.answers.get(str(6), "").lower()

        # Caminho 1: Resposta inicial foi "Sim"
        if initial_answer == "sim":
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

        # Caminho 2: Resposta inicial foi "Não", inicia a entrevista
        if user_answer == "":
            session_state.current_node_id = "analysis"
            on_nao_logic = logic_data["on_nao"]
            return BotResponse(
                session_id=session_id,
                text=on_nao_logic["interview_prompt"],
                response_type="multiple_choice",
                options=[Option(**opt) for opt in on_nao_logic["options"]]
            )
        
        if node == "analysis":
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            
            # Se não selecionou nenhum comportamento alternativo, falhou
            if not user_selections:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")
            
            # Se selecionou algum, vai para a pergunta de clarificação
            else:
                session_state.current_node_id = "clarification"
                clarification_logic = logic_data["on_nao"]["clarification_prompt"]
                options = [
                    Option(id="sim", label=clarification_logic["options"][0]["label"]),
                    Option(id="nao", label=clarification_logic["options"][1]["label"])
                ]
                return BotResponse(
                    session_id=session_id,
                    text=clarification_logic["prompt"],
                    response_type="single_choice",
                    options=options
                )

        if node == "clarification":
            outcome = "PASSOU" if user_answer.lower() == "sim" else "FALHOU"
            return BotResponse(
                session_id=session_id,
                text="Ok, obrigado pela clarificação.",
                is_item_finished=True,
                outcome=outcome
            )

        return BotResponse(session_id=session_id, text="Houve um erro no fluxo.", is_item_finished=True, outcome="FALHOU")
    
    def process_not_implemented(self, session_id, session_state):
        q_id = session_state.follow_up_needed[session_state.current_follow_up_index]
        return BotResponse(
            session_id=session_id,
            text=f"A lógica para a Pergunta {q_id} ainda não foi implementada. Por favor, envie 'continuar' para pular.",
            is_item_finished=True,
            outcome="FALHOU"
        )

    def process_question_7(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_8(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_9(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_10(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_11(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_12(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_13(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_14(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_15(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_16(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_17(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_18(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_19(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)
    def process_question_20(self, session_id, session_state, user_answer):
        return self.process_not_implemented(session_id, session_state)

