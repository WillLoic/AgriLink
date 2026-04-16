import 'package:flutter/material.dart';
import 'package:pluto_grid/pluto_grid.dart'; 
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../services/history_service.dart';
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html; 

class HistoryView extends StatefulWidget {
  const HistoryView({super.key});

  @override
  State<HistoryView> createState() => _HistoryViewState();
}

class _HistoryViewState extends State<HistoryView> {
  final DashboardService _dashboardService = DashboardService();
  final _storage = const FlutterSecureStorage();
  
  List<Map<String, dynamic>> _historique = [];
  Map<String, dynamic>? _stats;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      final token = await _storage.read(key: 'jwt_token');
      if (token == null) throw Exception("Token non trouvé");

      final data = await _dashboardService.getDashboardData(token);
      
      setState(() {
        _historique = List<Map<String, dynamic>>.from(data['historique']);
        _stats = {
          "total": data['total_scans'],
          "score": data['score'],
        };
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  // --- LOGIQUE D'EXPORT CSV ---
  void _exportToCSV() {
    if (_historique.isEmpty) return;
    String csvData = "Date,Statut,Score,Diagnostic\n";
    for (var item in _historique) {
      csvData += "${item['date']},${item['statut']},${((item['facteur'] ?? 0)*100).toInt()}%,${item['diagnostic']}\n";
    }
    final bytes = utf8.encode(csvData);
    final blob = html.Blob([bytes]);
    final url = html.Url.createObjectUrlFromBlob(blob);
    final anchor = html.document.createElement('a') as html.AnchorElement
      ..href = url
      ..download = 'historique_agrilink.csv';
    anchor.click();
    html.Url.revokeObjectUrl(url);
  }

  @override
  Widget build(BuildContext context) {
    const primaryGreen = Color(0xFF2E7D32);

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        title: const Text("📜 Historique des analyses"),
        actions: [
          IconButton(
            icon: const Icon(Icons.download_rounded),
            onPressed: _historique.isEmpty ? null : _exportToCSV,
          ),
          const SizedBox(width: 10),
        ],
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : _errorMessage != null 
          ? Center(child: Text("⚠️ $_errorMessage"))
          : _buildContent(primaryGreen),
    );
  }

  Widget _buildContent(Color primaryGreen) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildStatsGrid(),
              const SizedBox(height: 30),
              const Text("### 🃏 Vue détaillée", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 15),
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _historique.length,
                itemBuilder: (context, index) => _buildHistoryCard(_historique[index]),
              ),
              const SizedBox(height: 40),
              const Text("### 📊 Vue synthétique", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 15),
              _buildInteractiveTable(),
              const SizedBox(height: 40),
              _buildActionButtons(context, primaryGreen),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatsGrid() {
    return Row(
      children: [
        _statItem("Total des analyses", "${_stats?['total'] ?? 0}", Icons.analytics_outlined),
        _statItem("Score Global", "${_stats?['score'] ?? 0}/100", Icons.speed),
      ],
    );
  }

  Widget _statItem(String label, String value, IconData icon) {
    return Expanded(
      child: Card(
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: const BorderSide(color: Colors.black12)),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Icon(icon, color: Colors.grey, size: 28),
              const SizedBox(height: 8),
              Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
              Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 22)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInteractiveTable() {
    return Container(
      height: 400,
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(10), border: Border.all(color: Colors.black12)),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(10),
        child: PlutoGrid(
          columns: [
            PlutoColumn(title: '📅 Date', field: 'date', type: PlutoColumnType.text(), width: 150),
            PlutoColumn(title: '🏥 Statut', field: 'statut', type: PlutoColumnType.text(), width: 120),
            PlutoColumn(title: '📊 Score', field: 'score', type: PlutoColumnType.text(), width: 100),
            PlutoColumn(title: '🔍 Diagnostic', field: 'diag', type: PlutoColumnType.text(), width: 500),
          ],
          rows: _historique.map((item) => PlutoRow(
            cells: {
              'date': PlutoCell(value: item['date']),
              'statut': PlutoCell(value: item['statut']),
              'score': PlutoCell(value: "${((item['facteur'] ?? 0) * 100).toInt()}%"),
              'diag': PlutoCell(value: item['diagnostic']),
            },
          )).toList(),
          mode: PlutoGridMode.select,
        ),
      ),
    );
  }

  Widget _buildHistoryCard(Map<String, dynamic> data) {
    final String statut = data['statut'] ?? "INCONNU";
    final double facteur = (data['facteur'] ?? 0).toDouble();
    
    // Mapping des couleurs SAIN / MALADE
    Color borderColor = (statut == "SAIN") ? const Color(0xFF28A745) : const Color(0xFFDC3545);
    Color bgColor = (statut == "SAIN") ? const Color(0xFFD4EDDA) : const Color(0xFFF8D7DA);

    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(10),
        border: Border(left: BorderSide(color: borderColor, width: 6)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("📅 Analyse - ${data['date']}", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                _buildScoreBadge(facteur, statut),
              ],
            ),
            const SizedBox(height: 10),
            Text("Statut général: $statut", style: const TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 5),
            Text("Diagnostic: ${data['diagnostic']}", style: const TextStyle(color: Colors.black87)),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreBadge(double facteur, String statut) {
    Color color = (statut == "SAIN") ? const Color(0xFF28A745) : const Color(0xFFDC3545);
    String label = (statut == "SAIN") ? "Excellent" : "Critique";
    String icon = (statut == "SAIN") ? "🌱" : "🚨";

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(15)),
      child: Text("$icon ${(facteur * 100).toInt()}% - $label", 
        style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }

  Widget _buildActionButtons(BuildContext context, Color green) {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () => Navigator.pushNamed(context, '/scan'),
            icon: const Icon(Icons.camera_alt, color: Colors.white),
            label: const Text("Nouvelle analyse", style: TextStyle(color: Colors.white)),
            style: ElevatedButton.styleFrom(backgroundColor: green, padding: const EdgeInsets.symmetric(vertical: 20)),
          ),
        ),
        const SizedBox(width: 15),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.dashboard),
            label: const Text("Dashboard"),
            style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 20)),
          ),
        ),
      ],
    );
  }
}