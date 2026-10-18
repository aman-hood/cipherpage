import 'dart:async';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

import '../features/auth/auth_service.dart';
import '../features/auth/login_screen.dart';
import '../features/home/home_screen.dart';

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  final AuthService _authService = AuthService();
  StreamSubscription<User?>? _authSubscription;
  User? _user;
  bool _isLoading = true;
  String? _profileError;

  @override
  void initState() {
    super.initState();
    _authSubscription = _authService.authStateChanges.listen(_handleAuthState);
  }

  Future<void> _handleAuthState(User? user) async {
    if (!mounted) return;
    if (user == null) {
      setState(() {
        _user = null;
        _profileError = null;
        _isLoading = false;
      });
      return;
    }

    if (!user.emailVerified) {
      await FirebaseAuth.instance.signOut();
      return;
    }

    setState(() {
      _isLoading = true;
      _profileError = null;
    });
    try {
      await _authService.syncWithBackend(user);
      if (mounted) {
        setState(() {
          _user = user;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _user = user;
          _profileError =
              'CipherPage could not verify your account with the backend.';
          _isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _authSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (_profileError != null) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(_profileError!, textAlign: TextAlign.center),
                const SizedBox(height: 16),
                const Text(
                  'Existing accounts may need a verified identity mapping before access is restored.',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => FirebaseAuth.instance.signOut(),
                  child: const Text('Sign out'),
                ),
              ],
            ),
          ),
        ),
      );
    }
    return _user == null ? const LoginScreen() : const HomeScreen();
  }
}
