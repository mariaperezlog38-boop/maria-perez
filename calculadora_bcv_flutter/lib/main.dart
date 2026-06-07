import 'package:flutter/material.dart';
import 'package:math_expressions/math_expressions.dart';
import 'package:intl/intl.dart';

void main() {
  runApp(const CalculadoraApp());
}

class CalculadoraApp extends StatelessWidget {
  const CalculadoraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Calculadora BCV',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _amountCtrl = TextEditingController();
  final TextEditingController _rateCtrl = TextEditingController();
  String _mode = 'USD a Bs';
  String _result = '';
  String? _error;

  double evaluateExpression(String expr) {
    if (expr.trim().isEmpty) throw Exception('Expresión vacía.');
    final sanitized = expr.replaceAll(',', '.');
    final parser = Parser();
    final contextModel = ContextModel();
    final parsed = parser.parse(sanitized);
    final eval = parsed.evaluate(EvaluationType.REAL, contextModel);
    return (eval is num) ? eval.toDouble() : double.parse(eval.toString());
  }

  double parseAmount(String value) {
    if (value.trim().isEmpty) throw Exception('El monto no puede estar vacío.');
    try {
      return evaluateExpression(value);
    } catch (e) {
      throw Exception('Ingresa un número o expresión válida.');
    }
  }

  double cleanRate(String raw) {
    var value = raw.replaceAll('Bs.', '').replaceAll('Bs', '').trim().replaceAll(' ', '');
    if (value.contains(',') && value.contains('.')) {
      value = value.replaceAll('.', '').replaceAll(',', '.');
    } else {
      value = value.replaceAll(',', '.');
    }
    return double.parse(value);
  }

  double convertAmount(double cantidad, double tasa, String modo) {
    if (tasa <= 0) throw Exception('La tasa debe ser mayor que cero.');
    if (cantidad < 0) throw Exception('El monto no puede ser negativo.');
    if (modo == 'USD a Bs') return cantidad * tasa;
    if (modo == 'Bs a USD') return cantidad / tasa;
    throw Exception('Modo de conversión no válido.');
  }

  String formatResult(double value, String modo) {
    final f = NumberFormat('#,##0.00', 'en_US');
    if (modo == 'USD a Bs') return '${f.format(value)} Bs';
    return '${f.format(value)} USD';
  }

  void onConvert() {
    setState(() {
      _error = null;
      _result = '';
    });
    try {
      final cantidad = parseAmount(_amountCtrl.text);
      final tasa = cleanRate(_rateCtrl.text);
      final converted = convertAmount(cantidad, tasa, _mode);
      setState(() {
        _result = formatResult(converted, _mode);
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    }
  }

  @override
  void dispose() {
    _amountCtrl.dispose();
    _rateCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Calculadora BCV')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Monto (acepta expresiones: 10+5/2):'),
            TextField(
              controller: _amountCtrl,
              keyboardType: TextInputType.text,
              decoration: const InputDecoration(hintText: 'Ej: 100, 10+5/2'),
            ),
            const SizedBox(height: 12),
            const Text('Tasa (ej: 30.5 o Bs. 30,5):'),
            TextField(
              controller: _rateCtrl,
              keyboardType: TextInputType.text,
              decoration: const InputDecoration(hintText: 'Ej: 30.5'),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Text('Modo:'),
                const SizedBox(width: 12),
                DropdownButton<String>(
                  value: _mode,
                  items: const [
                    DropdownMenuItem(value: 'USD a Bs', child: Text('USD a Bs')),
                    DropdownMenuItem(value: 'Bs a USD', child: Text('Bs a USD')),
                  ],
                  onChanged: (v) => setState(() => _mode = v ?? _mode),
                ),
                const Spacer(),
                ElevatedButton(onPressed: onConvert, child: const Text('Convertir')),
              ],
            ),
            const SizedBox(height: 18),
            if (_error != null) ...[
              Text(_error!, style: const TextStyle(color: Colors.red)),
              const SizedBox(height: 12),
            ],
            if (_result.isNotEmpty) ...[
              Text('Resultado:', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              Text(_result, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            ],
          ],
        ),
      ),
    );
  }
}
