#!/usr/bin/env python3
"""
JSON to RDF Converter

A tool to convert JSON data to RDF triples with schema support.
Supports multiple output formats including Turtle, N-Triples, and JSON-LD.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import typer
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel, Field

# Initialize Rich console for pretty output
console = Console()

# Default namespaces
DEFAULT_NS = Namespace("http://example.org/")
SCHEMA_NS = Namespace("http://schema.org/")

class ConversionConfig(BaseModel):
    """Configuration for JSON to RDF conversion."""
    base_uri: str = Field(default="http://example.org/", description="Base URI for resources")
    schema_uri: str = Field(default="http://schema.org/", description="Schema URI")
    output_format: str = Field(default="turtle", description="Output format (turtle, nt, json-ld, xml)")
    pretty_print: bool = Field(default=True, description="Pretty print output")
    generate_schema: bool = Field(default=True, description="Generate schema triples")

class JsonToRdfConverter:
    """Convert JSON data to RDF triples."""
    
    def __init__(self, config: ConversionConfig):
        self.config = config
        self.graph = Graph()
        self.base_ns = Namespace(config.base_uri)
        self.schema_ns = Namespace(config.schema_uri)
        
        # Bind namespaces
        self.graph.bind("", self.base_ns)
        self.graph.bind("schema", self.schema_ns)
        self.graph.bind("rdf", RDF)
        self.graph.bind("xsd", XSD)
    
    def _create_uri(self, identifier: str) -> URIRef:
        """Create a URI reference from an identifier."""
        if identifier.startswith(('http://', 'https://')):
            return URIRef(identifier)
        return self.base_ns[identifier]
    
    def _get_literal_type(self, value: Any) -> URIRef:
        """Determine the XSD type for a literal value."""
        if isinstance(value, bool):
            return XSD.boolean
        elif isinstance(value, int):
            return XSD.integer
        elif isinstance(value, float):
            return XSD.double
        elif isinstance(value, str):
            # Try to detect if it's a date/time
            if self._looks_like_date(value):
                return XSD.date
            return XSD.string
        return XSD.string
    
    def _looks_like_date(self, value: str) -> bool:
        """Simple heuristic to detect if a string looks like a date."""
        import re
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO datetime
        ]
        return any(re.match(pattern, value) for pattern in date_patterns)
    
    def _convert_value(self, subject: URIRef, predicate: URIRef, value: Any) -> None:
        """Convert a value to RDF and add to graph."""
        if isinstance(value, (dict, list)):
            # Handle complex objects
            if isinstance(value, dict):
                self._convert_object(subject, predicate, value)
            else:
                self._convert_array(subject, predicate, value)
        else:
            # Handle simple literals
            literal_type = self._get_literal_type(value)
            literal = Literal(value, datatype=literal_type)
            self.graph.add((subject, predicate, literal))
    
    def _convert_object(self, subject: URIRef, predicate: URIRef, obj: Dict[str, Any]) -> None:
        """Convert a JSON object to RDF."""
        # Create a new resource for this object
        obj_uri = self._create_uri(f"{subject.split('/')[-1]}_{predicate.split('/')[-1]}")
        
        # Link the subject to this object
        self.graph.add((subject, predicate, obj_uri))
        
        # Add type information if schema generation is enabled
        if self.config.generate_schema:
            self.graph.add((obj_uri, RDF.type, self.schema_ns.Thing))
        
        # Convert each property of the object
        for key, value in obj.items():
            prop_uri = self._create_uri(key)
            self._convert_value(obj_uri, prop_uri, value)
    
    def _convert_array(self, subject: URIRef, predicate: URIRef, array: List[Any]) -> None:
        """Convert a JSON array to RDF."""
        for i, item in enumerate(array):
            if isinstance(item, dict):
                # Create a new resource for each object in the array
                item_uri = self._create_uri(f"{subject.split('/')[-1]}_{predicate.split('/')[-1]}_{i}")
                self.graph.add((subject, predicate, item_uri))
                
                if self.config.generate_schema:
                    self.graph.add((item_uri, RDF.type, self.schema_ns.Thing))
                
                for key, value in item.items():
                    prop_uri = self._create_uri(key)
                    self._convert_value(item_uri, prop_uri, value)
            else:
                # For simple values, create a sequence or use rdf:List
                item_uri = self._create_uri(f"{subject.split('/')[-1]}_{predicate.split('/')[-1]}_{i}")
                self.graph.add((subject, predicate, item_uri))
                self._convert_value(item_uri, RDF.value, item)
    
    def convert(self, data: Union[Dict[str, Any], List[Any]], root_uri: Optional[str] = None) -> Graph:
        """Convert JSON data to RDF graph."""
        if root_uri is None:
            root_uri = self._create_uri("root")
        else:
            root_uri = self._create_uri(root_uri)
        
        if isinstance(data, dict):
            # Add type information for the root object
            if self.config.generate_schema:
                self.graph.add((root_uri, RDF.type, self.schema_ns.Thing))
            
            # Convert each property
            for key, value in data.items():
                prop_uri = self._create_uri(key)
                self._convert_value(root_uri, prop_uri, value)
        
        elif isinstance(data, list):
            # Handle root-level arrays
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    item_uri = self._create_uri(f"item_{i}")
                    self.graph.add((root_uri, self._create_uri("item"), item_uri))
                    
                    if self.config.generate_schema:
                        self.graph.add((item_uri, RDF.type, self.schema_ns.Thing))
                    
                    for key, value in item.items():
                        prop_uri = self._create_uri(key)
                        self._convert_value(item_uri, prop_uri, value)
                else:
                    self._convert_value(root_uri, self._create_uri("value"), item)
        
        return self.graph
    
    def serialize(self, format: Optional[str] = None) -> str:
        """Serialize the graph to the specified format."""
        fmt = format or self.config.output_format
        return self.graph.serialize(format=fmt, pretty=self.config.pretty_print)

def convert_json_to_rdf(
    input_file: str = typer.Argument(..., help="Input JSON file path"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("turtle", "--format", "-f", help="Output format (turtle, nt, json-ld, xml)"),
    base_uri: str = typer.Option("http://example.org/", "--base-uri", help="Base URI for resources"),
    schema_uri: str = typer.Option("http://schema.org/", "--schema-uri", help="Schema URI"),
    pretty: bool = typer.Option(True, "--pretty/--no-pretty", help="Pretty print output"),
    generate_schema: bool = typer.Option(True, "--schema/--no-schema", help="Generate schema triples"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
) -> None:
    """Convert JSON file to RDF format."""
    
    # Validate input file
    input_path = Path(input_file)
    if not input_path.exists():
        console.print(f"[red]Error: Input file '{input_file}' not found[/red]")
        raise typer.Exit(1)
    
    if verbose:
        console.print(f"[blue]Reading JSON from: {input_path}[/blue]")
    
    try:
        # Read JSON data
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if verbose:
            console.print(f"[green]Successfully loaded JSON data[/green]")
        
        # Create converter configuration
        config = ConversionConfig(
            base_uri=base_uri,
            schema_uri=schema_uri,
            output_format=format,
            pretty_print=pretty,
            generate_schema=generate_schema
        )
        
        # Convert to RDF
        converter = JsonToRdfConverter(config)
        graph = converter.convert(data)
        
        if verbose:
            console.print(f"[green]Converted to RDF with {len(graph)} triples[/green]")
        
        # Serialize output
        rdf_output = converter.serialize()
        
        # Write to file or print to stdout
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rdf_output)
            console.print(f"[green]RDF output written to: {output_path}[/green]")
        else:
            console.print(rdf_output)
        
        # Show statistics
        if verbose:
            stats_table = Table(title="Conversion Statistics")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")
            
            stats_table.add_row("Input file", str(input_path))
            stats_table.add_row("Output format", format)
            stats_table.add_row("Triples generated", str(len(graph)))
            stats_table.add_row("Base URI", base_uri)
            stats_table.add_row("Schema URI", schema_uri)
            
            console.print(stats_table)
    
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON format - {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

def main():
    """Main entry point."""
    typer.run(convert_json_to_rdf)

if __name__ == "__main__":
    main()