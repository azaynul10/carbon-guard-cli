#!/usr/bin/env python3
"""
Receipt Image Handler - Process receipt images for CO2 estimation
Handles both image files (with OCR) and text files
"""

import os
from simple_receipt_co2 import extract_receipt_items, estimate_co2_from_items, print_co2_analysis

# Try to import OCR libraries
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def process_receipt_image(image_path: str):
    """
    Process receipt image and estimate CO2 emissions
    
    Args:
        image_path: Path to receipt image file
    """
    
    if not OCR_AVAILABLE:
        print("❌ OCR libraries not available")
        print("📦 Install with: pip install pillow pytesseract")
        print("🔧 Also install tesseract-ocr system package")
        return None
    
    try:
        print(f"🔍 Processing receipt image: {image_path}")
        
        # Load and preprocess image
        image = Image.open(image_path)
        print(f"📷 Image size: {image.size}")
        
        # Convert to grayscale for better OCR
        if image.mode != 'L':
            image = image.convert('L')
            print("🔄 Converted to grayscale")
        
        # Extract text using OCR
        print("🔤 Extracting text with OCR...")
        text = pytesseract.image_to_string(image)
        
        print("📝 Extracted text:")
        print("-" * 40)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("-" * 40)
        
        # Parse items and estimate CO2
        items = extract_receipt_items(text)
        co2_results = estimate_co2_from_items(items)
        
        # Print analysis
        print_co2_analysis(items, co2_results)
        
        return {
            'items': items,
            'co2_results': co2_results,
            'raw_text': text
        }
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None

def process_receipt_file(file_path: str):
    """
    Process receipt file (image or text) and estimate CO2
    
    Args:
        file_path: Path to receipt file
    """
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    # Get file extension
    _, ext = os.path.splitext(file_path.lower())
    
    # Handle different file types
    if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        # Image file - use OCR
        return process_receipt_image(file_path)
    
    elif ext in ['.txt', '.text']:
        # Text file - read directly
        try:
            with open(file_path, 'r') as f:
                text = f.read()
            
            print(f"📄 Processing text file: {file_path}")
            
            items = extract_receipt_items(text)
            co2_results = estimate_co2_from_items(items)
            
            print_co2_analysis(items, co2_results)
            
            return {
                'items': items,
                'co2_results': co2_results,
                'raw_text': text
            }
            
        except Exception as e:
            print(f"❌ Error reading text file: {e}")
            return None
    
    else:
        print(f"❌ Unsupported file type: {ext}")
        print("✅ Supported formats: .jpg, .jpeg, .png, .bmp, .tiff, .txt")
        return None

def demo_receipt_processing():
    """Demo receipt processing capabilities"""
    
    print("🧾 Receipt Processing Demo")
    print("=" * 40)
    
    print(f"📦 OCR Available: {'✅ Yes' if OCR_AVAILABLE else '❌ No'}")
    
    if OCR_AVAILABLE:
        print("🔤 Can process image files: .jpg, .jpeg, .png, .bmp, .tiff")
    else:
        print("📝 Can only process text files: .txt")
        print("💡 To enable image processing:")
        print("   pip install pillow pytesseract")
        print("   # Also install tesseract-ocr system package")
    
    print("\n📄 Supported text file formats: .txt")
    
    # Show sample usage
    print(f"\n💡 Usage Examples:")
    print(f"   python3 receipt_image_handler.py receipt.jpg")
    print(f"   python3 receipt_image_handler.py receipt.txt")
    
    # Process sample text file if it exists
    if os.path.exists('sample_receipt.txt'):
        print(f"\n🔍 Processing sample_receipt.txt...")
        result = process_receipt_file('sample_receipt.txt')
        if result:
            total_co2 = result['co2_results']['total_co2_kg']
            print(f"\n✅ Sample analysis complete!")
            print(f"🌿 Total CO2: {total_co2} kg")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Process file provided as argument
        file_path = sys.argv[1]
        
        print("🧾 Receipt CO2 Estimator")
        print(f"Using emission factors like beef=20kgCO2/kg")
        print()
        
        result = process_receipt_file(file_path)
        
        if result:
            print(f"\n✅ Processing complete!")
            total_co2 = result['co2_results']['total_co2_kg']
            items_count = len(result['items'])
            print(f"📊 {items_count} items analyzed")
            print(f"🌿 Total CO2: {total_co2} kg ({total_co2*1000:.0f}g)")
            
            # Save results
            import json
            output_file = f"{os.path.splitext(file_path)[0]}_co2_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"💾 Results saved to: {output_file}")
    
    else:
        # Run demo
        demo_receipt_processing()
