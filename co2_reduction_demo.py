#!/usr/bin/env python3
"""
CO2 Reduction Planning Demo
Demonstrates generating reduction plans and exporting anonymized data to CSV
"""

import json
import os
from datetime import datetime
from typing import List
from co2_reduction_planner import CO2ReductionPlanner
from anonymized_csv_exporter import AnonymizedCSVExporter

def create_sample_audit_data():
    """Create sample audit data for demonstration"""
    
    # Ensure carbon_data directory exists
    os.makedirs('carbon_data', exist_ok=True)
    
    # Sample AWS audit data
    aws_audit = {
        'service': 'ec2',
        'region': 'us-east-1',
        'total_instances': 5,
        'co2_kg_per_hour': 2.5,
        'estimated_cost_usd': 15.75,
        'audit_timestamp': datetime.now().isoformat(),
        'instances': [
            {'instance_id': 'i-1234567890abcdef0', 'instance_type': 'm5.large'},
            {'instance_id': 'i-0987654321fedcba0', 'instance_type': 't3.medium'},
            {'instance_id': 'i-abcdef1234567890', 'instance_type': 'c5.xlarge'}
        ]
    }
    
    with open('carbon_data/aws_audit_demo.json', 'w') as f:
        json.dump(aws_audit, f, indent=2)
    
    # Sample local audit data
    local_audit = {
        'script_path': 'ml_training_script.py',
        'execution_duration_seconds': 3600,
        'total_co2_kg': 0.125,
        'total_energy_kwh': 0.25,
        'avg_cpu_percent': 85.5,
        'peak_memory_mb': 2048,
        'execution_successful': True,
        'audit_timestamp': datetime.now().isoformat()
    }
    
    with open('carbon_data/local_audit_demo.json', 'w') as f:
        json.dump(local_audit, f, indent=2)
    
    # Sample personal audit data
    personal_audit = {
        'summary': {
            'total_receipts': 3,
            'total_co2_kg': 45.2,
            'category_breakdown': {
                'beef': 25.8,
                'chicken': 8.4,
                'dairy': 6.2,
                'vegetables': 2.1,
                'transport': 2.7
            }
        },
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    with open('carbon_data/personal_audit_demo.json', 'w') as f:
        json.dump(personal_audit, f, indent=2)
    
    print("✅ Sample audit data created in carbon_data/")

def demo_reduction_planning():
    """Demonstrate CO2 reduction plan generation"""
    
    print("🌍 CO2 REDUCTION PLANNING DEMO")
    print("=" * 50)
    
    # Create planner
    planner = CO2ReductionPlanner()
    
    # Generate different types of plans
    plans = []
    
    # 1. AWS-focused plan
    print("\n🔍 Generating AWS-focused reduction plan...")
    aws_plan = planner.generate_reduction_plan(
        target_reduction=30.0,
        timeframe_months=6,
        focus_areas=['aws']
    )
    plans.append(('AWS Plan', aws_plan))
    
    # 2. Personal lifestyle plan
    print("🔍 Generating personal lifestyle plan...")
    personal_plan = planner.generate_reduction_plan(
        target_reduction=25.0,
        timeframe_months=12,
        focus_areas=['personal']
    )
    plans.append(('Personal Plan', personal_plan))
    
    # 3. Comprehensive plan
    print("🔍 Generating comprehensive plan...")
    comprehensive_plan = planner.generate_reduction_plan(
        target_reduction=35.0,
        timeframe_months=9,
        focus_areas=['aws', 'personal', 'dev']
    )
    plans.append(('Comprehensive Plan', comprehensive_plan))
    
    # Display and save plans
    for plan_name, plan in plans:
        print(f"\n{'='*20} {plan_name.upper()} {'='*20}")
        planner.print_reduction_plan(plan)
        
        # Save plan
        plan_file = planner.save_plan(plan, f"carbon_data/{plan['plan_id']}.json")
        print(f"💾 {plan_name} saved to: {plan_file}")
    
    return plans

def demo_csv_export():
    """Demonstrate anonymized CSV export"""
    
    print("\n📊 ANONYMIZED CSV EXPORT DEMO")
    print("=" * 50)
    
    # Create exporter
    exporter = AnonymizedCSVExporter()
    
    # Export all data
    exported_files = exporter.export_all_data(
        output_prefix='demo_carbon_export',
        data_directory='carbon_data'
    )
    
    print(f"\n📁 Exported Files:")
    for file_path in exported_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   📄 {file_path} ({size:,} bytes)")
    
    # Show sample of exported data
    if exported_files:
        print(f"\n🔍 Sample of exported data:")
        sample_file = [f for f in exported_files if 'summary' in f][0]
        
        print(f"📋 Contents of {sample_file}:")
        with open(sample_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:5]):  # Show first 5 lines
                print(f"   {i+1}: {line.strip()}")
        
        if len(lines) > 5:
            print(f"   ... and {len(lines)-5} more rows")
    
    return exported_files

