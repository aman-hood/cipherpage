import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:firebase_core/firebase_core.dart';
import 'core/auth_wrapper.dart';
import 'core/firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Load environment variables
  await dotenv.load(fileName: ".env");

  // Firebase client configuration is public project metadata, never a service-account key.
  await Firebase.initializeApp(options: firebaseOptionsFromEnvironment());

  runApp(const CipherPageApp());
}

class CipherPageApp extends StatelessWidget {
  const CipherPageApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CipherPage',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      home: const AuthWrapper(),
    );
  }
}
