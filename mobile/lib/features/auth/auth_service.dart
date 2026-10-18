import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_sign_in/google_sign_in.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final Dio _dio = Dio();
  static Future<void>? _googleInitialization;

  Stream<User?> get authStateChanges => _auth.authStateChanges();

  String get _apiBaseUrl {
    final value = dotenv.env['API_BASE_URL']?.trim() ?? '';
    if (value.isEmpty) {
      throw StateError(
          'Set API_BASE_URL in mobile/.env before using the backend.');
    }
    final uri = Uri.tryParse(value);
    if (uri == null || !uri.hasScheme || !uri.hasAuthority) {
      throw StateError('API_BASE_URL must be an absolute HTTP(S) URL.');
    }
    if (['production', 'prod', 'staging']
            .contains((dotenv.env['ENVIRONMENT'] ?? '').toLowerCase()) &&
        uri.scheme != 'https') {
      throw StateError('API_BASE_URL must use HTTPS in production.');
    }
    return '${value.replaceFirst(RegExp(r'/+$'), '')}/api/v1';
  }

  Future<void> syncWithBackend(User user) async {
    final token = await user.getIdToken();
    if (token == null) throw StateError('Firebase did not return an ID token.');
    await _dio.get(
      '$_apiBaseUrl/auth/me',
      options: Options(headers: {'Authorization': 'Bearer $token'}),
    );
  }

  Future<UserCredential> signInWithEmail(String email, String password) async {
    final credential = await _auth.signInWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );
    await credential.user?.reload();
    final user = _auth.currentUser;
    if (user == null || !user.emailVerified) {
      await _auth.signOut();
      throw FirebaseAuthException(
        code: 'email-not-verified',
        message: 'Verify your email address before signing in.',
      );
    }
    await user.getIdToken(true);
    return credential;
  }

  Future<void> registerWithEmail({
    required String name,
    required String email,
    required String password,
  }) async {
    try {
      final credential = await _auth.createUserWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );
      final user = credential.user;
      if (user == null) throw StateError('Firebase did not create an account.');
      await user.updateDisplayName(name.trim());
      await user.sendEmailVerification();
      await _auth.signOut();
    } catch (_) {
      if (_auth.currentUser != null) await _auth.signOut();
      rethrow;
    }
  }

  Future<UserCredential> signInWithGoogle() async {
    final serverClientId =
        dotenv.env['GOOGLE_SIGN_IN_SERVER_CLIENT_ID']?.trim();
    if (serverClientId == null || serverClientId.isEmpty) {
      throw StateError(
          'Set GOOGLE_SIGN_IN_SERVER_CLIENT_ID to enable Google sign-in.');
    }
    _googleInitialization ??= GoogleSignIn.instance.initialize(
      clientId: dotenv.env['GOOGLE_SIGN_IN_CLIENT_ID']?.trim(),
      serverClientId: serverClientId,
    );
    await _googleInitialization;

    final googleUser = await GoogleSignIn.instance.authenticate();
    final idToken = googleUser.authentication.idToken;
    if (idToken == null)
      throw StateError('Google sign-in did not return an ID token.');
    final credential = GoogleAuthProvider.credential(idToken: idToken);
    final userCredential = await _auth.signInWithCredential(credential);
    final user = userCredential.user;
    if (user == null || !user.emailVerified) {
      await _auth.signOut();
      throw FirebaseAuthException(
          code: 'email-not-verified',
          message: 'Google account email is not verified.');
    }
    await user.getIdToken(true);
    return userCredential;
  }

  Future<void> sendPasswordReset(String email) =>
      _auth.sendPasswordResetEmail(email: email.trim());

  Future<void> signOut() async {
    final user = _auth.currentUser;
    Object? revokeError;
    if (user != null) {
      try {
        final token = await user.getIdToken();
        if (token == null)
          throw StateError('Firebase did not return an ID token.');
        await _dio.post(
          '$_apiBaseUrl/auth/logout',
          options: Options(headers: {'Authorization': 'Bearer $token'}),
        );
      } catch (error) {
        revokeError = error;
      }
    }
    await _auth.signOut();
    try {
      await GoogleSignIn.instance.signOut();
    } catch (_) {
      // Email/password sessions do not initialize the Google provider.
    }
    if (revokeError != null) {
      throw StateError(
          'Signed out on this device, but the server could not revoke the session.');
    }
  }
}
