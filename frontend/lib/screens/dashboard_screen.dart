import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/dashboard_provider.dart';
import '../models/models.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<DashboardProvider>(
        context,
        listen: false,
      ).fetchDashboardData();
    });
  }

  IconData _getAccountIcon(String type) {
    switch (type.toLowerCase()) {
      case 'savings':
        return Icons.savings;
      case 'credit_card':
        return Icons.credit_card;
      case 'investment':
        return Icons.trending_up;
      default:
        return Icons.account_balance;
    }
  }

  void _showAddAccountDialog(BuildContext context) {
    final nameCtrl = TextEditingController();
    final balanceCtrl = TextEditingController();

    String selectedType = 'checking';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(20),
        ),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          top: 24,
          left: 24,
          right: 24,
          bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Create Account',
              style: Theme.of(ctx).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(
                labelText: 'Account Name',
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 12),

            TextField(
              controller: balanceCtrl,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: const InputDecoration(
                labelText: 'Initial Balance',
                prefixText: '\$ ',
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 12),

            DropdownButtonFormField<String>(
              value: selectedType,
              decoration: const InputDecoration(
                labelText: 'Account Type',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(
                  value: 'checking',
                  child: Text('Checking'),
                ),
                DropdownMenuItem(
                  value: 'savings',
                  child: Text('Savings'),
                ),
                DropdownMenuItem(
                  value: 'credit_card',
                  child: Text('Credit Card'),
                ),
                DropdownMenuItem(
                  value: 'investment',
                  child: Text('Investment'),
                ),
              ],
              onChanged: (value) {
                selectedType = value!;
              },
            ),

            const SizedBox(height: 20),

            ElevatedButton(
              onPressed: () async {
                final name = nameCtrl.text.trim();
                final balance =
                    double.tryParse(balanceCtrl.text.trim()) ?? 0.0;

                if (name.isNotEmpty) {
                  final nav = Navigator.of(ctx);

                  final success =
                      await Provider.of<DashboardProvider>(
                    context,
                    listen: false,
                  ).createAccount(
                    name,
                    selectedType,
                    balance,
                  );

                  if (success) {
                    nav.pop();
                  }
                }
              },
              child: const Text('Add Account'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final dash = context.watch<DashboardProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Wealthline',
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              dash.fetchDashboardData();
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              Provider.of<AuthProvider>(
                context,
                listen: false,
              ).logout();
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => dash.fetchDashboardData(),
        child: dash.isLoading
            ? const Center(
                child: CircularProgressIndicator(),
              )
            : dash.error != null
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisAlignment:
                            MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.cloud_off,
                            size: 64,
                            color: Colors.grey,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            dash.error!,
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () {
                              dash.fetchDashboardData();
                            },
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    ),
                  )
                : ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      Card(
                        elevation: 2,
                        shape: RoundedRectangleBorder(
                          borderRadius:
                              BorderRadius.circular(16),
                        ),
                        color: Theme.of(context)
                            .colorScheme
                            .primaryContainer,
                        child: Padding(
                          padding:
                              const EdgeInsets.all(20),
                          child: Column(
                            crossAxisAlignment:
                                CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Total Net Worth',
                                style: TextStyle(
                                  color: Theme.of(context)
                                      .colorScheme
                                      .onPrimaryContainer
                                      .withOpacity(0.7),
                                ),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                '\$${dash.totalNetWorth.toStringAsFixed(2)}',
                                style: Theme.of(context)
                                    .textTheme
                                    .headlineMedium
                                    ?.copyWith(
                                      fontWeight:
                                          FontWeight.bold,
                                      color: Theme.of(context)
                                          .colorScheme
                                          .onPrimaryContainer,
                                    ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(height: 16),

                      if (dash.cashFlow != null) ...[
                        Row(
                          children: [
                            Expanded(
                              child: _MetricCard(
                                title: 'Income',
                                amount:
                                    '\$${dash.cashFlow!.totalIncome.toStringAsFixed(2)}',
                                icon:
                                    Icons.arrow_downward,
                                color: Colors.green,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _MetricCard(
                                title: 'Expenses',
                                amount:
                                    '\$${dash.cashFlow!.totalExpense.toStringAsFixed(2)}',
                                icon:
                                    Icons.arrow_upward,
                                color: Colors.red,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                      ],

                      Row(
                        mainAxisAlignment:
                            MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Accounts',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  fontWeight:
                                      FontWeight.bold,
                                ),
                          ),
                          TextButton.icon(
                            onPressed: () =>
                                _showAddAccountDialog(
                                    context),
                            icon: const Icon(
                              Icons.add,
                              size: 18,
                            ),
                            label: const Text('Add'),
                          ),
                        ],
                      ),

                      const SizedBox(height: 8),

                      if (dash.accounts.isEmpty)
                        const Padding(
                          padding:
                              EdgeInsets.symmetric(
                            vertical: 32,
                          ),
                          child: Center(
                            child: Text(
                              'No accounts created yet.',
                            ),
                          ),
                        )
                      else
                        ListView.builder(
                          shrinkWrap: true,
                          physics:
                              const NeverScrollableScrollPhysics(),
                          itemCount:
                              dash.accounts.length,
                          itemBuilder:
                              (context, index) {
                            final acc =
                                dash.accounts[index];

                            return Card(
                              margin:
                                  const EdgeInsets.only(
                                bottom: 8,
                              ),
                              child: ListTile(
                                leading: CircleAvatar(
                                  backgroundColor:
                                      Theme.of(context)
                                          .colorScheme
                                          .surfaceContainerHighest,
                                  child: Icon(
                                    _getAccountIcon(
                                        acc.type),
                                    color:
                                        Theme.of(context)
                                            .colorScheme
                                            .primary,
                                  ),
                                ),
                                title: Text(
                                  acc.name,
                                  style:
                                      const TextStyle(
                                    fontWeight:
                                        FontWeight
                                            .w600,
                                  ),
                                ),
                                subtitle: Text(
                                  acc.type
                                      .toUpperCase(),
                                  style:
                                      const TextStyle(
                                    fontSize: 11,
                                  ),
                                ),
                                trailing: Text(
                                  '\$${acc.balance.toStringAsFixed(2)}',
                                  style:
                                      TextStyle(
                                    fontWeight:
                                        FontWeight
                                            .bold,
                                    fontSize: 15,
                                    color: acc.balance <
                                            0
                                        ? Colors.red
                                        : Colors
                                            .black87,
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                    ],
                  ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String amount;
  final IconData icon;
  final Color color;

  const _MetricCard({
    required this.title,
    required this.amount,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor:
                  color.withOpacity(0.15),
              child: Icon(
                icon,
                color: color,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    amount,
                    style: const TextStyle(
                      fontWeight:
                          FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}