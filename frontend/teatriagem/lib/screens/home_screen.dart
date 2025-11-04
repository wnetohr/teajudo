import 'package:flutter/material.dart';
import 'questionnaire_screen.dart'; // Importa a tela do questionário

// --- TELA INICIAL (HomeScreen) ---
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Triagem de Autismo Infantil'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Bem-vindo(a)',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 16),
              const Text(
                'Este aplicativo usa o M-CHAT-R/F para apoiar na triagem de sinais de TEA.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const QuestionnaireScreen()),
                  );
                },
                child: const Text('Iniciar Nova Triagem'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
