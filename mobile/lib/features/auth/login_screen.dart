import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'auth_service.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;
  String? _noticeMessage;
  final AuthService _authService = AuthService();

  Future<void> _signIn() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _noticeMessage = null;
    });

    try {
      await _authService.signInWithEmail(
        _emailController.text,
        _passwordController.text,
      );
    } on FirebaseAuthException catch (e) {
      setState(() {
        _errorMessage = e.message ?? 'Unable to sign in.';
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'An unexpected error occurred.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _signInWithGoogle() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _noticeMessage = null;
    });
    try {
      await _authService.signInWithGoogle();
    } catch (e) {
      setState(() {
        _errorMessage = e is FirebaseAuthException
            ? e.message ?? 'Google sign-in failed.'
            : e.toString();
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _sendPasswordReset() async {
    setState(() {
      _errorMessage = null;
      _noticeMessage = null;
    });
    if (_emailController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Enter your email address first.');
      return;
    }
    try {
      await _authService.sendPasswordReset(_emailController.text);
      setState(() => _noticeMessage =
          'If an account exists, Firebase will send a password reset email.');
    } on FirebaseAuthException catch (e) {
      setState(() => _errorMessage =
          e.message ?? 'Unable to send a password reset email.');
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'CipherPage',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'LAG — Learn • Apply • Grow',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
              const SizedBox(height: 48),
              if (_errorMessage != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 16),
                  color: Colors.red.withValues(alpha: 0.1),
                  child: Text(
                    _errorMessage!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
              if (_noticeMessage != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 16),
                  color: Colors.green.withValues(alpha: 0.1),
                  child: Text(_noticeMessage!,
                      style: const TextStyle(color: Colors.green)),
                ),
              TextField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.email),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: _isLoading ? null : _sendPasswordReset,
                  child: const Text('Forgot password?'),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                decoration: const InputDecoration(
                  labelText: 'Password',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.lock),
                ),
                obscureText: true,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _signIn,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Sign in'),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: _isLoading ? null : _signInWithGoogle,
                icon: const Icon(Icons.g_mobiledata, size: 24),
                label: const Text('Sign in with Google'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
              const SizedBox(height: 24),
              TextButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const RegisterScreen(),
                    ),
                  );
                },
                child: const Text("Don't have an account? Sign up"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
