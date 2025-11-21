"""
Extract KSRTC bus route data from PDF files
"""
import pdfplumber
import json
import re
from datetime import datetime, time

def extract_pdf_data(pdf_path):
    """Extract text from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

def parse_bus_routes(text, city_name):
    """Parse bus routes from extracted text"""
    routes = []
    stops = set()
    
    # Split into lines
    lines = text.split('\n')
    
    # Basic parsing - adjust based on actual PDF format
    current_route = None
    route_number = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for route patterns (this is a basic example)
        # Adjust regex based on actual PDF format
        
        # Example patterns to find stops
        if any(keyword in line.lower() for keyword in ['bus', 'route', 'service']):
            if current_route:
                routes.append(current_route)
            current_route = {
                'route_number': f"{city_name[:4].upper()}{route_number:03d}",
                'route_name': line[:100],
                'stops': [],
                'city': city_name
            }
            route_number += 1
        elif current_route and len(line) > 3:
            # Add as potential stop
            stops.add(line[:100])
            current_route['stops'].append(line[:100])
    
    if current_route:
        routes.append(current_route)
    
    return routes, list(stops)

def main():
    """Main extraction function"""
    
    # Extract from both PDFs
    pdf1 = r"c:\Users\Darshith M S\OneDrive\Desktop\New folder (4)\SHIVAMOGGA_1762846076.pdf"
    pdf2 = r"c:\Users\Darshith M S\OneDrive\Desktop\New folder (4)\MysuruCityBS_MYSR.pdf"
    
    print("Extracting from Shivamogga PDF...")
    text1 = extract_pdf_data(pdf1)
    routes1, stops1 = parse_bus_routes(text1, "Shivamogga")
    
    print("Extracting from Mysuru PDF...")
    text2 = extract_pdf_data(pdf2)
    routes2, stops2 = parse_bus_routes(text2, "Mysuru")
    
    # Combine data
    all_routes = routes1 + routes2
    all_stops = list(set(stops1 + stops2))
    
    # Save raw text for manual inspection
    with open('shivamogga_text.txt', 'w', encoding='utf-8') as f:
        f.write(text1)
    
    with open('mysuru_text.txt', 'w', encoding='utf-8') as f:
        f.write(text2)
    
    print(f"\nExtracted {len(all_routes)} routes")
    print(f"Found {len(all_stops)} unique stops")
    
    # Save to JSON
    output_data = {
        'routes': all_routes,
        'stops': all_stops,
        'extraction_date': datetime.now().isoformat()
    }
    
    with open('ksrtc_data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\nData saved to ksrtc_data.json")
    print("Raw text saved to shivamogga_text.txt and mysuru_text.txt")
    print("\nPlease review the text files to understand the PDF structure")
    print("Then we'll create proper parsing logic")

if __name__ == "__main__":
    main()
