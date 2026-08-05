class CashFlowSummary {
  final double totalIncome;
  final double totalExpense;
  final double netSavings;

  CashFlowSummary({
    required this.totalIncome,
    required this.totalExpense,
    required this.netSavings,
  });

  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is num) return value.toDouble();
    return double.tryParse(value.toString()) ?? 0.0;
  }

  factory CashFlowSummary.fromJson(Map<String, dynamic> json) {
    return CashFlowSummary(
      totalIncome: _parseDouble(json['income'] ?? json['total_income']),
      totalExpense: _parseDouble(json['expense'] ?? json['total_expense']),
      netSavings: _parseDouble(json['net'] ?? json['net_savings']),
    );
  }
}