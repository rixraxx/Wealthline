class Transaction {
  final String id;
  final String accountId;
  final int? categoryId;
  final String? categoryName;
  final double amount;
  final String type; // 'income', 'expense', or 'transfer'
  final String? description;
  final DateTime date;
  final DateTime? createdAt;

  Transaction({
    required this.id,
    required this.accountId,
    this.categoryId,
    this.categoryName,
    required this.amount,
    required this.type,
    this.description,
    required this.date,
    this.createdAt,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id']?.toString() ?? '',
      accountId: json['account_id']?.toString() ?? '',
      categoryId: json['category_id'] != null 
          ? int.tryParse(json['category_id'].toString()) 
          : null,
      categoryName: json['category_name'] as String?,
      amount: double.tryParse(json['amount']?.toString() ?? '') ?? 0.0,
      type: json['type'] as String? ?? 'expense',
      description: json['description'] as String?,
      date: json['date'] != null 
          ? DateTime.parse(json['date'].toString()) 
          : DateTime.now(),
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at'].toString()) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'account_id': accountId,
      'category_id': categoryId,
      'category_name': categoryName,
      'amount': amount,
      'type': type,
      'description': description,
      'date': date.toIso8601String(),
      'created_at': createdAt?.toIso8601String(),
    };
  }
}