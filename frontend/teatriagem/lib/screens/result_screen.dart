import 'package:flutter/material.dart';
import '../models/api_models.dart'; // Importa os modelos de dados
import '../theme/app_text_styles.dart'; // Importa os estilos de texto padronizados
import 'followup_screen.dart'; // Tela de entrevista de seguimento

// --- TELA DE RESULTADO (ResultScreen) ---
class ResultScreen extends StatelessWidget {
  final BotResponse response;
  const ResultScreen({super.key, required this.response});

  @override
  Widget build(BuildContext context) {
    // Determina o tipo de risco com base na resposta
    // Médio: end_of_form = false (precisa de follow-up)
    // Elevado: outcome contém "alto" ou "elevado"
    // Baixo: o resto
    final bool isMediumRisk = response.endOfForm == false;
    final bool isHighRisk = !isMediumRisk && 
        ((response.outcome?.toLowerCase().contains('alto') ?? false) || 
         (response.outcome?.toLowerCase().contains('elevado') ?? false) ||
         response.text.toLowerCase().contains('risco alto') ||
         response.text.toLowerCase().contains('risco elevado'));
    
    // Define cores baseado no tipo de risco
    final Color primaryColor = isHighRisk 
        ? Colors.red[100]! 
        : (isMediumRisk ? Colors.orange[100]! : Colors.green[100]!);
    final Color borderColor = isHighRisk 
        ? Colors.red[400]! 
        : (isMediumRisk ? Colors.orange[400]! : Colors.green[400]!);
    final Color iconBgColor = isHighRisk 
        ? Colors.red[300]! 
        : (isMediumRisk ? Colors.orange[300]! : Colors.green[300]!);
    final Color titleColor = isHighRisk 
        ? Colors.red[800]! 
        : (isMediumRisk ? Colors.orange[800]! : Colors.green[800]!);
    final Color buttonColor = isHighRisk 
        ? Colors.red[600]! 
        : (isMediumRisk ? Colors.orange[600]! : Colors.green[600]!);
    final IconData resultIcon = isHighRisk 
        ? Icons.warning 
        : (isMediumRisk ? Icons.info : Icons.check_circle);
    
    // Extrai o texto principal (primeiro bloco)
    String mainText = response.text;
    String? followUpMessage;
    
    if (response.responseType != 'text_only' && response.text.contains('\n\n')) {
      final parts = response.text.split('\n\n');
      if (parts.length >= 2) {
        mainText = parts[0];
        followUpMessage = parts[1];
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Resultado da Triagem',
          style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold),
        ),
        automaticallyImplyLeading: false, // Remove o botão "voltar"
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 24),
              
              // Container Principal - Resultado
              Card(
                elevation: 8,
                color: primaryColor,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(
                    color: borderColor,
                    width: 2,
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(28.0),
                  child: Column(
                    children: [
                      // Ícone do resultado
                      Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: iconBgColor,
                        ),
                        child: Center(
                          child: Icon(
                            resultIcon,
                            size: 50,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Título do resultado
                      Text(
                        isHighRisk 
                            ? 'Risco Elevado' 
                            : (isMediumRisk ? 'Risco Médio' : 'Risco Baixo'),
                        style: AppTextStyles.titleMedium.copyWith(
                          color: titleColor,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Texto principal do resultado
                      Text(
                        mainText,
                        style: AppTextStyles.bodyLarge.copyWith(
                          color: Colors.black87,
                          height: 1.6,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
              
              // Container Secundário - Mensagem de Follow-up (se houver)
              if (followUpMessage != null) ...[
                const SizedBox(height: 24),
                Card(
                  elevation: 4,
                  color: Colors.blue[50],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(
                      color: Colors.blue[300]!,
                      width: 1.5,
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      children: [
                        Icon(
                          Icons.lightbulb_outline,
                          size: 40,
                          color: Colors.blue[700],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          followUpMessage,
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: Colors.blue[900],
                            height: 1.5,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
              
              // Container de Orientação para Risco Elevado
              if (isHighRisk) ...[
                const SizedBox(height: 24),
                Card(
                  elevation: 4,
                  color: Colors.blue[50],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(
                      color: Colors.blue[300]!,
                      width: 1.5,
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      children: [
                        Icon(
                          Icons.priority_high,
                          size: 40,
                          color: Colors.blue[700],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'É recomendado procurar ajuda médica especializada o mais breve possível para uma avaliação completa.',
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: Colors.blue[900],
                            height: 1.5,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
              
              // Container de Orientação para Risco Baixo
              if (!isMediumRisk && !isHighRisk) ...[
                const SizedBox(height: 24),
                Card(
                  elevation: 4,
                  color: Colors.blue[50],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(
                      color: Colors.blue[300]!,
                      width: 1.5,
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      children: [
                        Icon(
                          Icons.check_circle,
                          size: 40,
                          color: Colors.blue[700],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Continue acompanhando o desenvolvimento de seu filho(a). Se notar qualquer mudança no comportamento, consulte um especialista.',
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: Colors.blue[900],
                            height: 1.5,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
              
              const SizedBox(height: 32),
              
              // Botões de Ação
              if (isMediumRisk) ...[
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: buttonColor,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: () {
                    // Navega para a tela de seguimento passando o sessionId
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(
                        builder: (_) => FollowUpScreen(sessionId: response.sessionId),
                      ),
                    );
                  },
                  child: Text(
                    'Iniciar Entrevista de Seguimento',
                    style: AppTextStyles.labelLarge.copyWith(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                  ),
                ),
              ] else ...[
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: buttonColor,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: () {
                    // Volta para a tela inicial, limpando o histórico
                    Navigator.of(context).popUntil((route) => route.isFirst);
                  },
                  child: Text(
                    'Voltar à Tela Inicial',
                    style: AppTextStyles.labelLarge.copyWith(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                  ),
                ),
              ],
              
              const SizedBox(height: 12),
              
              // Botão secundário - Voltar à Tela Inicial (para médio e elevado)
              if (isMediumRisk)
                OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    side: BorderSide(color: Colors.grey[400]!, width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: () {
                    // Volta para a tela inicial, limpando o histórico
                    Navigator.of(context).popUntil((route) => route.isFirst);
                  },
                  child: Text(
                    'Voltar à Tela Inicial',
                    style: AppTextStyles.labelMedium.copyWith(
                      color: Colors.grey[700],
                    ),
                  ),
                ),
              
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
