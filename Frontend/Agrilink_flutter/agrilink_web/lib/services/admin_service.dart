import 'dart:convert';
import 'package:http/http.dart' as http;
import '../shared/widgets/constants.dart';

class AdminService {
  final String _url = API_URL.baseUrl;

  // Récupérer tous les utilisateurs
  Future<List<dynamic>> getAllUsers(String token) async {
    final response = await http.get(
      Uri.parse('$_url/api/v1/admin/users'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception("Erreur lors de la récupération des utilisateurs");
  }

  // Récupérer les stats (Note l'URL : /api/v1/analytics selon ton code Flask)
  Future<Map<String, dynamic>> getGlobalStats(String token) async {
    final response = await http.get(
      Uri.parse('$_url/api/v1/analytics'), 
      headers: {'Authorization': 'Bearer $token'},
    );
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception("Erreur lors de la récupération des analytics");
  }

  // Promotion
  Future<bool> promoteUser(String token, int userId) async {
    final response = await http.post(
      Uri.parse('$_url/api/v1/admin/promote/$userId'),
      headers: {'Authorization': 'Bearer $token'},
    );
    return response.statusCode == 200;
  }

  // Rétrogradation
  Future<bool> demoteUser(String token, int userId) async {
    final response = await http.post(
      Uri.parse('$_url/api/v1/admin/demote/$userId'),
      headers: {'Authorization': 'Bearer $token'},
    );
    return response.statusCode == 200;
  }
}