import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../providers/dashboard_provider.dart';

class StockIntakeCard extends StatefulWidget {
  const StockIntakeCard({super.key});

  @override
  State<StockIntakeCard> createState() => _StockIntakeCardState();
}

class _StockIntakeCardState extends State<StockIntakeCard> {
  final _formKey = GlobalKey<FormState>();
  final _barcodeController = TextEditingController();
  final _qtyController = TextEditingController(text: '1');
  final _locationController = TextEditingController();
  final _userController = TextEditingController();

  String _selectedMovementType = 'IN';
  bool _autoCreateSku = true;
  bool _isSubmitting = false;

  final List<String> _movementTypes = ['IN', 'OUT', 'TRANSFER', 'ADJUSTMENT'];

  @override
  void dispose() {
    _barcodeController.dispose();
    _qtyController.dispose();
    _locationController.dispose();
    _userController.dispose();
    super.dispose();
  }

  Future<void> _submitStockIntake() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final response = await apiService.stockIntake(
        barcode: _barcodeController.text.trim(),
        qty: int.parse(_qtyController.text),
        locationCode: _locationController.text.isEmpty
            ? null
            : _locationController.text.trim(),
        movementType: _selectedMovementType,
        autoCreateSku: _autoCreateSku,
        createdBy: _userController.text.isEmpty
            ? null
            : _userController.text.trim(),
      );

      if (mounted) {
        // Update dashboard stats and activity
        final dashboardProvider = Provider.of<DashboardProvider>(context, listen: false);
        dashboardProvider.addStockMovement(response);

        // Show bottom-right toast notification
        final overlay = Overlay.of(context);
        final overlayEntry = OverlayEntry(
          builder: (context) => _ToastNotification(
            message: 'Stock intake successful',
            skuCode: response['sku_code'],
            quantity: response['qty'] ?? int.parse(_qtyController.text),
            movementType: _selectedMovementType,
          ),
        );
        
        overlay.insert(overlayEntry);
        Future.delayed(const Duration(seconds: 4), () {
          overlayEntry.remove();
        });

        // Clear form for next entry
        _barcodeController.clear();
        _qtyController.text = '1';
        if (_selectedMovementType == 'IN') {
          _locationController.clear();
        }
        
        // Focus back to barcode field
        FocusScope.of(context).requestFocus(FocusNode());
        Future.delayed(const Duration(milliseconds: 100), () {
          if (mounted) {
            FocusScope.of(context).requestFocus(FocusNode());
          }
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(child: Text('Error: $e')),
              ],
            ),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.qr_code_scanner,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 12),
                Text(
                  'Stock Intake',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Scan or enter barcode to process stock movements',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
            const SizedBox(height: 24),
            Form(
              key: _formKey,
              child: Column(
                children: [
                  // Barcode Input
                  TextFormField(
                    controller: _barcodeController,
                    decoration: InputDecoration(
                      labelText: 'Barcode *',
                      hintText: 'Enter or scan barcode',
                      prefixIcon: const Icon(Icons.qr_code),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Barcode is required';
                      }
                      return null;
                    },
                    autofocus: true,
                  ),
                  const SizedBox(height: 16),
                  
                  // Quantity and Movement Type Row
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: _qtyController,
                          decoration: InputDecoration(
                            labelText: 'Quantity *',
                            prefixIcon: const Icon(Icons.numbers),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          keyboardType: TextInputType.number,
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'Required';
                            }
                            final qty = int.tryParse(value);
                            if (qty == null) {
                              return 'Invalid number';
                            }
                            return null;
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _selectedMovementType,
                          decoration: InputDecoration(
                            labelText: 'Movement Type',
                            prefixIcon: const Icon(Icons.swap_horiz),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          items: _movementTypes.map((type) {
                            return DropdownMenuItem(
                              value: type,
                              child: Text(type),
                            );
                          }).toList(),
                          onChanged: (value) {
                            setState(() {
                              _selectedMovementType = value!;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  
                  // Location Input
                  TextFormField(
                    controller: _locationController,
                    decoration: InputDecoration(
                      labelText: 'Location',
                      hintText: 'e.g., WH-A-01',
                      prefixIcon: const Icon(Icons.location_on),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // User Input
                  TextFormField(
                    controller: _userController,
                    decoration: InputDecoration(
                      labelText: 'User/Created By',
                      hintText: 'Your email or username',
                      prefixIcon: const Icon(Icons.person),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Auto-create SKU Checkbox
                  CheckboxListTile(
                    title: const Text('Auto-create SKU if not found'),
                    subtitle: const Text(
                      'Automatically create a new SKU for unknown barcodes',
                    ),
                    value: _autoCreateSku,
                    onChanged: (value) {
                      setState(() {
                        _autoCreateSku = value ?? true;
                      });
                    },
                    controlAffinity: ListTileControlAffinity.leading,
                    contentPadding: EdgeInsets.zero,
                  ),
                  const SizedBox(height: 24),
                  
                  // Submit Button
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: FilledButton.icon(
                      onPressed: _isSubmitting ? null : _submitStockIntake,
                      icon: _isSubmitting
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.check),
                      label: Text(
                        _isSubmitting ? 'Processing...' : 'Submit Stock Intake',
                      ),
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

// Toast notification widget for bottom-right display
class _ToastNotification extends StatefulWidget {
  final String message;
  final String skuCode;
  final int quantity;
  final String movementType;

  const _ToastNotification({
    required this.message,
    required this.skuCode,
    required this.quantity,
    required this.movementType,
  });

  @override
  State<_ToastNotification> createState() => _ToastNotificationState();
}

class _ToastNotificationState extends State<_ToastNotification>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(1.5, 0),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeIn,
    ));

    _controller.forward();

    // Auto-dismiss after 3.5 seconds
    Future.delayed(const Duration(milliseconds: 3500), () {
      if (mounted) {
        _controller.reverse();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Color _getMovementColor() {
    switch (widget.movementType) {
      case 'IN':
        return Colors.green;
      case 'OUT':
        return Colors.red;
      case 'TRANSFER':
        return Colors.blue;
      case 'ADJUSTMENT':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  IconData _getMovementIcon() {
    switch (widget.movementType) {
      case 'IN':
        return Icons.arrow_downward;
      case 'OUT':
        return Icons.arrow_upward;
      case 'TRANSFER':
        return Icons.swap_horiz;
      case 'ADJUSTMENT':
        return Icons.tune;
      default:
        return Icons.help_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Positioned(
      bottom: 24,
      right: 24,
      child: SlideTransition(
        position: _slideAnimation,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: Material(
            elevation: 8,
            borderRadius: BorderRadius.circular(12),
            child: Container(
              constraints: const BoxConstraints(maxWidth: 360),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _getMovementColor(),
                  width: 2,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: _getMovementColor().withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      _getMovementIcon(),
                      color: _getMovementColor(),
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Flexible(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.check_circle,
                              color: Colors.green,
                              size: 16,
                            ),
                            const SizedBox(width: 6),
                            Text(
                              widget.message,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'SKU: ${widget.skuCode}',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[700],
                          ),
                        ),
                        Text(
                          '${widget.movementType}: ${widget.quantity > 0 ? '+' : ''}${widget.quantity} units',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
