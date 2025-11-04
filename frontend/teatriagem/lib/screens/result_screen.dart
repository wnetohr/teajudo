import 'package:flutter/material.dart';
import '../models/api_models.dart'; // Importa os modelos de dados

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
                    response.text,
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
                    // TODO: Navegar para a tela da Entrevista de Seguimento
                    // Por enquanto, apenas exibimos uma mensagem
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Iniciando entrevista...')),
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
