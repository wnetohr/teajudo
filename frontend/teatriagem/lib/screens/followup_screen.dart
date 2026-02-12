import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_svg/flutter_svg.dart';
import '../models/api_models.dart';
import '../theme/app_text_styles.dart'; // Importa os estilos de texto padronizados
import 'dart:io' show Platform;
import 'result_screen.dart';

// Temporariamente suprime avisos de uso de membros obsoletos (Radio APIs).
// TODO: migrar para RadioGroup quando atualizar SDK/implementação.
// ignore_for_file: deprecated_member_use

// URL Base da API (mantém alinhado com questionnaire_screen)
const String _prodUrl = 'https://chatbot-mchatrf.onrender.com';
const bool isProduction = true;

String get aPIUrl {
  if (isProduction) {
    return '$_prodUrl/chat';
  }
  if (kIsWeb) {
    return 'http://localhost:8000/chat';
  }
  if (Platform.isAndroid) {
    return 'http://10.0.2.2:8000/chat';
  }
  return 'http://localhost:8000/chat';
}

class FollowUpScreen extends StatefulWidget {
  final String sessionId;
  const FollowUpScreen({super.key, required this.sessionId});

  @override
  State<FollowUpScreen> createState() => _FollowUpScreenState();
}

class _FollowUpScreenState extends State<FollowUpScreen> {
  BotResponse? _currentResponse;
  bool _isLoading = true;
  String? _errorMessage;
  final Set<String> _selected = {}; // para múltipla escolha
  String? _selectedSingle;

  @override
  void initState() {
    super.initState();
    _startFollowUp();
  }

  Future<void> _startFollowUp() async {
    await _sendAnswer(""); // inicia a entrevista de seguimento
  }

  Future<void> _sendAnswer(String answer) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final message = UserMessage(sessionId: widget.sessionId, text: answer);

      print('═════════════════════════════════════════');
      print('[ENVIANDO] Mensagem para API: ${message.toJson()}');
      print('[SESSION_ID] ${widget.sessionId}');
      print('═════════════════════════════════════════');

      final response = await http.post(
        Uri.parse(aPIUrl),
        headers: {'Content-Type': 'application/json'},
        body: message.toJson(),
      );

      print('═════════════════════════════════════════');
      print('[RESPOSTA_BRUTA] Status: ${response.statusCode}');
      print('[RESPOSTA_BODY] ${response.body}');
      print('═════════════════════════════════════════');

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        final jsonData = jsonDecode(decodedBody);

        print('═════════════════════════════════════════');
        print('[RESPOSTA_JSON COMPLETA - FOLLOW UP]');
        print(jsonEncode(jsonData));
        print('═════════════════════════════════════════');

        final responseData = BotResponse.fromJson(jsonData);

        // REMOVER LIMPEZA: Usar o texto original completo, não remover instruções
        String cleanedText = responseData.text;

        print('═════════════════════════════════════════');
        print('[BOT_RESPONSE_PARSED - FOLLOW UP]');
        print('Question ID: ${responseData.questionId}');
        print('Texto completo (SEM limpeza): $cleanedText');
        print('Tipo de resposta: ${responseData.responseType}');
        print('Número de opções: ${responseData.options.length}');
        print(
          'Opções: ${responseData.options.map((o) => '${o.id}: ${o.label}').join(' | ')}',
        );
        print('Item finalizado: ${responseData.isItemFinished}');
        print('Fim do formulário: ${responseData.endOfForm}');
        print('Resultado: ${responseData.outcome}');
        print('Score: ${responseData.score}');
        print('═════════════════════════════════════════');

        final responseToUse = BotResponse(
          sessionId: responseData.sessionId,
          text: cleanedText,
          responseType: responseData.responseType,
          options: responseData.options,
          isItemFinished: responseData.isItemFinished,
          endOfForm: responseData.endOfForm,
          outcome: responseData.outcome,
          score: responseData.score,
          questionId: responseData.questionId,
        );

