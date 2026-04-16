import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../shared/widgets/constants.dart'; // Pour ton API_URL

class ScanService {
  final String _url = API_URL.baseUrl;

  // 1. Récupérer le quota
  Future<Map<String, dynamic>> getQuota(String token) async {
    final response = await http.get(
      Uri.parse('$_url/api/v1/scan/quota'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception("Erreur quota");
  }

  // 2. Envoyer le scan
  Future<Map<String, dynamic>> uploadScan(Uint8List imageBytes, String fileName, String token) async {
    var request = http.MultipartRequest('POST', Uri.parse('$_url/api/v1/scan'));
    
    request.headers['Authorization'] = 'Bearer $token';

    // Ajout du fichier (méthode spécifique pour le Web via bytes)
    request.files.add(http.MultipartFile.fromBytes(
      'photo', 
      imageBytes,
      filename: fileName,
      contentType: MediaType('image', 'jpeg'),
    ));

    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      // On renvoie le corps de l'erreur (422, 429, 503) pour que ton UI puisse l'afficher
      return {
        "error_code": response.statusCode,
        "data": json.decode(response.body)
      };
    }
  }
}