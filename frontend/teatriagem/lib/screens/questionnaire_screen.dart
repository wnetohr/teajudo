import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

import '../models/api_models.dart'; // Importa os modelos de dados
import 'result_screen.dart'; // Importa a tela de resultado

// --- CONFIGURAÇÃO DA API ---
// Seleciona a URL da API conforme a plataforma em que o app está rodando.
// - Android emulator (Android Studio): 10.0.2.2 -> host machine
// - iOS simulator: localhost -> host machine
// - Web: localhost (mas o backend precisa permitir CORS)
// - Dispositivo físico: use o IP da máquina (ex.: http://192.168.x.y:8000)
String get aPIUrl {
  if (kIsWeb) {
    return 'http://localhost:8000/chat';
  }

  // Platform.* is not supported on web, por isso protegemos com kIsWeb
  if (Platform.isAndroid) {
    return 'http://10.0.2.2:8000/chat';
  }

  // iOS simulator e outras plataformas de desktop usam localhost
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
