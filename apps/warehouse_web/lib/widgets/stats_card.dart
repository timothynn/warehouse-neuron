import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';

class StatsCard extends StatelessWidget {
  const StatsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Overview',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 24),
            LayoutBuilder(
              builder: (context, constraints) {
                final isWide = constraints.maxWidth > 600;
                return isWide
                    ? Row(
                        children: _buildStatItems(context)
                            .map((item) => Expanded(child: item))
                            .toList(),
                      )
                    : Column(
                        children: _buildStatItems(context),
                      );
              },
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildStatItems(BuildContext context) {
    final stats = Provider.of<DashboardProvider>(context).stats;
    
    return [
      _StatItem(
        icon: Icons.inventory_2,
        label: 'Total SKUs',
        value: stats.totalSkus.toString(),
        color: Colors.blue,
        trend: null,
      ),
      _StatItem(
        icon: Icons.location_on,
        label: 'Locations',
        value: stats.locations.toString(),
        color: Colors.green,
        trend: null,
      ),
      _StatItem(
        icon: Icons.swap_horiz,
        label: 'Today\'s Movements',
        value: stats.todayMovements.toString(),
        color: Colors.orange,
        trend: null,
      ),
      _StatItem(
        icon: Icons.warehouse,
        label: 'Total Units',
        value: stats.totalUnits.toString(),
        color: Colors.purple,
        trend: null,
      ),
    ];
  }
}

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  final String? trend;

  const _StatItem({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
    this.trend,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              size: 32,
              color: color,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
            textAlign: TextAlign.center,
          ),
          if (trend != null) ...[
            const SizedBox(height: 4),
            Text(
              trend!,
              style: TextStyle(
                color: Colors.green,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
