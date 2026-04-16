import 'dart:convert';
import 'package:http/http.dart' as http;
import '../shared/widgets/constants.dart'; // Pour API_URL

class DashboardService {
  final String _url = API_URL.baseUrl;

  Future<Map<String, dynamic>> getDashboardData(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$_url/api/v1/dashboard/stats'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception("Erreur serveur : ${response.statusCode}");
      }
    } catch (e) {
      throw Exception("Impossible de contacter l'API : $e");
    }
  }
}