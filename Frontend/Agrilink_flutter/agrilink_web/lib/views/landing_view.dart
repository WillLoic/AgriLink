import 'package:flutter/material.dart';
import 'package:agrilink_web/routes.dart'; // N'oublie pas d'importer tes routes pour la navigation

class LandingView extends StatelessWidget {
  const LandingView({super.key});

  // --- NOUVELLE SECTION : EN SAVOIR PLUS ---
  // Note : Pas d'@override ici car c'est une fonction perso
  Widget _buildEnSavoirPlus() {
    return Container(
      width: 400,
      margin: const EdgeInsets.symmetric(vertical: 20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: BorderRadius.circular(15),
      ),
      child: ExpansionTile(
        leading: const Text("📖", style: TextStyle(fontSize: 20)),
        title: const Text(
          "En savoir plus sur AgriLink",
          style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2C3E50)),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("🌟 Découvrez AgriLink", 
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF28A745))),
                const SizedBox(height: 10),
                const Text(
                  "AgriLink est la première plateforme agricole qui utilise l'intelligence artificielle pour analyser la santé de vos cultures en quelques secondes.",
                  style: TextStyle(color: Color(0xFF7F8C8D), height: 1.5),
                ),
                const SizedBox(height: 15),
                _buildStep("1. 📸", "Prenez une photo de votre plante"),
                _buildStep("2. 🤖", "Notre IA analyse l'état de santé"),
                _buildStep("3. 💊", "Recevez des recommandations"),
                _buildStep("4. 📊", "Suivez l'évolution sur le dashboard"),
                const Divider(height: 30),
                const Text("Avantages :", style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 10),
                _buildAvantage("✅ Diagnostic instantané et précis"),
                _buildAvantage("✅ Recommandations personnalisées"),
                _buildAvantage("✅ Suivi historique complet"),
                _buildAvantage("✅ Interface simple et intuitive"),
              ],
            ),
          )
        ],
      ),
    );
  }

  Widget _buildStep(String icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Text("$icon $text", style: const TextStyle(fontWeight: FontWeight.w500)),
    );
  }

  Widget _buildAvantage(String text) {
    return Text(text, style: const TextStyle(color: Color(0xFF2E7D32), height: 1.8));
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
        child: SingleChildScrollView(
          child: Padding(
            // Récupère 10% de la largeur de l'écran dynamiquement
            padding: EdgeInsets.symmetric(
              horizontal: MediaQuery.of(context).size.width * 0.1, 
            ),
            child: Column(
              children: [
                const SizedBox(height: 20),
                _buildHeroHeader(),
                const SizedBox(height: 20),
                _buildActionButtons(context),
                _buildEnSavoirPlus(), // Ton expander est bien ici
                const SizedBox(height: 40),
                _buildSectionTitle("✨ Fonctionnalités principales"),
                _buildFeaturesGrid(),
                _buildStatsSection(),
                _buildCTASection(context),
                _buildSectionTitle("🌾 Cultures supportées"),
                _buildCulturesGrid(),
                _buildFooter(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // --- LES AUTRES FONCTIONS (Gardées telles quelles dans ton code) ---
  Widget _buildHeroHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 60, horizontal: 20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 30,
            offset: const Offset(0, 10),
          )
        ],
      ),
      child: Column(
        children: const [
          Text("🌱 AgriLink",
              style: TextStyle(
                fontSize: 56,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                shadows: [Shadow(blurRadius: 4, color: Colors.black38, offset: Offset(2, 2))],
              )),
          SizedBox(height: 20),
          Text("Révolutionnez votre agriculture avec l'intelligence artificielle",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 22, color: Colors.white, fontWeight: FontWeight.w500)),
          SizedBox(height: 30),
          Text(
            "Analysez la santé de vos cultures en temps réel, obtenez des recommandations personnalisées\net améliorez vos rendements grâce à notre technologie IA de pointe.",
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 18, color: Colors.white, height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    return Column(
      children: [
        _buildButton(
          text: "🚀 Commencer maintenant",
          isPrimary: true,
          onPressed: () => Navigator.pushNamed(context, AppRoutes.register),
        ),
        const SizedBox(height: 20),
        _buildButton(
          text: "🔐 J'ai déjà un compte",
          isPrimary: false,
          onPressed: () => Navigator.pushNamed(context, AppRoutes.login)
        ),
      ],
    );
  }

  Widget _buildButton({required String text, required bool isPrimary, required VoidCallback onPressed}) {
    return Container(
      width: 400,
      height: 55,
      decoration: isPrimary
          ? BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF28A745), Color(0xFF20C997)]),
              borderRadius: BorderRadius.circular(50),
              boxShadow: [BoxShadow(color: const Color(0xFF28A745).withOpacity(0.3), blurRadius: 15, offset: const Offset(0, 4))],
            )
          : BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(50),
              border: Border.all(color: Colors.white, width: 2),
            ),
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(50)),
        ),
        child: Text(text, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
      ),
    );
  }

  Widget _buildFeaturesGrid() {
    return LayoutBuilder(builder: (context, constraints) {
      return Wrap(
        spacing: 20,
        runSpacing: 20,
        children: [
          _buildFeatureCard("📸", "Analyse par photo", "Prenez simplement une photo de votre plante avec votre smartphone. Notre IA analyse automatiquement les signes de maladie, parasites et carences.", constraints.maxWidth),
          _buildFeatureCard("🩺", "Diagnostic instantané", "Recevez un diagnostic précis en quelques secondes avec un niveau de confiance et des recommandations de traitement adaptées.", constraints.maxWidth),
          _buildFeatureCard("📊", "Suivi historique", "Gardez un historique complet de vos analyses et suivez l'évolution de la santé de vos parcelles au fil du temps.", constraints.maxWidth),
        ],
      );
    });
  }

  Widget _buildFeatureCard(String icon, String title, String desc, double maxWidth) {
    double width = maxWidth > 900 ? (maxWidth - 60) / 3 : maxWidth;
    return Container(
      width: width,
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(15),
        border: const Border(left: BorderSide(color: Color(0xFF28A745), width: 5)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 25, offset: const Offset(0, 8))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(icon, style: const TextStyle(fontSize: 48)),
          const SizedBox(height: 20),
          Text(title, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF2C3E50))),
          const SizedBox(height: 15),
          Text(desc, style: const TextStyle(color: Color(0xFF7F8C8D), fontSize: 16, height: 1.6)),
        ],
      ),
    );
  }

  Widget _buildStatsSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(40),
      margin: const EdgeInsets.symmetric(vertical: 40),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(15),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 25)],
      ),
      child: Column(
        children: [
          const Text("🌍 Impact d'AgriLink", style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF2C3E50))),
          const SizedBox(height: 40),
          Wrap(
            spacing: 50,
            runSpacing: 30,
            alignment: WrapAlignment.center,
            children: [
              _buildStatItem("500+", "Agriculteurs actifs"),
              _buildStatItem("10K+", "Analyses réalisées"),
              _buildStatItem("95%", "Précision diagnostic"),
              _buildStatItem("24h", "Support technique"),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String number, String label) {
    return Column(
      children: [
        Text(number, style: const TextStyle(fontSize: 40, fontWeight: FontWeight.bold, color: Color(0xFF28A745))),
        Text(label, style: const TextStyle(fontSize: 18, color: Color(0xFF7F8C8D))),
      ],
    );
  }

  Widget _buildCTASection(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 50, horizontal: 30),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF667EEA), Color(0xFF764BA2)]),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          const Text("Prêt à révolutionner votre agriculture ?", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white)),
          const SizedBox(height: 20),
          const Text("Rejoignez des milliers d'agriculteurs qui ont déjà adopté AgriLink", style: TextStyle(fontSize: 18, color: Colors.white70)),
          const SizedBox(height: 30),
          _buildButton(text: "🌱 Créer mon compte gratuit", isPrimary: true, onPressed: () => Navigator.pushNamed(context, AppRoutes.register), // Vers Inscription aussi
),
        ],
      ),
    );
  }

  Widget _buildCulturesGrid() {
    final cultures = ["Maïs", "Riz", "Cacao", "Café", "Manioc", "Tomates", "Pommes de terre", "Blé", "Soja", "Arachide"];
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 20),
      child: Wrap(
        spacing: 15,
        runSpacing: 15,
        alignment: WrapAlignment.center,
        children: cultures.map((c) => Container(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(10),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 8)],
          ),
          child: Text("🌱 $c", style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        )).toList(),
      ),
    );
  }

  Widget _buildFooter() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(40),
      decoration: const BoxDecoration(border: Border(top: BorderSide(color: Color(0xFFECF0F1)))),
      child: Column(
        children: const [
          Text("AgriLink - Révolutionnez votre agriculture avec l'IA", style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF7F8C8D))),
          SizedBox(height: 10),
          Text("🏢 Siège social | 📧 willloic36@gmail.com | 📞 +237 692 25 34 74", style: TextStyle(fontSize: 14, color: Color(0xFF7F8C8D))),
          SizedBox(height: 20),
          Text("© 2026 AgriLink. Tous droits réservés. | Conditions générales", style: TextStyle(fontSize: 12, color: Color(0xFF7F8C8D))),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 20),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Text(title, style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF2C3E50))),
      ),
    );
  }
}