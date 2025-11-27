import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/api_models.dart';
import 'dart:io' show Platform;
import 'result_screen.dart';

// Helper para escolher host conforme plataforma (duplica lógica do questionnaire)
String get aPIUrl {
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
      debugPrint('FollowUp: sending payload -> "${answer}" (session=${widget.sessionId})');
      final message = UserMessage(sessionId: widget.sessionId, text: answer);
      final response = await http.post(
        Uri.parse(aPIUrl),
        headers: {'Content-Type': 'application/json'},
        body: message.toJson(),
      );

      if (response.statusCode == 200) {
        final responseData = BotResponse.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));

        // Se o backend retornar um cabeçalho + pergunta (separados por duas quebras de linha),
        // removemos o cabeçalho e usamos apenas a parte da pergunta aqui.
        String cleanedText = responseData.text;
        if (cleanedText.contains('\n\n')) {
          final parts = cleanedText.split('\n\n');
          if (parts.length > 1) {
            // Mantemos somente a parte após o primeiro bloco de texto (a pergunta)
            cleanedText = parts.sublist(1).join('\n\n');
          }
        }

        final responseToUse = BotResponse(
          sessionId: responseData.sessionId,
          text: cleanedText,
          responseType: responseData.responseType,
          options: responseData.options,
          isItemFinished: responseData.isItemFinished,
          endOfForm: responseData.endOfForm,
          outcome: responseData.outcome,
          score: responseData.score,
        );

        debugPrint('FollowUp: parsed responseType=${responseData.responseType}; isItemFinished=${responseData.isItemFinished}; endOfForm=${responseData.endOfForm}');
        debugPrint('FollowUp: options -> ${responseData.options.map((o) => o.id).toList()}');

        if (responseToUse.endOfForm) {
          // Transiciona para a tela de resultado final
          if (mounted) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => ResultScreen(response: responseData)),
            );
          }
          return;
        }

        setState(() {
          // Usa a versão 'cleaned' da resposta para atualizar a UI
          _currentResponse = responseToUse;
          // DEBUG: log resposta bruta e texto
          debugPrint('FollowUp: response status=${response.statusCode}');
          debugPrint('FollowUp: response body (text) -> ${responseData.text}');
          _isLoading = false;
          _selected.clear();
          _selectedSingle = null;
        });
      } else {
        throw Exception('Falha ao carregar dados da API');
      }
    } catch (e) {
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Entrevista de Seguimento')),
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
                                child: Text(
                                  _currentResponse!.text,
                                  style: Theme.of(context).textTheme.titleLarge,
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                            Expanded(child: SingleChildScrollView(child: _buildOptions())),
                            const SizedBox(height: 12),
                            // Se o item foi concluído mas o formulário não terminou,
                            // o backend pede para enviar 'continuar' para iniciar o próximo follow-up.
                            if (_currentResponse!.isItemFinished && !_currentResponse!.endOfForm) ...[
                              ElevatedButton(
                                onPressed: () => _sendAnswer('continuar'),
                                child: const Text('Continuar'),
                              ),
                            ] else ...[
                              // Para múltipla escolha permitimos enviar mesmo sem seleção.
                              // Se a API fornecer uma opção com id 'none', enviamos 'none'.
                              // Caso contrário, enviamos string vazia (o backend deve interpretar).
                              if (_currentResponse!.responseType == 'multiple_choice' && _selected.isEmpty)
                                Padding(
                                  padding: const EdgeInsets.only(bottom: 8.0),
                                  child: Text(
                                    'Nenhuma opção selecionada — será enviado "none".',
                                    style: Theme.of(context).textTheme.bodySmall,
                                    textAlign: TextAlign.center,
                                  ),
                                ),
                              ElevatedButton(
                                onPressed: (_currentResponse!.responseType == 'multiple_choice'
                                        ? true // sempre permite enviar; payload tratado abaixo
                                        : (_selectedSingle != null))
                                    ? () {
                                        String payload;
                                        if (_currentResponse!.responseType == 'multiple_choice') {
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
                          ],
                        ),
        ),
      ),
    );
  }
}
