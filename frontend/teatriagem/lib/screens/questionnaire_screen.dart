import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

import '../models/api_models.dart'; // Importa os modelos de dados
import 'result_screen.dart'; // Importa a tela de resultado

// URL Base da sua API no Render
const String _prodUrl = 'https://chatbot-mchatrf.onrender.com';

// Se quiser voltar a testar localmente no futuro, apenas mude para false
const bool isProduction = true; 

String get aPIUrl {
  if (isProduction) {
    // Na nuvem, funciona igual para Android, iOS e Web
    return '$_prodUrl/chat';
  }

  // --- LÓGICA ANTIGA (PARA TESTE LOCAL NO SEU PC) ---
  if (kIsWeb) {
    return 'http://localhost:8000/chat';
  }

  if (Platform.isAndroid) {
    // Android Emulator
    return 'http://10.0.2.2:8000/chat'; 
  }

  // iOS Simulator
  return 'http://localhost:8000/chat';
}

// --- TELA DO QUESTIONÁRIO (QuestionnaireScreen) ---
class QuestionnaireScreen extends StatefulWidget {
  const QuestionnaireScreen({super.key});

  @override
  State<QuestionnaireScreen> createState() => _QuestionnaireScreenState();
}

class _QuestionnaireScreenState extends State<QuestionnaireScreen> {
  // Estado da tela
  final String _sessionId = const Uuid().v4();
  BotResponse? _currentResponse;
  bool _isLoading = true;
  String? _errorMessage;
  int _questionNumber = 0;

  @override
  void initState() {
    super.initState();
    _startQuestionnaire();
  }

  // Inicia o questionário enviando uma mensagem "start"
  Future<void> _startQuestionnaire() async {
    // A primeira mensagem pode ser qualquer coisa para iniciar
    await _sendAnswer("start", isInitial: true);
  }

  // Envia a resposta para a API e atualiza a tela
  Future<void> _sendAnswer(String answer, {bool isInitial = false}) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      if (!isInitial) {
        _questionNumber++;
      }
    });

    try {
      final message = UserMessage(sessionId: _sessionId, text: answer);

      final response = await http.post(
        Uri.parse(aPIUrl),
        headers: {'Content-Type': 'application/json'},
        body: message.toJson(),
      );

      if (response.statusCode == 200) {
        // Usa utf8.decode para garantir acentuação correta
        final responseData =
            BotResponse.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));

        // Se a API retornar o fim do formulário (Risco Baixo/Alto)
        // OU se o tipo de resposta mudar (início do follow-up de Risco Médio),
        // vamos para a tela de resultado.
        if (responseData.endOfForm ||
            responseData.responseType != 'text_only') {
          if (mounted) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(
                builder: (context) => ResultScreen(response: responseData),
              ),
            );
          }
        } else {
          // Caso contrário, apenas atualiza a pergunta na tela
          setState(() {
            _currentResponse = responseData;
            if (isInitial) {
              _questionNumber = 1; // Corrige o contador na primeira pergunta
            }
            _isLoading = false;
          });
        }
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Questionário Inicial'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4.0),
          child: _isLoading
              ? const LinearProgressIndicator()
              : LinearProgressIndicator(
                  value: _questionNumber / 20.0, // Progresso de 20 perguntas
                ),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: _buildContent(),
        ),
      ),
    );
  }

  Widget _buildContent() {
    if (_isLoading && _currentResponse == null) {
      return const CircularProgressIndicator();
    }

    if (_errorMessage != null) {
      return Text(
        _errorMessage!,
        style: const TextStyle(color: Colors.red, fontSize: 16),
        textAlign: TextAlign.center,
      );
    }

    if (_currentResponse == null) {
      return const Text('Iniciando questionário...');
    }

    // O layout principal da pergunta
    return Column(
      children: [
        // Texto da Pergunta
        Expanded(
          child: Center(
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Text(
                  _currentResponse!.text,
                  style: Theme.of(context).textTheme.headlineSmall,
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ),
        ),

        // Botões de Resposta
        if (!_isLoading)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              ElevatedButton(
                onPressed: () => _sendAnswer('Não'),
                style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red[700]),
                child:
                    const Text('Não', style: TextStyle(color: Colors.white)),
              ),
              ElevatedButton(
                onPressed: () => _sendAnswer('Sim'),
                style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green[700]),
                child: const Text('Sim', style: TextStyle(color: Colors.white)),
              ),
            ],
          ),

        if (_isLoading) const CircularProgressIndicator(),

        const SizedBox(height: 24), // Espaçamento inferior
      ],
    );
  }
}
