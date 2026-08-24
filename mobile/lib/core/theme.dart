import 'package:flutter/material.dart';

class AppTheme {
  static const Color brandDark = Color(0xFF0f172a);    // slate-900
  static const Color brandPrimary = Color(0xFF3b82f6); // Learn (Blue)
  static const Color brandWarning = Color(0xFFf59e0b); // Apply (Amber)
  static const Color brandAccent = Color(0xFF10b981);  // Grow (Emerald)

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: brandDark,
      primaryColor: brandPrimary,
      appBarTheme: const AppBarTheme(
        backgroundColor: brandDark,
        elevation: 0,
        centerTitle: true,
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Color(0xFF1e293b), // slate-800
        selectedItemColor: brandPrimary,
        unselectedItemColor: Colors.grey,
      ),
      useMaterial3: true,
    );
  }
}
