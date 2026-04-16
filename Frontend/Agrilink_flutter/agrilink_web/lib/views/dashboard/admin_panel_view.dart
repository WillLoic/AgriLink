import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import '../../services/admin_service.dart';
import '../../routes.dart';

class AdminPanelView extends StatefulWidget {
  const AdminPanelView({super.key});

  @override
  State<AdminPanelView> createState() => _AdminPanelViewState();
}

class _AdminPanelViewState extends State<AdminPanelView> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final AdminService _adminService = AdminService();
  final _storage = const FlutterSecureStorage();

  bool _isLoading = true;
  List<dynamic> _users = [];
  Map<String, dynamic>? _analytics;
  String? _token;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _checkAccessAndFetchData();
  }

  Future<void> _checkAccessAndFetchData() async {
    try {
      final token = await _storage.read(key: 'jwt_token');
      
      // RIGUEUR : On vérifie le rôle directement dans le token avant toute chose
      if (token == null || JwtDecoder.isExpired(token)) {
        _logout();
        return;
      }

      Map<String, dynamic> decodedToken = JwtDecoder.decode(token);
      String role = decodedToken['role']?.toString().toLowerCase() ?? 'user';

      if (role != 'admin') {
        // Si l'utilisateur n'est pas admin, on le dégage immédiatement
        if (mounted) Navigator.pop(context);
        return;
      }

      _token = token;
      
      // RÉCUPÉRATION DES VRAIES DONNÉES
      final usersData = await _adminService.getAllUsers(token);
      final statsData = await _adminService.getGlobalStats(token);

      setState(() {
        _users = usersData;
        _analytics = statsData;
        _isLoading = false;
      });
    } catch (e) {
      print("Erreur Admin Panel: $e");
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Erreur de chargement des données Admin")),
        );
      }
    }
  }

  void _logout() {
    Navigator.pushReplacementNamed(context, '/login');
  }

  Future<void> _handleRoleChange(int userId, String currentRole) async {
    bool success = false;
    String targetRole = currentRole.toLowerCase() == 'admin' ? 'user' : 'admin';

    try {
      if (targetRole == 'admin') {
        success = await _adminService.promoteUser(_token!, userId);
      } else {
        // Rigueur : Le backend interdit l'auto-rétrogradation, 
        // on pourrait ajouter un check ici aussi pour l'UI
        success = await _adminService.demoteUser(_token!, userId);
      }

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Statut mis à jour : $targetRole")),
        );
        _checkAccessAndFetchData(); // On recharge la liste pour voir le changement
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Erreur : Impossible de modifier le rôle")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    const primaryGreen = Color(0xFF2E7D32);
    const adminOrange = Color(0xFFFF9800);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 2,
        // --- AJOUT DU BOUTON RETOUR ---
        leading: IconButton(
          icon: const Icon(Icons.dashboard_outlined, color: Colors.black87),
          onPressed: () => Navigator.pushNamed(context, AppRoutes.dashboard), // Retour au Dashboard
          tooltip: "Retour au Dashboard",
        ),
        title: const Text("⚙️ Panel d'Administration", style: TextStyle(color: Colors.black)),
        bottom: TabBar(
          controller: _tabController,
          labelColor: primaryGreen,
          unselectedLabelColor: Colors.grey,
          indicatorColor: primaryGreen,
          tabs: const [
            Tab(icon: Icon(Icons.people), text: "Utilisateurs"),
            Tab(icon: Icon(Icons.bar_chart), text: "Statistiques"),
          ],
        ),
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator(color: primaryGreen))
        : TabBarView(
            controller: _tabController,
            children: [
              _buildUserManagementTab(primaryGreen, adminOrange),
              _buildStatisticsTab(primaryGreen),
            ],
          ),
    );
  }

  Widget _buildUserManagementTab(Color green, Color orange) {
    return RefreshIndicator(
      onRefresh: _checkAccessAndFetchData,
      child: ListView(
        padding: const EdgeInsets.all(15),
        children: [
          Row(
            children: [
              _buildSmallStat("Total Membres", "${_users.length}", Colors.blue),
              const SizedBox(width: 10),
              _buildSmallStat("Admins", "${_users.where((u) => u['role'].toString().toLowerCase() == 'admin').length}", orange),
            ],
          ),
          const SizedBox(height: 20),
          const Text("Gestion des comptes", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          const SizedBox(height: 10),
          
          ..._users.map((user) {
            bool isAdmin = user['role'].toString().toLowerCase() == 'admin';
            return Container(
              margin: const EdgeInsets.only(bottom: 15),
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: isAdmin ? const Color(0xFFFFF3E0) : Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border(left: BorderSide(color: isAdmin ? orange : green, width: 5)),
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 5)],
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        backgroundColor: isAdmin ? orange.withOpacity(0.2) : green.withOpacity(0.1),
                        child: Text(isAdmin ? "🛡️" : "👤"),
                      ),
                      const SizedBox(width: 15),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(user['nom'] ?? 'Sans nom', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            Text(user['email'] ?? 'Pas d\'email', style: const TextStyle(color: Colors.grey, fontSize: 13)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const Divider(height: 25),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text("🌾 ${user['culture_type'] ?? 'Non spécifiée'}", style: const TextStyle(fontSize: 12)),
                      ElevatedButton(
                        onPressed: () => _handleRoleChange(user['id'], user['role']),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: isAdmin ? Colors.redAccent : green,
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        ),
                        child: Text(
                          isAdmin ? "RÉTROGRADER" : "PROMOUVOIR",
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  )
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  // --- STATS TAB ---
  Widget _buildStatisticsTab(Color green) {
    var recent = _analytics?['recent_activity'] ?? {};
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("📈 Performances Système", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          const SizedBox(height: 20),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 15,
            mainAxisSpacing: 15,
            childAspectRatio: 1.4,
            children: [
              _buildMetricCard("Utilisateurs", "${_analytics?['total_users'] ?? 0}", Icons.group, Colors.blue),
              _buildMetricCard("Total Scans", "${_analytics?['total_scans'] ?? 0}", Icons.qr_code_2, Colors.green),
              _buildMetricCard("Logins (30j)", "${recent['logins_30_days'] ?? 0}", Icons.login, Colors.orange),
              _buildMetricCard("Scans (30j)", "${recent['scans_30_days'] ?? 0}", Icons.analytics, Colors.purple),
            ],
          ),
          const SizedBox(height: 30),
          const Text("📸 Évolution des Scans (7 derniers jours)", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 15),
          _buildLineChart(green, _getScanSpots()),
        ],
      ),
    );
  }

  List<FlSpot> _getScanSpots() {
    // Rigueur : Idéalement, transforme les données de ton API en FlSpot
    // Ici on garde une structure de base si l'API ne renvoie pas encore la série temporelle
    return [const FlSpot(0, 2), const FlSpot(1, 5), const FlSpot(2, 3), const FlSpot(3, 8), const FlSpot(4, 6), const FlSpot(5, 9), const FlSpot(6, 7)];
  }

  Widget _buildLineChart(Color color, List<FlSpot> spots) {
    return Container(
      height: 200,
      padding: const EdgeInsets.only(right: 20, top: 10),
      child: LineChart(
        LineChartData(
          gridData: const FlGridData(show: false),
          titlesData: const FlTitlesData(
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: true, border: Border(bottom: BorderSide(color: Colors.grey.shade300), left: BorderSide(color: Colors.grey.shade300))),
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              color: color,
              barWidth: 4,
              belowBarData: BarAreaData(show: true, color: color.withOpacity(0.1)),
              dotData: const FlDotData(show: true),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSmallStat(String label, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 15),
        decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
        child: Column(
          children: [
            Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color)),
            Text(label, style: TextStyle(color: color, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(15),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10)],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 11)),
        ],
      ),
    );
  }
}