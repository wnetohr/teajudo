import 'package:flutter/material.dart';
import 'questionnaire_screen.dart'; // Importa a tela do questionário

// --- TELA INICIAL (HomeScreen) ---
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final baseTextStyle = Theme.of(context)
      .textTheme
      .headlineSmall
      ?.copyWith(fontWeight: FontWeight.bold, fontSize: 48);
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Replaced by cleaned logo `logo2.png`. Load with high filter
              // quality and request a cached width scaled to the device DPR
              // to reduce aliasing when the engine resizes the image.
              Builder(builder: (ctx) {
                final dpr = MediaQuery.of(ctx).devicePixelRatio;
                // request a higher-res cache to improve downscaling quality
                final cacheW = (dpr * 96 * 2).round();
                return Image.asset(
                  'lib/images/logo2.png',
                  width: 96,
                  height: 96,
                  fit: BoxFit.contain,
                  cacheWidth: cacheW,
                  filterQuality: FilterQuality.high,
                );
              }),
              const SizedBox(height: 12),

              // App name with colored letters and a slight black stroke to improve contrast
              SizedBox(
                height: 56,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // Stroke: drawn first using Paint via TextStyle.foreground
                    RichText(
                      text: TextSpan(
                        style: baseTextStyle?.copyWith(foreground: Paint()
                          ..style = PaintingStyle.stroke
                          ..strokeWidth = 4
                          ..color = Colors.black),
                        children: const [
                          TextSpan(text: 'T', style: TextStyle(color: Colors.red)),
                          TextSpan(text: 'E', style: TextStyle(color: Colors.yellow)),
                          TextSpan(text: 'AJUDO', style: TextStyle(color: Colors.blue)),
                        ],
                      ),
                    ),
                    // Fill: drawn on top
                    RichText(
                      text: TextSpan(
                        style: baseTextStyle,
                        children: const [
                          TextSpan(text: 'T', style: TextStyle(color: Colors.red)),
                          TextSpan(text: 'E', style: TextStyle(color: Colors.yellow)),
                          TextSpan(text: 'AJUDO', style: TextStyle(color: Colors.blue)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 8),

              // Start button
              ElevatedButton(
                style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 12)),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const QuestionnaireScreen()),
                  );
                },
                child: const Text('Iniciar Formulário'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
