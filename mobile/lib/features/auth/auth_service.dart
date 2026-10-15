import 'dart:async';
import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  final SupabaseClient _supabase = Supabase.instance.client;
  final Dio _dio = Dio();
  StreamSubscription<AuthState>? _authStateSubscription;

  void initialize() {
    _authStateSubscription = _supabase.auth.onAuthStateChange.listen((data) {
      final session = data.session;
      if (session != null) {
        _syncWithBackend(session.accessToken);
      }
    });
  }

  void dispose() {
    _authStateSubscription?.cancel();
  }

  Future<void> _syncWithBackend(String token) async {
    try {
      // In a real app, this should come from .env
      // Using 10.0.2.2 for Android emulator to reach localhost:8000
      // or localhost:8000 for iOS simulator / web
      const baseUrl = 'http://10.0.2.2:8000/api/v1';
      
      final response = await _dio.get(
        '$baseUrl/auth/me',
        options: Options(
          headers: {
            'Authorization': 'Bearer $token',
          },
        ),
      );
      
      if (response.statusCode == 200) {
        // Backend synced successfully
      }
    } catch (e) {
      // Handle error gracefully or log it with a logging framework
    }
  }

  Future<void> signOut() async {
    await _supabase.auth.signOut();
  }
}
