import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:cipherpage_mobile/core/firebase_options.dart';

void main() {
  setUp(() => dotenv.clean());

  test('Firebase options use the configured public project values', () {
    dotenv.loadFromString(
      envString: '''
FIREBASE_API_KEY=public-api-key
FIREBASE_APP_ID=mobile-app-id
FIREBASE_MESSAGING_SENDER_ID=sender-id
FIREBASE_PROJECT_ID=cipherpage-test
FIREBASE_AUTH_DOMAIN=cipherpage-test.firebaseapp.com
FIREBASE_STORAGE_BUCKET=cipherpage-test.appspot.com
''',
    );

    final options = firebaseOptionsFromEnvironment();

    expect(options, isA<FirebaseOptions>());
    expect(options.apiKey, 'public-api-key');
    expect(options.appId, 'mobile-app-id');
    expect(options.messagingSenderId, 'sender-id');
    expect(options.projectId, 'cipherpage-test');
    expect(options.authDomain, 'cipherpage-test.firebaseapp.com');
    expect(options.storageBucket, 'cipherpage-test.appspot.com');
  });

  test('Firebase options fail closed when required config is missing', () {
    dotenv.loadFromString(envString: 'FIREBASE_PROJECT_ID=cipherpage-test');

    expect(firebaseOptionsFromEnvironment, throwsA(isA<StateError>()));
  });
}
