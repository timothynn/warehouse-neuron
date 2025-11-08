import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Update this to your backend URL
  static const String baseUrl = 'http://localhost:8000';

  // Health check
  Future<Map<String, dynamic>> healthCheck() async {
    final response = await http.get(Uri.parse('$baseUrl/health'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to check health');
    }
  }

  // Stock intake
  Future<Map<String, dynamic>> stockIntake({
    required String barcode,
    int qty = 1,
    String? locationCode,
    String movementType = 'IN',
    bool autoCreateSku = false,
    String? createdBy,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/stock/intake'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'barcode': barcode,
        'qty': qty,
        if (locationCode != null) 'location_code': locationCode,
        'movement_type': movementType,
        'auto_create_sku': autoCreateSku,
        if (createdBy != null) 'created_by': createdBy,
      }),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to process stock intake');
    }
  }

  // Get API info
  Future<Map<String, dynamic>> getApiInfo() async {
    final response = await http.get(Uri.parse(baseUrl));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to get API info');
    }
  }
}
