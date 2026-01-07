# Guia de Estilos de Texto - TEAJUDO

## Visão Geral

Todos os estilos de texto da aplicação foram padronizados no arquivo `lib/theme/app_text_styles.dart`. Isso garante consistência visual em toda a aplicação e facilita futuras alterações globais.

## Como Usar

### 1. Importar o arquivo de estilos

```dart
import '../theme/app_text_styles.dart';
```

### 2. Aplicar os estilos

```dart
Text(
  'Seu texto aqui',
  style: AppTextStyles.bodyLarge,
)
```

## Estilos Disponíveis

### Titles (Títulos Grandes)
- **`titleExtraLarge`** - 48px, bold (para títulos principais)
- **`titleLarge`** - 28px, bold
- **`titleMedium`** - 24px, bold
- **`titleSmall`** - 20px, bold

### Headings (Cabeçalhos/Subtítulos)
- **`headingLarge`** - 22px, bold, azul
- **`headingMedium`** - 18px, bold, azul
- **`headingSmall`** - 16px, bold, azul

### Body (Texto de Corpo)
- **`bodyLarge`** - 16px, normal (para parágrafos principais)
- **`bodyMedium`** - 14px, normal
- **`bodySmall`** - 12px, normal, cinza mais claro

### Labels (Botões e Labels)
- **`labelLarge`** - 16px, semi-bold (para botões)
- **`labelMedium`** - 14px, semi-bold
- **`labelSmall`** - 12px, semi-bold, cinza

### Específicos
- **`question`** - 20px, medium weight (para perguntas do questionário)
- **`instruction`** - 16px, normal (para instruções)

## Exemplos de Uso

### Pergunta no Questionário
```dart
Text(
  _currentResponse!.text,
  style: AppTextStyles.question,
  textAlign: TextAlign.center,
)
```

### Texto de Instrução
```dart
Text(
  'Por favor, leia com atenção:',
  style: AppTextStyles.instruction,
)
```

### Texto em Negrito
```dart
Text.rich(
  TextSpan(
    text: 'Isto não é um diagnóstico',
    style: AppTextStyles.bodyMedium.copyWith(fontWeight: FontWeight.bold),
  ),
)
```

### Texto com Cor Customizada
```dart
Text(
  'Seu texto',
  style: AppTextStyles.labelLarge.copyWith(color: Colors.red),
)
```

### Texto com Tamanho Customizado
```dart
Text(
  'Seu texto',
  style: AppTextStyles.bodyLarge.copyWith(fontSize: 18),
)
```

## Métodos Auxiliares

O arquivo também fornece métodos auxiliares para modificações rápidas:

```dart
AppTextStyles.copyWithColor(style, Colors.blue)
AppTextStyles.copyWithSize(style, 18)
AppTextStyles.copyWithWeight(style, FontWeight.bold)
```

## Benefícios

✅ Consistência visual em toda a aplicação  
✅ Fácil manutenção - alterar estilos em um único lugar  
✅ Nomes descritivos e intuitivos  
✅ Reduz duplicação de código  
✅ Melhora a escalabilidade do projeto  

## Próximos Passos (Sugestões)

- Considere adicionar estilos para temas escuro (dark mode)
- Adicione estilos para animações de transição
- Crie variações para diferentes tamanhos de tela (responsivo)
