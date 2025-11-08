import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../providers/dashboard_provider.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _apiUrlController = TextEditingController();
  bool _showNotifications = true;
  bool _autoRefresh = true;
  int _refreshInterval = 30; // seconds
  String _defaultMovementType = 'IN';
  bool _autoCreateSku = true;

  @override
  void initState() {
    super.initState();
    _apiUrlController.text = ApiService.baseUrl;
  }

  @override
  void dispose() {
    _apiUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          _buildSection(
            context,
            title: 'API Configuration',
            icon: Icons.api,
            children: [
              TextField(
                controller: _apiUrlController,
                decoration: const InputDecoration(
                  labelText: 'API Base URL',
                  hintText: 'http://localhost:8000',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.link),
                ),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _testConnection,
                icon: const Icon(Icons.check_circle),
                label: const Text('Test Connection'),
              ),
            ],
          ),
          const SizedBox(height: 32),
          _buildSection(
            context,
            title: 'Notifications',
            icon: Icons.notifications,
            children: [
              SwitchListTile(
                title: const Text('Show Notifications'),
                subtitle: const Text('Display toast notifications for actions'),
                value: _showNotifications,
                onChanged: (value) {
                  setState(() {
                    _showNotifications = value;
                  });
                },
              ),
            ],
          ),
          const SizedBox(height: 32),
          _buildSection(
            context,
            title: 'Dashboard',
            icon: Icons.dashboard,
            children: [
              SwitchListTile(
                title: const Text('Auto Refresh'),
                subtitle: const Text('Automatically refresh dashboard data'),
                value: _autoRefresh,
                onChanged: (value) {
                  setState(() {
                    _autoRefresh = value;
                  });
                },
              ),
              if (_autoRefresh) ...[
                const SizedBox(height: 16),
                ListTile(
                  title: const Text('Refresh Interval'),
                  subtitle: Text('Every $_refreshInterval seconds'),
                  trailing: SizedBox(
                    width: 200,
                    child: Slider(
                      value: _refreshInterval.toDouble(),
                      min: 10,
                      max: 120,
                      divisions: 11,
                      label: '$_refreshInterval seconds',
                      onChanged: (value) {
                        setState(() {
                          _refreshInterval = value.toInt();
                        });
                      },
                    ),
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 32),
          _buildSection(
            context,
            title: 'Stock Intake Defaults',
            icon: Icons.inventory,
            children: [
              DropdownButtonFormField<String>(
                value: _defaultMovementType,
                decoration: const InputDecoration(
                  labelText: 'Default Movement Type',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.swap_horiz),
                ),
                items: ['IN', 'OUT', 'TRANSFER', 'ADJUSTMENT']
                    .map((type) => DropdownMenuItem(
                          value: type,
                          child: Text(type),
                        ))
                    .toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _defaultMovementType = value;
                    });
                  }
                },
              ),
              const SizedBox(height: 16),
              SwitchListTile(
                title: const Text('Auto-create SKU'),
                subtitle: const Text('Automatically create new SKUs if not found'),
                value: _autoCreateSku,
                onChanged: (value) {
                  setState(() {
                    _autoCreateSku = value;
                  });
                },
              ),
            ],
          ),
          const SizedBox(height: 32),
          _buildSection(
            context,
            title: 'Data Management',
            icon: Icons.storage,
            children: [
              ListTile(
                leading: const Icon(Icons.refresh, color: Colors.blue),
                title: const Text('Clear Activity Cache'),
                subtitle: const Text('Remove all cached activity data'),
                trailing: const Icon(Icons.chevron_right),
                onTap: _clearActivityCache,
              ),
              ListTile(
                leading: const Icon(Icons.download, color: Colors.green),
                title: const Text('Export Activity'),
                subtitle: const Text('Download activity log as CSV'),
                trailing: const Icon(Icons.chevron_right),
                onTap: _exportActivity,
              ),
            ],
          ),
          const SizedBox(height: 32),
          _buildSection(
            context,
            title: 'About',
            icon: Icons.info,
            children: [
              const ListTile(
                leading: Icon(Icons.apps),
                title: Text('Version'),
                subtitle: Text('0.1.0 - Phase A'),
              ),
              const ListTile(
                leading: Icon(Icons.code),
                title: Text('Build'),
                subtitle: Text('Development'),
              ),
              ListTile(
                leading: const Icon(Icons.description),
                title: const Text('Documentation'),
                subtitle: const Text('View README and API guide'),
                trailing: const Icon(Icons.open_in_new),
                onTap: () {
                  // TODO: Open documentation
                },
              ),
            ],
          ),
          const SizedBox(height: 48),
        ],
      ),
    );
  }

  Widget _buildSection(
    BuildContext context, {
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            ...children,
          ],
        ),
      ),
    );
  }

  Future<void> _testConnection() async {
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      await apiService.healthCheck();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 12),
                Text('Connection successful!'),
              ],
            ),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
            margin: EdgeInsets.only(bottom: 80, right: 20, left: 20),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(child: Text('Connection failed: $e')),
              ],
            ),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
            margin: const EdgeInsets.only(bottom: 80, right: 20, left: 20),
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }
  }

  void _clearActivityCache() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Activity Cache'),
        content: const Text(
          'This will remove all cached activity data from the dashboard. '
          'Are you sure you want to continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Provider.of<DashboardProvider>(context, listen: false)
                  .clearActivity();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Activity cache cleared'),
                  behavior: SnackBarBehavior.floating,
                  margin: EdgeInsets.only(bottom: 80, right: 20, left: 20),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  void _exportActivity() {
    // TODO: Implement CSV export
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Export feature coming soon!'),
        behavior: SnackBarBehavior.floating,
        margin: EdgeInsets.only(bottom: 80, right: 20, left: 20),
      ),
    );
  }
}
