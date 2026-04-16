import 'package:flutter/material.dart';
import '../../routes.dart';
import '../../services/auth_service.dart'; // Import du service ajouté

class ResetPasswordView extends StatefulWidget {
  const ResetPasswordView({super.key});

  @override
  State<ResetPasswordView> createState() => _ResetPasswordViewState();
}

class _ResetPasswordViewState extends State<ResetPasswordView> {
  bool _isPasswordVisible = false;
  bool _isLoading = false; // État de chargement
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  // Variables pour les retours visuels d'erreurs
  String? _passwordError;
  String? _confirmError;

  String? _token;
  final _authService = AuthService();

  @override
  void initState() {
    super.initState();
    // On attend la fin du build pour lire les arguments de la route
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final settings = ModalRoute.of(context)?.settings;
      if (settings?.arguments is String) {
        _token = settings?.arguments as String;
      } else {
        // Logique de secours : extraire manuellement de l'URL si besoin
        final uri = Uri.base;
        _token = uri.queryParameters['token'];
      }
      
      if (_token == null) {
        print("Alerte : Aucun token trouvé dans l'URL");
      }
    });
  }

  void _handleResetPassword() async {
    if (_token == null) {
    // Tentative de récupération de dernière minute si le callback a tardé
    final uri = Uri.base;
    _token = uri.queryParameters['token'];
  }

  if (_token == null) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Lien invalide ou token expiré.")),
    );
    return;
  }
    if (_passwordController.text.length < 6) {
      setState(() => _passwordError = "Trop court (min 6)");
      return;
    }
    if (_confirmPasswordController.text != _passwordController.text) {
      setState(() => _confirmError = "Les mots de passe divergent");
      return;
    }
    if (_token == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Token manquant. Repassez par le lien du mail.")),
      );
      return;
    }

    setState(() => _isLoading = true);

    final result = await _authService.resetPassword(_token!, _passwordController.text);

    setState(() => _isLoading = false);

    if (result['success']) {
      _showSuccessDialog();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['message']), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFFF5F7FA), Color(0xFFC3CFE2)],
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            child: Container(
              width: 450,
              padding: const EdgeInsets.all(40),
              margin: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(25),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 20, offset: const Offset(0, 10))
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text("🛡️", style: TextStyle(fontSize: 50)),
                  const SizedBox(height: 20),
                  const Text(
                    "Nouveau mot de passe",
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF2C3E50)),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    "Choisissez un mot de passe robuste pour protéger votre compte AgriLink.",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Color(0xFF7F8C8D), height: 1.4),
                  ),
                  const SizedBox(height: 35),

                  _buildPasswordField(
                    controller: _passwordController,
                    label: "Nouveau mot de passe",
                    errorText: _passwordError,
                  ),
                  const SizedBox(height: 20),

                  _buildPasswordField(
                    controller: _confirmPasswordController,
                    label: "Confirmer le mot de passe",
                    errorText: _confirmError,
                  ),
                  
                  const SizedBox(height: 35),

                  _buildResetButton(),
                  
                  const SizedBox(height: 20),
                  
                  TextButton(
                    onPressed: _isLoading ? null : () => Navigator.pushNamed(context, AppRoutes.login),
                    child: const Text("Annuler et revenir", style: TextStyle(color: Color(0xFF7F8C8D))),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPasswordField({
    required TextEditingController controller, 
    required String label,
    String? errorText,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          enabled: !_isLoading,
          obscureText: !_isPasswordVisible,
          decoration: InputDecoration(
            errorText: errorText,
            prefixIcon: const Icon(Icons.lock_reset_rounded, color: Color(0xFF28A745)),
            suffixIcon: IconButton(
              icon: Icon(_isPasswordVisible ? Icons.visibility : Icons.visibility_off, size: 20),
              onPressed: () => setState(() => _isPasswordVisible = !_isPasswordVisible),
            ),
            filled: true,
            fillColor: const Color(0xFFF8F9FA),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(15), borderSide: BorderSide.none),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(15),
              borderSide: const BorderSide(color: Color(0xFF28A745), width: 1.5),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildResetButton() {
    return Container(
      width: double.infinity,
      height: 55,
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF28A745), Color(0xFF20C997)]),
        borderRadius: BorderRadius.circular(50),
        boxShadow: [
          BoxShadow(color: const Color(0xFF28A745).withOpacity(0.3), blurRadius: 15, offset: const Offset(0, 8))
        ],
      ),
      child: ElevatedButton(
        onPressed: _isLoading ? null : _handleResetPassword,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(50)),
        ),
        child: _isLoading 
          ? Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: const [
                SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                ),
                SizedBox(width: 12),
                Text("MODIFICATION DU MOT DE PASSE PATIENTEZ QUELQUES SECONDES...", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
              ],
            )
          : const Text("METTRE À JOUR", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
      ),
    );
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text("✅ Succès"),
        content: const Text("Votre mot de passe a été réinitialisé avec succès !"),
        actions: [
          TextButton(
            onPressed: () => Navigator.pushNamed(context, AppRoutes.login),
            child: const Text("Se connecter maintenant", style: TextStyle(color: Color(0xFF28A745), fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}