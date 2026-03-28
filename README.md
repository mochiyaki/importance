# Importance - Custom Clearance Agent Workforce

A modular, multi-agent system designed for small B2B import clearance operations. The system automates document processing, compliance verification, and shipment coordination through specialized AI agents.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Agents](#agents)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [API Reference](#api-reference)
- [Future Enhancements](#future-enhancements)

## Overview

Importance is a custom clearance automation system that helps small B2B import businesses streamline their customs clearance processes. The system uses specialized AI agents to:

1. **Process intake** - Extract and validate information from invoices and shipping documents
2. **Generate documentation** - Create required government forms (CBP7501, etc.) with accurate data
3. **Supervise and verify** - Review all processed shipments and trigger final actions

### Target Audience

- Small to medium-sized import businesses
- Customs brokers with moderate volume
- Companies handling repetitive import documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Import Clearance System                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────────┐         ┌─────────────────┐
│  Agent 1:    │          │   Agent 2:       │         │   Agent 3:      │
│   Intake     │          │    Expert        │         │   Supervisor    │
│              │          │                  │         │                 │
│ - Invoice    │          │ - Generate CBP   │         │ - Verify data   │
│   parsing    │          │   7501 forms     │         │ - Check         │
│ - Document   │          │ - Create Python  │         │   compliance    │
│   validation │          │   scripts        │         │ - Process ship. │
│ - Data       │          │                  │         │ - Human         │
│   extraction │          │                  │         │   trigger       │
└──────────────┘          └──────────────────┘         └─────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    ▼
                          ┌──────────────────┐
                          │   Shared Memory  │
                          │   & Context      │
                          └──────────────────┘
```

## Agents

### Agent 1: Intake Processor

**Purpose**: Process incoming import documents and extract relevant data.

**Capabilities**:
- Invoice parsing (PDF, image, text)
- Document validation and verification
- Data extraction and normalization
- Initial quality checks

**Input Types**:
- Commercial invoices
- Packing lists
- Bills of lading
- Phosphates and chemical documentation

**Output**:
- Structured JSON data
- Validation reports
- Data quality scores

**Tools**:
- OCR for image-based documents
- PDF parsing libraries
- Data validation rules

### Agent 2: Documentation Expert

**Purpose**: Generate accurate government and compliance documentation.

**Capabilities**:
- Generate CBP Form 7501 (Customs Entry Summary)
- Create other required import documents
- Python script generation for document population
- Format compliance verification

**Output Forms**:
- CBP 7501 (Entry Summary)
- CBP 3461 (Bill of Lading)
- ISF (Import Security Filing) data
- ACE (Automated Commercial Environment) submissions

**Technical Implementation**:
- Python scripts that populate PDF templates
- PDF manipulation using PyPDF2, reportlab
- JSON-to-document mapping

### Agent 3: Supervisor

**Purpose**: Verify processed shipments and trigger final actions.

**Capabilities**:
- Cross-reference Agent 1 and Agent 2 outputs
- Compliance verification
- Decision-making on shipment release
- Human notification and approval workflow

**Verification Checks**:
- Data consistency across documents
- Compliance with regulations
- Error detection and resolution
- Final approval workflow

## Project Structure

```
importance/
├── src/
│   ├── agents/
│   │   ├── intake.py          # Agent 1: Intake processor
│   │   ├── expert.py          # Agent 2: Documentation expert
│   │   └── supervisor.py      # Agent 3: Supervisor
│   ├── documents/
│   │   ├── parser.py          # Document parsing utilities
│   │   ├── formatter.py       # Document formatting
│   │   └── templates/         # Form templates
│   │       ├── cbp7501.json
│   │       └── cbp7501.pdf
│   ├── core/
│   │   ├── agent.py           # Base agent class
│   │   ├── memory.py          # Shared memory system
│   │   └── context.py         # Context management
│   └── utils/
│       ├── logging.py
│       └── validators.py
├── tests/
│   ├── test_agents.py
│   ├── test_documents.py
│   └── test_integration.py
├── examples/
│   ├── sample_invoice.pdf
│   └── workflow_example.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Tech Stack

### Core Languages
- **Python 3.10+** - Main implementation language

### Key Libraries
- **PyPDF2** - PDF manipulation
- **PyMuPDF (fitz)** - Advanced PDF processing
- **pdfplumber** - PDF text extraction
- **OpenCV** - Image processing for OCR
- **pytesseract** - OCR capabilities
- **requests** - API communication
- **pydantic** - Data validation
- **logging** - System logging

### Future Additions
- **LangChain** - Agent orchestration
- **Redis** - Shared memory/cache
- **FastAPI** - Web interface
- **React** - Frontend dashboard

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Adobe Acrobat (optional, for advanced PDF features)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/importance.git
cd importance
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the system:
```bash
python -m src.agents.intake
```

## Usage

### Basic Workflow

1. **Agent 1 - Intake**:
```python
from src.agents.intake import IntakeAgent

agent = IntakeAgent()
result = agent.process_document("invoice.pdf")
print(result.data)  # Extracted data
print(result.validation)  # Validation report
```

2. **Agent 2 - Expert**:
```python
from src.agents.expert import ExpertAgent

agent = ExpertAgent()
cbp_form = agent.generate_cbp7501(intake_data)
print(cbp_form.json())  # Generated form data
```

3. **Agent 3 - Supervisor**:
```python
from src.agents.supervisor import SupervisorAgent

agent = SupervisorAgent()
verification = agent.verify_shipment(expert_output)
print(verification.status)  # "approved" or "requires_review"
```

### Complete Workflow Example

```python
from src.agents.intake import IntakeAgent
from src.agents.expert import ExpertAgent
from src.agents.supervisor import SupervisorAgent

# Process invoice
intake = IntakeAgent()
invoice_data = intake.process_document("commercial_invoice.pdf")

# Generate CBP form
expert = ExpertAgent()
cbp_form = expert.generate_cbp7501(invoice_data)

# Supervisor verification
supervisor = SupervisorAgent()
result = supervisor.verify_shipment(cbp_form)

if result.status == "approved":
    print("Shipment cleared for import")
else:
    print(f"Requires review: {result.remarks}")
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Linting
flake8 src/

# Type checking
mypy src/
```

### Adding New Agents
1. Create agent file in `src/agents/`
2. Inherit from `src/core/agent.py`
3. Implement `process()` method
4. Add to agent registry

## API Reference

### IntakeAgent
- `process_document(file_path)` - Process document and extract data
- `validate_data(data)` - Validate extracted data
- `normalize_data(data)` - Normalize data to standard format

### ExpertAgent
- `generate_cbp7501(data)` - Generate CBP Form 7501
- `create_python_script(template, data)` - Create population script
- `validate_form(form)` - Verify form completeness

### SupervisorAgent
- `verify_shipment(expert_output)` - Verify processed shipment
- `trigger_human_review(data)` - Request human review
- `process_shipment(data)` - Final shipment processing

## Future Enhancements

1. **Additional Agents**:
   - Agent 4: Compliance researcher (regulation lookup)
   - Agent 5: Communication liaison (customs broker interaction)

2. **Web Interface**:
   - Upload portal
   - Document tracking
   - Status dashboard

3. **Integrations**:
   - ACE (Automated Commercial Environment)
   - USDA APHIS systems
   - FDA entry systems

4. **Machine Learning**:
   - Invoice template learning
   - Error pattern detection
   - Process optimization

5. **Cloud Deployment**:
   - AWS/GCP deployment packages
   - Serverless functions for agents
   - Managed queues for workload distribution

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request