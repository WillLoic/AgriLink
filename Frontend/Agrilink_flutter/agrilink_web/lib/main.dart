import 'package:flutter/material.dart';
import 'routes.dart';
import 'core/theme/app_theme.dart';

void main() {
  runApp(const AgriLinkApp());
}

class AgriLinkApp extends StatelessWidget {
  const AgriLinkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AgriLink ',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      initialRoute: AppRoutes.landing, // Démarre sur la Landing
      routes: AppRoutes.routes,
      onGenerateRoute: AppRoutes.onGenerateRoute, // Ajoute cette ligne !
    );
  }
}