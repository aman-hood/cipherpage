import 'package:flutter/material.dart';
import '../core/theme.dart';

class HomeScaffold extends StatefulWidget {
  const HomeScaffold({super.key});

  @override
  State<HomeScaffold> createState() => _HomeScaffoldState();
}

class _HomeScaffoldState extends State<HomeScaffold> {
  int _currentIndex = 0;

  // The 3 phases of our LAG Framework mapped to mobile screens
  final List<Widget> _tabs = [
    const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.menu_book, size: 80, color: AppTheme.brandPrimary),
          SizedBox(height: 20),
          Text("LEARN", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.brandPrimary)),
          Text("Premium Video Lectures", style: TextStyle(color: Colors.grey)),
        ],
      )
    ),
    const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.code, size: 80, color: AppTheme.brandWarning),
          SizedBox(height: 20),
          Text("APPLY", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.brandWarning)),
          Text("Mobile Code Editor & Grading", style: TextStyle(color: Colors.grey)),
        ],
      )
    ),
    const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.rocket_launch, size: 80, color: AppTheme.brandAccent),
          SizedBox(height: 20),
          Text("GROW", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.brandAccent)),
          Text("Badges & Career Portfolios", style: TextStyle(color: Colors.grey)),
        ],
      )
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Image.asset('assets/images/logo.png', height: 40),
      ),
      body: _tabs[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.menu_book),
            label: 'Learn',
            activeIcon: Icon(Icons.menu_book, color: AppTheme.brandPrimary),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.code),
            label: 'Apply',
            activeIcon: Icon(Icons.code, color: AppTheme.brandWarning),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.rocket_launch),
            label: 'Grow',
            activeIcon: Icon(Icons.rocket_launch, color: AppTheme.brandAccent),
          ),
        ],
      ),
    );
  }
}
