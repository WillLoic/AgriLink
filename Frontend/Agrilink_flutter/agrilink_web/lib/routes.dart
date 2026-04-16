import 'package:flutter/material.dart';
import 'views/landing_view.dart';
import 'views/auth/login_view.dart';
import 'views/auth/register_view.dart';
import 'views/auth/password_recovery_view.dart';
import 'views/auth/reset_password_view.dart';
import 'views/dashboard/user_dashboard_view.dart';
import 'views/dashboard/admin_panel_view.dart';
import 'views/scan/scan_view.dart';
import 'views/history/history_view.dart';

class AppRoutes {
  static const String landing = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String recovery = '/recovery';
  static const String resetPassword = '/reset_password';
  static const String dashboard = '/dashboard';
  static const String adminPanel = '/admin-panel';
  static const String scan = '/scan';
  static const String history = '/history';

  static Map<String, WidgetBuilder> get routes => {
    landing: (context) => const LandingView(),
    login: (context) => const LoginView(),
    register: (context) => const RegisterView(), // Attention à la casse de ton fichier
    recovery: (context) => const PasswordRecoveryView(),
    //resetPassword: (context) => const ResetPasswordView(),
    dashboard: (context) => const DashboardView(),
    adminPanel: (context) => const AdminPanelView(),
    scan: (context) => const ScanView(),
    history: (context) => const HistoryView(),
  };
  // Ajoute cette fonction pour gérer les paramètres d'URL
  static Route<dynamic>? onGenerateRoute(RouteSettings settings) {
    // Analyse du nom de la route (ex: /reset-password?token=abc)
    final Uri uri = Uri.parse(settings.name ?? '');

    if (uri.path == resetPassword) {
      // On récupère le token soit dans les arguments, soit dans la query de l'URL
      final token = settings.arguments as String? ?? uri.queryParameters['token'];
      
      return MaterialPageRoute(
        builder: (context) => const ResetPasswordView(),
        // On passe le token via les settings pour que ResetPasswordView puisse le lire
        settings: RouteSettings(name: resetPassword, arguments: token),
      );
    }

    return null; // Laisse Flutter utiliser le Map 'routes' par défaut
  }
}
