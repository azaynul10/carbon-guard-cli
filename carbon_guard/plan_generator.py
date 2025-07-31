"""CO2 reduction plan generation module."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PlanGenerator:
    """Generates CO2 reduction plans based on audit data."""

    # Pre-defined action templates for different focus areas
    ACTION_TEMPLATES = {
        "aws": [
            {
                "title": "Optimize EC2 Instance Types",
                "description": "Right-size EC2 instances based on actual usage patterns",
                "category": "infrastructure",
                "co2_reduction": 15.0,
                "cost_impact": -200.0,  # Negative means cost savings
                "effort_level": "medium",
                "timeline_weeks": 2,
                "prerequisites": ["CloudWatch monitoring enabled"],
                "steps": [
                    "Analyze CloudWatch metrics for CPU and memory utilization",
                    "Identify over-provisioned instances",
                    "Create instance resize plan",
                    "Schedule maintenance windows for resizing",
                    "Monitor performance after changes",
                ],
            },
            {
                "title": "Implement Auto Scaling",
                "description": "Set up auto scaling groups to match demand",
                "category": "infrastructure",
                "co2_reduction": 25.0,
                "cost_impact": -300.0,
                "effort_level": "high",
                "timeline_weeks": 4,
                "prerequisites": [
                    "Load balancer configured",
                    "Application supports horizontal scaling",
                ],
                "steps": [
                    "Create launch templates",
                    "Configure auto scaling groups",
                    "Set up scaling policies",
                    "Test scaling behavior",
                    "Monitor and tune thresholds",
                ],
            },
            {
                "title": "Migrate to ARM-based Instances",
                "description": "Switch to Graviton processors for better energy efficiency",
                "category": "infrastructure",
                "co2_reduction": 20.0,
                "cost_impact": -150.0,
                "effort_level": "medium",
                "timeline_weeks": 3,
                "prerequisites": ["Application compatibility with ARM"],
                "steps": [
                    "Test application on ARM instances",
                    "Update deployment scripts",
                    "Plan migration schedule",
                    "Execute migration",
                    "Validate performance",
                ],
            },
            {
                "title": "Optimize S3 Storage Classes",
                "description": "Move infrequently accessed data to cheaper, lower-carbon storage",
                "category": "storage",
                "co2_reduction": 10.0,
                "cost_impact": -100.0,
                "effort_level": "low",
                "timeline_weeks": 1,
                "prerequisites": ["S3 access patterns analyzed"],
                "steps": [
                    "Analyze S3 access patterns",
                    "Create lifecycle policies",
                    "Test data retrieval",
                    "Apply policies to buckets",
                    "Monitor cost and access patterns",
                ],
            },
            {
                "title": "Schedule Non-Critical Workloads",
                "description": "Run batch jobs during off-peak hours when grid is cleaner",
                "category": "scheduling",
                "co2_reduction": 12.0,
                "cost_impact": -50.0,
                "effort_level": "medium",
                "timeline_weeks": 2,
                "prerequisites": [
                    "Workloads identified",
                    "Scheduling system available",
                ],
                "steps": [
                    "Identify batch workloads",
                    "Analyze grid carbon intensity patterns",
                    "Create scheduling rules",
                    "Implement job scheduling",
                    "Monitor execution and carbon impact",
                ],
            },
        ],
        "local": [
            {
                "title": "Optimize Algorithm Efficiency",
                "description": "Refactor code to reduce computational complexity",
                "category": "code",
                "co2_reduction": 30.0,
                "cost_impact": 0.0,
                "effort_level": "high",
                "timeline_weeks": 6,
                "prerequisites": ["Code profiling completed"],
                "steps": [
                    "Profile application performance",
                    "Identify computational bottlenecks",
                    "Research more efficient algorithms",
                    "Implement optimizations",
                    "Test and validate improvements",
                ],
            },
            {
                "title": "Implement Caching Strategies",
                "description": "Add caching to reduce redundant computations",
                "category": "performance",
                "co2_reduction": 20.0,
                "cost_impact": 50.0,
                "effort_level": "medium",
                "timeline_weeks": 3,
                "prerequisites": ["Cache infrastructure available"],
                "steps": [
                    "Identify cacheable operations",
                    "Choose appropriate caching strategy",
                    "Implement cache layer",
                    "Test cache hit rates",
                    "Monitor performance improvements",
                ],
            },
            {
                "title": "Optimize Database Queries",
                "description": "Improve database query efficiency and indexing",
                "category": "database",
                "co2_reduction": 15.0,
                "cost_impact": 0.0,
                "effort_level": "medium",
                "timeline_weeks": 2,
                "prerequisites": ["Database access available"],
                "steps": [
                    "Analyze slow query logs",
                    "Identify missing indexes",
                    "Optimize query structure",
                    "Add appropriate indexes",
                    "Monitor query performance",
                ],
            },
            {
                "title": "Reduce Memory Usage",
                "description": "Optimize memory allocation and garbage collection",
                "category": "memory",
                "co2_reduction": 10.0,
                "cost_impact": 0.0,
                "effort_level": "medium",
                "timeline_weeks": 4,
                "prerequisites": ["Memory profiling tools available"],
                "steps": [
                    "Profile memory usage patterns",
                    "Identify memory leaks",
                    "Optimize data structures",
                    "Tune garbage collection",
                    "Validate memory improvements",
                ],
            },
        ],
        "personal": [
            {
                "title": "Reduce Meat Consumption",
                "description": "Replace high-carbon meat with plant-based alternatives",
                "category": "diet",
                "co2_reduction": 40.0,
                "cost_impact": -20.0,
                "effort_level": "medium",
                "timeline_weeks": 8,
                "prerequisites": ["Dietary preferences flexible"],
                "steps": [
                    "Research plant-based protein sources",
                    "Plan weekly meal menus",
                    "Try new recipes gradually",
                    "Track dietary changes",
                    "Monitor health and satisfaction",
                ],
            },
            {
                "title": "Optimize Transportation",
                "description": "Use public transport, cycling, or walking more frequently",
                "category": "transport",
                "co2_reduction": 35.0,
                "cost_impact": -100.0,
                "effort_level": "low",
                "timeline_weeks": 2,
                "prerequisites": ["Alternative transport options available"],
                "steps": [
                    "Map current transportation patterns",
                    "Identify alternative routes",
                    "Test public transport options",
                    "Plan combined trips",
                    "Track transportation changes",
                ],
            },
            {
                "title": "Reduce Energy Consumption",
                "description": "Implement energy-saving practices at home",
                "category": "energy",
                "co2_reduction": 25.0,
                "cost_impact": -150.0,
                "effort_level": "low",
                "timeline_weeks": 1,
                "prerequisites": ["Home energy audit completed"],
                "steps": [
                    "Conduct home energy audit",
                    "Replace inefficient appliances",
                    "Improve insulation",
                    "Adjust thermostat settings",
                    "Monitor energy usage",
                ],
            },
            {
                "title": "Buy Local and Seasonal",
                "description": "Choose locally produced, seasonal foods",
                "category": "consumption",
                "co2_reduction": 15.0,
                "cost_impact": 0.0,
                "effort_level": "low",
                "timeline_weeks": 2,
                "prerequisites": ["Local markets available"],
                "steps": [
                    "Research local food sources",
                    "Learn seasonal food calendar",
                    "Plan shopping around local options",
                    "Try farmers markets",
                    "Track local food purchases",
                ],
            },
        ],
    }

    def __init__(self, config: Optional[Dict] = None):
        """Initialize plan generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.data_directory = self.config.get("data_directory", "carbon_data")

    def generate_plan(
        self,
        target_reduction: float = 20.0,
        timeframe_months: int = 12,
        focus_area: str = "all",
    ) -> Dict[str, Any]:
        """Generate a CO2 reduction plan.

        Args:
            target_reduction: Target CO2 reduction percentage
            timeframe_months: Timeframe in months
            focus_area: Focus area ('aws', 'local', 'personal', 'all')

        Returns:
            Dictionary containing the reduction plan
        """
        logger.info(
            f"Generating CO2 reduction plan: {target_reduction}% in {timeframe_months} months"
        )

        # Load existing audit data to inform the plan
        baseline_data = self._load_baseline_data()

        # Select relevant actions based on focus area
        available_actions = self._get_available_actions(focus_area, baseline_data)

        # Prioritize and select actions to meet target
        selected_actions = self._select_actions(
            available_actions, target_reduction, timeframe_months
        )

        # Create implementation timeline
        timeline = self._create_timeline(selected_actions, timeframe_months)

        # Calculate plan metrics
        plan_metrics = self._calculate_plan_metrics(selected_actions, baseline_data)

        plan = {
            "plan_id": self._generate_plan_id(),
            "created_at": datetime.now().isoformat(),
            "target_reduction_percent": target_reduction,
            "timeframe_months": timeframe_months,
            "focus_area": focus_area,
            "baseline_data": baseline_data,
            "actions": selected_actions,
            "timeline": timeline,
            "estimated_reduction": plan_metrics["total_reduction"],
            "estimated_cost": plan_metrics["total_cost"],
            "implementation_complexity": plan_metrics["avg_complexity"],
            "success_probability": plan_metrics["success_probability"],
            "milestones": self._create_milestones(selected_actions, timeframe_months),
        }

        return plan

    def _load_baseline_data(self) -> Dict[str, Any]:
        """Load baseline data from previous audits."""
        baseline = {
            "aws_co2_kg_per_hour": 0.0,
            "local_co2_kg_per_execution": 0.0,
            "personal_co2_kg_per_month": 0.0,
            "total_monthly_co2_kg": 0.0,
            "data_sources": [],
        }

        try:
            # Look for recent audit files
            data_dir = self.data_directory
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.endswith(".json"):
                        filepath = os.path.join(data_dir, filename)
                        try:
                            with open(filepath) as f:
                                data = json.load(f)

                            # Extract relevant metrics
                            if "aws" in filename.lower():
                                baseline["aws_co2_kg_per_hour"] += data.get(
                                    "co2_kg_per_hour", 0
                                )
                                baseline["data_sources"].append(
                                    f"AWS audit: {filename}"
                                )
                            elif "local" in filename.lower():
                                baseline["local_co2_kg_per_execution"] += data.get(
                                    "total_co2_kg", 0
                                )
                                baseline["data_sources"].append(
                                    f"Local audit: {filename}"
                                )
                            elif "personal" in filename.lower():
                                baseline["personal_co2_kg_per_month"] += data.get(
                                    "total_co2_kg", 0
                                )
                                baseline["data_sources"].append(
                                    f"Personal audit: {filename}"
                                )

                        except Exception as e:
                            logger.warning(f"Could not load data from {filepath}: {e}")

            # Calculate total monthly CO2
            baseline["total_monthly_co2_kg"] = (
                baseline["aws_co2_kg_per_hour"] * 24 * 30
                + baseline["local_co2_kg_per_execution"] * 100  # AWS running 24/7
                + baseline["personal_co2_kg_per_month"]  # Assume 100 executions/month
            )

        except Exception as e:
            logger.warning(f"Could not load baseline data: {e}")

        return baseline

    def _get_available_actions(
        self, focus_area: str, baseline_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get available actions based on focus area and baseline data."""
        available_actions = []

        if focus_area == "all":
            for area_actions in self.ACTION_TEMPLATES.values():
                available_actions.extend(area_actions)
        else:
            available_actions = self.ACTION_TEMPLATES.get(focus_area, [])

        # Filter actions based on baseline data availability
        filtered_actions = []
        for action in available_actions:
            # Check if we have relevant baseline data
            if self._action_applicable(action, baseline_data):
                # Adjust action parameters based on baseline
                adjusted_action = self._adjust_action_for_baseline(
                    action, baseline_data
                )
                filtered_actions.append(adjusted_action)

        return filtered_actions

    def _action_applicable(
        self, action: Dict[str, Any], baseline_data: Dict[str, Any]
    ) -> bool:
        """Check if an action is applicable given the baseline data."""
        category = action.get("category", "")

        # AWS actions require AWS baseline data
        if category in ["infrastructure", "storage", "scheduling"]:
            return baseline_data["aws_co2_kg_per_hour"] > 0

        # Local actions require local baseline data
        elif category in ["code", "performance", "database", "memory"]:
            return baseline_data["local_co2_kg_per_execution"] > 0

        # Personal actions are always applicable
        elif category in ["diet", "transport", "energy", "consumption"]:
            return True

        return True  # Default to applicable

    def _adjust_action_for_baseline(
        self, action: Dict[str, Any], baseline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust action parameters based on baseline data."""
        adjusted_action = action.copy()

        # Scale CO2 reduction based on baseline emissions
        total_baseline = baseline_data["total_monthly_co2_kg"]
        if total_baseline > 0:
            # Adjust reduction percentage based on baseline size
            if total_baseline > 1000:  # High emissions
                adjusted_action["co2_reduction"] *= 1.2
            elif total_baseline < 100:  # Low emissions
                adjusted_action["co2_reduction"] *= 0.8

        return adjusted_action

    def _select_actions(
        self,
        available_actions: List[Dict[str, Any]],
        target_reduction: float,
        timeframe_months: int,
    ) -> List[Dict[str, Any]]:
        """Select actions to meet the target reduction within timeframe."""
        # Sort actions by impact/effort ratio
        scored_actions = []
        for action in available_actions:
            effort_score = {"low": 1, "medium": 2, "high": 3}.get(
                action["effort_level"], 2
            )
            timeline_score = action["timeline_weeks"] / 4  # Convert to months

            # Prioritize actions that fit within timeframe
            if timeline_score <= timeframe_months:
                impact_effort_ratio = action["co2_reduction"] / (
                    effort_score * timeline_score
                )
                scored_actions.append((impact_effort_ratio, action))

        # Sort by score (highest first)
        scored_actions.sort(key=lambda x: x[0], reverse=True)

        # Select actions until target is met
        selected_actions = []
        cumulative_reduction = 0.0

        for score, action in scored_actions:
            if cumulative_reduction < target_reduction:
                selected_actions.append(action)
                cumulative_reduction += action["co2_reduction"]

            # Stop if we've exceeded target significantly
            if cumulative_reduction > target_reduction * 1.5:
                break

        return selected_actions

    def _create_timeline(
        self, actions: List[Dict[str, Any]], timeframe_months: int
    ) -> Dict[str, Any]:
        """Create implementation timeline for selected actions."""
        timeline = {
            "total_duration_months": timeframe_months,
            "phases": [],
            "milestones": [],
        }

        # Sort actions by timeline (shortest first for quick wins)
        sorted_actions = sorted(actions, key=lambda x: x["timeline_weeks"])

        current_week = 0
        phase_num = 1

        for action in sorted_actions:
            phase = {
                "phase_number": phase_num,
                "start_week": current_week,
                "end_week": current_week + action["timeline_weeks"],
                "action": action["title"],
                "deliverables": action.get("steps", []),
                "dependencies": action.get("prerequisites", []),
            }

            timeline["phases"].append(phase)

            # Add milestone
            milestone = {
                "week": current_week + action["timeline_weeks"],
                "title": f"Complete: {action['title']}",
                "expected_co2_reduction": action["co2_reduction"],
            }
            timeline["milestones"].append(milestone)

            current_week += action["timeline_weeks"]
            phase_num += 1

        return timeline

    def _calculate_plan_metrics(
        self, actions: List[Dict[str, Any]], baseline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall plan metrics."""
        total_reduction = sum(action["co2_reduction"] for action in actions)
        total_cost = sum(action.get("cost_impact", 0) for action in actions)

        # Calculate average complexity
        effort_scores = {"low": 1, "medium": 2, "high": 3}
        avg_complexity = (
            sum(effort_scores.get(action["effort_level"], 2) for action in actions)
            / len(actions)
            if actions
            else 0
        )

        # Estimate success probability based on complexity and timeline
        complexity_factor = max(0.3, 1.0 - (avg_complexity - 1) * 0.2)
        timeline_factor = max(
            0.5, 1.0 - len(actions) * 0.05
        )  # More actions = lower probability
        success_probability = complexity_factor * timeline_factor

        return {
            "total_reduction": total_reduction,
            "total_cost": total_cost,
            "avg_complexity": avg_complexity,
            "success_probability": success_probability,
            "actions_count": len(actions),
        }

    def _create_milestones(
        self, actions: List[Dict[str, Any]], timeframe_months: int
    ) -> List[Dict[str, Any]]:
        """Create key milestones for the plan."""
        milestones = []

        # Add quarterly milestones
        for quarter in range(1, min(5, timeframe_months // 3 + 1)):
            milestone_week = quarter * 12

            # Calculate expected reduction by this milestone
            actions_by_week = [
                a for a in actions if a["timeline_weeks"] <= milestone_week
            ]
            expected_reduction = sum(a["co2_reduction"] for a in actions_by_week)

            milestones.append(
                {
                    "week": milestone_week,
                    "title": f"Q{quarter} Review",
                    "type": "review",
                    "expected_co2_reduction": expected_reduction,
                    "deliverables": [
                        "Measure actual CO2 reduction",
                        "Review action effectiveness",
                        "Adjust plan if needed",
                    ],
                }
            )

        return milestones

    def _generate_plan_id(self) -> str:
        """Generate a unique plan ID."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"carbon_plan_{timestamp}"

    def save_plan(self, plan: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Save plan to file.

        Args:
            plan: Plan dictionary
            output_path: Optional output file path

        Returns:
            Path to saved plan file
        """
        if not output_path:
            os.makedirs(self.data_directory, exist_ok=True)
            output_path = os.path.join(self.data_directory, f"{plan['plan_id']}.json")

        with open(output_path, "w") as f:
            json.dump(plan, f, indent=2, default=str)

        logger.info(f"Plan saved to: {output_path}")
        return output_path

    def load_plan(self, plan_path: str) -> Dict[str, Any]:
        """Load plan from file.

        Args:
            plan_path: Path to plan file

        Returns:
            Plan dictionary
        """
        with open(plan_path) as f:
            plan = json.load(f)

        return plan

    def update_plan_progress(
        self,
        plan: Dict[str, Any],
        completed_actions: List[str],
        actual_reductions: Dict[str, float],
    ) -> Dict[str, Any]:
        """Update plan with progress information.

        Args:
            plan: Original plan dictionary
            completed_actions: List of completed action titles
            actual_reductions: Actual CO2 reductions achieved

        Returns:
            Updated plan dictionary
        """
        updated_plan = plan.copy()
        updated_plan["last_updated"] = datetime.now().isoformat()
        updated_plan["progress"] = {
            "completed_actions": completed_actions,
            "completion_rate": len(completed_actions) / len(plan["actions"])
            if plan["actions"]
            else 0,
            "actual_reductions": actual_reductions,
            "total_actual_reduction": sum(actual_reductions.values()),
            "variance_from_plan": sum(actual_reductions.values())
            - plan["estimated_reduction"],
        }

        return updated_plan
