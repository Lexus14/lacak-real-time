"""
Enhanced Input Validation and Sanitization
Provides robust validation for phone numbers, NIK, and general input
"""

import re
from typing import Optional, Tuple

class InputValidator:
    # Indonesian phone number regex
    PHONE_REGEX = r'^08[0-9]{8,11}$'
    NIK_REGEX = r'^[0-9]{16}$'
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """
        Validate and sanitize phone number
        Returns: (is_valid, cleaned_phone_or_error_msg)
        """
        if not phone:
            return False, "Nomor tidak boleh kosong"
        
        # Remove whitespace and special chars
        cleaned = re.sub(r'[^0-9+]', '', phone)
        
        # Convert +62 to 0
        if cleaned.startswith('+62'):
            cleaned = '0' + cleaned[3:]
        elif cleaned.startswith('62'):
            cleaned = '0' + cleaned[2:]
        
        # Validate format
        if not re.match(InputValidator.PHONE_REGEX, cleaned):
            return False, "Format nomor tidak valid (harus 08xxx, 10-13 digit)"
        
        return True, cleaned
    
    @staticmethod
    def validate_nik(nik: str) -> Tuple[bool, Optional[str]]:
        """
        Validate and sanitize NIK
        Returns: (is_valid, cleaned_nik_or_error_msg)
        """
        if not nik:
            return False, "NIK tidak boleh kosong"
        
        # Remove whitespace and special chars
        cleaned = re.sub(r'[^0-9]', '', nik)
        
        # Check length
        if len(cleaned) != 16:
            return False, "NIK harus 16 digit"
        
        # Validate format (basic)
        if not re.match(InputValidator.NIK_REGEX, cleaned):
            return False, "Format NIK tidak valid"
        
        return True, cleaned
    
    @staticmethod
    def sanitize_sql(text: str) -> str:
        """Sanitize text to prevent SQL injection"""
        # Remove dangerous characters
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text
    
    @staticmethod
    def validate_target(target: str) -> Tuple[bool, str, str]:
        """
        Validate target (phone or NIK)
        Returns: (is_valid, type, cleaned_value_or_error)
        """
        # Try phone first
        is_valid, result = InputValidator.validate_phone(target)
        if is_valid:
            return True, "phone", result
        
        # Try NIK
        is_valid, result = InputValidator.validate_nik(target)
        if is_valid:
            return True, "nik", result
        
        return False, "unknown", "Format tidak valid (harus nomor 08xxx atau NIK 16 digit)"

# Global validator instance
validator = InputValidator()