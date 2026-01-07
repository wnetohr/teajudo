import 'package:flutter/material.dart';

/// Estilos de texto padronizados para toda a aplicação
class AppTextStyles {
  // Titles - Títulos grandes
  static const TextStyle titleExtraLarge = TextStyle(
    fontSize: 48,
    fontWeight: FontWeight.bold,
    color: Colors.black87,
    height: 1.2,
  );

  static const TextStyle titleLarge = TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.bold,
    color: Colors.black87,
    height: 1.3,
  );

  static const TextStyle titleMedium = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: Colors.black87,
    height: 1.3,
  );

  static const TextStyle titleSmall = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.bold,
    color: Colors.black87,
    height: 1.3,
  );

  // Headings - Subtítulos/Cabeçalhos
  static const TextStyle headingLarge = TextStyle(
    fontSize: 22,
    fontWeight: FontWeight.bold,
    color: Colors.blue,
    height: 1.3,
  );

  static const TextStyle headingMedium = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.bold,
    color: Colors.blue,
    height: 1.3,
  );

  static const TextStyle headingSmall = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.bold,
    color: Colors.blue,
    height: 1.3,
  );

  // Body - Texto de corpo
  static const TextStyle bodyLarge = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: Colors.black87,
    height: 1.5,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: Colors.black87,
    height: 1.5,
  );

  static const TextStyle bodySmall = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: Colors.black54,
    height: 1.4,
  );

  // Labels - Botões e labels
  static const TextStyle labelLarge = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: Colors.black87,
    height: 1.2,
  );

  static const TextStyle labelMedium = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: Colors.black87,
    height: 1.2,
  );

  static const TextStyle labelSmall = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w600,
    color: Colors.black54,
    height: 1.2,
  );

  // Question style - Especifico para perguntas
  static const TextStyle question = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w500,
    color: Colors.black87,
    height: 1.4,
  );

  // Instruction style - Para instruções/avisos
  static const TextStyle instruction = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: Colors.black87,
    height: 1.5,
  );

  // Helper method para criar TextStyle baseado no tema
  static TextStyle copyWithColor(TextStyle style, Color color) {
    return style.copyWith(color: color);
  }

  static TextStyle copyWithSize(TextStyle style, double size) {
    return style.copyWith(fontSize: size);
  }

  static TextStyle copyWithWeight(TextStyle style, FontWeight weight) {
    return style.copyWith(fontWeight: weight);
  }
}
