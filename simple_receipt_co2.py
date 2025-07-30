#!/usr/bin/env python3
"""
Simple Receipt CO2 Estimator
Extract items from receipt and estimate CO2 emissions (e.g., beef=20kgCO2/kg)
"""

import re
from typing import Dict, List, Tuple

def extract_receipt_items(receipt_text: str) -> List[Dict]:
    """
    Extract items from receipt text
    
    Args:
        receipt_text: Raw text from receipt (OCR or manual input)
        
    Returns:
        List of items with names, prices, and quantities
    """
    
    items = []
    lines = receipt_text.strip().split('\n')
    
    # Pattern to match price (e.g., $12.99, 12.99)
    price_pattern = r'\$?(\d+\.\d{2})'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip total/tax lines
        if any(word in line.lower() for word in ['total', 'tax', 'subtotal', 'change']):
            continue
        
        # Look for lines with prices
        price_matches = re.findall(price_pattern, line)
        if price_matches:
            price = float(price_matches[-1])  # Last price is usually item price
            
            # Extract item name (text before price)
            item_name = re.sub(r'\$?\d+\.\d{2}.*$', '', line).strip()
            
            # Extract quantity
            quantity = 1.0
            qty_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:x|@|lb|kg)', item_name, re.IGNORECASE)
            if qty_match:
                quantity = float(qty_match.group(1))
            
            # Clean item name
            clean_name = re.sub(r'\d+(?:\.\d+)?\s*(?:x|@|lb|kg)\s*', '', item_name, re.IGNORECASE)
            clean_name = clean_name.strip().lower()
            
            if clean_name and price > 0:
                items.append({
                    'name': clean_name,
                    'price': price,
                    'quantity': quantity,
                    'raw_line': line
                })
    
    return items

def estimate_co2_from_items(items: List[Dict]) -> Dict:
    """
    Estimate CO2 emissions from receipt items
    
    Args:
        items: List of items from receipt
        
    Returns:
        Dictionary with CO2 analysis
    """
    
    # CO2 emission factors (kg CO2 per kg of product)
    CO2_FACTORS = {
        # Meat (as requested: beef=20kgCO2/kg)
        'beef': 20.0,
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
        
        # Dairy
        'milk': 3.2,
        'cheese': 13.5,
        'butter': 9.0,
        'yogurt': 2.2,
        
        # Vegetables & Fruits
        'tomatoes': 2.1,
        'potatoes': 0.5,
        'carrots': 0.4,
        'lettuce': 1.3,
        'apples': 0.4,
        'bananas': 0.9,
        
        # Grains
        'bread': 0.9,
        'rice': 2.7,
        'pasta': 1.1,
        
        # Beverages
        'coffee': 4.9,
        'beer': 0.7,
        'wine': 1.3,
    }
    
    # Typical prices per kg (for weight estimation)
    PRICE_PER_KG = {
        'beef': 15.0, 'pork': 10.0, 'chicken': 8.0, 'fish': 18.0,
        'milk': 1.5, 'cheese': 12.0, 'bread': 4.0,
        'vegetables': 3.0, 'fruits': 4.0, 'rice': 2.0
    }
    
    results = {
        'total_co2_kg': 0.0,
        'items_analyzed': [],
        'unmatched_items': []
    }
    
    for item in items:
        item_name = item['name'].lower()
        price = item['price']
        quantity = item['quantity']
        
        # Find CO2 factor
        co2_factor = 0.0
        matched_product = None
        
        for product, factor in CO2_FACTORS.items():
            if product in item_name:
                co2_factor = factor
                matched_product = product
                break
        
        if co2_factor > 0:
            # Estimate weight from price
            price_per_kg = PRICE_PER_KG.get(matched_product, 5.0)
            estimated_weight_kg = (price / price_per_kg) * quantity
            
            # Calculate CO2
            co2_kg = estimated_weight_kg * co2_factor
            
            results['items_analyzed'].append({
                'name': item['name'],
                'matched_product': matched_product,
                'price': price,
                'estimated_weight_kg': round(estimated_weight_kg, 2),
                'co2_factor': co2_factor,
                'co2_kg': round(co2_kg, 3),
                'co2_g': round(co2_kg * 1000, 1)
            })
            
            results['total_co2_kg'] += co2_kg
        else:
            results['unmatched_items'].append(item['name'])
    
    results['total_co2_kg'] = round(results['total_co2_kg'], 3)
    return results

