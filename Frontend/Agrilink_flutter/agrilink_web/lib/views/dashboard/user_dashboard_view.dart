import 'package:flutter/material.dart';
import '../../routes.dart';
import '../../services/dashboard_service.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart'; // Import indispensable pour le stockage sécurisé du token
import 'package:jwt_decoder/jwt_decoder.dart'; // Import du décodeur JWT pour extraire les rôles du token
import '../../services/admin_service.dart'; // Import du nouveau service admin

class DashboardView extends StatefulWidget {
  const DashboardView({super.key});

  @override
  State<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends State<DashboardView> {
  final DashboardService _dashboardService = DashboardService();
  final AdminService _adminService = AdminService(); // Instance pour les stats globales
  final _storage = const FlutterSecureStorage();

  bool _isLoading = true;
  String? _errorMessage;
  Map<String, dynamic> _stats = {};
  String userRole = 'user';

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // 1. Récupération du token
      final String? token = await _storage.read(key: 'jwt_token');

      if (token == null || JwtDecoder.isExpired(token)) {
        if (mounted) Navigator.pushReplacementNamed(context, AppRoutes.login);
        return;
      }

      // 2. Décodage du rôle
      Map<String, dynamic> decodedToken = JwtDecoder.decode(token);
      String extractedRole = decodedToken['role']?.toString().toLowerCase() ?? 'user';

      // 3. Appel simultané ou séquentiel des services
      // On récupère d'abord les stats personnelles de l'utilisateur
      final Map<String, dynamic> data = await _dashboardService.fetchDashboardData(token);

      // 4. RIGUEUR : Si Admin, on enrichit l'objet data avec les stats globales
      if (extractedRole == 'admin') {
        try {
          final globalStats = await _adminService.getGlobalStats(token);
          // On injecte les données globales dans notre map locale
          data['global_users'] = globalStats['total_users'];
          data['global_scans'] = globalStats['total_scans'];
        } catch (adminError) {
          print("Erreur silencieuse lors de la récupération des stats globales: $adminError");
          // On ne bloque pas l'affichage du dashboard si seules les stats admin échouent
          data['global_users'] = "Erreur";
          data['global_scans'] = "Erreur";
        }
      }

      if (mounted) {
        setState(() {
          _stats = data;
          userRole = extractedRole;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = "Erreur de connexion au serveur.";
          _isLoading = false;
        });
      }
    }
  }


  /// Helper pour transformer le score numérique en label de confiance
  String _getConfianceStatus(int score) {
    if (score >= 75) return 'Excellent';
    if (score >= 50) return 'Correct';
    return 'Critique';
  }

  @override
  Widget build(BuildContext context) {
    const primaryGreen = Color(0xFF2E7D32);

    // Écran de chargement
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: primaryGreen)),
      );
    }

    // Écran d'erreur avec bouton de réessai
    if (_errorMessage != null) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
              TextButton(onPressed: _loadDashboardData, child: const Text("Réessayer")),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7F6),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Text(
          "Dashboard : ${_stats['agriculteur'] ?? 'Utilisateur'}",
          style: const TextStyle(color: Colors.black87, fontSize: 18, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded, color: Colors.redAccent),
            onPressed: () => Navigator.pushReplacementNamed(context, AppRoutes.login),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboardData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // --- SCORE CARD DYNAMIQUE ---
              _buildScoreCard(
                _stats['score'] ?? 0, 
                _getConfianceStatus(_stats['score'] ?? 0)
              ),

              const SizedBox(height: 25),

              // --- METRICS DYNAMIQUES ---
              Row(
                children: [
                  _buildMetricCard("Scans Effectués", "${_stats['total_scans'] ?? 0}", Icons.qr_code_scanner),
                  const SizedBox(width: 15),
                  _buildMetricCard("Culture", "${_stats['culture'] ?? 'N/A'}", Icons.grass),
                ],
              ),

              const SizedBox(height: 30),

              // --- ACTIONS ---
              const Text("Actions Rapides", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 15),
              Row(
                children: [
                  _buildActionButton("Nouveau Scan", Icons.add_a_photo, primaryGreen, () => Navigator.pushNamed(context, AppRoutes.scan)),
                  const SizedBox(width: 15),
                  _buildActionButton("Historique", Icons.history, Colors.blueGrey, () => Navigator.pushNamed(context, AppRoutes.history)),
                ],
              ),

              // --- SECTION ADMIN CONDITIONNELLE ---
              if (userRole == 'admin') ...[
                const SizedBox(height: 40),
                const Divider(),
                const SizedBox(height: 20),
                const Row(
                  children: [
                    Icon(Icons.admin_panel_settings, color: Colors.orange),
                    SizedBox(width: 10),
                    Text("Statistiques Globales (Admin)", 
                         style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold, color: Colors.orange)),
                  ],

                ),
                const SizedBox(height: 20),
                _buildAdminAnalytics(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  // --- WIDGETS DE CONSTRUCTION ---

  Widget _buildScoreCard(int score, String statut) {
    Color color = score >= 75 ? const Color(0xFF2ECC71) : score >= 50 ? const Color(0xFFF1C40F) : const Color(0xFFE74C3C);
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(25),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border(left: BorderSide(color: color, width: 10)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 15)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("SCORE DE CRÉDIBILITÉ", 
              style: TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
          const SizedBox(height: 10),
          RichText(
            text: TextSpan(
              children: [
                TextSpan(text: "$score", 
                    style: TextStyle(fontSize: 50, fontWeight: FontWeight.bold, color: color)),
                const TextSpan(text: " / 100", 
                    style: TextStyle(fontSize: 20, color: Colors.grey)),
              ],
            ),
          ),
          const SizedBox(height: 10),
          Text("📌 Statut : $statut", style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 15)),
        ],
      ),
    );
  }

  Widget _buildMetricCard(String label, String value, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(15),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: const Color(0xFF2E7D32), size: 20),
            const SizedBox(height: 10),
            Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold), overflow: TextOverflow.ellipsis),
            Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(String label, IconData icon, Color color, VoidCallback onTap) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(15),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 20),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(15),
            boxShadow: [BoxShadow(color: color.withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 4))],
          ),
          child: Column(
            children: [
              Icon(icon, color: Colors.white),
              const SizedBox(height: 8),
              Text(label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAdminAnalytics() {
    return Column(
      children: [
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 15,
          mainAxisSpacing: 15,
          childAspectRatio: 1.5,
          children: [
            // Utilisation des clés 'global_users' et 'global_scans' injectées plus haut
            _buildAdminMiniCard(
              "Utilisateurs", 
              "${_stats['global_users'] ?? '...'}", 
              Icons.people
            ),
            _buildAdminMiniCard(
              "Total Scans", 
              "${_stats['global_scans'] ?? '...'}", 
              Icons.analytics
            ),
          ],
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          height: 50,
          child: OutlinedButton.icon(
            onPressed: () => Navigator.pushNamed(context, AppRoutes.adminPanel),
            icon: const Icon(Icons.settings),
            label: const Text("ACCÉDER AU PANEL ADMIN"),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.orange,
              side: const BorderSide(color: Colors.orange),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildAdminMiniCard(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF3E0),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.orange.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.orange),
          const SizedBox(height: 5),
          Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          Text(label, style: const TextStyle(fontSize: 11, color: Colors.black54)),
        ],
      ),
    );
  }
}