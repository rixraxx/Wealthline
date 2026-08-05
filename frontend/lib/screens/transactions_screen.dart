import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../providers/transactions_provider.dart';
import '../providers/dashboard_provider.dart';
import '../models/models.dart';
import '../widgets/add_transaction_bottom_sheet.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  final ScrollController _scrollController = ScrollController();
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();

    _scrollController.addListener(_onScroll);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<TransactionsProvider>(
        context,
        listen: false,
      ).fetchTransactions(refresh: true);

      Provider.of<DashboardProvider>(
        context,
        listen: false,
      ).fetchDashboardData();
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      Provider.of<TransactionsProvider>(
        context,
        listen: false,
      ).loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    final txProvider = Provider.of<TransactionsProvider>(context);
    final dashProvider = Provider.of<DashboardProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Transactions',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),

      // FAB Added Here
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          showModalBottomSheet(
            context: context,
            isScrollControlled: true,
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.vertical(
                top: Radius.circular(20),
              ),
            ),
            builder: (ctx) => const AddTransactionBottomSheet(),
          );
        },
        icon: const Icon(Icons.add),
        label: const Text('Add Transaction'),
      ),

      body: Column(
        children: [
          // Search & Filter Header
          Container(
            padding: const EdgeInsets.all(12),
            color: Theme.of(context).colorScheme.surfaceContainerLow,
            child: Column(
              children: [
                // Search
                TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Search description...',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _searchController.clear();
                              txProvider.setSearchQuery('');
                              setState(() {});
                            },
                          )
                        : null,
                    filled: true,
                    fillColor: Colors.white,
                    contentPadding: const EdgeInsets.symmetric(
                      vertical: 0,
                      horizontal: 16,
                    ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                  ),
                  onChanged: (value) {
                    txProvider.setSearchQuery(value);
                    setState(() {});
                  },
                ),

                const SizedBox(height: 10),

                Row(
                  children: [
                    // Account Filter (UPDATED: Changed <int?> to <String?>)
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String?>(
                            value: txProvider.selectedAccountId?.toString(),
                            isExpanded: true,
                            hint: const Text(
                              'All Accounts',
                              style: TextStyle(fontSize: 13),
                            ),
                            items: [
                              const DropdownMenuItem<String?>(
                                value: null,
                                child: Text(
                                  'All Accounts',
                                  style: TextStyle(fontSize: 13),
                                ),
                              ),
                              ...dashProvider.accounts.map(
                                (acc) => DropdownMenuItem<String?>(
                                  value: acc.id,
                                  child: Text(
                                    acc.name,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(fontSize: 13),
                                  ),
                                ),
                              ),
                            ],
                            onChanged: (value) {
                              txProvider.setAccountFilter(value);
                            },
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(width: 8),

                    // Type Filter
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: txProvider.selectedType ?? 'all',
                            isExpanded: true,
                            items: const [
                              DropdownMenuItem(
                                value: 'all',
                                child: Text(
                                  'All Types',
                                  style: TextStyle(fontSize: 13),
                                ),
                              ),
                              DropdownMenuItem(
                                value: 'income',
                                child: Text(
                                  'Income',
                                  style: TextStyle(fontSize: 13),
                                ),
                              ),
                              DropdownMenuItem(
                                value: 'expense',
                                child: Text(
                                  'Expenses',
                                  style: TextStyle(fontSize: 13),
                                ),
                              ),
                            ],
                            onChanged: (value) {
                              txProvider.setTypeFilter(value);
                            },
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Transactions List
          Expanded(
            child: RefreshIndicator(
              onRefresh: () =>
                  txProvider.fetchTransactions(refresh: true),
              child: txProvider.isLoading
                  ? const Center(
                      child: CircularProgressIndicator(),
                    )
                  : txProvider.error != null
                      ? Center(
                          child: Text(txProvider.error!),
                        )
                      : txProvider.transactions.isEmpty
                          ? const Center(
                              child: Text(
                                'No transactions match your search/filter.',
                              ),
                            )
                          : ListView.builder(
                              controller: _scrollController,
                              padding: const EdgeInsets.symmetric(vertical: 8),
                              itemCount:
                                  txProvider.transactions.length +
                                      (txProvider.hasMore ? 1 : 0),
                              itemBuilder: (context, index) {
                                if (index ==
                                    txProvider.transactions.length) {
                                  return const Padding(
                                    padding: EdgeInsets.all(16),
                                    child: Center(
                                      child:
                                          CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    ),
                                  );
                                }

                                final Transaction tx = txProvider.transactions[index];

                                final bool isIncome =
                                    tx.type.toLowerCase() == 'income';

                                return Card(
                                  margin:
                                      const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 4,
                                  ),
                                  child: ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: isIncome
                                          ? Colors.green.shade50
                                          : Colors.red.shade50,
                                      child: Icon(
                                        isIncome
                                            ? Icons.arrow_downward
                                            : Icons.arrow_upward,
                                        color: isIncome
                                            ? Colors.green
                                            : Colors.red,
                                      ),
                                    ),
                                    title: Text(
                                      tx.description ??
                                          (isIncome
                                              ? 'Income'
                                              : 'Expense'),
                                      style: const TextStyle(
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    subtitle: Text(
                                      '${DateFormat('MMM dd, yyyy').format(tx.date)}'
                                      '${tx.categoryName != null ? " • ${tx.categoryName}" : ""}',
                                      style: const TextStyle(
                                        fontSize: 12,
                                      ),
                                    ),
                                    trailing: Text(
                                      '${isIncome ? "+" : "-"}\$${tx.amount.abs().toStringAsFixed(2)}',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 15,
                                        color: isIncome
                                            ? Colors.green.shade700
                                            : Colors.red.shade700,
                                      ),
                                    ),
                                  ),
                                );
                              },
                            ),
            ),
          ),
        ],
      ),
    );
  }
}