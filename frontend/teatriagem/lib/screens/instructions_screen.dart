import 'package:flutter/material.dart';
import 'questionnaire_screen.dart';

class InstructionsScreen extends StatelessWidget {
  const InstructionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final baseHeading = theme.textTheme.titleLarge;
    final baseBody = theme.textTheme.bodyMedium;
    final headingStyle = baseHeading?.copyWith(
      fontWeight: FontWeight.bold,
      color: Colors.blue,
      fontSize: (baseHeading?.fontSize ?? 22) + 4,
    );
    final bodyStyle = baseBody?.copyWith(
      fontSize: (baseBody?.fontSize ?? 14) + 2,
      height: 1.4,
    );

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
                      Text.rich(
                        TextSpan(
                          text: '',
                          style: bodyStyle,
                          children: [
                            TextSpan(
                              text: 'Isto não é um diagnóstico',
                              style: bodyStyle?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            TextSpan(text: '. Este aplicativo serve apenas para identificar possíveis sinais de autismo. O resultado é um alerta, mas não substitui uma consulta médica. '),
                            TextSpan(
                              text: 'Somente um especialista pode confirmar o diagnóstico',
                              style: bodyStyle?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            TextSpan(text: '.'),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text('Nossas perguntas seguem o método M-CHAT-R/F. Ele é um questionário usado no mundo todo como o primeiro passo para identificar sinais de autismo.', style: bodyStyle),
                      const SizedBox(height: 12),
                      Text.rich(
                        TextSpan(
                          text: '',
                          style: bodyStyle,
                          children: [
                            TextSpan(
                              text: 'Responda com total sinceridade',
                              style: bodyStyle?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            TextSpan(text: '. Considere como seu filho(a) se comporta na '),
                            TextSpan(
                              text: 'maior parte do tempo',
                              style: bodyStyle?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            TextSpan(text: ', e não apenas em momentos raros.'),
                          ],
                        ),
                      ),
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
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
                      minimumSize: const Size(160, 44),
                      foregroundColor: Colors.blue,
                      textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
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
