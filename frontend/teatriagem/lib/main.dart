import 'package:flutter/material.dart';
import 'screens/home_screen.dart'; // Importa a nova tela inicial

void main() {
  runApp(const AutismScreeningApp());
}

class AutismScreeningApp extends StatelessWidget {
  const AutismScreeningApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Triagem TEA',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
        scaffoldBackgroundColor: Colors.grey[50],
        appBarTheme: const AppBarTheme(
          // Define the global color for the AppBar icons (back button, actions)
          iconTheme: IconThemeData(color: Colors.blue),
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          margin: const EdgeInsets.symmetric(vertical: 8.0),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ),
      // A home do app agora é a classe que está no arquivo separado
      home: const HomeScreen(),
    );
  }
}

