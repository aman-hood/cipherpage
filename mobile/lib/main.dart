import 'package:flutter/material.dart';
import 'core/theme.dart';
import 'presentation/home_scaffold.dart';

void main() {
  runApp(const CipherPageApp());
}

class CipherPageApp extends StatelessWidget {
  const CipherPageApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CipherPage Mobile',
      theme: AppTheme.darkTheme,
      home: const HomeScaffold(),
      debugShowCheckedModeBanner: false,
    );
  }
}
