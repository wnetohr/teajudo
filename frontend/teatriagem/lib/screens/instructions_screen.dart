import 'package:flutter/material.dart';
import 'questionnaire_screen.dart';

class InstructionsScreen extends StatelessWidget {
  const InstructionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final headingStyle = theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold, color: Colors.blue);
    final bodyStyle = theme.textTheme.bodyMedium;

    return Scaffold(
      appBar: AppBar(title: const Text('Instruções',style: TextStyle(color: Colors.blue),)),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text('Importante: Antes de Começarmos', style: headingStyle, textAlign: TextAlign.left),
                      const SizedBox(height: 12),
                      Text('Por favor, leia com atenção:', style: bodyStyle),
                      const SizedBox(height: 16),
                      Text('Não é um diagnóstico: Este aplicativo é uma ferramenta de rastreio. O resultado indica apenas se há sinais de risco para o Transtorno do Espectro Autista (TEA), mas não substitui uma avaliação médica completa.', style: bodyStyle),
                      const SizedBox(height: 12),
                      Text('Metodologia Científica: Utilizamos o formulário M-CHAT-R/F, um instrumento reconhecido internacionalmente para triagem inicial.', style: bodyStyle),
                      const SizedBox(height: 12),
                      Text('Sua participação é fundamental: Para que o resultado seja confiável, precisamos que você responda a todas as perguntas com a máxima sinceridade, pensando no comportamento habitual da criança.', style: bodyStyle),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),

              // Continue button centered at bottom
              SizedBox(
                width: double.infinity,
                child: Center(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                      minimumSize: const Size(140, 40),
                      foregroundColor: Colors.blue,
                    ),
                    onPressed: () {
                      // Replace the instructions screen by the questionnaire
                      Navigator.of(context).pushReplacement(
                        MaterialPageRoute(builder: (_) => const QuestionnaireScreen()),
                      );
                    },
                    child: const Text('Continuar'),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
