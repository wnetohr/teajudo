import 'package:flutter/material.dart';
import 'questionnaire_screen.dart'; // Importa a tela do questionário
import 'instructions_screen.dart';
import '../theme/app_text_styles.dart';

// --- TELA INICIAL (HomeScreen) ---
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
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
                final cacheW = (dpr * 126 * 2).round();
                return Image.asset(
                  'lib/images/logo2.png',
                  width: 126,
                  height: 126,
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
                        style: AppTextStyles.titleExtraLarge.copyWith(foreground: Paint()
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
                        style: AppTextStyles.titleExtraLarge,
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

              const SizedBox(height: 12),

              // Welcome text (same size as button label)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8.0),
                child: Text(
                  'Olá! Um olhar atento pode mudar tudo. Boas vindas ao TEAJUDO, à sua ferramenta de apoio na triagem do autismo.',
                  style: AppTextStyles.labelLarge.copyWith(color: Colors.blue),
                  textAlign: TextAlign.center,
                ),
              ),

              const SizedBox(height: 18),

              // Start button
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 12),
                  foregroundColor: Colors.blue,
                ),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const InstructionsScreen()),
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
