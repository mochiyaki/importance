"""
Agent 1: Intake Processor for the Importance clearance system.

This agent processes incoming import documents (invoices, bills of lading)
and extracts relevant data for further processing by other agents.
"""

from typing import Any, Dict, List, Optional
import os
import re

from src.core.agent import BaseAgent, AgentResult
from src.documents.parser import get_parser, InvoiceParser, BillOfLadingParser


class IntakeAgent(BaseAgent):
    """
    Agent 1: Intake Processor
    
    Processes incoming import documents and extracts relevant data
    for the clearance workflow.
    """
    
    # Document types this agent can handle
    SUPPORTED_DOCUMENT_TYPES = [
        "invoice",
        "commercial_invoice",
        "packing_list",
        "bill_of_lading",
        "bol",
        "manifest"
    ]
    
    # Validation rules for key data fields
    VALIDATION_RULES = {
        "invoice_number": {"required": True, "pattern": r"^[A-Z0-9-]{6,}$"},
        "supplier_name": {"required": True, "min_length": 3},
        "buyer_name": {"required": True, "min_length": 3},
        "total_amount": {"required": True, "min_value": 0},
        "currency": {"required": True, "pattern": r"^(USD|EUR|GBP|CAD|JPY|CNY)$"},
        "items": {"required": True, "min_count": 1}
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("IntakeAgent", config)
        self.parsers = {
            "invoice": InvoiceParser(),
            "commercial_invoice": InvoiceParser(),
            "bill_of_lading": BillOfLadingParser(),
            "bol": BillOfLadingParser()
        }
    
    def process(self, input_data: Any) -> AgentResult:
        """
        Process incoming document and extract data.
        
        Args:
            input_data: Can be file path (str), file content (str), or dict with 'type' and 'content' keys
            
        Returns:
            AgentResult with extracted data and validation results
        """
        try:
            # Parse input data
            doc_type, content = self._parse_input(input_data)
            
            # Get appropriate parser
            parser = self.parsers.get(doc_type)
            if not parser:
                return AgentResult(
                    success=False,
                    errors=[f"Unsupported document type: {doc_type}"]
                )
            
            # Parse document
            extracted_data = parser.parse(content)
            
            # Validate extracted data
            validation_result = self._validate_data(extracted_data, doc_type)
            
            if not validation_result["valid"]:
                return AgentResult(
                    success=False,
                    data=extracted_data,
                    errors=validation_result["errors"]
                )
            
            # Normalize data to standard format
            normalized_data = self._normalize_data(extracted_data, doc_type)
            
            self.log_info(f"Successfully processed {doc_type} document")
            
            return AgentResult(
                success=True,
                data=normalized_data,
                metadata={
                    "document_type": doc_type,
                    "validation_score": self._calculate_validation_score(validation_result),
                    "processing_timestamp": self._get_timestamp()
                }
            )
            
        except Exception as e:
            self.log_error(f"Processing error: {str(e)}")
            return AgentResult(
                success=False,
                errors=[f"Processing error: {str(e)}"]
            )
    
    def _parse_input(self, input_data: Any) -> tuple:
        """Parse input data and return (doc_type, content)."""
        if isinstance(input_data, str):
            # Check if it's a file path
            if os.path.exists(input_data):
                return self._parse_file(input_data)
            else:
                # Assume it's direct content
                return "invoice", input_data
                
        elif isinstance(input_data, dict):
            # Expected format: {"type": "invoice", "content": "..."}
            doc_type = input_data.get("type", "invoice")
            content = input_data.get("content", "")
            return doc_type, content
            
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
    
    def _parse_file(self, file_path: str) -> tuple:
        """Parse a document file and return (doc_type, content)."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine document type based on file name or content
        doc_type = self._detect_document_type(file_path, content)
        return doc_type, content
    
    def _detect_document_type(self, file_path: str, content: str) -> str:
        """Detect document type from file path or content."""
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.pdf', '.doc', '.docx']:
            return "invoice"  # Default to invoice for binary files
        
        # Check content patterns
        if "bill of lading" in content.lower():
            return "bill_of_lading"
        if "invoice" in content.lower():
            return "invoice"
        if "packing list" in content.lower():
            return "packing_list"
        
        return "invoice"  # Default
    
    def _validate_data(self, data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Validate extracted data against rules."""
        errors = []
        
        for field, rules in self.VALIDATION_RULES.items():
            value = data.get(field)
            
            # Check required fields
            if rules.get("required") and value is None:
                errors.append(f"Missing required field: {field}")
                continue
            
            # Check pattern
            if value and "pattern" in rules:
                if not re.match(rules["pattern"], str(value)):
                    errors.append(f"Field {field} doesn't match pattern")
            
            # Check min_length
            if value and "min_length" in rules:
                if len(str(value)) < rules["min_length"]:
                    errors.append(f"Field {field} is too short")
            
            # Check min_value
            if value and "min_value" in rules:
                try:
                    if float(value) < rules["min_value"]:
                        errors.append(f"Field {field} is below minimum value")
                except (ValueError, TypeError):
                    errors.append(f"Field {field} is not a valid number")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _normalize_data(self, data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Normalize extracted data to standard format."""
        normalized = {
            "document_type": doc_type,
            "invoice_number": data.get("invoice_number"),
            "invoice_date": data.get("invoice_date"),
            "supplier": {
                "name": data.get("supplier"),
                "address": data.get("supplier_address"),
                "country": data.get("supplier_country")
            },
            "buyer": {
                "name": data.get("buyer"),
                "address": data.get("buyer_address"),
                "country": data.get("buyer_country")
            },
            "items": data.get("items", []),
            "totals": {
                "amount": data.get("total_amount"),
                "currency": data.get("currency", "USD")
            },
            "raw_data": data.get("raw_text", "")
        }
        
        return normalized
    
    def _calculate_validation_score(self, validation_result: Dict[str, Any]) -> float:
        """Calculate a validation score from 0 to 100."""
        if validation_result["valid"]:
            return 100.0
        
        total_rules = len(self.VALIDATION_RULES)
        error_count = len(validation_result["errors"])
        
        # Calculate score based on errors vs total rules
        score = max(0, 100 - (error_count * 20))
        return float(score)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def process_batch(self, inputs: List[Any]) -> List[AgentResult]:
        """Process multiple documents in batch."""
        results = []
        for input_item in inputs:
            result = self.process(input_item)
            results.append(result)
        return results


# Example usage
if __name__ == "__main__":
    # Sample invoice text
    sample_invoice = """
    COMMERCIAL INVOICE
    
    Invoice Number: INV-2024-001
    Date: 2024-01-15
    
    Supplier: ABC Trading Co.
    Address: 123 Main Street, Shanghai, China
    Country: China
    
    Buyer: XYZ Imports Inc.
    Address: 456 Market Street, New York, NY
    Country: USA
    
    Items:
    1. Widget A - 100 units @ $10.00
    2. Widget B - 50 units @ $25.00
    
    Total: $2250.00
    Currency: USD
    """
    
    agent = IntakeAgent()
    result = agent.process(sample_invoice)
    
    if result.success:
        print("Data extracted successfully:")
        print(f"Invoice Number: {result.data.get('invoice_number')}")
        print(f"Supplier: {result.data.get('supplier', {}).get('name')}")
        print(f"Buyer: {result.data.get('buyer', {}).get('name')}")
        print(f"Total Amount: {result.data.get('totals', {}).get('amount')}")
    else:
        print(f"Validation errors: {result.errors}")