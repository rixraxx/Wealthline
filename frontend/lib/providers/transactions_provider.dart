import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/models.dart';

class TransactionsProvider extends ChangeNotifier {
  List _transactions = [];
  bool _isLoading = false;
  bool _isLoadingMore = false;
  String? _error;

  // Pagination & Filtering state
  int _page = 1;
  final int _size = 20;
  bool _hasMore = true;
  String _searchQuery = '';
  String? _selectedAccountId;
  String? _selectedType; // 'income', 'expense', or null for All

  List get transactions => _transactions;
  bool get isLoading => _isLoading;
  bool get isLoadingMore => _isLoadingMore;
  bool get hasMore => _hasMore;
  String? get error => _error;
  String get searchQuery => _searchQuery;
  String? get selectedAccountId => _selectedAccountId;
  String? get selectedType => _selectedType;

  final _storage = const FlutterSecureStorage();
  Timer? _debounceTimer;

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

  // Build query string based on current active filters
  Uri _buildUri(int page) {
    final queryParams = {
      'page': page.toString(),
      'size': _size.toString(),
      if (_searchQuery.isNotEmpty) 'search': _searchQuery,
      if (_selectedAccountId != null) 'account_id': _selectedAccountId.toString(),
      if (_selectedType != null && _selectedType != 'all') 'type': _selectedType!,
    };

    return Uri.parse('$baseUrl/transactions/').replace(queryParameters: queryParams);
  }

  // Initial fetch or reset refresh
  Future fetchTransactions({bool refresh = false}) async {
    if (refresh) {
      _page = 1;
      _hasMore = true;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final headers = await _getHeaders();
      final response = await http.get(_buildUri(1), headers: headers);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List items = data is Map ? (data['items'] ?? []) : data;

        _transactions = items.map((json) => Transaction.fromJson(json)).toList();
        _page = 1;
        _hasMore = items.length >= _size;
      } else {
        throw Exception('Failed to load transactions (${response.statusCode})');
      }
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Load next page on scroll reach
  Future<void> loadMore() async {
    if (_isLoadingMore || !_hasMore || _isLoading) return;


    _isLoadingMore = true;
    notifyListeners();

    try {
      final nextPage = _page + 1;
      final headers = await _getHeaders();
      final response = await http.get(_buildUri(nextPage), headers: headers);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List items = data is Map ? (data['items'] ?? []) : data;

        if (items.isNotEmpty) {
          _transactions.addAll(items.map((json) => Transaction.fromJson(json)).toList());
          _page = nextPage;
          _hasMore = items.length >= _size;
        } else {
          _hasMore = false;
        }
      }
    } catch (_) {
      // Keep existing transactions on pagination failure
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  // Update search query with 400ms debounce
  void setSearchQuery(String query) {
    _searchQuery = query;
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 400), () {
      fetchTransactions(refresh: true);
    });
  }

  void setAccountFilter(String? accountId) {
    _selectedAccountId = accountId;
    fetchTransactions(refresh: true);
  }

  void setTypeFilter(String? type) {
    _selectedType = type;
    fetchTransactions(refresh: true);
  }

  void clearFilters() {
    _searchQuery = '';
    _selectedAccountId = null;
    _selectedType = null;
    fetchTransactions(refresh: true);
  }
  // Create a new transaction via POST /api/v1/transactions
  Future createTransaction({
    required int accountId,
    int? categoryId,
    required double amount,
    required String type,
    required String description,
    required DateTime date,
  }) async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/transactions/'),
        headers: headers,
        body: jsonEncode({
          'account_id': accountId,
          if (categoryId != null) 'category_id': categoryId,
          'amount': amount,
          'type': type,
          'description': description,
          'date': date.toIso8601String(),
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        // Refresh transactions list after successful creation
        await fetchTransactions(refresh: true);
        return true;
      } else {
        final data = jsonDecode(response.body);
        _error = data['detail'] ?? 'Failed to create transaction.';
      }
    } catch (e) {
      _error = 'Connection error: unable to create transaction.';
    }
    notifyListeners();
    return false;
  }
}