def print_co2_analysis(items: List[Dict], co2_results: Dict) -> None:
    """Print formatted CO2 analysis"""
    
    print("🧾 RECEIPT CO2 ANALYSIS")
    print("=" * 50)
    
    print(f"📝 Total items: {len(items)}")
    print(f"✅ Items analyzed: {len(co2_results['items_analyzed'])}")
    print(f"❓ Unmatched items: {len(co2_results['unmatched_items'])}")
    print(f"🌿 Total CO2: {co2_results['total_co2_kg']} kg ({co2_results['total_co2_kg']*1000:.0f}g)")
    
    print(f"\n📊 ITEM BREAKDOWN:")
    print("-" * 50)
    print(f"{'Item':<15} {'Product':<12} {'Weight':<8} {'CO2':<10}")
    print("-" * 50)
    
    for item in co2_results['items_analyzed']:
        print(f"{item['name'][:14]:<15} "
              f"{item['matched_product'][:11]:<12} "
              f"{item['estimated_weight_kg']:<7.2f}kg "
              f"{item['co2_g']:<9.1f}g")
    
    if co2_results['unmatched_items']:
        print(f"\n❓ UNMATCHED ITEMS:")
        for item in co2_results['unmatched_items']:
            print(f"   • {item}")
    
    # CO2 equivalents
    total_co2 = co2_results['total_co2_kg']
    if total_co2 > 0:
        print(f"\n🌍 CO2 EQUIVALENTS:")
        km_driven = total_co2 / 0.21  # 210g CO2/km
        print(f"   🚗 Driving: {km_driven:.1f} km")
        print(f"   📱 Phone charges: {total_co2 / 0.008:.0f}")

def demo_receipt_analysis():
    """Demo with sample receipt text"""
    
    sample_receipt = """
    GROCERY STORE
    2024-01-15
    
    Ground Beef 1lb        $12.99
    Chicken Breast         $8.49
    Milk 1gal             $3.29
    Whole Wheat Bread     $2.49
    Bananas 2lb           $1.89
    Cheddar Cheese        $4.99
    Tomatoes 1.5lb        $3.49
    
    Subtotal              $37.63
    Tax                   $2.26
    Total                 $39.89
    """
    
    print("🔍 DEMO: Analyzing sample receipt")
    print("Receipt text:")
    print(sample_receipt)
    
    # Extract items
    items = extract_receipt_items(sample_receipt)
    
    # Estimate CO2
    co2_results = estimate_co2_from_items(items)
    
    # Print analysis
    print_co2_analysis(items, co2_results)
    
    return items, co2_results

def analyze_receipt_file(file_path: str) -> Tuple[List[Dict], Dict]:
    """
    Analyze receipt from text file
    
    Args:
        file_path: Path to text file containing receipt text
        
    Returns:
        Tuple of (items, co2_results)
    """
    
    try:
        with open(file_path, 'r') as f:
            receipt_text = f.read()
        
        print(f"🔍 Analyzing receipt from: {file_path}")
        
        items = extract_receipt_items(receipt_text)
        co2_results = estimate_co2_from_items(items)
        
        print_co2_analysis(items, co2_results)
        
        return items, co2_results
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return [], {}
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return [], {}

# Main execution
if __name__ == "__main__":
    import sys
    
    print("🧾 Simple Receipt CO2 Estimator")
    print("Using emission factors like beef=20kgCO2/kg")
    print()
    
    if len(sys.argv) > 1:
        # Analyze file provided as argument
        file_path = sys.argv[1]
        analyze_receipt_file(file_path)
    else:
        # Run demo
        demo_receipt_analysis()
    
    print(f"\n💡 Usage:")
    print(f"   python3 simple_receipt_co2.py receipt.txt")
    print(f"   # Or run without arguments for demo")
    
    print(f"\n🔬 CO2 Factors Used:")
    print(f"   • Beef: 20 kg CO2/kg (as requested)")
    print(f"   • Chicken: 6.9 kg CO2/kg")
    print(f"   • Milk: 3.2 kg CO2/kg")
    print(f"   • Cheese: 13.5 kg CO2/kg")
    print(f"   • And many more...")
