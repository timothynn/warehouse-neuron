class StockIntakeRequest {
  final String barcode;
  final int qty;
  final String? locationCode;
  final String movementType;
  final bool autoCreateSku;
  final String? createdBy;

  StockIntakeRequest({
    required this.barcode,
    this.qty = 1,
    this.locationCode,
    this.movementType = 'IN',
    this.autoCreateSku = false,
    this.createdBy,
  });

  Map<String, dynamic> toJson() {
    return {
      'barcode': barcode,
      'qty': qty,
      if (locationCode != null) 'location_code': locationCode,
      'movement_type': movementType,
      'auto_create_sku': autoCreateSku,
      if (createdBy != null) 'created_by': createdBy,
    };
  }
}

class StockIntakeResponse {
  final String movementId;
  final String skuId;
  final String skuCode;
  final int onHand;

  StockIntakeResponse({
    required this.movementId,
    required this.skuId,
    required this.skuCode,
    required this.onHand,
  });

  factory StockIntakeResponse.fromJson(Map<String, dynamic> json) {
    return StockIntakeResponse(
      movementId: json['movement_id'],
      skuId: json['sku_id'],
      skuCode: json['sku_code'],
      onHand: json['on_hand'],
    );
  }
}

class StockMovement {
  final String id;
  final String skuCode;
  final String? location;
  final int qty;
  final String movementType;
  final String? createdBy;
  final DateTime createdAt;

  StockMovement({
    required this.id,
    required this.skuCode,
    this.location,
    required this.qty,
    required this.movementType,
    this.createdBy,
    required this.createdAt,
  });

  factory StockMovement.fromJson(Map<String, dynamic> json) {
    return StockMovement(
      id: json['id'],
      skuCode: json['sku_code'],
      location: json['location'],
      qty: json['qty'],
      movementType: json['movement_type'],
      createdBy: json['created_by'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
