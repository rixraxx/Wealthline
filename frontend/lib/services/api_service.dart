import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  // Use 10.0.2.2 for Android Emulator, localhost for Web/iOS/Desktop
  static final String baseUrl = Platform.isAndroid 
      ? 'http://10.0.2.2:8000/api/v1' 
      : 'http://localhost:8000/api/v1';

  final _storage = const FlutterSecureStorage();

  Future<String?> _getToken() async {
    return await _storage.read(key: 'access_token');
  }

  Future<Map<String, String>> _headers() async {
    final token = await _getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // Auth: Login
  Future<bool> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _storage.write(key: 'access_token', value: data['access_token']);
      return true;
    } else if (response.statusCode == 429) {
      throw Exception('Rate limit exceeded. Please wait a minute before retrying.');
    }
    return false;
  }

  // Accounts: Fetch List
  Future<List<dynamic>> getAccounts() async {
    final headers = await _headers();
    final response = await http.get(
      Uri.parse('$baseUrl/accounts/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load accounts');
  }
}