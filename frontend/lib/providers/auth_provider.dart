import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

enum AuthStatus { unauthenticated, authenticating, authenticated }

class AuthProvider extends ChangeNotifier {
  AuthStatus _status = AuthStatus.unauthenticated;
  String? _errorMessage;
  final _storage = const FlutterSecureStorage();

  AuthStatus get status => _status;
  String? get errorMessage => _errorMessage;
  bool get isLoading => _status == AuthStatus.authenticating;

  // Platform-aware Base URL (10.0.2.2 for Android Emulator, localhost for iOS/Web/Desktop)
  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000/api/v1';
    return Platform.isAndroid
        ? 'http://10.0.2.2:8000/api/v1'
        : 'http://localhost:8000/api/v1';
  }

  // Check stored JWT on app initialization
  Future tryAutoLogin() async {
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      _status = AuthStatus.authenticated;
      notifyListeners();
      return true;
    }
    return false;
  }

  // Perform Login Call to FastAPI Backend
  Future login(String email, String password) async {
    _status = AuthStatus.authenticating;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['access_token'];
        await _storage.write(key: 'access_token', value: token);

        _status = AuthStatus.authenticated;
        notifyListeners();
        return true;
      } else if (response.statusCode == 429) {
        _errorMessage = 'Rate limit exceeded. Please wait a minute before retrying.';
      } else if (response.statusCode == 401) {
        _errorMessage = 'Invalid email or password.';
      } else {
        final data = jsonDecode(response.body);
        _errorMessage = data['detail'] ?? 'Login failed. Please try again.';
      }
    } catch (e) {
      _errorMessage = 'Unable to connect to backend server ($baseUrl).';
    }

    _status = AuthStatus.unauthenticated;
    notifyListeners();
    return false;
  }

  // Logout & Clear Token
  Future logout() async {
    await _storage.delete(key: 'access_token');
    _status = AuthStatus.unauthenticated;
    notifyListeners();
  }
}