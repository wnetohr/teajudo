import 'package:flutter/material.dart';
import '../models/api_models.dart'; // Importa os modelos de dados
import 'followup_screen.dart'; // Tela de entrevista de seguimento

// --- TELA DE RESULTADO (ResultScreen) ---
class ResultScreen extends StatelessWidget {
  final BotResponse response;
  const ResultScreen({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    // Determina se é Risco Médio (e precisa de follow-up)
    // A API retorna end_of_form = false para Risco Médio
    final bool isMediumRisk = response.endOfForm == false;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Resultado da Triagem'),
        automaticallyImplyLeading: false, // Remove o botão "voltar"
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Card(
                color: isMediumRisk ? Colors.orange[100] : Colors.blue[100],
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Text(
                    // Se houver follow-up embutido na resposta (blocos separados por dupla quebra de linha),
                    // mostramos os dois primeiros blocos: resumo + aviso de início da entrevista.
                    (() {
                      if (response.responseType != 'text_only' && response.text.contains('\n\n')) {
                        final parts = response.text.split('\n\n');
                        if (parts.length >= 2) {
                          return '${parts[0]}\n\n${parts[1]}';
                        }
                        return parts[0];
                      }
                      return response.text;
                    })(),
                    style: Theme.of(context).textTheme.bodyLarge,
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
              const SizedBox(height: 48),

              // Botão Condicional
              if (isMediumRisk)
                ElevatedButton(
                  onPressed: () {
                    // Navega para a tela de seguimento passando o sessionId
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(
                        builder: (_) => FollowUpScreen(sessionId: response.sessionId),
                      ),
                    );
                  },
                  child: const Text('Iniciar Entrevista de Seguimento'),
                ),

              const SizedBox(height: 16),
              TextButton(
                onPressed: () {
                  // Volta para a tela inicial, limpando o histórico
                  Navigator.of(context).popUntil((route) => route.isFirst);
                },
                child: const Text('Voltar à Tela Inicial'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
