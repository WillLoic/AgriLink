import 'package:flutter/foundation.dart'; // Import indispensable pour kReleaseMode

class API_URL {
  // --- LOGIQUE DE DÉTECTION D'URL ---
  // kReleaseMode est 'true' quand tu compiles pour Render (prod)
  // kReleaseMode est 'false' quand tu lances sur ton PC (debug)
  static String get baseUrl {
    if (kReleaseMode) {
      //return "http://127.0.0.1:5000"; // Ton URL Locale
      return "https://agrilink-f9on.onrender.com"; // Ton URL Render
    } else {
      return "http://127.0.0.1:5000"; // Ton URL Locale
    }
  }
}
