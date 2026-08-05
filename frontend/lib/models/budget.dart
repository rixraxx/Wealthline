class Budget {
  final String id;
  final String userId;
  final int? categoryId;
  final String name;
  final double amountLimit;
  final double currentSpent;
  final String period; // 'monthly', 'yearly'
  final DateTime startDate;
  final DateTime endDate;

  Budget({
    required this.id,
    required this.userId,
    this.categoryId,
    required this.name,
    required this.amountLimit,
    this.currentSpent = 0.0,
    required this.period,
    required this.startDate,
    required this.endDate,
  });

  double get remaining => amountLimit - currentSpent;
  double get progress => amountLimit > 0 ? (currentSpent / amountLimit).clamp(0.0, 1.0) : 0.0;
  bool get isExceeded => currentSpent > amountLimit;

  factory Budget.fromJson(Map<String, dynamic> json) {
    return Budget(
      id: json['id']?.toString() ?? '',
      userId: json['user_id']?.toString() ?? '',
      categoryId: json['category_id'] != null 
          ? int.tryParse(json['category_id'].toString()) 
          : null,
      name: json['name'] as String? ?? 'Budget',
      amountLimit: double.tryParse(json['amount_limit']?.toString() ?? '') ?? 0.0,
      currentSpent: double.tryParse(json['current_spent']?.toString() ?? '') ?? 0.0,
      period: json['period'] as String? ?? 'monthly',
      startDate: DateTime.parse(json['start_date'].toString()),
      endDate: DateTime.parse(json['end_date'].toString()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'category_id': categoryId,
      'name': name,
      'amount_limit': amountLimit,
      'current_spent': currentSpent,
      'period': period,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
    };
  }
}