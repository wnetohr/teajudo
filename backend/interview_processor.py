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
        Refatorado para garantir que a lógica de finalização/transição sempre execute.
        """
        response = None
        is_initial_call = user_answer == "" and session_state.current_node_id is None
        is_continue_call = user_answer.lower() == "continuar" and session_state.current_node_id is None

        # Determina qual método específico da pergunta chamar
        if is_initial_call or is_continue_call:
            question_id = session_state.follow_up_needed[session_state.current_follow_up_index]
            process_method = self.method_factory.get(question_id, self.process_not_implemented)
            response = process_method(session_id, session_state, "") # Inicia a entrevista do item
        else:
            # Processamento normal de uma resposta no meio de uma entrevista de item
            question_id = session_state.follow_up_needed[session_state.current_follow_up_index]
            process_method = self.method_factory.get(question_id, self.process_not_implemented)
            response = process_method(session_id, session_state, user_answer)

        # Adiciona a mensagem inicial apenas na primeira chamada da entrevista inteira
        if is_initial_call:
             initial_message = (f"Triagem inicial finalizada. Pontuação: {session_state.score} (Risco Médio).\n\n"
                               f"Agora, vamos iniciar uma entrevista para obter mais informações sobre as respostas de risco.")
             response.text = initial_message + "\n\n" + response.text

        # AGORA, a lógica de finalização/transição é executada APÓS a chamada do método específico
        if response and response.is_item_finished:
            session_state.current_follow_up_index += 1
            session_state.current_node_id = None 

            if session_state.current_follow_up_index >= len(session_state.follow_up_needed):
                # Marca fim de formulário e calcula a recomendação final baseada na pontuação
                score = session_state.score
                disclaimer = "\n\nLembre-se: esta é uma ferramenta de triagem e não um diagnóstico. Os resultados devem ser discutidos com um pediatra ou profissional de saúde qualificado."

                if score <= 2:
                    final_text = (f"Entrevista de seguimento concluída! Pontuação final: {score} (Baixo Risco). "
                                  f"Não é necessário procurar um neuropediatra neste momento.")
                elif score >= 8:
                    final_text = (f"Entrevista de seguimento concluída! Pontuação final: {score} (Risco Elevado). "
                                  f"Recomenda-se procurar um neuropediatra/serviço de avaliação especializada o quanto antes.")
                else:
                    final_text = (f"Entrevista de seguimento concluída! Pontuação final: {score} (Risco Médio). "
                                  f"Recomenda-se discutir os resultados com o pediatra; considerar encaminhamento para neuropediatra se houver preocupação clínica.")

                response.text += "\n\n" + final_text + disclaimer
                response.end_of_form = True
                response.score = score
            else:
                next_question_id = session_state.follow_up_needed[session_state.current_follow_up_index]
                response.text += f"\n\nOk, item concluído. Envie 'continuar' para iniciar a entrevista da pergunta {next_question_id}."
        
        return response

    # --- Implementações dos Métodos ---
    # (process_question_1 a process_question_12 permanecem iguais)

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

            pass_count = sum(1 for sel in user_selections if sel in pass_ids)
            fail_count = sum(1 for sel in user_selections if sel in fail_ids)

            if pass_count == 0 and fail_count == 0:
                session_state.current_node_id = None
                return self.process_question_1(session_id, session_state, "")

            if pass_count > fail_count:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

            if fail_count > pass_count:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")

            session_state.current_node_id = "tiebreaker"
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

        elif node == "tiebreaker":
            outcome = "FALHOU"
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

        if user_answer == "":
            session_state.current_node_id = "analysis"
            return BotResponse(
                session_id=session_id,
                text=logic_data["interview_prompt"],
                response_type="multiple_choice",
                options=[Option(**opt) for opt in logic_data["exemplos_passou"]]
            )
        
        if node == "analysis":
            pass_ids = {ex['id'] for ex in logic_data["exemplos_passou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
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

        if user_answer == "":
            session_state.current_node_id = "analysis"
            return BotResponse(
                session_id=session_id,
                text=logic_data["interview_prompt"],
                response_type="multiple_choice",
                options=[Option(**opt) for opt in logic_data["exemplos_passou"]]
            )
        
        if node == "analysis":
            pass_ids = {ex['id'] for ex in logic_data["exemplos_passou"]}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
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

        if initial_answer == "não":
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

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

            if not has_fail:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")
            else:
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

        if initial_answer == "sim":
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

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
            
            if not user_answer or not user_selections:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")
            
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

        if user_answer == "":
            session_state.current_node_id = "awaiting_intro"
            return BotResponse(
                session_id=session_id,
                text=logic_data['intro_text'],
                response_type="single_choice",
                options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
            )

        if node == "awaiting_intro":
            if user_answer.lower() == "sim":
                session_state.current_node_id = "awaiting_attention_call_method"
                attention_node = nodes['ask_how_attention_is_called']
                return BotResponse(
                    session_id=session_id,
                    text=attention_node['prompt'],
                    response_type="single_choice",
                    options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                )
            else:
                session_state.current_node_id = "awaiting_nao_path_examples"
                nao_path_node = nodes['nao_path']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(nao_path_node['options'])]
                return BotResponse(
                    session_id=session_id,
                    text=nao_path_node['prompt'],
                    response_type="multiple_choice",
                    options=options
                )

        if node == "awaiting_nao_path_examples":
            if not user_answer:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")
            else:
                session_state.current_node_id = "awaiting_attention_call_method"
                attention_node = nodes['ask_how_attention_is_called']
                return BotResponse(
                    session_id=session_id,
                    text=attention_node['prompt'],
                    response_type="single_choice",
                    options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                )

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

        if node == "awaiting_pointing_purpose":
            outcome = "PASSOU" if user_answer.lower() == "both" else "FALHOU"
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome=outcome)


        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 7.", is_item_finished=True, outcome="FALHOU")

    def process_question_8(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[8]['follow_up']
        nodes = logic_data['nodes']
        initial_answer = session_state.answers.get(str(8), "").lower()

        if user_answer == "":
            if initial_answer == 'sim':
                session_state.current_node_id = "awaiting_sim_path_start"
                node_data = nodes['sim_path_start']
                return BotResponse(
                    session_id=session_id, text=node_data['prompt'], response_type="single_choice",
                    options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                )
            else:
                session_state.current_node_id = "awaiting_nao_path_start"
                node_data = nodes['nao_path_start']
                return BotResponse(
                    session_id=session_id, text=node_data['prompt'], response_type="single_choice",
                    options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                )

        if node == "awaiting_sim_path_start":
            if user_answer.lower() == "sim":
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            else:
                session_state.current_node_id = "awaiting_central_checklist"
                node_data = nodes['central_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="multiple_choice", options=options)

        if node == "awaiting_nao_path_start":
            if user_answer.lower() == "sim":
                session_state.current_node_id = "awaiting_nao_freq_check"
                node_data = nodes['nao_path_frequency_check']
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="single_choice", options=[Option(id="sim", label="Sim"), Option(id="nao", label="Não")])
            else:
                session_state.current_node_id = "awaiting_central_checklist"
                node_data = nodes['central_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="multiple_choice", options=options)

        if node == "awaiting_nao_freq_check":
            outcome = "PASSOU" if user_answer.lower() == "sim" else "FALHOU"
            return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome=outcome)

        if node == "awaiting_central_checklist":
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            if "none" in user_selections or not user_answer:
                outcome = "FALHOU"
            else:
                outcome = "PASSOU"
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome=outcome)

        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 8.", is_item_finished=True, outcome="FALHOU")

    def process_question_9(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[9]['follow_up']
        nodes = logic_data['nodes']

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

        if node == "awaiting_checklist":
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            if "none" in user_selections or not user_answer:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")
            else:
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
                outcome = "PASSOU" if pass_count > fail_count else "FALHOU"
            else:
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

    def process_question_12(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[12]['follow_up']
        initial_answer = session_state.answers.get(str(12), "").lower()

        if initial_answer == "não":
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

        on_sim_logic = logic_data.get('on_sim', {})
        nodes = on_sim_logic.get('nodes', {})

        if user_answer == "":
            session_state.current_node_id = "noise_checklist"
            node_data = nodes.get('noise_checklist', {})
            options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data.get('options', []))]
            return BotResponse(
                session_id=session_id, text=node_data.get('prompt', ''),
                response_type="multiple_choice", options=options
            )

        if node == "noise_checklist":
            user_selections = {item.strip().lower() for item in user_answer.split(',')} if user_answer else set()
            if len(user_selections) < 2:
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            else:
                session_state.current_node_id = "reaction_checklist"
                node_data = nodes.get('reaction_checklist', {})
                all_options = [Option(**opt) for opt in node_data.get("exemplos_passou", []) + node_data.get("exemplos_falhou", [])]
                return BotResponse(
                    session_id=session_id, text=node_data.get('prompt', ''),
                    response_type="multiple_choice", options=all_options
                )

        if node == "reaction_checklist":
            node_data = nodes.get('reaction_checklist', {})
            pass_ids = {ex['id'] for ex in node_data.get("exemplos_passou", [])}
            fail_ids = {ex['id'] for ex in node_data.get("exemplos_falhou", [])}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            has_pass = any(sel in pass_ids for sel in user_selections)
            has_fail = any(sel in fail_ids for sel in user_selections)

            if has_pass and not has_fail:
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            elif not has_pass and has_fail:
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="FALHOU")
            elif has_pass and has_fail:
                 session_state.current_node_id = "tiebreaker"
                 tiebreaker_logic = node_data.get("tiebreaker", {})
                 pass_labels = "; ".join([opt['label'] for opt in node_data.get("exemplos_passou", [])])
                 fail_labels = "; ".join([opt['label'] for opt in node_data.get("exemplos_falhou", [])])
                 options = [Option(id="passou_freq", label=pass_labels), Option(id="falhou_freq", label=fail_labels)]
                 return BotResponse(session_id=session_id, text=tiebreaker_logic.get('prompt', ''), response_type="single_choice", options=options)
            else:
                 session_state.current_node_id = "noise_checklist"
                 return self.process_question_12(session_id, session_state, "")
        
        if node == "tiebreaker":
            outcome = "PASSOU" if user_answer.lower() == "passou_freq" else "FALHOU"
            return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome=outcome)

        return BotResponse(session_id=session_id, text="Houve um erro no fluxo.", is_item_finished=True, outcome="FALHOU")

    def process_question_13(self, session_id, session_state, user_answer):
        logic_data = self.questions[13]['follow_up']
        initial_answer = session_state.answers.get(str(13), "").lower()

        # Rota para resposta inicial "Não" (risco), que falha imediatamente no seguimento
        if initial_answer == "não":
            # A entrevista para este item nem começa formalmente, o resultado já está definido.
            return BotResponse(
                session_id=session_id,
                text="Para esta pergunta, a resposta inicial ('Não') já define o resultado do seguimento como FALHOU.",
                is_item_finished=True,
                outcome="FALHOU"
            )

        # Rota para resposta inicial "Sim" (sem risco), que aciona a entrevista de clarificação
        # A entrevista só começa se a resposta do usuário for vazia
        if user_answer == "":
            session_state.current_node_id = "clarification"
            on_sim_logic = logic_data["on_sim"]
            options = [
                Option(id="sim", label=on_sim_logic["options"][0]["label"]),
                Option(id="nao", label=on_sim_logic["options"][1]["label"])
            ]
            return BotResponse(
                session_id=session_id,
                text=on_sim_logic["prompt"],
                response_type="single_choice",
                options=options
            )

        # Processa a resposta da pergunta de clarificação
        if session_state.current_node_id == "clarification":
            outcome = "PASSOU" if user_answer.lower() == "sim" else "FALHOU"
            return BotResponse(
                session_id=session_id,
                text="Ok, entendido.",
                is_item_finished=True,
                outcome=outcome
            )
        
        # Fallback de segurança
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 13.", is_item_finished=True, outcome="FALHOU")

    def process_question_14(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[14]['follow_up']
        nodes = logic_data['nodes']
        # initial_answer = session_state.answers.get(str(14), "").lower() # Não é necessário para este fluxo

        # Início da entrevista para o item 14 (vai direto para checklist)
        if user_answer == "":
            session_state.current_node_id = "awaiting_checklist"
            node_data = nodes['situation_checklist']
            options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
            options.append(Option(id="none", label="Nenhuma das opções"))
            return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="multiple_choice", options=options)

        # Processa a resposta da lista de situações
        if node == "awaiting_checklist":
            user_selections = {item.strip().lower() for item in user_answer.split(',')} if user_answer else set()
            count = len(user_selections) if "none" not in user_selections else 0

            if count == 0:
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="FALHOU")
            elif count >= 2:
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            elif count == 1:
                session_state.current_node_id = "awaiting_daily_check"
                node_data = nodes['daily_check']
                options = [Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="single_choice", options=options)

        # Processa a resposta da verificação diária
        if node == "awaiting_daily_check":
            if user_answer.lower() == "sim":
                session_state.current_node_id = "awaiting_five_times_check"
                node_data = nodes['five_times_check']
                options = [Option(id="sim", label="Sim"), Option(id="nao", label="Não")]
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="single_choice", options=options)
            else: # "Não"
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="FALHOU")

        # Processa a resposta da verificação de 5 vezes
        if node == "awaiting_five_times_check":
            outcome = "PASSOU" if user_answer.lower() == "sim" else "FALHOU"
            return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome=outcome)

        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 14.", is_item_finished=True, outcome="FALHOU")
    def process_question_15(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[15]['follow_up']

        # Início da entrevista: Apresenta a lista de exemplos de imitação
        if user_answer == "":
            session_state.current_node_id = "analysis"
            options = [Option(**opt) for opt in logic_data["options"]]
            # Adiciona a opção "Nenhuma das opções" para clareza
            options.append(Option(id="none", label="Nenhuma das opções"))
            return BotResponse(
                session_id=session_id,
                text=logic_data["interview_prompt"],
                response_type="multiple_choice",
                options=options
            )
        
        # Análise da resposta do usuário
        if node == "analysis":
            user_selections = {item.strip().lower() for item in user_answer.split(',')} if user_answer else set()
            
            # Conta quantas opções válidas (diferentes de 'none') foram selecionadas
            valid_selection_count = sum(1 for sel in user_selections if sel != "none")

            # Aplica a regra: 2 ou mais seleções = PASSOU, 1 ou 0 = FALHOU
            outcome = "PASSOU" if valid_selection_count >= 2 else "FALHOU"

            return BotResponse(
                session_id=session_id,
                text="Ok, entendido.",
                is_item_finished=True,
                outcome=outcome
            )
        
        # Fallback de segurança
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 15.", is_item_finished=True, outcome="FALHOU")
    
    def process_question_16(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[16]['follow_up']
        initial_answer = session_state.answers.get(str(16), "").lower()

        # Rota para resposta inicial "Sim" (sem risco)
        if initial_answer == "sim":
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

        # Rota para resposta inicial "Não" (risco), aciona a entrevista
        on_nao_logic = logic_data.get("on_nao", {})

        # Início da entrevista para o caminho "Não"
        if user_answer == "":
            session_state.current_node_id = "analysis"
            all_options = [Option(**opt) for opt in on_nao_logic.get("exemplos_passou", []) + on_nao_logic.get("exemplos_falhou", [])]
            return BotResponse(
                session_id=session_id,
                text=on_nao_logic.get("interview_prompt", ""),
                response_type="multiple_choice",
                options=all_options
            )

        # Análise das respostas
        if node == "analysis":
            pass_ids = {ex['id'] for ex in on_nao_logic.get("exemplos_passou", [])}
            fail_ids = {ex['id'] for ex in on_nao_logic.get("exemplos_falhou", [])}
            user_selections = {item.strip().lower() for item in user_answer.split(',')}
            has_pass = any(sel in pass_ids for sel in user_selections)
            has_fail = any(sel in fail_ids for sel in user_selections)

            if has_pass and not has_fail:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")
            elif not has_pass and has_fail:
                return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="FALHOU")
            elif has_pass and has_fail:
                session_state.current_node_id = "tiebreaker"
                tiebreaker_logic = on_nao_logic.get("tiebreaker", {})
                
                # **AJUSTE TIEBREAKER:** Mostrar os exemplos reais
                pass_labels_list = [opt['label'] for opt in on_nao_logic.get("exemplos_passou", [])]
                fail_labels_list = [opt['label'] for opt in on_nao_logic.get("exemplos_falhou", [])]
                pass_label_str = "Comportamentos como: " + "; ".join(pass_labels_list)
                fail_label_str = "Comportamentos como: " + "; ".join(fail_labels_list)
                
                options = [
                    Option(id="passou_freq", label=pass_label_str),
                    Option(id="falhou_freq", label=fail_label_str)
                ]
                return BotResponse(
                    session_id=session_id,
                    text=tiebreaker_logic.get("prompt", "Qual destes conjuntos de comportamento é mais frequente?"),
                    response_type="single_choice",
                    options=options
                )
            else: # Resposta inválida
                session_state.current_node_id = None
                return self.process_question_16(session_id, session_state, "")

        # Processa a resposta do tiebreaker
        if node == "tiebreaker":
            outcome = "PASSOU" if user_answer.lower() == "passou_freq" else "FALHOU"
            return BotResponse(
                session_id=session_id,
                text="Ok, obrigado pela clarificação.",
                is_item_finished=True,
                outcome=outcome
            )

        # Fallback de segurança
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 16.", is_item_finished=True, outcome="FALHOU")
    def process_question_17(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[17]['follow_up']

        # 1. Início da entrevista: Apresenta a lista de exemplos
        if user_answer == "":
            session_state.current_node_id = "analysis"
            
            # Cria a lista de opções a partir dos "exemplos_passou"
            options = [Option(**opt) for opt in logic_data["exemplos_passou"]]
            # Adiciona a opção "Nenhuma das opções" conforme solicitado
            options.append(Option(id="none", label="Nenhuma das opções"))
            
            return BotResponse(
                session_id=session_id,
                text=logic_data["interview_prompt"],
                response_type="multiple_choice",
                options=options
            )
        
        # 2. Análise da resposta do usuário
        if node == "analysis":
            user_selections = {item.strip().lower() for item in user_answer.split(',')} if user_answer else set()

            # Lógica: Se o usuário selecionou 'none' OU não selecionou nada, é FALHOU.
            # Se selecionou qualquer outra opção (que só pode ser um 'passou'), o resultado é PASSOU.
            if "none" in user_selections or not user_selections:
                outcome = "FALHOU"
            else:
                outcome = "PASSOU"

            return BotResponse(
                session_id=session_id,
                text="Ok, entendido.",
                is_item_finished=True,
                outcome=outcome
            )
        
        # Fallback de segurança
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 17.", is_item_finished=True, outcome="FALHOU")
    def process_question_18(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[18]['follow_up']
        initial_answer = session_state.answers.get(str(18), "").lower()

        # 1. Início da entrevista - bifurca baseado na resposta inicial
        if user_answer == "":
            if initial_answer == 'sim':
                session_state.current_node_id = "awaiting_sim_path"
                node_data = logic_data["on_sim"]['nodes']['sim_path_start']
                options = [
                    Option(id="no_cue", label=node_data["options"][0]["label"]), # "Não, ele entendeu a ordem sem nenhuma dica."
                    Option(id="yes_cue", label=node_data["options"][1]["label"]) # "Sim, o exemplo que pensei tinha alguma dica."
                ]
                return BotResponse(session_id=session_id, text=node_data["prompt"], response_type="single_choice", options=options)
            
            else: # initial_answer == 'não'
                session_state.current_node_id = "awaiting_nao_path"
                node_data = logic_data["on_nao"]['nodes']['nao_path_start']
                options = [
                    Option(id="sim", label=node_data["options"][0]["label"]),
                    Option(id="nao", label=node_data["options"][1]["label"])
                ]
                return BotResponse(session_id=session_id, text=node_data["prompt"], response_type="single_choice", options=options)

        # 2. Processa o caminho do "Sim" inicial
        if node == "awaiting_sim_path":
            if user_answer.lower() == "no_cue":
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            else: # "yes_cue"
                session_state.current_node_id = "awaiting_no_cues_checklist"
                node_data = logic_data['nodes']['no_cues_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="multiple_choice", options=options)

        # 3. Processa o caminho do "Não" inicial
        if node == "awaiting_nao_path":
            if user_answer.lower() == "sim": # JSON diz: "Sim" -> "no_cues_checklist"
                session_state.current_node_id = "awaiting_no_cues_checklist"
                node_data = logic_data['nodes']['no_cues_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="multiple_choice", options=options)
            else: # "Não" -> "dinnertime_check"
                session_state.current_node_id = "awaiting_dinnertime_check"
                node_data = logic_data["on_nao"]['nodes']['dinnertime_check']
                options = [
                    Option(id="sim", label=node_data["options"][0]["label"]),
                    Option(id="nao", label=node_data["options"][1]["label"])
                ]
                return BotResponse(session_id=session_id, text=node_data["prompt"], response_type="single_choice", options=options)

        # 4. Processa a resposta do "Dinnertime Check"
        if node == "awaiting_dinnertime_check":
            if user_answer.lower() == "sim": # JSON diz: "Sim" -> "no_cues_checklist"
                session_state.current_node_id = "awaiting_no_cues_checklist"
                node_data = logic_data['nodes']['no_cues_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(session_id=session_id, text=node_data['prompt'], response_type="multiple_choice", options=options)
            else: # "Não" -> "final_falhou"
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="FALHOU")

        # 5. Processa a lista de verificação final (destino comum)
        if node == "awaiting_no_cues_checklist":
            user_selections = {item.strip().lower() for item in user_answer.split(',')} if user_answer else set()
            if "none" in user_selections or not user_answer:
                outcome = "FALHOU"
            else:
                outcome = "PASSOU"
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome=outcome)

        # Fallback
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 18.", is_item_finished=True, outcome="FALHOU")
    
    def process_question_19(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[19]['follow_up']
        initial_answer = session_state.answers.get(str(19), "").lower()

        # Rota para resposta inicial "Sim" (sem risco)
        if initial_answer == "sim":
            return BotResponse(session_id=session_id, text="Ok, entendido.", is_item_finished=True, outcome="PASSOU")

        # Rota para resposta inicial "Não" (risco), aciona a entrevista
        on_nao_logic = logic_data.get('on_nao', {})
        nodes = on_nao_logic.get('nodes', {})

        # 1. Início da entrevista (o user_answer == "" inicia o primeiro nó)
        if user_answer == "":
            session_state.current_node_id = "awaiting_noise_check"
            node_data = nodes.get('startling_noise_check', {})
            options = [
                Option(id="sim", label=node_data.get('options', [{}])[0].get('label', 'Sim')),
                Option(id="nao", label=node_data.get('options', [{}, {}])[1].get('label', 'Não'))
            ]
            return BotResponse(
                session_id=session_id,
                text=node_data.get('prompt', 'Seu filho ouve um barulho estranho?'),
                response_type="single_choice",
                options=options
            )

        # 2. Processa a resposta do "startling_noise_check"
        if node == "awaiting_noise_check":
            if user_answer.lower() == "sim":
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            else: # "Não"
                session_state.current_node_id = "awaiting_stranger_check"
                node_data = nodes.get('stranger_check', {})
                options = [
                    Option(id="sim", label=node_data.get('options', [{}])[0].get('label', 'Sim')),
                    Option(id="nao", label=node_data.get('options', [{}, {}])[1].get('label', 'Não'))
                ]
                return BotResponse(
                    session_id=session_id,
                    text=node_data.get('prompt', 'Pessoa estranha se aproxima?'),
                    response_type="single_choice",
                    options=options
                )

        # 3. Processa a resposta do "stranger_check"
        if node == "awaiting_stranger_check":
            if user_answer.lower() == "sim":
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            else: # "Não"
                session_state.current_node_id = "awaiting_scary_check"
                node_data = nodes.get('scary_thing_check', {})
                options = [
                    Option(id="sim", label=node_data.get('options', [{}])[0].get('label', 'Sim')),
                    Option(id="nao", label=node_data.get('options', [{}, {}])[1].get('label', 'Não'))
                ]
                return BotResponse(
                    session_id=session_id,
                    text=node_data.get('prompt', 'Vê algo não familiar?'),
                    response_type="single_choice",
                    options=options
                )

        # 4. Processa a resposta do "scary_thing_check"
        if node == "awaiting_scary_check":
            outcome = "PASSOU" if user_answer.lower() == "sim" else "FALHOU"
            return BotResponse(
                session_id=session_id,
                text="Ok.",
                is_item_finished=True,
                outcome=outcome
            )

        # Fallback de segurança
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 19.", is_item_finished=True, outcome="FALHOU")
    def process_question_20(self, session_id, session_state, user_answer):
        node = session_state.current_node_id
        logic_data = self.questions[20]['follow_up']
        initial_answer = session_state.answers.get(str(20), "").lower()

        # 1. Início da entrevista (user_answer == "")
        if user_answer == "":
            if initial_answer == "não":
                # Resposta inicial "Não" vai direto para a lista de reações
                session_state.current_node_id = "awaiting_reaction_checklist"
                node_data = logic_data['nodes']['reaction_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(
                    session_id=session_id,
                    text=node_data['prompt'],
                    response_type="multiple_choice",
                    options=options
                )
            else: # Resposta inicial "Sim"
                # Vai para a pergunta de clarificação
                session_state.current_node_id = "awaiting_clarification"
                node_data = logic_data['on_sim']['nodes']['clarification_check']
                options = [
                    Option(id="sim", label=node_data['options'][0]['label']),
                    Option(id="nao", label=node_data['options'][1]['label'])
                ]
                return BotResponse(
                    session_id=session_id,
                    text=node_data['prompt'],
                    response_type="single_choice",
                    options=options
                )

        # 2. Processa a resposta da "clarificação" (do caminho "Sim" inicial)
        if node == "awaiting_clarification":
            if user_answer.lower() == "sim":
                return BotResponse(session_id=session_id, text="Ok.", is_item_finished=True, outcome="PASSOU")
            else: # "Não"
                # Vai para a lista de reações
                session_state.current_node_id = "awaiting_reaction_checklist"
                node_data = logic_data['nodes']['reaction_checklist']
                options = [Option(id=f"opt{i+1}", label=opt['label']) for i, opt in enumerate(node_data['options'])]
                options.append(Option(id="none", label="Nenhuma das opções"))
                return BotResponse(
                    session_id=session_id,
                    text=node_data['prompt'],
                    response_type="multiple_choice",
                    options=options
                )
        
        # 3. Processa a resposta da "lista de reações" (destino comum)
        if node == "awaiting_reaction_checklist":
            user_selections = {item.strip().lower() for item in user_answer.split(',')} if user_answer else set()
            
            # Se selecionou "none" ou nada, falhou. Qualquer outra seleção é "PASSOU".
            if "none" in user_selections or not user_selections:
                outcome = "FALHOU"
            else:
                outcome = "PASSOU"
                
            return BotResponse(
                session_id=session_id,
                text="Ok, entendido.",
                is_item_finished=True,
                outcome=outcome
            )

        # Fallback de segurança
        return BotResponse(session_id=session_id, text="Houve um erro no fluxo da pergunta 20.", is_item_finished=True, outcome="FALHOU")
    # --- Métodos de Placeholder (agora eles não avançam o fluxo) ---
    def process_not_implemented(self, session_id, session_state):
        q_id = session_state.follow_up_needed[session_state.current_follow_up_index]
        return BotResponse(
            session_id=session_id,
            text=f"A lógica para a Pergunta {q_id} ainda não foi implementada. Por favor, envie 'continuar' para pular.",
            is_item_finished=True,
            outcome="FALHOU" # Assume FALHOU para itens não implementados
        )
        

