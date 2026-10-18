import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../auth/auth_service.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  Future<void> _signOut() async {
    await AuthService().signOut();
  }

  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;
    final email = user?.email ?? 'Unknown User';
    final name = user?.displayName ?? 'Student';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _signOut,
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.check_circle_outline,
              size: 100,
              color: Colors.green,
            ),
            const SizedBox(height: 24),
            Text(
              'Welcome, $name!',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              email,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 48),
            const Text(
              'You are signed in with Firebase Authentication.\nCipherPage data is served by the FastAPI backend.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
