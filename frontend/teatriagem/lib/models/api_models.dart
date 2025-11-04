import 'dart:convert';

// --- MODELOS DE DADOS DART (Espelho da API) ---
// Estes arquivos devem espelhar as classes do seu 'models.py'

// Espelho do models.py -> BotResponse
class BotResponse {
  final String sessionId;
  final String text;
  final String responseType;
  final List<Option> options;
  final bool isItemFinished;
  final bool endOfForm;
  final String? outcome;
  final int? score;

  BotResponse({
    required this.sessionId,
    required this.text,
    required this.responseType,
    required this.options,
    required this.isItemFinished,
    required this.endOfForm,
    this.outcome,
    this.score,
  });

  factory BotResponse.fromJson(Map<String, dynamic> json) {
    var optionsList = json['options'] as List;
    List<Option> options = optionsList.map((i) => Option.fromJson(i)).toList();

    return BotResponse(
      sessionId: json['session_id'],
      text: json['text'],
      responseType: json['response_type'],
      options: options,
      isItemFinished: json['is_item_finished'],
      endOfForm: json['end_of_form'],
      outcome: json['outcome'],
      score: json['score'],
    );
  }
}

// Espelho do models.py -> Option
class Option {
  final String id;
  final String label;

  Option({required this.id, required this.label});

  factory Option.fromJson(Map<String, dynamic> json) {
    return Option(
      id: json['id'],
      label: json['label'],
    );
  }
}

// Espelho do models.py -> UserMessage
class UserMessage {
  final String sessionId;
  final String text;

  UserMessage({required this.sessionId, required this.text});

  String toJson() {
    return jsonEncode({
      'session_id': sessionId,
      'text': text,
    });
  }
}
