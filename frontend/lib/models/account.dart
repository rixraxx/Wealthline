class Account {
  final String id;
  final String userId;
  final String name;
  final String type; // e.g., 'checking', 'savings', 'credit_card', 'investment'
  final double balance;
  final String currency;
  final bool isActive;
  final DateTime? createdAt;

  Account({
    required this.id,
    required this.userId,
    required this.name,
    required this.type,
    required this.balance,
    this.currency = 'USD',
    this.isActive = true,
    this.createdAt,
  });

  factory Account.fromJson(Map<String, dynamic> json) {
    return Account(
      id: json['id']?.toString() ?? '',
      userId: json['user_id']?.toString() ?? '',
      name: json['name'] as String? ?? 'Unnamed Account',
      type: json['type'] as String? ?? 'checking',
      balance: double.tryParse(json['balance']?.toString() ?? '') ?? 0.0,
      currency: json['currency'] as String? ?? 'USD',
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at'].toString()) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'name': name,
      'type': type,
      'balance': balance,
      'currency': currency,
      'is_active': isActive,
      'created_at': createdAt?.toIso8601String(),
    };
  }
}