import 'package:flutter/foundation.dart';
import '../models/stock_models.dart';

class DashboardStats {
  final int totalSkus;
  final int locations;
  final int todayMovements;
  final int totalUnits;

  DashboardStats({
    required this.totalSkus,
    required this.locations,
    required this.todayMovements,
    required this.totalUnits,
  });

  DashboardStats copyWith({
    int? totalSkus,
    int? locations,
    int? todayMovements,
    int? totalUnits,
  }) {
    return DashboardStats(
      totalSkus: totalSkus ?? this.totalSkus,
      locations: locations ?? this.locations,
      todayMovements: todayMovements ?? this.todayMovements,
      totalUnits: totalUnits ?? this.totalUnits,
    );
  }
}

class ActivityItem {
  final String id;
  final String skuCode;
  final String movementType;
  final int quantity;
  final String? location;
  final String? user;
  final DateTime timestamp;

  ActivityItem({
    required this.id,
    required this.skuCode,
    required this.movementType,
    required this.quantity,
    this.location,
    this.user,
    required this.timestamp,
  });

  factory ActivityItem.fromStockIntakeResponse(Map<String, dynamic> response) {
    return ActivityItem(
      id: response['movement_id'].toString(),
      skuCode: response['sku_code'],
      movementType: response['movement_type'] ?? 'IN',
      quantity: response['qty'] ?? 0,
      location: response['location'],
      user: response['created_by'],
      timestamp: DateTime.now(), // Use current time since API doesn't return it
    );
  }
}

class DashboardProvider with ChangeNotifier {
  DashboardStats _stats = DashboardStats(
    totalSkus: 0,
    locations: 0,
    todayMovements: 0,
    totalUnits: 0,
  );

  final List<ActivityItem> _recentActivity = [];
  final int _maxActivityItems = 50;

  DashboardStats get stats => _stats;
  List<ActivityItem> get recentActivity => List.unmodifiable(_recentActivity);

  void addStockMovement(Map<String, dynamic> response) {
    // Add to recent activity
    final activityItem = ActivityItem.fromStockIntakeResponse(response);
    _recentActivity.insert(0, activityItem);

    // Keep only the last N items
    if (_recentActivity.length > _maxActivityItems) {
      _recentActivity.removeRange(_maxActivityItems, _recentActivity.length);
    }

    // Update stats
    _updateStats(response);
    
    notifyListeners();
  }

  void _updateStats(Map<String, dynamic> response) {
    final Set<String> skus = {response['sku_code']};
    final Set<String> locations = {};
    
    // Count unique SKUs and locations from recent activity
    for (final item in _recentActivity) {
      skus.add(item.skuCode);
      if (item.location != null) {
        locations.add(item.location!);
      }
    }

    // Count today's movements
    final now = DateTime.now();
    final todayStart = DateTime(now.year, now.month, now.day);
    final todayMovements = _recentActivity.where((item) {
      return item.timestamp.isAfter(todayStart);
    }).length;

    // Calculate total units (sum of IN movements minus OUT movements)
    int totalUnits = 0;
    for (final item in _recentActivity) {
      if (item.movementType == 'IN') {
        totalUnits += item.quantity;
      } else if (item.movementType == 'OUT') {
        totalUnits -= item.quantity;
      }
    }

    _stats = DashboardStats(
      totalSkus: skus.length,
      locations: locations.length,
      todayMovements: todayMovements,
      totalUnits: totalUnits.abs(),
    );
  }

  void clearActivity() {
    _recentActivity.clear();
    _stats = DashboardStats(
      totalSkus: 0,
      locations: 0,
      todayMovements: 0,
      totalUnits: 0,
    );
    notifyListeners();
  }
}
