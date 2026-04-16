import 'dart:convert'; // Ajouté pour le formatage des coordonnées
import 'package:flutter/material.dart';
import '../../routes.dart';
import '../../services/auth_service.dart'; // Import du service ajouté

class RegisterView extends StatefulWidget {
  const RegisterView({super.key});
  
  @override
  State<RegisterView> createState() => _RegisterViewState();
}

class _RegisterViewState extends State<RegisterView> {
  bool _isPasswordVisible = false;
  bool _isLoading = false; 
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _phoneController = TextEditingController();
  String _selectedCulture = "Maïs"; // Valeur par défaut
  final List<String> _cultures = [
  "Maïs", "Riz", "Cacao", "Café", "Manioc", 
  "Tomates", "Pommes de terre", "Blé", "Soja", "Arachide"
];

  // Instance du service
  final AuthService _authService = AuthService();

  String? _nameError;
  String? _emailError;
  String? _phoneError;
  String? _passError;
  String? _confirmError;

  void _validateEmail(String val) {
    setState(() {
      if (val.isNotEmpty && !val.contains('@')) {
        _emailError = "L'email n'est pas valide (il manque le @)";
      } else {
        _emailError = null;
      }
    });
  }

  void _handleRegister() async {
    setState(() {
      _nameError = _nameController.text.isEmpty ? "Le nom est requis" : null;
      _phoneError = _phoneController.text.isEmpty ? "Le numéro est requis" : null;
      _passError = _passwordController.text.isEmpty ? "Le mot de passe est requis" : null;
      
      if (_confirmPasswordController.text != _passwordController.text) {
        _confirmError = "Les mots de passe ne correspondent pas";
      } else {
        _confirmError = null;
      }
    });

    if (_nameError == null && _emailError == null && _phoneError == null && _passError == null && _confirmError == null) {
      setState(() => _isLoading = true);
      
      // Simulation/Préparation des coordonnées (Ton backend attend un JSON string de coords)
      // Note : En phase finale, on utilisera le package 'geolocator' ici.
      String initialCoords = jsonEncode([[5.3484, -4.0305], [5.3485, -4.0306], [5.3486, -4.0307], [5.3484, -4.0305]]);

      // Appel réel au service
      final result = await _authService.register(
        nom: _nameController.text,
        phone: _phoneController.text,
        email: _emailController.text,
        password: _passwordController.text,
        cultureType: _selectedCulture,
        coords: initialCoords,
      );
      
      if (!mounted) return;
      setState(() => _isLoading = false);
      
      if (result['success']) {
        // --- CONNEXION AUTOMATIQUE SILENCIEUSE ---
      setState(() => _isLoading = true); // On garde l'état de chargement
      
      // On appelle la méthode login du service avec les identifiants déjà en mémoire
      final loginResult = await _authService.login(
        _phoneController.text,
        _passwordController.text,
      );

      if (!mounted) return;
      setState(() => _isLoading = false);

      if (loginResult['success']) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Inscription réussie ! Bienvenue sur AgriLink 🌱"),
            backgroundColor: Color(0xFF28A745),
            behavior: SnackBarBehavior.floating,
          ),
        );

        // Redirection directe vers le Dashboard (en vidant la pile de navigation)
        Navigator.pushNamedAndRemoveUntil(
          context, 
          AppRoutes.dashboard, 
          (route) => false,
        );
      } else {
        // Cas rare : inscrit mais login échoue (ex: serveur tombé entre temps)
        Navigator.pushReplacementNamed(context, AppRoutes.login);
      }
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
            padding: const EdgeInsets.symmetric(vertical: 40),
            child: TweenAnimationBuilder(
              duration: const Duration(milliseconds: 600),
              tween: Tween<double>(begin: 0, end: 1),
              builder: (context, double value, child) {
                return Opacity(
                  opacity: value,
                  child: Transform.scale(
                    scale: 0.95 + (0.05 * value),
                    child: child,
                  ),
                );
              },
              child: _buildRegisterCard(),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRegisterCard() {
    return Container(
      width: 500,
      padding: const EdgeInsets.all(40),
      margin: const EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(25),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 40,
            offset: const Offset(0, 20),
          )
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text("🌱", style: TextStyle(fontSize: 45)),
          const SizedBox(height: 15),
          const Text(
            "Rejoindre AgriLink",
            style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Color(0xFF2C3E50)),
          ),
          const SizedBox(height: 10),
          const Text(
            "Créez votre compte en quelques secondes",
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF7F8C8D)),
          ),
          const SizedBox(height: 35),
          
          _buildTextField(
            controller: _nameController,
            label: "Nom Complet",
            icon: Icons.person_outline_rounded,
            hint: "Loïc Agre",
            errorText: _nameError,
          ),
          const SizedBox(height: 15),
          _buildTextField(
            controller: _emailController,
            label: "Adresse Email",
            icon: Icons.alternate_email_rounded,
            hint: "loic@agrilink.com",
            errorText: _emailError,
            onChanged: _validateEmail,
          ),
          const SizedBox(height: 15),
          _buildTextField(
            controller: _phoneController,
            label: "Numéro de téléphone",
            icon: Icons.phone_android_rounded,
            hint: "+237 6XX XXX XXX",
            errorText: _phoneError,
          ),
          const SizedBox(height: 15),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "Type de culture",
                style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2C3E50), fontSize: 13),
              ),
              const SizedBox(height: 6),
              DropdownButtonFormField<String>(
                value: _selectedCulture,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: const Color(0xFFF8F9FA),
                  prefixIcon: const Icon(Icons.agriculture, color: Color(0xFF28A745), size: 20),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                ),
                items: _cultures.map((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                onChanged: (newValue) {
                  setState(() {
                    _selectedCulture = newValue!;
                  });
                },
              ),
            ],
          ),
          const SizedBox(height: 15),
          _buildTextField(
            controller: _passwordController,
            label: "Mot de passe",
            icon: Icons.lock_outline_rounded,
            isPassword: true,
            hint: "••••••••",
            errorText: _passError,
          ),
          const SizedBox(height: 15),
          _buildTextField(
            controller: _confirmPasswordController,
            label: "Confirmer le mot de passe",
            icon: Icons.security_rounded,
            isPassword: true,
            hint: "••••••••",
            errorText: _confirmError,
          ),

          const SizedBox(height: 35),
          
          _buildRegisterButton(),
          
          const SizedBox(height: 20),
          
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text("Déjà inscrit ?"),
              TextButton(
                onPressed: () => Navigator.pushNamed(context, AppRoutes.login),
                child: const Text(
                  "Se connecter",
                  style: TextStyle(color: Color(0xFF28A745), fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Retour", style: TextStyle(color: Color(0xFF7F8C8D))),
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
    Function(String)? onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2C3E50), fontSize: 13),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: controller,
          onChanged: onChanged,
          enabled: !_isLoading, // Désactivation lors du chargement
          obscureText: isPassword && !_isPasswordVisible,
          decoration: InputDecoration(
            errorText: errorText,
            hintText: hint,
            prefixIcon: Icon(icon, color: const Color(0xFF28A745), size: 20),
            suffixIcon: isPassword 
              ? IconButton(
                  icon: Icon(_isPasswordVisible ? Icons.visibility : Icons.visibility_off, size: 20),
                  onPressed: () => setState(() => _isPasswordVisible = !_isPasswordVisible),
                )
              : null,
            filled: true,
            fillColor: const Color(0xFFF8F9FA),
            contentPadding: const EdgeInsets.symmetric(vertical: 15),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF28A745), width: 1.5),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRegisterButton() {
    return Container(
      width: double.infinity,
      height: 55,
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF28A745), Color(0xFF20C997)]),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF28A745).withOpacity(0.25),
            blurRadius: 15,
            offset: const Offset(0, 8),
          )
        ],
      ),
      child: ElevatedButton(
        onPressed: _isLoading ? null : _handleRegister,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        child: _isLoading 
          ? const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
            )
          : const Text(
              "CRÉER MON COMPTE",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
            ),
      ),
    );
  }
}