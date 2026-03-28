"""
Document parsing utilities for the Importance clearance system.

This module provides utilities for parsing various import documents
including invoices, bills of lading, and customs forms.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import re
from datetime import datetime


class DocumentParser(ABC):
    """Base class for document parsers."""
    
    @abstractmethod
    def parse(self, content: str) -> Dict[str, Any]:
        """Parse document content and extract structured data."""
        pass
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text in various formats."""
        # Common date patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
            r'(\d{2}-\d{2}-\d{4})',  # MM-DD-YYYY
            r'(\w+\s+\d{1,2},?\s+\d{4})',  # Month DD, YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def _extract_number(self, text: str, decimal: bool = True) -> Optional[float]:
        """Extract number from text."""
        text = re.sub(r'[^\d.\-]', '', text)
        if decimal:
            match = re.search(r'[-]?\d+\.\d+', text)
        else:
            match = re.search(r'[-]?\d+', text)
        if match:
            return float(match.group())
        return None
    
    def _extract_currency(self, text: str) -> Optional[float]:
        """Extract currency value from text."""
        # Remove currency symbols and commas
        text = re.sub(r'[$€£,]', '', text)
        return self._extract_number(text)


class InvoiceParser(DocumentParser):
    """Parser for commercial invoices."""
    
    def parse(self, content: str) -> Dict[str, Any]:
        """Parse invoice content."""
        result = {
            "invoice_number": None,
            "invoice_date": None,
            "supplier": None,
            "buyer": None,
            "items": [],
            "total_amount": None,
            "currency": None,
            "raw_text": content
        }
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = self._clean_text(line)
            
            # Extract invoice number
            if not result["invoice_number"]:
                invoice_match = re.search(r'invoice\s*#[:\s]*([A-Z0-9-]+)', line, re.IGNORECASE)
                if invoice_match:
                    result["invoice_number"] = invoice_match.group(1)
            
            # Extract date
            if not result["invoice_date"]:
                date_match = re.search(r'(?:date|invoice\s*date)[:\s]*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})', line, re.IGNORECASE)
                if date_match:
                    result["invoice_date"] = date_match.group(1)
            
            # Extract currency
            if not result["currency"]:
                if '$' in line:
                    result["currency"] = 'USD'
                elif '€' in line:
                    result["currency"] = 'EUR'
                elif '£' in line:
                    result["currency"] = 'GBP'
            
            # Extract total amount
            if not result["total_amount"]:
                total_match = re.search(r'total[:\s]*[\$€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line, re.IGNORECASE)
                if total_match:
                    result["total_amount"] = float(total_match.group(1).replace(',', ''))
        
        # Extract items (typically listed in table format)
        result["items"] = self._extract_items(lines)
        
        return result
    
    def _extract_items(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract line items from invoice."""
        items = []
        current_item = {}
        
        item_patterns = [
            r'(\d+)\s+(.+?)\s+(\d+(?:\.\d+)?)\s+([\d,]+\.?\d*)',  # Qty Description Qty Price
            r'(\d+)\s+(\d+(?:\.\d+)?)\s+(.+?)\s+([\d,]+\.?\d*)',  # Qty Price Description Total
        ]
        
        for line in lines:
            line = self._clean_text(line)
            
            for pattern in item_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    # Determine which format matched and extract accordingly
                    if len(groups) >= 4:
                        current_item = {
                            "quantity": float(groups[0]),
                            "description": groups[1],
                            "unit_price": self._extract_number(groups[2]) if groups[2] else None,
                            "total": self._extract_number(groups[3]) if groups[3] else None
                        }
                        items.append(current_item)
                        current_item = {}
                    break
        
        return items


class BillOfLadingParser(DocumentParser):
    """Parser for bills of lading."""
    
    def parse(self, content: str) -> Dict[str, Any]:
        """Parse bill of lading content."""
        result = {
            "bol_number": None,
            "shipper": None,
            "consignee": None,
            "notify_party": None,
            "port_of_loading": None,
            "port_of_discharge": None,
            "vessel_name": None,
            "total_packages": None,
            "weight": None,
            "weight_unit": None,
            "measurements": None,
            "raw_text": content
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line = self._clean_text(line)
            
            if not result["bol_number"]:
                bol_match = re.search(r'bill\s*of\s*lading[:\s]*([A-Z0-9-]+)', line, re.IGNORECASE)
                if bol_match:
                    result["bol_number"] = bol_match.group(1)
            
            if not result["shipper"]:
                shipper_match = re.search(r'shipper[:\s]*(.+?)(?:\n|$)', line, re.IGNORECASE)
                if shipper_match:
                    result["shipper"] = shipper_match.group(1).strip()
            
            if not result["consignee"]:
                consignee_match = re.search(r'consignee[:\s]*(.+?)(?:\n|$)', line, re.IGNORECASE)
                if consignee_match:
                    result["consignee"] = consignee_match.group(1).strip()
        
        return result


def get_parser(document_type: str) -> DocumentParser:
    """Get parser for document type."""
    parsers = {
        "invoice": InvoiceParser,
        "bill_of_lading": BillOfLadingParser,
        "billoflading": BillOfLadingParser,
        "bol": BillOfLadingParser
    }
    
    parser_class = parsers.get(document_type.lower(), DocumentParser)
    return parser_class()