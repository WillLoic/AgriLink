import 'package:flutter/material.dart';
import '../../services/auth_service.dart'; // Import du service ajouté

class PasswordRecoveryView extends StatefulWidget {
  const PasswordRecoveryView({super.key});

  @override
  State<PasswordRecoveryView> createState() => _PasswordRecoveryViewState();
}

class _PasswordRecoveryViewState extends State<PasswordRecoveryView> {
  final _emailController = TextEditingController();
  bool _isLoading = false; // État de chargement
  String? _emailError; // Variable pour l'erreur visuelle
  final _authService = AuthService(); // Ajoute l'instance du service

  void _handleRecovery() async {
    if (_emailController.text.isEmpty || !_emailController.text.contains('@')) {
      setState(() => _emailError = "Veuillez entrer un email valide");
      return;
    }

    setState(() => _isLoading = true);

    final result = await _authService.forgotPassword(_emailController.text);

    setState(() => _isLoading = false);

    if (result['success']) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Lien de récupération envoyé ! Check tes mails."),
          backgroundColor: Color(0xFF28A745),
        ),
      );
      // Optionnel : Rediriger vers l'accueil ou informer de l'étape suivante
    } else {
      setState(() => _emailError = result['message']);
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
          child: Container(
            width: 450,
            padding: const EdgeInsets.all(40),
            margin: const EdgeInsets.symmetric(horizontal: 20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(25),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 20)],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text("🔑", style: TextStyle(fontSize: 50)),
                const SizedBox(height: 20),
                const Text(
                  "Mot de passe oublié ?",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF2C3E50)),
                ),
                const SizedBox(height: 15),
                const Text(
                  "Entrez votre adresse email. Nous vous enverrons un lien pour réinitialiser votre mot de passe.",
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xFF7F8C8D), height: 1.5),
                ),
                const SizedBox(height: 35),
                
                TextField(
                  controller: _emailController,
                  enabled: !_isLoading, // Désactive le champ pendant l'envoi
                  decoration: InputDecoration(
                    labelText: "Votre Email",
                    errorText: _emailError, // Affichage de l'erreur
                    prefixIcon: const Icon(Icons.email_outlined, color: Color(0xFF28A745)),
                    filled: true,
                    fillColor: const Color(0xFFF8F9FA),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(15), borderSide: BorderSide.none),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(15),
                      borderSide: const BorderSide(color: Color(0xFF28A745), width: 1.5),
                    ),
                  ),
                ),
                
                const SizedBox(height: 30),
                
                _buildRecoveryButton(),
                
                const SizedBox(height: 20),
                
                TextButton(
                  onPressed: _isLoading ? null : () => Navigator.pop(context),
                  child: const Text("← Retour à la connexion", style: TextStyle(color: Color(0xFF7F8C8D))),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRecoveryButton() {
    return Container(
      width: double.infinity,
      height: 55,
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF28A745), Color(0xFF20C997)]),
        borderRadius: BorderRadius.circular(50),
      ),
      child: ElevatedButton(
        onPressed: _isLoading ? null : _handleRecovery,
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
                  "ENVOI EN COURS...",
                  style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 14),
                ),
              ],
            )
          : const Text(
              "ENVOYER LE LIEN",
              style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
            ),
      ),
    );
  }
}