def show_key_recommendations():
    """Show key CO2 reduction recommendations"""
    
    print("\n🎯 KEY CO2 REDUCTION RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = [
        {
            'category': 'AWS Infrastructure',
            'actions': [
                'Use Graviton instances (20% CO2 reduction)',
                'Implement auto-scaling (25% reduction)',
                'Right-size instances (15% reduction)',
                'Optimize S3 storage classes (12% reduction)'
            ]
        },
        {
            'category': 'Personal Lifestyle',
            'actions': [
                'Eat plant-based (40% reduction)',
                'Optimize transportation (35% reduction)',
                'Reduce energy consumption (20% reduction)',
                'Buy local and seasonal (15% reduction)'
            ]
        },
        {
            'category': 'Development Practices',
            'actions': [
                'Optimize algorithms (30% reduction)',
                'Implement caching (20% reduction)',
                'Optimize database queries (15% reduction)'
            ]
        }
    ]
    
    for rec in recommendations:
        print(f"\n📋 {rec['category']}:")
        for action in rec['actions']:
            print(f"   • {action}")
    
    print(f"\n💡 Implementation Tips:")
    print(f"   🚀 Start with quick wins (low effort, high impact)")
    print(f"   📊 Monitor progress monthly")
    print(f"   🎯 Set realistic targets (20-30% reduction)")
    print(f"   👥 Get team/family buy-in")
    print(f"   📈 Track both CO2 and cost savings")

def analyze_export_data(exported_files: List[str]):
    """Analyze the exported CSV data"""
    
    print(f"\n📈 EXPORT DATA ANALYSIS")
    print("=" * 50)
    
    import csv
    
    # Analyze summary file
    summary_file = [f for f in exported_files if 'summary' in f]
    if summary_file:
        print(f"📊 Summary Statistics:")
        
        with open(summary_file[0], 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = row['metric_category']
                metric = row['metric_name']
                value = row['value']
                unit = row['unit']
                points = row['data_points']
                
                print(f"   {category.upper()}: {metric} = {value} {unit} ({points} data points)")
    
    # Count total records across all files
    total_records = 0
    for file_path in exported_files:
        if file_path.endswith('.csv') and 'key' not in file_path:
            try:
                with open(file_path, 'r') as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for row in reader) - 1  # Subtract header
                    total_records += row_count
                    print(f"   📄 {os.path.basename(file_path)}: {row_count} records")
            except Exception as e:
                print(f"   ⚠️  Could not read {file_path}: {e}")
    
    print(f"\n📊 Total anonymized records exported: {total_records}")
    print(f"🔐 All personal identifiers have been anonymized")
    print(f"📈 Data ready for analysis and reporting")

def main():
    """Main demo function"""
    
    print("🌍 CARBON GUARD: CO2 REDUCTION PLANNING & EXPORT DEMO")
    print("=" * 60)
    print("This demo shows:")
    print("• CO2 reduction plan generation with specific actions")
    print("• Anonymized data export to CSV for analysis")
    print("• Key recommendations like 'Use Graviton instances' and 'Eat plant-based'")
    print()
    
    # Step 1: Create sample data
    print("📁 Step 1: Creating sample audit data...")
    create_sample_audit_data()
    
    # Step 2: Generate reduction plans
    print("\n🎯 Step 2: Generating CO2 reduction plans...")
    plans = demo_reduction_planning()
    
    # Step 3: Export to CSV
    print("\n📊 Step 3: Exporting anonymized data to CSV...")
    exported_files = demo_csv_export()
    
    # Step 4: Show key recommendations
    show_key_recommendations()
    
    # Step 5: Analyze exported data
    analyze_export_data(exported_files)
    
    # Summary
    print(f"\n✅ DEMO COMPLETE!")
    print(f"📋 Generated {len(plans)} reduction plans")
    print(f"📁 Exported {len(exported_files)} CSV files")
    print(f"🔐 All data anonymized for privacy")
    print(f"🌿 Ready to implement CO2 reduction strategies!")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Review generated reduction plans")
    print(f"   2. Prioritize actions by impact/effort ratio")
    print(f"   3. Start with quick wins (e.g., right-sizing instances)")
    print(f"   4. Use CSV exports for progress tracking")
    print(f"   5. Monitor CO2 reductions monthly")

if __name__ == "__main__":
    main()
