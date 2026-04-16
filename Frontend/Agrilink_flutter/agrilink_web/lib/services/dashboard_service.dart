import 'dart:convert';
import 'package:http/http.dart' as http;
import '../shared/widgets/constants.dart'; // Pour ton URL API_URL

class DashboardService {
  final String _url = API_URL.baseUrl; // Utilise la constante définie

  Future<Map<String, dynamic>> fetchDashboardData(String token) async {
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
      throw Exception("Erreur lors de la récupération des stats");
    }
  }
}