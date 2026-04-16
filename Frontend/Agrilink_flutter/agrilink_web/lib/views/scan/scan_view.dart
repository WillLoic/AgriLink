import 'dart:typed_data'; // Requis pour le traitement des images sur le Web
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import '../../routes.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart'; // Pour le token
import '../../services/scan_service.dart'; // Ajustez le chemin selon votre projet

class ScanView extends StatefulWidget {
  const ScanView({super.key});

  @override
  State<ScanView> createState() => _ScanViewState();
}

class _ScanViewState extends State<ScanView> with SingleTickerProviderStateMixin {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  bool _isCameraInitialized = false;
  bool _isAnalyzing = false;
  Map<String, dynamic>? _analysisResult; 

  // Variables pour le quota dynamique
  int _dailyUsed = 0;
  int _dailyLimit = 10;
  int _dailyRemaining = 10;

  late AnimationController _laserController;
  final ImagePicker _picker = ImagePicker();
  XFile? _capturedFile;
  String _source = "Appareil Photo";
  
  // Instances des services
  final ScanService _scanService = ScanService();
  final _storage = const FlutterSecureStorage();

  @override
  void initState() {
    super.initState();
    _initScanner();
    _loadInitialQuota(); // Charger le quota au démarrage
    _laserController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);
  }

  // Récupération initiale du quota depuis le backend
  Future<void> _loadInitialQuota() async {
    try {
      final token = await _storage.read(key: 'jwt_token');
      if (token != null) {
        final quota = await _scanService.getQuota(token);
        setState(() {
          _dailyUsed = quota['daily_used'];
          _dailyLimit = quota['daily_limit'];
          _dailyRemaining = quota['daily_remaining'];
        });
      }
    } catch (e) {
      debugPrint("Erreur quota : $e");
    }
  }

  Future<void> _initScanner() async {
    try {
      _cameras = await availableCameras();
      if (_cameras != null && _cameras!.isNotEmpty) {
        await _controller?.dispose();
        _controller = CameraController(_cameras![0], ResolutionPreset.medium, enableAudio: false);
        await _controller!.initialize();
        if (!mounted) return;
        setState(() => _isCameraInitialized = true);
      }
    } catch (e) {
      debugPrint("Erreur caméra : $e");
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    _laserController.dispose();
    super.dispose();
  }

  Future<void> _takePicture() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    try {
      final image = await _controller!.takePicture();
      setState(() => _capturedFile = image);
    } catch (e) {
      debugPrint("Erreur capture : $e");
    }
  }

  // --- LOGIQUE D'ANALYSE CONNECTÉE AU BACKEND ---
  Future<void> _startAnalysis() async {
    if (_capturedFile == null) return;

    setState(() {
      _isAnalyzing = true;
      _analysisResult = null;
    });

    try {
      final token = await _storage.read(key: 'jwt_token');
      if (token == null) throw Exception("Non authentifié");

      // Lecture des bytes (Indispensable pour Flutter Web)
      final Uint8List imageBytes = await _capturedFile!.readAsBytes();
      
      final result = await _scanService.uploadScan(
        imageBytes, 
        _capturedFile!.name, 
        token
      );

      if (!mounted) return;

      if (result.containsKey('error_code')) {
        // Gestion des erreurs (422, 429, 503...) via SnackBar
        final errorData = result['data'];
        _showErrorSnackBar("${errorData['error'] ?? 'Erreur'}: ${errorData['message']}");
      } else {
        setState(() {
          _analysisResult = result;
        });
        // Rafraîchir le quota après un scan réussi
        _loadInitialQuota();
      }
    } catch (e) {
      _showErrorSnackBar("Erreur de connexion : Impossible de joindre le serveur.");
    } finally {
      if (mounted) setState(() => _isAnalyzing = false);
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.redAccent),
    );
  }

  void _resetScan() {
    setState(() {
      _capturedFile = null;
      _analysisResult = null;
      _isAnalyzing = false;
    });
    _initScanner();
  }

  @override
  Widget build(BuildContext context) {
    const primaryGreen = Color(0xFF2E7D32);

    return Scaffold(
      appBar: AppBar(
        // --- AJOUT DU BOUTON RETOUR ---
        leading: IconButton(
          icon: const Icon(Icons.dashboard_outlined, color: Colors.black87),
          onPressed: () => Navigator.pushNamed(context, AppRoutes.dashboard), // Retour au Dashboard
          tooltip: "Retour au Dashboard",
        ),
        title: const Text("📸 Diagnostic Santé IA")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(vertical: 20),
        child: Center(
          child: Column(
            children: [
              _buildQuotaInfo(),
              const SizedBox(height: 20),
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(value: "Appareil Photo", label: Text("Caméra"), icon: Icon(Icons.videocam)),
                  ButtonSegment(value: "Importer", label: Text("Fichier"), icon: Icon(Icons.file_upload)),
                ],
                selected: {_source},
                onSelectionChanged: (val) {
                  setState(() {
                    _source = val.first;
                    _capturedFile = null;
                    _analysisResult = null;
                  });
                  if (_source == "Appareil Photo") _initScanner();
                },
              ),
              const SizedBox(height: 20),
              _buildMainZone(primaryGreen),
              const SizedBox(height: 30),
              
              if (_capturedFile != null && _analysisResult == null)
                ElevatedButton(
                  onPressed: _isAnalyzing ? null : _startAnalysis,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: primaryGreen,
                    padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                  ),
                  child: _isAnalyzing 
                    ? const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)),
                          SizedBox(width: 12),
                          Text("Analyse en cours...", style: TextStyle(color: Colors.white)),
                        ],
                      )
                    : const Text("🔍 LANCER L'ANALYSE IA", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                ),

              if (_analysisResult != null) _buildResultSection(primaryGreen),

              const SizedBox(height: 40),
              const Divider(indent: 50, endIndent: 50),
              _buildFullErrorExpander(),
              const SizedBox(height: 50),
            ],
          ),
        ),
      ),
    );
  }

  // --- RENDU DES RÉSULTATS ---
  Widget _buildResultSection(Color primaryGreen) {
    final status = _analysisResult!['statut_sante'];
    final color = status == "SAIN" ? Colors.green : (status == "MALADE" ? Colors.red : Colors.orange);
    final protocole = _analysisResult!['protocole_intervention'] as Map<String, dynamic>;

    return Container(
      constraints: const BoxConstraints(maxWidth: 800),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("✅ Analyse terminée !", style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 18)),
          const SizedBox(height: 20),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text("🔍 Diagnostic", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 10),
                    RichText(text: TextSpan(
                      style: const TextStyle(color: Colors.black, fontSize: 15),
                      children: [
                        const TextSpan(text: "Statut : ", style: TextStyle(fontWeight: FontWeight.bold)),
                        TextSpan(text: status, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
                      ]
                    )),
                    Text("📊 Niveau de santé : ${((_analysisResult!['facteur_sante'] ?? 0.0) * 100).toInt()}%"),
                    Text("🎯 Confiance : ${_analysisResult!['confiance_diagnostic'] ?? 'N/A'}"),
                    const Divider(),
                    const Text("💬 Diagnostic détaillé :", style: TextStyle(fontWeight: FontWeight.bold)),
                    Text(_analysisResult!['diagnostic_precis'] ?? 'Aucun détail fourni'),
                  ],
                ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text("🩺 Action Recommandée", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 10),
                    _recommendationCard("🧪 Option A : Chimique", protocole['option_A_chimique'], Colors.blue.shade50, Colors.blue),
                    const SizedBox(height: 10),
                    _recommendationCard("🌱 Option B : Biologique", protocole['option_B_biologique'], Colors.green.shade50, Colors.green),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ElevatedButton.icon(
            onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Sauvegardé !"))),
            icon: const Icon(Icons.save),
            label: const Text("💾 Sauvegarder l'analyse"),
            style: ElevatedButton.styleFrom(minimumSize: const Size(double.infinity, 50)),
          )
        ],
      ),
    );
  }

  Widget _recommendationCard(String title, Map<String, dynamic>? data, Color bg, Color accent) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(8), border: Border.all(color: accent.withOpacity(0.3))),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(color: accent, fontWeight: FontWeight.bold)),
          const SizedBox(height: 5),
          Text("Produit : ${data?['produit_actif'] ?? 'N/A'}", style: const TextStyle(fontSize: 13)),
          Text("Dosage : ${data?['dosage_recommande'] ?? 'N/A'}", style: const TextStyle(fontSize: 13)),
        ],
      ),
    );
  }

  // --- QUOTA DYNAMIQUE ---
  Widget _buildQuotaInfo() {
    return Container(
      margin: const EdgeInsets.only(top: 20),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: Colors.blue[50], borderRadius: BorderRadius.circular(8)),
      child: Text("📸 Scans aujourd'hui : $_dailyUsed/$_dailyLimit — Restants : $_dailyRemaining", 
        style: const TextStyle(color: Colors.blue, fontWeight: FontWeight.bold)),
    );
  }

  Widget _buildMainZone(Color green) {
    if (_capturedFile != null) {
      return Column(
        children: [
          Container(
            width: 600, height: 400,
            decoration: BoxDecoration(border: Border.all(color: Colors.grey)),
            child: Image.network(_capturedFile!.path, fit: BoxFit.contain),
          ),
          const SizedBox(height: 10),
          if (!_isAnalyzing)
            OutlinedButton.icon(
              onPressed: _resetScan, 
              icon: const Icon(Icons.refresh), 
              label: const Text("Recommencer"),
            ),
        ],
      );
    }

    if (_source == "Appareil Photo") {
      return Container(
        width: 600, height: 400,
        decoration: BoxDecoration(color: Colors.black, borderRadius: BorderRadius.circular(12)),
        child: Stack(
          children: [
            if (_isCameraInitialized && _controller != null && _controller!.value.isInitialized)
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Center(child: CameraPreview(_controller!)),
              )
            else
              const Center(child: CircularProgressIndicator(color: Colors.white)),
            _buildLaserEffect(green),
            Positioned(
              bottom: 20, left: 0, right: 0,
              child: Center(
                child: ElevatedButton.icon(
                  onPressed: _takePicture,
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: Colors.black),
                  icon: const Icon(Icons.camera_alt),
                  label: const Text("Prendre la photo"),
                ),
              ),
            ),
          ],
        ),
      );
    }

    return GestureDetector(
      onTap: () async {
        final img = await _picker.pickImage(source: ImageSource.gallery);
        if (img != null) setState(() => _capturedFile = img);
      },
      child: Container(
        width: 600, height: 200,
        decoration: BoxDecoration(color: Colors.white, border: Border.all(color: Colors.black12), borderRadius: BorderRadius.circular(8)),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.cloud_upload_outlined, size: 40, color: Colors.grey),
            Text("Cliquez pour parcourir vos fichiers", style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Widget _buildLaserEffect(Color green) {
    return AnimatedBuilder(
      animation: _laserController,
      builder: (context, child) {
        return Positioned(
          top: _laserController.value * 390,
          left: 0, right: 0,
          child: Container(
            height: 2, 
            decoration: BoxDecoration(color: green, boxShadow: [BoxShadow(color: green, blurRadius: 10, spreadRadius: 1)]),
          ),
        );
      },
    );
  }

  Widget _buildFullErrorExpander() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: SizedBox(
        width: 600,
        child: ExpansionTile(
          shape: const Border(),
          leading: const Icon(Icons.info_outline, color: Colors.blue),
          title: const Text("ℹ️ Informations sur les erreurs possibles", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
          children: [
            _errorListTile("🔄 Service temporairement indisponible (503)", "Le service IA est très sollicité. Patientez quelques minutes."),
            _errorListTile("📊 Limite d'utilisation atteinte (429)", "Vous avez fait trop d'analyses récemment. Revenez dans 1 heure."),
            _errorListTile("🤖 Erreur du service IA (502)", "Problème technique temporaire. Réessayez plus tard."),
            _errorListTile("📷 Image rejetée (422)", "La photo n'est pas assez nette ou ne contient pas de plante visible."),
          ],
        ),
      ),
    );
  }

  Widget _errorListTile(String title, String subtitle) {
    return ListTile(
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.redAccent)),
      subtitle: Text(subtitle, style: const TextStyle(fontSize: 12)),
      dense: true,
    );
  }
}