#!/usr/bin/env python3
"""
Receipt CO2 Parser - Extract items from receipt images and estimate CO2 emissions
Uses OCR to parse receipt text and calculates carbon footprint based on emission factors
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Try to import OCR libraries
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  OCR libraries not available. Install with: pip install pillow pytesseract")

def extract_items_from_receipt(image_path: str) -> Dict:
    """
    Extract items from receipt image using OCR
    
    Args:
        image_path: Path to receipt image
        
    Returns:
        Dictionary with extracted items and metadata
    """
    
    if not OCR_AVAILABLE:
        return simulate_receipt_parsing()
    
    try:
        # Load and preprocess image
        image = Image.open(image_path)
        
        # Convert to grayscale for better OCR
        if image.mode != 'L':
            image = image.convert('L')
        
        # Extract text using OCR
        text = pytesseract.image_to_string(image)
        
        # Parse the extracted text
        return parse_receipt_text(text)
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return simulate_receipt_parsing()

def parse_receipt_text(text: str) -> Dict:
    """
    Parse receipt text to extract items and prices
    
    Args:
        text: Raw OCR text from receipt
        
    Returns:
        Dictionary with parsed receipt data
    """
    
    lines = text.strip().split('\n')
    
    receipt_data = {
        'store_name': '',
        'date': '',
        'items': [],
        'subtotal': 0.0,
        'tax': 0.0,
        'total': 0.0,
        'raw_text': text
    }
    
    # Extract store name (usually first meaningful line)
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) > 3 and not re.match(r'^[\d\s\-\/\$\.]+$', line):
            receipt_data['store_name'] = line
            break
    
    # Extract date
    date_patterns = [
        r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
        r'\b\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\b'
    ]
    
    for line in lines:
        for pattern in date_patterns:
            date_match = re.search(pattern, line)
            if date_match:
                receipt_data['date'] = date_match.group()
                break
        if receipt_data['date']:
            break
    
    # Extract items and prices
    items = []
    price_pattern = r'\$?(\d+\.\d{2})'
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue
        
        # Skip header/footer lines
        if any(word in line.lower() for word in ['total', 'subtotal', 'tax', 'change', 'cash', 'card']):
            # Extract totals
            if 'subtotal' in line.lower():
                price_match = re.search(price_pattern, line)
                if price_match:
                    receipt_data['subtotal'] = float(price_match.group(1))
            elif 'total' in line.lower() and 'subtotal' not in line.lower():
                price_match = re.search(price_pattern, line)
                if price_match:
                    receipt_data['total'] = float(price_match.group(1))
            elif 'tax' in line.lower():
                price_match = re.search(price_pattern, line)
                if price_match:
                    receipt_data['tax'] = float(price_match.group(1))
            continue
        
        # Look for item lines with prices
        price_matches = re.findall(price_pattern, line)
        if price_matches:
            price = float(price_matches[-1])  # Last price is usually the item price
            
            # Extract item name (everything before the price)
            item_text = re.sub(r'\$?\d+\.\d{2}.*$', '', line).strip()
            
            # Extract quantity if present
            quantity = extract_quantity(item_text)
            
            # Clean item name
            item_name = clean_item_name(item_text)
            
            if item_name and price > 0:
                items.append({
                    'name': item_name,
                    'price': price,
                    'quantity': quantity,
                    'unit_price': price / quantity if quantity > 0 else price,
                    'raw_line': line
                })
    
    receipt_data['items'] = items
    return receipt_data

def extract_quantity(item_text: str) -> float:
    """Extract quantity from item text"""
    
    quantity_patterns = [
        r'(\d+(?:\.\d+)?)\s*x\s*',      # "2x item"
        r'(\d+(?:\.\d+)?)\s*@',         # "3 @ $1.50"
        r'(\d+(?:\.\d+)?)\s*lb',        # "1.5 lb"
        r'(\d+(?:\.\d+)?)\s*kg',        # "2.3 kg"
        r'(\d+(?:\.\d+)?)\s*oz',        # "16 oz"
        r'(\d+(?:\.\d+)?)\s*g\b',       # "500 g"
        r'(\d+(?:\.\d+)?)\s*lbs?',      # "2 lbs"
    ]
    
    for pattern in quantity_patterns:
        match = re.search(pattern, item_text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    return 1.0  # Default quantity

def clean_item_name(item_text: str) -> str:
    """Clean and normalize item name"""
    
    # Remove quantity indicators
    item_text = re.sub(r'\d+(?:\.\d+)?\s*[x@]?\s*', '', item_text, flags=re.IGNORECASE)
    item_text = re.sub(r'\d+(?:\.\d+)?\s*(lb|kg|oz|g|lbs)\s*', '', item_text, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    item_text = ' '.join(item_text.split())
    
    return item_text.lower().strip()

def estimate_co2_emissions(receipt_data: Dict) -> Dict:
    """
    Estimate CO2 emissions for receipt items
    
    Args:
        receipt_data: Parsed receipt data
        
    Returns:
        Dictionary with CO2 emission estimates
    """
    
    # CO2 emission factors (kg CO2 per kg of product)
    EMISSION_FACTORS = {
        # Meat & Protein
        'beef': 20.0,           # As specified in the request
        'steak': 20.0,
        'ground beef': 20.0,
        'hamburger': 20.0,
        'pork': 12.1,
        'bacon': 12.1,
        'ham': 12.1,
        'chicken': 6.9,
        'turkey': 10.9,
        'fish': 6.1,
        'salmon': 6.1,
        'tuna': 6.1,
        'eggs': 4.2,
        
        # Dairy
        'milk': 3.2,
        'cheese': 13.5,
        'butter': 9.0,
        'yogurt': 2.2,
        'cream': 4.0,
        
        # Vegetables & Fruits
        'tomatoes': 2.1,
        'potatoes': 0.5,
        'onions': 0.5,
        'carrots': 0.4,
        'lettuce': 1.3,
        'broccoli': 2.0,
        'spinach': 2.0,
        'apples': 0.4,
        'bananas': 0.9,
        'oranges': 0.4,
        'grapes': 1.1,
        
        # Grains & Bread
        'bread': 0.9,
        'rice': 2.7,
        'pasta': 1.1,
        'cereal': 1.6,
        'flour': 0.6,
        
        # Beverages
        'coffee': 4.9,
        'tea': 1.8,
        'beer': 0.7,
        'wine': 1.3,
        'soda': 0.4,
        'juice': 1.1,
        
        # Processed Foods
        'chips': 3.5,
        'cookies': 2.8,
        'chocolate': 18.7,
        'ice cream': 4.0,
        'pizza': 3.4,
        
        # Household Items (per item, not per kg)
        'detergent': 2.5,
        'soap': 1.2,
        'shampoo': 1.8,
        'toothpaste': 0.8,
        'toilet paper': 1.3,
        'paper towels': 1.7,
    }
    
    # Category keywords for matching
    CATEGORY_KEYWORDS = {
        'beef': ['beef', 'steak', 'ground beef', 'hamburger', 'roast beef'],
        'pork': ['pork', 'bacon', 'ham', 'sausage', 'pork chop'],
        'chicken': ['chicken', 'poultry', 'chicken breast', 'chicken thigh'],
        'fish': ['fish', 'salmon', 'tuna', 'cod', 'shrimp', 'seafood'],
        'milk': ['milk', 'whole milk', 'skim milk', '2% milk', '1% milk'],
        'cheese': ['cheese', 'cheddar', 'mozzarella', 'swiss', 'parmesan'],
        'bread': ['bread', 'loaf', 'bagel', 'roll', 'baguette'],
        'vegetables': ['vegetables', 'lettuce', 'tomato', 'carrot', 'broccoli', 'spinach', 'onion'],
        'fruits': ['apple', 'banana', 'orange', 'grape', 'strawberry', 'fruit'],
    }
    
    co2_data = {
        'total_co2_kg': 0.0,
        'items_with_emissions': [],
        'category_breakdown': {},
        'unmatched_items': [],
        'estimation_method': 'keyword_matching'
    }
    
    for item in receipt_data.get('items', []):
        item_name = item['name'].lower()
        quantity = item['quantity']
        price = item['price']
        
        # Find matching emission factor
        emission_factor = 0.0
        matched_category = None
        
        # Direct match first
        for product, factor in EMISSION_FACTORS.items():
            if product in item_name:
                emission_factor = factor
                matched_category = product
                break
        
        # Category keyword matching if no direct match
        if emission_factor == 0.0:
            for category, keywords in CATEGORY_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in item_name:
                        emission_factor = EMISSION_FACTORS.get(category, 0.0)
                        matched_category = category
                        break
                if emission_factor > 0:
                    break
        
        if emission_factor > 0:
            # Estimate weight based on price and typical costs
            estimated_weight_kg = estimate_weight_from_price(item_name, price, quantity)
            
            # Calculate CO2 emissions
            co2_emissions = estimated_weight_kg * emission_factor
            
            item_co2 = {
                'name': item['name'],
                'category': matched_category,
                'quantity': quantity,
                'price': price,
                'estimated_weight_kg': estimated_weight_kg,
                'emission_factor_kg_co2_per_kg': emission_factor,
                'co2_emissions_kg': co2_emissions,
                'co2_emissions_g': co2_emissions * 1000
            }
            
            co2_data['items_with_emissions'].append(item_co2)
            co2_data['total_co2_kg'] += co2_emissions
            
            # Update category breakdown
            category_group = matched_category.split('_')[0] if '_' in matched_category else matched_category
            if category_group not in co2_data['category_breakdown']:
                co2_data['category_breakdown'][category_group] = 0
            co2_data['category_breakdown'][category_group] += co2_emissions
            
        else:
            co2_data['unmatched_items'].append(item['name'])
    
    return co2_data

def estimate_weight_from_price(item_name: str, price: float, quantity: float) -> float:
    """
    Estimate weight in kg based on item name, price, and quantity
    This is a rough approximation based on typical grocery prices
    """
    
    # Typical price per kg for different categories (USD)
    PRICE_PER_KG_ESTIMATES = {
        'beef': 15.0,
        'steak': 20.0,
        'pork': 10.0,
        'chicken': 8.0,
        'fish': 18.0,
        'milk': 1.5,    # per liter, assume 1kg ≈ 1L
        'cheese': 12.0,
        'bread': 4.0,
        'vegetables': 3.0,
        'fruits': 4.0,
        'rice': 2.0,
        'pasta': 2.5,
        'coffee': 15.0,
        'chocolate': 8.0,
    }
    
    # Find matching price estimate
    price_per_kg = 5.0  # Default
    
    for category, price_estimate in PRICE_PER_KG_ESTIMATES.items():
        if category in item_name.lower():
            price_per_kg = price_estimate
            break
    
    # Calculate estimated weight
    estimated_weight = (price / price_per_kg) * quantity
    
    # Apply reasonable bounds (0.01kg to 10kg per item)
    return max(0.01, min(10.0, estimated_weight))

def simulate_receipt_parsing() -> Dict:
    """
    Simulate receipt parsing when OCR is not available
    Returns sample receipt data for demonstration
    """
    
    return {
        'store_name': 'Sample Grocery Store',
        'date': '2024-01-15',
        'items': [
            {'name': 'ground beef', 'price': 12.99, 'quantity': 1.0, 'unit_price': 12.99, 'raw_line': 'Ground Beef 1lb $12.99'},
            {'name': 'chicken breast', 'price': 8.49, 'quantity': 1.0, 'unit_price': 8.49, 'raw_line': 'Chicken Breast $8.49'},
            {'name': 'milk', 'price': 3.29, 'quantity': 1.0, 'unit_price': 3.29, 'raw_line': 'Milk 1gal $3.29'},
            {'name': 'bread', 'price': 2.49, 'quantity': 1.0, 'unit_price': 2.49, 'raw_line': 'Whole Wheat Bread $2.49'},
            {'name': 'bananas', 'price': 1.89, 'quantity': 2.0, 'unit_price': 0.95, 'raw_line': 'Bananas 2lb $1.89'},
            {'name': 'cheese', 'price': 4.99, 'quantity': 1.0, 'unit_price': 4.99, 'raw_line': 'Cheddar Cheese $4.99'},
            {'name': 'tomatoes', 'price': 3.49, 'quantity': 1.5, 'unit_price': 2.33, 'raw_line': 'Tomatoes 1.5lb $3.49'},
        ],
        'subtotal': 37.63,
        'tax': 2.26,
        'total': 39.89,
        'raw_text': 'Sample receipt text (OCR not available)'
    }

def print_receipt_analysis(receipt_data: Dict, co2_data: Dict) -> None:
    """Print formatted receipt analysis with CO2 emissions"""
    
    print("🧾 RECEIPT ANALYSIS & CO2 ESTIMATION")
    print("=" * 60)
    
    # Receipt info
    print(f"🏪 Store: {receipt_data.get('store_name', 'Unknown')}")
    print(f"📅 Date: {receipt_data.get('date', 'Unknown')}")
    print(f"📝 Items: {len(receipt_data.get('items', []))}")
    print(f"💰 Total: ${receipt_data.get('total', 0):.2f}")
    
    # CO2 summary
    print(f"\n🌿 CARBON FOOTPRINT SUMMARY:")
    print(f"   Total CO2: {co2_data['total_co2_kg']:.3f} kg ({co2_data['total_co2_kg']*1000:.1f}g)")
    print(f"   Items analyzed: {len(co2_data['items_with_emissions'])}")
    print(f"   Unmatched items: {len(co2_data['unmatched_items'])}")
    
    # Category breakdown
    if co2_data['category_breakdown']:
        print(f"\n📊 CO2 BY CATEGORY:")
        for category, co2_kg in sorted(co2_data['category_breakdown'].items(), 
                                     key=lambda x: x[1], reverse=True):
            percentage = (co2_kg / co2_data['total_co2_kg']) * 100 if co2_data['total_co2_kg'] > 0 else 0
            print(f"   {category.title()}: {co2_kg:.3f} kg ({percentage:.1f}%)")
    
    # Item details
    print(f"\n📋 ITEM DETAILS:")
    print("-" * 60)
    print(f"{'Item':<20} {'Price':<8} {'Weight':<8} {'CO2 (g)':<10}")
    print("-" * 60)
    
    for item in co2_data['items_with_emissions']:
        print(f"{item['name'][:19]:<20} "
              f"${item['price']:<7.2f} "
              f"{item['estimated_weight_kg']:<7.2f}kg "
              f"{item['co2_emissions_g']:<10.1f}")
    
    # Unmatched items
    if co2_data['unmatched_items']:
        print(f"\n⚠️  UNMATCHED ITEMS:")
        for item in co2_data['unmatched_items']:
            print(f"   • {item}")
    
    # CO2 equivalents
    total_co2 = co2_data['total_co2_kg']
    if total_co2 > 0:
        print(f"\n🌍 CO2 EQUIVALENTS:")
        km_driven = total_co2 / 0.21  # 210g CO2/km for average car
        print(f"   🚗 Driving: {km_driven:.2f} km")
        
        trees_needed = total_co2 / 21.77 * 365  # Trees needed for 1 day
        print(f"   🌳 Tree-days to offset: {trees_needed:.1f}")
        
        phone_charges = total_co2 / 0.008  # ~8g CO2 per smartphone charge
        print(f"   📱 Smartphone charges: {phone_charges:.0f}")

def main():
    """Main function for receipt CO2 analysis"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract items from receipt and estimate CO2 emissions')
    parser.add_argument('image', nargs='?', help='Receipt image file')
    parser.add_argument('--demo', action='store_true', help='Run with sample data')
    parser.add_argument('--output', '-o', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    if args.demo or not args.image:
        print("🔍 Running receipt analysis demo (OCR not available)")
        receipt_data = simulate_receipt_parsing()
    else:
        print(f"🔍 Analyzing receipt: {args.image}")
        receipt_data = extract_items_from_receipt(args.image)
    
    # Estimate CO2 emissions
    co2_data = estimate_co2_emissions(receipt_data)
    
    # Print analysis
    print_receipt_analysis(receipt_data, co2_data)
    
    # Save results if requested
    if args.output:
        results = {
            'receipt_data': receipt_data,
            'co2_analysis': co2_data,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {args.output}")
    
    return {
        'receipt_data': receipt_data,
        'co2_analysis': co2_data
    }

if __name__ == "__main__":
    main()
