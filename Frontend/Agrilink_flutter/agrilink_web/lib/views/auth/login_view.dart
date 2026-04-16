import 'package:flutter/material.dart';
import '../../routes.dart';
import '../../services/auth_service.dart'; // Import du service ajouté

class LoginView extends StatefulWidget {
  const LoginView({super.key});

  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  bool _isPasswordVisible = false;
  bool _isLoading = false; 
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  
  // Instance du service pour la communication Backend
  final AuthService _authService = AuthService(); 

  String? _phoneError;
  String? _passwordError;

  void _handleLogin() async {
    setState(() {
      _phoneError = null;
      _passwordError = null;
    });

    bool isValid = true;

    if (_phoneController.text.isEmpty) {
      setState(() => _phoneError = "Le numéro de téléphone est requis");
      isValid = false;
    } 

    if (_passwordController.text.isEmpty) {
      setState(() => _passwordError = "Le mot de passe est requis");
      isValid = false;
    }

    if (isValid) {
      setState(() => _isLoading = true); 

      // Appel réel au service AuthService (Flask Backend)
      final result = await _authService.login(
        _phoneController.text,
        _passwordController.text,
      );

      if (!mounted) return;
      setState(() => _isLoading = false); 

      if (result['success']) {
        // Si le token est reçu et stocké, on dirige vers le dashboard
        Navigator.pushReplacementNamed(context, AppRoutes.dashboard);
      } else {
        // Affichage de l'erreur réelle renvoyée par ton API Flask
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['message'] ?? "Identifiants incorrects. Réessayez."),
            backgroundColor: Colors.redAccent,
            behavior: SnackBarBehavior.floating,
            margin: const EdgeInsets.all(20),
          ),
        );
      }
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
            child: TweenAnimationBuilder(
              duration: const Duration(milliseconds: 800),
              tween: Tween<double>(begin: 0, end: 1),
              builder: (context, double value, child) {
                return Opacity(
                  opacity: value,
                  child: Transform.translate(
                    offset: Offset(0, 30 * (1 - value)),
                    child: child,
                  ),
                );
              },
              child: _buildLoginCard(),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLoginCard() {
    return Container(
      width: 450,
      padding: const EdgeInsets.all(40),
      margin: const EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(25),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 30,
            offset: const Offset(0, 15),
          )
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text("🌱", style: TextStyle(fontSize: 50)),
          const SizedBox(height: 10),
          const Text(
            "Bon retour !",
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF2C3E50)),
          ),
          const SizedBox(height: 8),
          const Text(
            "Connectez-vous pour gérer vos cultures",
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF7F8C8D), fontSize: 16),
          ),
          const SizedBox(height: 40),
          
          _buildTextField(
            controller: _phoneController,
            label: "Numéro de téléphone",
            icon: Icons.phone,
            hint: "06 12 34 56 78",
            errorText: _phoneError,
          ),
          
          const SizedBox(height: 20),
          
          _buildTextField(
            controller: _passwordController,
            label: "Mot de passe",
            icon: Icons.lock_outline_rounded,
            isPassword: true,
            hint: "••••••••",
            errorText: _passwordError,
          ),
          
          Align(
            alignment: Alignment.centerRight,
            child: TextButton(
              onPressed: _isLoading ? null : () => Navigator.pushNamed(context, AppRoutes.recovery),
              child: const Text(
                "Mot de passe oublié ?",
                style: TextStyle(color: Color(0xFF28A745), fontWeight: FontWeight.w600),
              ),
            ),
          ),
          
          const SizedBox(height: 30),
          
          _buildLoginButton(),
          
          const SizedBox(height: 25),
          
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text("Nouveau sur AgriLink ?"),
              TextButton(
                onPressed: _isLoading ? null : () => Navigator.pushNamed(context, AppRoutes.register),
                child: const Text(
                  "Créer un compte",
                  style: TextStyle(color: Color(0xFF28A745), fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          
          TextButton.icon(
            onPressed: _isLoading ? null : () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back, size: 16),
            label: const Text("Retour à l'accueil"),
            style: TextButton.styleFrom(foregroundColor: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    String? hint,
    bool isPassword = false,
    String? errorText,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2C3E50), fontSize: 14),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          enabled: !_isLoading, 
          obscureText: isPassword && !_isPasswordVisible,
          decoration: InputDecoration(
            hintText: hint,
            errorText: errorText,
            prefixIcon: Icon(icon, color: const Color(0xFF28A745)),
            suffixIcon: isPassword 
              ? IconButton(
                  icon: Icon(_isPasswordVisible ? Icons.visibility : Icons.visibility_off, color: Colors.grey),
                  onPressed: () => setState(() => _isPasswordVisible = !_isPasswordVisible),
                )
              : null,
            filled: true,
            fillColor: const Color(0xFFF8F9FA),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(15),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(15),
              borderSide: const BorderSide(color: Color(0xFF28A745), width: 2),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLoginButton() {
    return Container(
      width: double.infinity,
      height: 55,
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF28A745), Color(0xFF20C997)]),
        borderRadius: BorderRadius.circular(50),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF28A745).withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          )
        ],
      ),
      child: ElevatedButton(
        onPressed: _isLoading ? null : _handleLogin, 
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
                Text(
                  "CONNEXION EN COURS...",
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                ),
              ],
            )
          : const Text(
              "SE CONNECTER",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white, letterSpacing: 1.2),
            ),
      ),
    );
  }
}