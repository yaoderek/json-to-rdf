# JSON to RDF Converter

A powerful Python tool to convert JSON data to RDF (Resource Description Framework) triples with schema support. This converter supports multiple output formats including Turtle, N-Triples, JSON-LD, and XML.

## Features

- 🚀 **Multiple Output Formats**: Support for Turtle, N-Triples, JSON-LD, and XML
- 📊 **Schema Generation**: Automatic generation of schema.org triples
- 🎯 **Type Detection**: Automatic detection of data types (string, integer, boolean, date)
- 🔧 **Configurable**: Customizable base URIs, schema URIs, and output options
- 💻 **CLI Interface**: Easy-to-use command-line interface with rich output
- 📝 **Pretty Output**: Formatted and readable RDF output
- 🧪 **Comprehensive Testing**: Example files and test cases included

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd json-to-rdf
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Convert a JSON file to RDF (Turtle format by default):

```bash
python main.py input.json
```

### Advanced Usage

```bash
# Convert to specific format
python main.py input.json --format turtle
python main.py input.json --format nt
python main.py input.json --format json-ld
python main.py input.json --format xml

# Save output to file
python main.py input.json --output output.ttl

# Custom base URI
python main.py input.json --base-uri "http://mycompany.com/"

# Custom schema URI
python main.py input.json --schema-uri "http://mycompany.com/schema/"

# Verbose output with statistics
python main.py input.json --verbose

# Disable pretty printing
python main.py input.json --no-pretty

# Disable schema generation
python main.py input.json --no-schema
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_file` | Input JSON file path | Required |
| `--output, -o` | Output file path | stdout |
| `--format, -f` | Output format (turtle, nt, json-ld, xml) | turtle |
| `--base-uri` | Base URI for resources | http://example.org/ |
| `--schema-uri` | Schema URI | http://schema.org/ |
| `--pretty/--no-pretty` | Pretty print output | True |
| `--schema/--no-schema` | Generate schema triples | True |
| `--verbose, -v` | Verbose output | False |

## Examples

### Example 1: Basic Object Conversion

**Input JSON** (`examples/sample.json`):
```json
{
  "person": {
    "name": "John Doe",
    "age": 30,
    "email": "john.doe@example.com"
  }
}
```

**Command**:
```bash
python main.py examples/sample.json --verbose
```

**Output** (Turtle format):
```turtle
@prefix : <http://example.org/> .
@prefix schema: <http://schema.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:root a schema:Thing ;
    :person :root_person .

:root_person a schema:Thing ;
    :name "John Doe"^^xsd:string ;
    :age "30"^^xsd:integer ;
    :email "john.doe@example.com"^^xsd:string .
```

### Example 2: Array Conversion

**Input JSON** (`examples/array_sample.json`):
```json
[
  {
    "id": 1,
    "title": "First Item"
  },
  {
    "id": 2,
    "title": "Second Item"
  }
]
```

**Command**:
```bash
python main.py examples/array_sample.json --format json-ld
```

### Example 3: Custom URIs

```bash
python main.py input.json \
  --base-uri "http://mycompany.com/data/" \
  --schema-uri "http://mycompany.com/schema/" \
  --output output.ttl
```

## Supported Data Types

The converter automatically detects and maps JSON data types to appropriate XSD types:

| JSON Type | XSD Type | Example |
|-----------|----------|---------|
| `string` | `xsd:string` | `"hello"` |
| `number` (integer) | `xsd:integer` | `42` |
| `number` (float) | `xsd:double` | `3.14` |
| `boolean` | `xsd:boolean` | `true` |
| `string` (date-like) | `xsd:dateTime` | `"2023-01-01T10:00:00"` |

## Output Formats

### Turtle (.ttl)
Human-readable RDF format with prefixes and abbreviations.

### N-Triples (.nt)
Simple line-based format, one triple per line.

### JSON-LD (.jsonld)
JSON-based RDF format that can be embedded in web pages.

### XML (.xml)
RDF/XML format for XML-based applications.

## Project Structure

```
json-to-rdf/
├── main.py              # Main converter script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── examples/           # Example JSON files
│   ├── sample.json
│   └── array_sample.json
└── venv/              # Virtual environment (created during setup)
```

## Dependencies

- **rdflib**: RDF library for Python
- **rdflib-jsonld**: JSON-LD support for rdflib
- **pydantic**: Data validation and settings management
- **typer**: Modern CLI library
- **rich**: Rich text and beautiful formatting in the terminal
- **click**: CLI library (dependency of typer)

## Development

### Running Tests

Test the converter with the provided examples:

```bash
# Test basic conversion
python main.py examples/sample.json --verbose

# Test array conversion
python main.py examples/array_sample.json --verbose

# Test different formats
python main.py examples/sample.json --format nt --output test.nt
python main.py examples/sample.json --format json-ld --output test.jsonld
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on the project repository.
