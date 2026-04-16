// Modèle pour une entrée d'historique (utilisé dans Dashboard et History)
class ScanHistoryItem {
  final String date;
  final String statut;
  final double facteur;
  final String diagnostic;

  ScanHistoryItem({required this.date, required this.statut, required this.facteur, required this.diagnostic});

  factory ScanHistoryItem.fromJson(Map<String, dynamic> json) => ScanHistoryItem(
    date: json['date'],
    statut: json['statut'],
    facteur: json['facteur'].toDouble(),
    diagnostic: json['diagnostic'],
  );
}

// Modèle pour le résultat d'un nouveau Scan (ScanView)
class ScanResult {
  final String statutSante;
  final String diagnosticPrecis;
  final double facteurSante;
  final Map<String, dynamic> protocoleIntervention;
  final double confianceIA; // À extraire de ton modèle Gemini

  ScanResult({
    required this.statutSante, 
    required this.diagnosticPrecis, 
    required this.facteurSante, 
    required this.protocoleIntervention,
    this.confianceIA = 0.85 // Valeur par défaut si non fournie
  });
}