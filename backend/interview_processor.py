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
    def process_question_7(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[7]['follow_up']
        nodes = logic_data['nodes']

        # 1. Início da entrevista para o item 7
        if user_answer == "":
            session_state.current_node_id = "awaiting_intro"
            return BotResponse(
                session_id=session_id,
                text=logic_data['intro_text'],
                response_type="single_choice",
                options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
            )

        # 2. Resposta à pergunta introdutória
        if node == "awaiting_intro":
            if user_answer.lower() == "sim":
                # O 'sim_path' é um pass-through, então vamos direto para 'ask_how_attention_is_called'
                session_state.current_node_id = "awaiting_attention_call_method"
                attention_node = nodes['ask_how_attention_is_called']
                return BotResponse(
                    session_id=session_id,
                    text=attention_node['prompt'],
                    response_type="single_choice",
                    options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                )
            else: # Resposta foi "Não"
                session_state.current_node_id = "awaiting_nao_path_examples"
                nao_path_node = nodes['nao_path']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(nao_path_node['options'])]
                return BotResponse(
                    session_id=session_id,
                    text=nao_path_node['prompt'],
                    response_type="multiple_choice",
                    options=options
                )

        # 3. Resposta aos exemplos do caminho "Não"
        if node == "awaiting_nao_path_examples":
            if not user_answer: # Se não selecionou nada, falhou
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")
            else: # Se selecionou algo, avança
                session_state.current_node_id = "awaiting_attention_call_method"
                attention_node = nodes['ask_how_attention_is_called']
                return BotResponse(
                    session_id=session_id,
                    text=attention_node['prompt'],
                    response_type="single_choice",
                    options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                )

        # 4. Resposta sobre como chama a atenção
        if node == "awaiting_attention_call_method":
            session_state.current_node_id = "awaiting_pointing_purpose"
            purpose_node = nodes['ask_pointing_purpose']
            options = [
                Option(id="both", label=purpose_node['options'][0]['label']),
                Option(id="help_only", label=purpose_node['options'][1]['label'])
            ]
            return BotResponse(
                session_id=session_id,
                text=purpose_node['prompt'],
                response_type="single_choice",
                options=options
            )

        # 5. Resposta final sobre o propósito de apontar
        if node == "awaiting_pointing_purpose":
            outcome = "PASSOU" if user_answer.lower() == "both" else "FALHOU"
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome=outcome)


        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 7.", is_item_finished=True, outcome="FALHOU")
    
    def process_question_8(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[8]['follow_up']
        nodes = logic_data['nodes']
        initial_answer = session_state.answers.get(str(8), "").lower()

        # 1. Início da entrevista para o item 8
        if user_answer == "":
            if initial_answer == 'sim':
                session_state.current_node_id = "awaiting_sim_path_start"
                node_data = nodes['sim_path_start']
                return BotResponse(
                    session_id=session_id, text=node_data['prompt'], response_type="single_choice",
                    options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                )
            else: # initial_answer == 'não'
                session_state.current_node_id = "awaiting_nao_path_start"
                node_data = nodes['nao_path_start']
                return BotResponse(
                    session_id=session_id, text=node_data['prompt'], response_type="single_choice",
                    options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                )

        # 2. Caminho do "Sim" inicial
        if node == "awaiting_sim_path_start":
            if user_answer.lower() == "sim":
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            else: # "Não"
                session_state.current_node_id = "awaiting_central_checklist"
                node_data = nodes['central_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="multiple_choice", options=options)

        # 3. Caminho do "Não" inicial
        if node == "awaiting_nao_path_start":
            if user_answer.lower() == "sim":
                session_state.current_node_id = "awaiting_nao_freq_check"
                node_data = nodes['nao_path_frequency_check']
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="single_choice", options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")])
            else: # "Não"
                session_state.current_node_id = "awaiting_central_checklist"
                node_data = nodes['central_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="multiple_choice", options=options)

        # 4. Verificação de frequência do caminho "Não"
        if node == "awaiting_nao_freq_check":
            outcome = "PASSOU" if user_answer.lower() == "sim" else "FALHOU"
            return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome=outcome)

        # 5. Lista de verificação central (para onde vários caminhos levam)
        if node == "awaiting_central_checklist":
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            if "none" in user_selections or not user_answer:
                outcome = "FALHOU"
            else:
                outcome = "PASSOU"
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome=outcome)
    def process_question_9(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[9]['follow_up']
        nodes = logic_data['nodes']

        # 1. Início da entrevista: Apresenta a lista de itens
        if user_answer == "":
            session_state.current_node_id = "awaiting_checklist"
            node_data = nodes['item_checklist']
            options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
            options.append(Option(id="none", label="Nenhuma das opções"))
            return BotResponse(
                session_id=session_id,
                text=node_data['prompt'],
                response_type="multiple_choice",
                options=options
            )

        # 2. Analisa a seleção da lista de itens
        if node == "awaiting_checklist":
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            if "none" in user_selections or not user_answer:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")
            else:
                # Se selecionou algum item, avança para a pergunta de intenção
                session_state.current_node_id = "awaiting_intent"
                node_data = nodes['ask_intent']
                options = [
                    Option(id="share", label=node_data['options'][0]['label']),
                    Option(id="help", label=node_data['options'][1]['label'])
                ]
                return BotResponse(
                    session_id=session_id,
                    text=node_data['prompt'],
                    response_type="single_choice",
                    options=options
                )
        
        # 3. Analisa a resposta sobre a intenção
        if node == "awaiting_intent":
            outcome = "PASSOU" if user_answer.lower() == "share" else "FALHOU"
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome=outcome)

        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 9.", is_item_finished=True, outcome="FALHOU")
    def process_question_10(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[10]['follow_up']

        if user_answer == "":
            session_state.current_node_id = "analysis"
            all_options = [Option(id=opt['id'], label=opt['label']) for opt in logic_data["exemplos_passou"] + logic_data["exemplos_falhou"]]
            return BotResponse(
                session_id=session_id, text=logic_data["interview_prompt"],
                response_type="multiple_choice", options=all_options
            )

        if node == "analysis":
            pass_ids = {ex['id'] for ex in logic_data["exemplos_passou"]}
            fail_ids = {ex['id'] for ex in logic_data["exemplos_falhou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            
            pass_count = sum(1 for sel in user_selections if sel in pass_ids)
            fail_count = sum(1 for sel in user_selections if sel in fail_ids)

            outcome = ""
            
            if pass_count > 0 and fail_count == 0:
                outcome = "PASSOU"
            elif fail_count > 0 and pass_count == 0:
                outcome = "FALHOU"
            elif pass_count > 0 and fail_count > 0:
                # Desempate automático baseado na contagem
                outcome = "PASSOU" if pass_count > fail_count else "FALHOU"
            else: # Nenhuma opção válida, pergunta novamente
                session_state.current_node_id = None
                return self.process_question_10(session_id, session_state, "")

            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome=outcome)
        
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo.", is_item_finished=True, outcome="FALHOU")
    def process_question_11(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[11]['follow_up']
        initial_answer = session_state.answers.get(str(11), "").lower()

        if initial_answer == "sim":
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

        # Início da entrevista para o caminho "Não"
        if user_answer == "":
            session_state.current_node_id = "analysis"
            on_nao_logic = logic_data["on_nao"]
            all_options = [Option(**opt) for opt in on_nao_logic["exemplos_passou"] + on_nao_logic["exemplos_falhou"]]
            return BotResponse(
                session_id=session_id,
                text=on_nao_logic["interview_prompt"],
                response_type="multiple_choice",
                options=all_options
            )

        if node == "analysis":
            on_nao_logic = logic_data["on_nao"]
            pass_ids = {ex['id'] for ex in on_nao_logic["exemplos_passou"]}
            fail_ids = {ex['id'] for ex in on_nao_logic["exemplos_falhou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            has_pass = any(sel in pass_ids for sel in user_selections)
            has_fail = any(sel in fail_ids for sel in user_selections)

            if has_pass and not has_fail:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")
            elif not has_pass and has_fail:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")
            elif has_pass and has_fail:
                session_state.current_node_id = "tiebreaker"
                tiebreaker_logic = on_nao_logic["tiebreaker"]
                
                # Junta os labels para criar as duas opções
                pass_labels = "; ".join([opt['label'] for opt in on_nao_logic["exemplos_passou"]])
                fail_labels = "; ".join([opt['label'] for opt in on_nao_logic["exemplos_falhou"]])
                
                options = [
                    Option(id="passou_freq", label=pass_labels),
                    Option(id="falhou_freq", label=fail_labels)
                ]
                return BotResponse(
                    session_id=session_id,
                    text=tiebreaker_logic["prompt"],
                    response_type="single_choice",
                    options=options
                )
            else:
                session_state.current_node_id = None
                return self.process_question_11(session_id, session_state, "")

        if node == "tiebreaker":
            outcome = "PASSOU" if user_answer.lower() == "passou_freq" else "FALHOU"
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