        if (responseToUse.endOfForm) {
          print('✓ [NAVEGANDO] Indo para tela de resultado final');
          // Transiciona para a tela de resultado final
          if (mounted) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(
                builder: (_) =>
                    ResultScreen(response: responseData, allowFollowUp: false),
              ),
            );
          }
          return;
        }

        // Se o item foi concluído, mostra feedback e automaticamente continua
        // SEM atualizar a UI com a mensagem intermediária
        if (responseToUse.isItemFinished &&
            !responseToUse.endOfForm &&
            answer.isNotEmpty &&
            answer != 'continuar') {
          print(
            '✓ [ITEM_FINALIZADO] Item completado, aguardando ${answer != 'continuar' ? '1.5s' : '0s'} para continuar',
          );
          if (mounted) {
            _showFeedbackSnackBar();
            Future.delayed(const Duration(milliseconds: 1500), () {
              if (mounted) {
                _sendAnswer('continuar'); // Continua automaticamente
              }
            });
          }
          return; // Não atualiza o estado, mantém a pergunta anterior visível
        }

        setState(() {
          // Usa a versão 'cleaned' da resposta para atualizar a UI
          _currentResponse = responseToUse;
          _isLoading = false;
          _selected.clear();
          _selectedSingle = null;
        });

        print('✓ [PERGUNTA_ATUALIZADA] Pergunta exibida no Follow Up');

        // Mostra feedback após responder (apenas para respostas normais, não para 'continuar')
        if (answer.isNotEmpty && answer != 'continuar' && mounted) {
          _showFeedbackSnackBar();
        }
      } else {
        throw Exception('Falha ao carregar dados da API');
      }
    } catch (e) {
      print('═════════════════════════════════════════');
      print('✗ [ERRO] $e');
      print('═════════════════════════════════════════');
      setState(() {
        _isLoading = false;
        _errorMessage = 'Erro de conexão: $e';
      });
    }
  }

  Widget _buildOptions() {
    if (_currentResponse == null) return const SizedBox.shrink();

    if (_currentResponse!.responseType == 'multiple_choice') {
      return Column(
        children: _currentResponse!.options.map((opt) {
          final checked = _selected.contains(opt.id);
          return CheckboxListTile(
            title: Text(opt.label),
            value: checked,
            onChanged: (v) {
              setState(() {
                if (v == true) {
                  _selected.add(opt.id);
                } else {
                  _selected.remove(opt.id);
                }
              });
            },
          );
        }).toList(),
      );
    }

    if (_currentResponse!.responseType == 'single_choice') {
      return Column(
        children: _currentResponse!.options.map((opt) {
          return RadioListTile<String>(
            title: Text(opt.label),
            value: opt.id,
            groupValue: _selectedSingle,
            onChanged: (v) {
              setState(() {
                _selectedSingle = v;
              });
            },
          );
        }).toList(),
      );
    }

    // Fallback: mostra texto simples se não houver opções
    return const SizedBox.shrink();
  }

  void _showFeedbackSnackBar() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: const [
            Icon(Icons.check_circle, color: Colors.white, size: 24),
            SizedBox(width: 12),
            Text(
              'Resposta registrada!',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            ),
          ],
        ),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        margin: const EdgeInsets.all(16),
        duration: const Duration(milliseconds: 1200),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Se question_id == 1: exibe texto completo (ambos parágrafos)
    // Se question_id != 1: remove o primeiro parágrafo e exibe só a pergunta limpa
    String displayText = _currentResponse?.text ?? '';
    bool isFirstQuestion = _currentResponse?.questionId == 1;

    if (!isFirstQuestion &&
        _currentResponse != null &&
        displayText.contains('\n\n')) {
      // Para perguntas que não são a primeira, remove o cabeçalho
      final parts = displayText.split('\n\n');
      if (parts.length > 1) {
        displayText = parts.sublist(1).join('\n\n').trim();
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Entrevista de Seguimento',
          style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: _isLoading && _currentResponse == null
              ? const CircularProgressIndicator()
              : _errorMessage != null
              ? Text(_errorMessage!, style: const TextStyle(color: Colors.red))
              : _currentResponse == null
              ? const Text('Iniciando entrevista...')
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Text(displayText, style: AppTextStyles.question),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Expanded(
                      child: SingleChildScrollView(child: _buildOptions()),
                    ),
                    const SizedBox(height: 12),
                    // Para múltipla escolha permitimos enviar mesmo sem seleção.
                    // Se a API fornecer uma opção com id 'none', enviamos 'none'.
                    // Caso contrário, enviamos string vazia (o backend deve interpretar).
                    if (_currentResponse!.responseType == 'multiple_choice' &&
                        _selected.isEmpty)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 8.0),
                        child: Text(
                          'Nenhuma opção marcada — vamos registrar "Nenhuma das opções acima".',
                          style: AppTextStyles.bodySmall,
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ElevatedButton(
                      onPressed:
                          (_currentResponse!.responseType == 'multiple_choice'
                              ? true // sempre permite enviar; payload tratado abaixo
                              : (_selectedSingle != null))
                          ? () {
                              String payload;
                              if (_currentResponse!.responseType ==
                                  'multiple_choice') {
                                if (_selected.isNotEmpty) {
                                  payload = _selected.join(',');
                                } else {
                                  // Sempre enviar 'none' quando nada foi selecionado.
                                  // Enviar string vazia faz o backend interpretar como chamada inicial.
                                  payload = 'none';
                                }
                              } else {
                                payload = _selectedSingle!;
                              }
                              _sendAnswer(payload);
                            }
                          : null,
                      child: const Text('Enviar'),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}
