import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/models.dart';
import '../models/cash_flow.dart';

class DashboardProvider extends ChangeNotifier {
  List _accounts = [];
  CashFlowSummary? _cashFlow;
  bool _isLoading = false;
  String? _error;

  List get accounts => _accounts;
  CashFlowSummary? get cashFlow => _cashFlow;
  bool get isLoading => _isLoading;
  String? get error => _error;

  double get totalNetWorth => _accounts.fold(0.0, (sum, acc) => sum + acc.balance);

  final _storage = const FlutterSecureStorage();

  static String get baseUrl {
    if (kIsWeb) return 'http://localhost:8000/api/v1';
    return Platform.isAndroid
        ? 'http://10.0.2.2:8000/api/v1'
        : 'http://localhost:8000/api/v1';
  }

  Future<Map<String, String>> _getHeaders() async {
    final token = await _storage.read(key: 'access_token');
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // Fetch Accounts & Cash Flow Summary in parallel
  Future fetchDashboardData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final headers = await _getHeaders();

      // 1. Fetch Accounts
      final accountsRes = await http.get(Uri.parse('$baseUrl/accounts/'), headers: headers);
      if (accountsRes.statusCode == 200) {
        final List data = jsonDecode(accountsRes.body);
        _accounts = data.map((json) => Account.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load accounts (${accountsRes.statusCode})');
      }

      // 2. Fetch Cash Flow Analytics
      final cashFlowRes = await http.get(Uri.parse('$baseUrl/analytics/cash-flow'), headers: headers);
      if (cashFlowRes.statusCode == 200) {
        _cashFlow = CashFlowSummary.fromJson(jsonDecode(cashFlowRes.body));
      } else {
        _cashFlow = CashFlowSummary(totalIncome: 0.0, totalExpense: 0.0, netSavings: 0.0);
      }
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Create a new Account
  Future createAccount(String name, String type, double balance) async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/accounts/'),
        headers: headers,
        body: jsonEncode({
          'name': name,
          'type': type,
          'balance': balance,
          'currency': 'USD',
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        await fetchDashboardData();
        return true;
      }
    } catch (_) {}
    return false;
  }
}