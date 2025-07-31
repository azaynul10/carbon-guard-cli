#!/usr/bin/env python3
"""
CO2 Reduction Plan Generator
Analyzes audit data and generates actionable reduction plans with specific recommendations
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List


class CO2ReductionPlanner:
    """Generates CO2 reduction plans based on audit data"""

    def __init__(self):
        # AWS-specific reduction actions
        self.aws_actions = [
            {
                "action": "Use Graviton instances",
                "description": "Migrate to ARM-based Graviton processors for better energy efficiency",
                "category": "infrastructure",
                "co2_reduction_percent": 20,
                "cost_impact": -15,  # Negative = cost savings
                "effort_level": "medium",
                "timeline_weeks": 4,
                "applicability": ["ec2", "rds"],
                "prerequisites": ["Application ARM compatibility check"],
                "implementation_steps": [
                    "Test application on Graviton instances",
                    "Update deployment scripts",
                    "Plan migration schedule",
                    "Execute gradual migration",
                    "Monitor performance metrics",
                ],
            },
            {
                "action": "Implement auto-scaling",
                "description": "Set up auto-scaling to match demand and reduce idle resources",
                "category": "optimization",
                "co2_reduction_percent": 25,
                "cost_impact": -30,
                "effort_level": "high",
                "timeline_weeks": 6,
                "applicability": ["ec2"],
                "prerequisites": [
                    "Load balancer setup",
                    "Application stateless design",
                ],
                "implementation_steps": [
                    "Create launch templates",
                    "Configure auto-scaling groups",
                    "Set up scaling policies",
                    "Test scaling behavior",
                    "Monitor and tune thresholds",
                ],
            },
            {
                "action": "Right-size instances",
                "description": "Optimize instance types based on actual usage patterns",
                "category": "optimization",
                "co2_reduction_percent": 15,
                "cost_impact": -25,
                "effort_level": "low",
                "timeline_weeks": 2,
                "applicability": ["ec2", "rds"],
                "prerequisites": ["CloudWatch monitoring data"],
                "implementation_steps": [
                    "Analyze CPU and memory utilization",
                    "Identify over-provisioned instances",
                    "Create rightsizing plan",
                    "Schedule maintenance windows",
                    "Execute instance type changes",
                ],
            },
            {
                "action": "Use Spot instances",
                "description": "Leverage Spot instances for fault-tolerant workloads",
                "category": "cost_optimization",
                "co2_reduction_percent": 10,
                "cost_impact": -60,
                "effort_level": "medium",
                "timeline_weeks": 3,
                "applicability": ["ec2"],
                "prerequisites": ["Fault-tolerant application design"],
                "implementation_steps": [
                    "Identify suitable workloads",
                    "Implement spot instance handling",
                    "Set up mixed instance types",
                    "Test interruption scenarios",
                    "Monitor cost and availability",
                ],
            },
            {
                "action": "Optimize S3 storage classes",
                "description": "Move infrequently accessed data to lower-carbon storage tiers",
                "category": "storage",
                "co2_reduction_percent": 12,
                "cost_impact": -40,
                "effort_level": "low",
                "timeline_weeks": 1,
                "applicability": ["s3"],
                "prerequisites": ["S3 access pattern analysis"],
                "implementation_steps": [
                    "Analyze object access patterns",
                    "Create lifecycle policies",
                    "Test data retrieval processes",
                    "Apply policies to buckets",
                    "Monitor storage costs and access",
                ],
            },
            {
                "action": "Schedule non-critical workloads",
                "description": "Run batch jobs during off-peak hours when grid is cleaner",
                "category": "scheduling",
                "co2_reduction_percent": 8,
                "cost_impact": -10,
                "effort_level": "medium",
                "timeline_weeks": 2,
                "applicability": ["ec2", "lambda"],
                "prerequisites": ["Workload scheduling system"],
                "implementation_steps": [
                    "Identify batch workloads",
                    "Analyze grid carbon intensity patterns",
                    "Create scheduling rules",
                    "Implement job scheduling",
                    "Monitor execution and carbon impact",
                ],
            },
        ]

        # Personal/lifestyle reduction actions
        self.personal_actions = [
            {
                "action": "Eat plant-based",
                "description": "Replace high-carbon meat with plant-based alternatives",
                "category": "diet",
                "co2_reduction_percent": 40,
                "cost_impact": -20,
                "effort_level": "medium",
                "timeline_weeks": 8,
                "applicability": ["food"],
                "prerequisites": ["Dietary flexibility"],
                "implementation_steps": [
                    "Research plant-based protein sources",
                    "Plan weekly meal menus",
                    "Try new recipes gradually",
                    "Track dietary changes",
                    "Monitor health and satisfaction",
                ],
            },
            {
                "action": "Reduce meat consumption",
                "description": 'Implement "Meatless Monday" and reduce portion sizes',
                "category": "diet",
                "co2_reduction_percent": 25,
                "cost_impact": -15,
                "effort_level": "low",
                "timeline_weeks": 4,
                "applicability": ["food"],
                "prerequisites": ["Willingness to change diet"],
                "implementation_steps": [
                    "Start with one meatless day per week",
                    "Reduce meat portion sizes",
                    "Explore meat alternatives",
                    "Track consumption changes",
                    "Gradually increase meatless days",
                ],
            },
            {
                "action": "Buy local and seasonal",
                "description": "Choose locally produced, seasonal foods to reduce transport emissions",
                "category": "consumption",
                "co2_reduction_percent": 15,
                "cost_impact": 0,
                "effort_level": "low",
                "timeline_weeks": 2,
                "applicability": ["food"],
                "prerequisites": ["Local markets available"],
                "implementation_steps": [
                    "Research local food sources",
                    "Learn seasonal food calendar",
                    "Plan shopping around local options",
                    "Try farmers markets",
                    "Track local food purchases",
                ],
            },
            {
                "action": "Optimize transportation",
                "description": "Use public transport, cycling, or walking more frequently",
                "category": "transport",
                "co2_reduction_percent": 35,
                "cost_impact": -100,
                "effort_level": "low",
                "timeline_weeks": 2,
                "applicability": ["transport"],
                "prerequisites": ["Alternative transport options"],
                "implementation_steps": [
                    "Map current transportation patterns",
                    "Identify alternative routes",
                    "Test public transport options",
                    "Plan combined trips",
                    "Track transportation changes",
                ],
            },
            {
                "action": "Reduce energy consumption",
                "description": "Implement energy-saving practices at home and office",
                "category": "energy",
                "co2_reduction_percent": 20,
                "cost_impact": -150,
                "effort_level": "low",
                "timeline_weeks": 1,
                "applicability": ["energy"],
                "prerequisites": ["Home energy audit"],
                "implementation_steps": [
                    "Conduct energy audit",
                    "Replace inefficient appliances",
                    "Improve insulation",
                    "Adjust thermostat settings",
                    "Monitor energy usage",
                ],
            },
        ]

        # Development/local optimization actions
        self.dev_actions = [
            {
                "action": "Optimize algorithms",
                "description": "Refactor code to reduce computational complexity and CPU usage",
                "category": "code",
                "co2_reduction_percent": 30,
                "cost_impact": 0,
                "effort_level": "high",
                "timeline_weeks": 6,
                "applicability": ["local"],
                "prerequisites": ["Code profiling completed"],
                "implementation_steps": [
                    "Profile application performance",
                    "Identify computational bottlenecks",
                    "Research more efficient algorithms",
                    "Implement optimizations",
                    "Test and validate improvements",
                ],
            },
            {
                "action": "Implement caching",
                "description": "Add caching layers to reduce redundant computations",
                "category": "performance",
                "co2_reduction_percent": 20,
                "cost_impact": 50,
                "effort_level": "medium",
                "timeline_weeks": 3,
                "applicability": ["local"],
                "prerequisites": ["Cache infrastructure"],
                "implementation_steps": [
                    "Identify cacheable operations",
                    "Choose appropriate caching strategy",
                    "Implement cache layer",
                    "Test cache hit rates",
                    "Monitor performance improvements",
                ],
            },
            {
                "action": "Optimize database queries",
                "description": "Improve database query efficiency and indexing",
                "category": "database",
                "co2_reduction_percent": 15,
                "cost_impact": 0,
                "effort_level": "medium",
                "timeline_weeks": 2,
                "applicability": ["local"],
                "prerequisites": ["Database access"],
                "implementation_steps": [
                    "Analyze slow query logs",
                    "Identify missing indexes",
                    "Optimize query structure",
                    "Add appropriate indexes",
                    "Monitor query performance",
                ],
            },
        ]

    def load_audit_data(self, data_directory: str = "carbon_data") -> Dict[str, Any]:
        """Load audit data from files"""

        audit_data = {
            "aws": [],
            "local": [],
            "personal": [],
            "total_co2_kg": 0,
            "data_sources": [],
        }

        if not os.path.exists(data_directory):
            return audit_data

        # Load JSON files from data directory
        for filename in os.listdir(data_directory):
            if filename.endswith(".json"):
                filepath = os.path.join(data_directory, filename)
                try:
                    with open(filepath) as f:
                        data = json.load(f)

                    # Categorize data based on content
                    if "service" in data or any(
                        service in data for service in ["ec2", "rds", "lambda", "s3"]
                    ):
                        audit_data["aws"].append(data)
                        audit_data["total_co2_kg"] += (
                            data.get("co2_kg_per_hour", 0) * 24 * 30
                        )  # Monthly estimate
                    elif "script_path" in data or "total_co2_kg" in data:
                        audit_data["local"].append(data)
                        audit_data["total_co2_kg"] += data.get("total_co2_kg", 0)
                    elif "receipts" in data or "items" in data:
                        audit_data["personal"].append(data)
                        if "summary" in data:
                            audit_data["total_co2_kg"] += data["summary"].get(
                                "total_co2_kg", 0
                            )
                        elif "total_co2_kg" in data:
                            audit_data["total_co2_kg"] += data["total_co2_kg"]

                    audit_data["data_sources"].append(filename)

                except Exception as e:
                    print(f"⚠️  Could not load {filename}: {e}")

        return audit_data

    def generate_reduction_plan(
        self,
        target_reduction: float = 20.0,
        timeframe_months: int = 12,
        focus_areas: List[str] = None,
    ) -> Dict[str, Any]:
        """Generate a CO2 reduction plan based on audit data"""

        if focus_areas is None:
            focus_areas = ["aws", "personal", "dev"]

        # Load audit data
        audit_data = self.load_audit_data()

        # Select applicable actions
        available_actions = []

        if "aws" in focus_areas and audit_data["aws"]:
            available_actions.extend(self.aws_actions)

        if "personal" in focus_areas and audit_data["personal"]:
            available_actions.extend(self.personal_actions)

        if "dev" in focus_areas and audit_data["local"]:
            available_actions.extend(self.dev_actions)

        # If no audit data, provide general recommendations
        if not audit_data["data_sources"]:
            available_actions = (
                self.aws_actions + self.personal_actions + self.dev_actions
            )

        # Score and select actions
        selected_actions = self._select_optimal_actions(
            available_actions, target_reduction, timeframe_months
        )

        # Create implementation timeline
        timeline = self._create_implementation_timeline(
            selected_actions, timeframe_months
        )

        # Calculate plan metrics
        plan_metrics = self._calculate_plan_metrics(selected_actions, audit_data)

        plan = {
            "plan_id": self._generate_plan_id(),
            "created_at": datetime.now().isoformat(),
            "target_reduction_percent": target_reduction,
            "timeframe_months": timeframe_months,
            "focus_areas": focus_areas,
            "baseline_data": {
                "total_co2_kg": audit_data["total_co2_kg"],
                "aws_sources": len(audit_data["aws"]),
                "local_sources": len(audit_data["local"]),
                "personal_sources": len(audit_data["personal"]),
                "data_sources": audit_data["data_sources"],
            },
            "selected_actions": selected_actions,
            "implementation_timeline": timeline,
            "estimated_metrics": plan_metrics,
            "success_factors": self._identify_success_factors(selected_actions),
            "monitoring_plan": self._create_monitoring_plan(selected_actions),
        }

        return plan

    def _select_optimal_actions(
        self,
        available_actions: List[Dict],
        target_reduction: float,
        timeframe_months: int,
    ) -> List[Dict]:
        """Select optimal actions to meet target reduction"""

        # Score actions based on impact/effort ratio and timeline fit
        scored_actions = []

        for action in available_actions:
            effort_score = {"low": 1, "medium": 2, "high": 3}[action["effort_level"]]
            timeline_fit = (
                1.0 if action["timeline_weeks"] <= timeframe_months * 4 else 0.5
            )

            # Calculate impact/effort ratio
            impact_effort_ratio = (
                action["co2_reduction_percent"] / effort_score
            ) * timeline_fit

            scored_actions.append((impact_effort_ratio, action))

        # Sort by score (highest first)
        scored_actions.sort(key=lambda x: x[0], reverse=True)

        # Select actions until target is met
        selected_actions = []
        cumulative_reduction = 0.0

        for score, action in scored_actions:
            if cumulative_reduction < target_reduction:
                selected_actions.append(action)
                # Use diminishing returns for cumulative calculation
                additional_reduction = action["co2_reduction_percent"] * (
                    1 - cumulative_reduction / 100
                )
                cumulative_reduction += additional_reduction

            if cumulative_reduction >= target_reduction * 1.2:  # Stop at 120% of target
                break

        return selected_actions

    def _create_implementation_timeline(
        self, actions: List[Dict], timeframe_months: int
    ) -> Dict[str, Any]:
        """Create implementation timeline for selected actions"""

        timeline = {
            "total_duration_months": timeframe_months,
            "phases": [],
            "milestones": [],
        }

        # Sort actions by timeline (quick wins first)
        sorted_actions = sorted(
            actions, key=lambda x: (x["timeline_weeks"], x["effort_level"])
        )

        current_week = 0
        phase_num = 1

        for action in sorted_actions:
            phase = {
                "phase_number": phase_num,
                "start_week": current_week,
                "end_week": current_week + action["timeline_weeks"],
                "action_title": action["action"],
                "category": action["category"],
                "expected_reduction": action["co2_reduction_percent"],
                "deliverables": action["implementation_steps"],
                "prerequisites": action["prerequisites"],
            }

            timeline["phases"].append(phase)

            # Add milestone
            milestone = {
                "week": current_week + action["timeline_weeks"],
                "title": f"Complete: {action['action']}",
                "expected_co2_reduction": action["co2_reduction_percent"],
                "success_criteria": f"Achieve {action['co2_reduction_percent']}% reduction in {action['category']}",
            }
            timeline["milestones"].append(milestone)

            current_week += action["timeline_weeks"]
            phase_num += 1

        return timeline

    def _calculate_plan_metrics(
        self, actions: List[Dict], audit_data: Dict
    ) -> Dict[str, Any]:
        """Calculate overall plan metrics"""

        total_reduction = sum(action["co2_reduction_percent"] for action in actions)
        total_cost_impact = sum(action["cost_impact"] for action in actions)

        # Calculate complexity score
        effort_scores = {"low": 1, "medium": 2, "high": 3}
        avg_complexity = (
            sum(effort_scores[action["effort_level"]] for action in actions)
            / len(actions)
            if actions
            else 0
        )

        # Estimate success probability
        complexity_factor = max(0.3, 1.0 - (avg_complexity - 1) * 0.2)
        timeline_factor = max(0.5, 1.0 - len(actions) * 0.05)
        success_probability = complexity_factor * timeline_factor

        # Calculate absolute CO2 savings
        baseline_co2 = audit_data["total_co2_kg"]
        estimated_co2_savings = (
            baseline_co2 * (total_reduction / 100) if baseline_co2 > 0 else 0
        )

        return {
            "total_reduction_percent": min(total_reduction, 80),  # Cap at 80%
            "estimated_co2_savings_kg": estimated_co2_savings,
            "total_cost_impact_usd": total_cost_impact,
            "average_complexity": avg_complexity,
            "success_probability": success_probability,
            "actions_count": len(actions),
            "implementation_duration_weeks": sum(
                action["timeline_weeks"] for action in actions
            ),
            "categories_covered": list({action["category"] for action in actions}),
        }

    def _identify_success_factors(self, actions: List[Dict]) -> List[str]:
        """Identify key success factors for the plan"""

        factors = [
            "Regular monitoring and measurement of CO2 reductions",
            "Strong leadership commitment and resource allocation",
            "Clear communication of environmental goals to all stakeholders",
        ]

        # Add action-specific factors
        categories = {action["category"] for action in actions}

        if "infrastructure" in categories:
            factors.append("Technical expertise in cloud infrastructure management")

        if "diet" in categories:
            factors.append("Gradual dietary changes with family/team support")

        if "code" in categories:
            factors.append("Development team training on efficient coding practices")

        if len(actions) > 5:
            factors.append("Phased implementation to avoid overwhelming changes")

        return factors

    def _create_monitoring_plan(self, actions: List[Dict]) -> Dict[str, Any]:
        """Create monitoring plan for tracking progress"""

        monitoring_plan = {
            "frequency": "monthly",
            "key_metrics": [
                "Total CO2 emissions (kg)",
                "CO2 reduction percentage vs baseline",
                "Cost savings achieved",
                "Actions completed vs planned",
            ],
            "monitoring_methods": {},
            "reporting_schedule": [
                {
                    "frequency": "weekly",
                    "audience": "implementation_team",
                    "format": "status_update",
                },
                {
                    "frequency": "monthly",
                    "audience": "management",
                    "format": "dashboard",
                },
                {
                    "frequency": "quarterly",
                    "audience": "stakeholders",
                    "format": "detailed_report",
                },
            ],
        }

        # Add category-specific monitoring
        categories = {action["category"] for action in actions}

        if "infrastructure" in categories:
            monitoring_plan["monitoring_methods"][
                "aws"
            ] = "CloudWatch metrics and cost reports"

        if "diet" in categories:
            monitoring_plan["monitoring_methods"][
                "personal"
            ] = "Receipt tracking and food diary"

        if "code" in categories:
            monitoring_plan["monitoring_methods"][
                "development"
            ] = "Performance profiling and energy monitoring"

        return monitoring_plan

    def _generate_plan_id(self) -> str:
        """Generate unique plan ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"co2_plan_{timestamp}"

    def print_reduction_plan(self, plan: Dict[str, Any]) -> None:
        """Print formatted reduction plan"""

        print("🌍 CO2 REDUCTION PLAN")
        print("=" * 60)

        # Plan overview
        print(f"📋 Plan ID: {plan['plan_id']}")
        print(f"🎯 Target Reduction: {plan['target_reduction_percent']}%")
        print(f"⏰ Timeframe: {plan['timeframe_months']} months")
        print(f"🔍 Focus Areas: {', '.join(plan['focus_areas'])}")

        # Baseline data
        baseline = plan["baseline_data"]
        print(f"\n📊 BASELINE DATA:")
        print(f"   🌿 Current CO2: {baseline['total_co2_kg']:.2f} kg")
        print(f"   📁 Data Sources: {len(baseline['data_sources'])}")

        # Selected actions
        print(f"\n🎯 SELECTED ACTIONS ({len(plan['selected_actions'])}):")
        print("-" * 60)

        for i, action in enumerate(plan["selected_actions"], 1):
            print(f"{i}. {action['action']}")
            print(f"   📝 {action['description']}")
            print(f"   📊 Impact: {action['co2_reduction_percent']}% reduction")
            print(
                f"   💰 Cost: {'$' + str(abs(action['cost_impact'])) + ' savings' if action['cost_impact'] < 0 else '$' + str(action['cost_impact']) + ' cost'}"
            )
            print(f"   ⚡ Effort: {action['effort_level'].title()}")
            print(f"   ⏱️  Timeline: {action['timeline_weeks']} weeks")
            print()

        # Plan metrics
        metrics = plan["estimated_metrics"]
        print(f"📈 PLAN METRICS:")
        print(f"   🌿 Total Reduction: {metrics['total_reduction_percent']:.1f}%")
        print(f"   💾 CO2 Savings: {metrics['estimated_co2_savings_kg']:.2f} kg")
        print(f"   💰 Cost Impact: ${metrics['total_cost_impact_usd']:.2f}")
        print(f"   📊 Success Probability: {metrics['success_probability']:.1%}")

        # Success factors
        print(f"\n🔑 SUCCESS FACTORS:")
        for factor in plan["success_factors"]:
            print(f"   • {factor}")

        # Next steps
        if plan["implementation_timeline"]["phases"]:
            next_phase = plan["implementation_timeline"]["phases"][0]
            print(f"\n🚀 NEXT STEPS:")
            print(f"   📋 Start with: {next_phase['action_title']}")
            print(
                f"   ⏰ Duration: {next_phase['end_week'] - next_phase['start_week']} weeks"
            )
            print(
                f"   📝 First step: {next_phase['deliverables'][0] if next_phase['deliverables'] else 'Begin implementation'}"
            )

    def save_plan(self, plan: Dict[str, Any], output_path: str = None) -> str:
        """Save plan to JSON file"""

        if not output_path:
            output_path = f"{plan['plan_id']}.json"

        with open(output_path, "w") as f:
            json.dump(plan, f, indent=2, default=str)

        return output_path


if __name__ == "__main__":
    planner = CO2ReductionPlanner()

    # Generate sample plan
    plan = planner.generate_reduction_plan(
        target_reduction=25.0, timeframe_months=6, focus_areas=["aws", "personal"]
    )

    # Print plan
    planner.print_reduction_plan(plan)

    # Save plan
    output_file = planner.save_plan(plan)
    print(f"\n💾 Plan saved to: {output_file}")
