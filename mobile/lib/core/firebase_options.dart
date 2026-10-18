import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:firebase_core/firebase_core.dart';

FirebaseOptions firebaseOptionsFromEnvironment() {
  final apiKey = dotenv.env['FIREBASE_API_KEY']?.trim() ?? '';
  final appId = dotenv.env['FIREBASE_APP_ID']?.trim() ?? '';
  final messagingSenderId =
      dotenv.env['FIREBASE_MESSAGING_SENDER_ID']?.trim() ?? '';
  final projectId = dotenv.env['FIREBASE_PROJECT_ID']?.trim() ?? '';

  if ([apiKey, appId, messagingSenderId, projectId]
      .any((value) => value.isEmpty)) {
    throw StateError(
      'Firebase mobile configuration is missing. Set the FIREBASE_* public project values in mobile/.env.',
    );
  }

  return FirebaseOptions(
    apiKey: apiKey,
    appId: appId,
    messagingSenderId: messagingSenderId,
    projectId: projectId,
    authDomain: dotenv.env['FIREBASE_AUTH_DOMAIN']?.trim().isNotEmpty == true
        ? dotenv.env['FIREBASE_AUTH_DOMAIN']!.trim()
        : null,
    storageBucket:
        dotenv.env['FIREBASE_STORAGE_BUCKET']?.trim().isNotEmpty == true
            ? dotenv.env['FIREBASE_STORAGE_BUCKET']!.trim()
            : null,
  );
}
