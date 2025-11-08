"""
Request validation utilities for warehouse API.

Provides custom validators for common data patterns like barcodes,
location codes, SKU codes, and other domain-specific formats.
"""

import re
from typing import Any


class BarcodeValidator:
    """
    Validates barcode format.
    
    Rules:
    - Length: 3-50 characters
    - Allowed: alphanumeric, hyphens, underscores
    - Case: normalized to uppercase
    - No leading/trailing whitespace
    """
    
    MIN_LENGTH = 3
    MAX_LENGTH = 50
    PATTERN = re.compile(r'^[A-Z0-9\-_]+$')
    
    @classmethod
    def validate(cls, value: str) -> str:
        """Validate and normalize barcode."""
        if not value:
            raise ValueError("Barcode cannot be empty")
        
        # Normalize to uppercase and strip whitespace
        normalized = value.upper().strip()
        
        # Check length
        if len(normalized) < cls.MIN_LENGTH:
            raise ValueError(
                f"Barcode must be at least {cls.MIN_LENGTH} characters long"
            )
        if len(normalized) > cls.MAX_LENGTH:
            raise ValueError(
                f"Barcode must not exceed {cls.MAX_LENGTH} characters"
            )
        
        # Check pattern
        if not cls.PATTERN.match(normalized):
            raise ValueError(
                "Barcode must contain only alphanumeric characters, "
                "hyphens, and underscores"
            )
        
        return normalized


class LocationCodeValidator:
    """
    Validates location code format.
    
    Format: ZONE-AISLE-BIN (e.g., WH-A-01, DOCK-B-05)
    
    Rules:
    - Format: 3 segments separated by hyphens
    - Zone: 2-6 uppercase letters
    - Aisle: 1-4 uppercase letters/numbers
    - Bin: 2-4 alphanumeric characters
    - Case: normalized to uppercase
    """
    
    PATTERN = re.compile(
        r'^([A-Z]{2,6})-([A-Z0-9]{1,4})-([A-Z0-9]{2,4})$'
    )
    
    @classmethod
    def validate(cls, value: str) -> str:
        """Validate and normalize location code."""
        if not value:
            raise ValueError("Location code cannot be empty")
        
        # Normalize to uppercase and strip whitespace
        normalized = value.upper().strip()
        
        # Check pattern
        match = cls.PATTERN.match(normalized)
        if not match:
            raise ValueError(
                "Location code must follow format ZONE-AISLE-BIN "
                "(e.g., WH-A-01, DOCK-B-05)"
            )
        
        return normalized


class SKUCodeValidator:
    """
    Validates SKU code format.
    
    Rules:
    - Length: 2-50 characters
    - Allowed: alphanumeric, hyphens, underscores, periods
    - Case: normalized to uppercase
    - No leading/trailing whitespace
    """
    
    MIN_LENGTH = 2
    MAX_LENGTH = 50
    PATTERN = re.compile(r'^[A-Z0-9\-_.]+$')
    
    @classmethod
    def validate(cls, value: str) -> str:
        """Validate and normalize SKU code."""
        if not value:
            raise ValueError("SKU code cannot be empty")
        
        # Normalize to uppercase and strip whitespace
        normalized = value.upper().strip()
        
        # Check length
        if len(normalized) < cls.MIN_LENGTH:
            raise ValueError(
                f"SKU code must be at least {cls.MIN_LENGTH} characters long"
            )
        if len(normalized) > cls.MAX_LENGTH:
            raise ValueError(
                f"SKU code must not exceed {cls.MAX_LENGTH} characters"
            )
        
        # Check pattern
        if not cls.PATTERN.match(normalized):
            raise ValueError(
                "SKU code must contain only alphanumeric characters, "
                "hyphens, underscores, and periods"
            )
        
        return normalized


class QuantityValidator:
    """
    Validates quantity values for stock operations.
    
    Rules:
    - Must be positive integer
    - Maximum: 1,000,000 units per operation
    """
    
    MIN_VALUE = 1
    MAX_VALUE = 1_000_000
    
    @classmethod
    def validate(cls, value: int) -> int:
        """Validate quantity value."""
        if not isinstance(value, int):
            raise ValueError("Quantity must be an integer")
        
        if value < cls.MIN_VALUE:
            raise ValueError(
                f"Quantity must be at least {cls.MIN_VALUE}"
            )
        
        if value > cls.MAX_VALUE:
            raise ValueError(
                f"Quantity cannot exceed {cls.MAX_VALUE}"
            )
        
        return value


class MovementTypeValidator:
    """
    Validates stock movement types.
    
    Allowed types:
    - intake: Receiving new stock
    - adjustment: Manual correction
    - transfer: Moving between locations
    - sale: Outbound sale
    - return: Customer return
    - damage: Damaged goods
    - loss: Lost/stolen
    """
    
    VALID_TYPES = {
        'intake',
        'adjustment',
        'transfer',
        'sale',
        'return',
        'damage',
        'loss'
    }
    
    @classmethod
    def validate(cls, value: str) -> str:
        """Validate movement type."""
        if not value:
            raise ValueError("Movement type cannot be empty")
        
        normalized = value.lower().strip()
        
        if normalized not in cls.VALID_TYPES:
            raise ValueError(
                f"Invalid movement type. Must be one of: "
                f"{', '.join(sorted(cls.VALID_TYPES))}"
            )
        
        return normalized


def validate_barcode(value: Any) -> str:
    """Pydantic validator function for barcodes."""
    if not isinstance(value, str):
        raise ValueError("Barcode must be a string")
    return BarcodeValidator.validate(value)


def validate_location_code(value: Any) -> str:
    """Pydantic validator function for location codes."""
    if not isinstance(value, str):
        raise ValueError("Location code must be a string")
    return LocationCodeValidator.validate(value)


def validate_sku_code(value: Any) -> str:
    """Pydantic validator function for SKU codes."""
    if not isinstance(value, str):
        raise ValueError("SKU code must be a string")
    return SKUCodeValidator.validate(value)


def validate_quantity(value: Any) -> int:
    """Pydantic validator function for quantities."""
    return QuantityValidator.validate(value)


def validate_movement_type(value: Any) -> str:
    """Pydantic validator function for movement types."""
    if not isinstance(value, str):
        raise ValueError("Movement type must be a string")
    return MovementTypeValidator.validate(value)
