import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../shared/widgets/constants.dart'; // Pour ton URL API_URL

class AuthService {
  final _storage = const FlutterSecureStorage();
  // Correction ICI : on récupère la chaîne de caractères réelle
  final String _url = API_URL.baseUrl;
  // 1. LOGIN
  Future<Map<String, dynamic>> login(String phone, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_url/api/v1/login'),
        // Ton backend attend du formData (parameters in: formData)
        body: {
          'phone': phone,
          'password': password,
        },
      );

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        // Sauvegarde du token
        await _storage.write(key: 'jwt_token', value: data['token']);
        return {'success': true};
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Erreur inconnue'
        };
      }
    } catch (e) {
      print("ERREUR DETAILLEE : $e"); // Ajoute ça !
      return {'success': false, 'message': 'Connexion au serveur impossible'};
    }
  }


  // 2. REGISTER
  Future<Map<String, dynamic>> register({
    required String nom,
    required String phone,
    required String email,
    required String password,
    required String cultureType,
    required String coords, // Liste JSON formatée
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_url/api/v1/register'),
        body: {
          'nom': nom,
          'phone': phone,
          'email': email,
          'password': password,
          'culture_type': cultureType,
          //'coords': coords,
        },
      );

      if (response.statusCode == 200) {
        return {'success': true};
      } else {
        final data = json.decode(response.body);
        return {'success': false, 'message': data['msg'] ?? 'Erreur inscription'};
      }
    } catch (e) {
      print("Erreur Register: $e");
      return {'success': false, 'message': 'Erreur réseau'};
    }
  }

  // 3. GET TOKEN (Utilitaire pour les autres services)
  Future<String?> getToken() async {
    return await _storage.read(key: 'jwt_token');
  }

  // 4. LOGOUT
  Future<void> logout() async {
    await _storage.delete(key: 'jwt_token');
  }

// 5. Demande de récupération (Forgot Password)
  Future<Map<String, dynamic>> forgotPassword(String email) async {
    try {
      final response = await http.post(
        Uri.parse('${API_URL.baseUrl}/api/v1/forgot-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}), // Ton Flask check le JSON en premier
      );

      final data = json.decode(response.body);
      return {
        'success': response.statusCode == 200,
        'message': data['message'] ?? data['error'] ?? 'Erreur'
      };
    } catch (e) {
      return {'success': false, 'message': 'Erreur réseau ($e)'};
    }
  }

  // 6. Réinitialisation réelle (Reset Password)
  Future<Map<String, dynamic>> resetPassword(String token, String newPassword) async {
    try {
      // ATTENTION : Ta route Flask utilise request.form.get('token')
      // Donc on n'envoie PAS de JSON ici, mais du body standard (Form Data)
      final response = await http.post(
        Uri.parse('${API_URL.baseUrl}/api/v1/reset-password'),
        body: {
          'token': token,
          'new_password': newPassword,
        },
      );

      final data = json.decode(response.body);
      return {
        'success': response.statusCode == 200,
        'message': data['message'] ?? data['error'] ?? 'Erreur'
      };
    } catch (e) {
      return {'success': false, 'message': 'Erreur réseau ($e)'};
    }
  }


}
