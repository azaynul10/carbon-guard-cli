#!/usr/bin/env python3
"""
Demo EC2 CO2 Calculator - Shows how the calculation works with sample data
"""

import json


def demo_ec2_co2_calculation():
    """Demonstrate EC2 CO2 calculation with sample data"""

    # Configuration
    REGION = "us-east-1"
    CARBON_INTENSITY = 0.3  # 300g/kWh = 0.3 kg/kWh
    DAYS_ANALYZED = 7

    # Sample EC2 instances (simulating real data)
    sample_instances = [
        {
            "id": "i-1234567890abcdef0",
            "type": "t3.medium",
            "hours": 168,
        },  # 7 days * 24 hours
        {
            "id": "i-0987654321fedcba0",
            "type": "m5.large",
            "hours": 120,
        },  # Partial uptime
        {"id": "i-abcdef1234567890", "type": "c5.xlarge", "hours": 84},  # 3.5 days
        {"id": "i-fedcba0987654321", "type": "r5.2xlarge", "hours": 168},  # Full week
        {
            "id": "i-1111222233334444",
            "type": "t2.micro",
            "hours": 168,
        },  # Always-on small instance
    ]

    # Power consumption estimates (watts)
    power_consumption = {
        "t2.micro": 10,
        "t2.small": 20,
        "t2.medium": 40,
        "t2.large": 80,
        "t3.micro": 10,
        "t3.small": 20,
        "t3.medium": 40,
        "t3.large": 80,
        "m5.large": 80,
        "m5.xlarge": 160,
        "m5.2xlarge": 320,
        "c5.large": 70,
        "c5.xlarge": 140,
        "c5.2xlarge": 280,
        "r5.large": 90,
        "r5.xlarge": 180,
        "r5.2xlarge": 360,
    }

    print("🌍 EC2 CO2 EMISSIONS CALCULATOR DEMO")
    print("=" * 50)
    print(f"📍 Region: {REGION}")
    print(f"📅 Analysis Period: {DAYS_ANALYZED} days")
    print(f"🔬 Carbon Intensity: {CARBON_INTENSITY} kg CO2/kWh (300g/kWh)")
    print(f"🖥️  Sample Instances: {len(sample_instances)}")
    print()

    # Calculate emissions for each instance
    results = []
    total_energy_kwh = 0
    total_co2_kg = 0

    print("📊 INSTANCE ANALYSIS:")
    print("-" * 80)
    print(
        f"{'Instance ID':<20} {'Type':<12} {'Hours':<8} {'Power':<8} {'Energy':<10} {'CO2 (g)':<10}"
    )
    print("-" * 80)

    for instance in sample_instances:
        instance_id = instance["id"]
        instance_type = instance["type"]
        running_hours = instance["hours"]

        # Get power consumption (default 50W if unknown)
        power_watts = power_consumption.get(instance_type, 50)

        # Calculate energy consumption
        energy_kwh = (power_watts / 1000) * running_hours

        # Calculate CO2 emissions
        co2_kg = energy_kwh * CARBON_INTENSITY
        co2_g = co2_kg * 1000

        # Store results
        result = {
            "instance_id": instance_id,
            "instance_type": instance_type,
            "running_hours": running_hours,
            "power_watts": power_watts,
            "energy_kwh": energy_kwh,
            "co2_kg": co2_kg,
            "co2_g": co2_g,
        }
        results.append(result)

        # Update totals
        total_energy_kwh += energy_kwh
        total_co2_kg += co2_kg

        # Print row
        print(
            f"{instance_id:<20} {instance_type:<12} {running_hours:<8.1f} "
            f"{power_watts:<8}W {energy_kwh:<10.2f} {co2_g:<10.1f}"
        )

    print("-" * 80)
    print(
        f"{'TOTALS':<20} {'':<12} {sum(i['hours'] for i in sample_instances):<8.1f} "
        f"{'':<8} {total_energy_kwh:<10.2f} {total_co2_kg * 1000:<10.1f}"
    )

    # Summary statistics
    print(f"\n📈 SUMMARY STATISTICS:")
    print(f"   🏭 Total Instances: {len(sample_instances)}")
    print(f"   ⚡ Total Energy Consumed: {total_energy_kwh:.2f} kWh")
    print(
        f"   🌿 Total CO2 Emissions: {total_co2_kg:.3f} kg ({total_co2_kg * 1000:.1f}g)"
    )
    print(f"   📊 Average per Instance: {total_co2_kg / len(sample_instances):.3f} kg")
    print(f"   📅 Average per Day: {total_co2_kg / DAYS_ANALYZED:.3f} kg/day")
    print(
        f"   💰 Estimated Monthly CO2: {total_co2_kg * 30 / DAYS_ANALYZED:.3f} kg/month"
    )

    # CO2 equivalents for context
    print(f"\n🌍 CO2 EQUIVALENTS:")
    km_driven = total_co2_kg / 0.21  # 210g CO2/km for average car
    print(f"   🚗 Equivalent to driving: {km_driven:.1f} km")

    flights_domestic = total_co2_kg / 250  # ~250kg CO2 for domestic flight
    print(f"   ✈️  Equivalent to: {flights_domestic:.2f} domestic flights")

    trees_needed = total_co2_kg / 21.77  # One tree absorbs ~22kg CO2/year
    print(f"   🌳 Trees needed (1 year): {trees_needed:.2f}")

    # Cost implications (rough estimates)
    print(f"\n💰 COST IMPLICATIONS:")
    carbon_tax_10_per_ton = total_co2_kg * 10 / 1000  # $10/ton CO2
    carbon_tax_50_per_ton = total_co2_kg * 50 / 1000  # $50/ton CO2
    print(f"   💸 Carbon tax @ $10/ton: ${carbon_tax_10_per_ton:.2f}")
    print(f"   💸 Carbon tax @ $50/ton: ${carbon_tax_50_per_ton:.2f}")

    # Optimization suggestions
    print(f"\n🔧 OPTIMIZATION SUGGESTIONS:")

    # Find highest emitters
    sorted_results = sorted(results, key=lambda x: x["co2_kg"], reverse=True)
    highest_emitter = sorted_results[0]

    print(
        f"   🎯 Highest emitter: {highest_emitter['instance_id']} ({highest_emitter['instance_type']})"
    )
    print(
        f"      - Emits {highest_emitter['co2_g']:.1f}g CO2 ({highest_emitter['co2_kg']/total_co2_kg*100:.1f}% of total)"
    )
    print(f"      - Consider right-sizing or scheduling")

    # Calculate potential savings
    potential_savings = total_co2_kg * 0.2  # 20% reduction
    print(f"   📉 20% reduction potential: {potential_savings:.3f} kg CO2 saved")
    print(f"   💡 Strategies: Auto-scaling, right-sizing, scheduling, ARM instances")

    return {
        "region": REGION,
        "days_analyzed": DAYS_ANALYZED,
        "carbon_intensity_kg_per_kwh": CARBON_INTENSITY,
        "total_instances": len(sample_instances),
        "total_energy_kwh": total_energy_kwh,
        "total_co2_kg": total_co2_kg,
        "daily_average_kg": total_co2_kg / DAYS_ANALYZED,
        "instances": results,
        "equivalents": {
            "km_driven": km_driven,
            "domestic_flights": flights_domestic,
            "trees_needed_1_year": trees_needed,
        },
    }


def save_demo_results(results, filename="demo_ec2_co2_results.json"):
    """Save demo results to JSON file"""
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Demo results saved to: {filename}")


if __name__ == "__main__":
    print("🚀 Running EC2 CO2 Calculator Demo...")
    print("   (This demo uses sample data - no AWS credentials required)")
    print()

    results = demo_ec2_co2_calculation()
    save_demo_results(results)

    print(f"\n✅ Demo complete!")
    print(
        f"🌿 Key takeaway: {results['total_co2_kg']:.3f} kg CO2 from {results['total_instances']} instances over {results['days_analyzed']} days"
    )
