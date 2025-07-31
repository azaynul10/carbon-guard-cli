"""AWS infrastructure CO2 auditing module."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AWSAuditor:
    """Audits AWS infrastructure for CO2 emissions estimation."""

    # CO2 emission factors (kg CO2 per kWh) by AWS region
    # Based on AWS Customer Carbon Footprint Tool data
    REGION_CARBON_INTENSITY = {
        "us-east-1": 0.000415,  # US East (N. Virginia)
        "us-east-2": 0.000523,  # US East (Ohio)
        "us-west-1": 0.000351,  # US West (N. California)
        "us-west-2": 0.000351,  # US West (Oregon)
        "eu-west-1": 0.000316,  # Europe (Ireland)
        "eu-central-1": 0.000338,  # Europe (Frankfurt)
        "ap-southeast-1": 0.000493,  # Asia Pacific (Singapore)
        "ap-northeast-1": 0.000506,  # Asia Pacific (Tokyo)
    }

    # Power consumption estimates (watts) for different instance types
    INSTANCE_POWER_CONSUMPTION = {
        "t2.nano": 5,
        "t2.micro": 10,
        "t2.small": 20,
        "t2.medium": 40,
        "t3.nano": 5,
        "t3.micro": 10,
        "t3.small": 20,
        "t3.medium": 40,
        "m5.large": 80,
        "m5.xlarge": 160,
        "m5.2xlarge": 320,
        "c5.large": 70,
        "c5.xlarge": 140,
        "c5.2xlarge": 280,
        "r5.large": 200,
        "r5.xlarge": 180,
        "r5.2xlarge": 360,
    }

    def __init__(
        self,
        region: str = "us-east-1",
        profile: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        """Initialize AWS auditor.

        Args:
            region: AWS region to audit
            profile: AWS profile to use
            config: Configuration dictionary
        """
        self.region = region
        self.profile = profile
        self.config = config or {}
        self.carbon_intensity = self.REGION_CARBON_INTENSITY.get(region, 0.0004)

        # Initialize AWS session
        try:
            if profile:
                self.session = boto3.Session(profile_name=profile, region_name=region)
            else:
                self.session = boto3.Session(region_name=region)
        except Exception as e:
            logger.error(f"Failed to initialize AWS session: {e}")
            raise

    def audit_all_services(self, estimate_only: bool = False) -> Dict[str, Any]:
        """Audit all supported AWS services.

        Args:
            estimate_only: If True, only provide estimates without detailed metrics

        Returns:
            Dictionary containing audit results for all services
        """
        results = {}

        # Audit EC2 instances
        try:
            results["ec2"] = self.audit_ec2(estimate_only)
        except Exception as e:
            logger.error(f"Failed to audit EC2: {e}")
            results["ec2"] = {"error": str(e), "co2_kg_per_hour": 0}

        # Audit RDS instances
        try:
            results["rds"] = self.audit_rds(estimate_only)
        except Exception as e:
            logger.error(f"Failed to audit RDS: {e}")
            results["rds"] = {"error": str(e), "co2_kg_per_hour": 0}

        # Audit Lambda functions
        try:
            results["lambda"] = self.audit_lambda(estimate_only)
        except Exception as e:
            logger.error(f"Failed to audit Lambda: {e}")
            results["lambda"] = {"error": str(e), "co2_kg_per_hour": 0}

        # Audit S3 storage
        try:
            results["s3"] = self.audit_s3(estimate_only)
        except Exception as e:
            logger.error(f"Failed to audit S3: {e}")
            results["s3"] = {"error": str(e), "co2_kg_per_hour": 0}

        return results

    def audit_services(
        self, services: List[str], estimate_only: bool = False
    ) -> Dict[str, Any]:
        """Audit specific AWS services.

        Args:
            services: List of service names to audit
            estimate_only: If True, only provide estimates without detailed metrics

        Returns:
            Dictionary containing audit results for specified services
        """
        results = {}

        for service in services:
            try:
                if service.lower() == "ec2":
                    results["ec2"] = self.audit_ec2(estimate_only)
                elif service.lower() == "rds":
                    results["rds"] = self.audit_rds(estimate_only)
                elif service.lower() == "lambda":
                    results["lambda"] = self.audit_lambda(estimate_only)
                elif service.lower() == "s3":
                    results["s3"] = self.audit_s3(estimate_only)
                else:
                    logger.warning(f"Unsupported service: {service}")
                    results[service] = {
                        "error": f"Unsupported service: {service}",
                        "co2_kg_per_hour": 0,
                    }
            except Exception as e:
                logger.error(f"Failed to audit {service}: {e}")
                results[service] = {"error": str(e), "co2_kg_per_hour": 0}

        return results

    def audit_ec2(self, estimate_only: bool = False) -> Dict[str, Any]:
        """Audit EC2 instances for CO2 emissions.

        Args:
            estimate_only: If True, only provide estimates without detailed metrics

        Returns:
            Dictionary containing EC2 audit results
        """
        ec2 = self.session.client("ec2")

        try:
            # Get running instances
            response = ec2.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
            )

            instances = []
            total_co2_per_hour = 0
            total_cost_per_hour = 0

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_type = instance["InstanceType"]
                    instance_id = instance["InstanceId"]

                    # Estimate power consumption
                    power_watts = self.INSTANCE_POWER_CONSUMPTION.get(instance_type, 50)
                    power_kwh = power_watts / 1000  # Convert to kWh

                    # Calculate CO2 emissions
                    co2_per_hour = power_kwh * self.carbon_intensity

                    # Estimate cost (rough approximation)
                    cost_per_hour = self._estimate_instance_cost(instance_type)

                    # Extract tags - return as dictionary for most tests
                    tags = {}
                    if "Tags" in instance:
                        for tag in instance["Tags"]:
                            tags[tag["Key"]] = tag["Value"]

                    # Format launch time as ISO string if present
                    launch_time = None
                    if "LaunchTime" in instance and instance["LaunchTime"]:
                        if hasattr(instance["LaunchTime"], "isoformat"):
                            launch_time = instance["LaunchTime"].isoformat()
                        else:
                            launch_time = str(instance["LaunchTime"])

                    instance_data = {
                        "instance_id": instance_id,
                        "instance_type": instance_type,
                        "state": instance["State"]["Name"],  # Add state field
                        "availability_zone": instance.get("Placement", {}).get(
                            "AvailabilityZone"
                        ),  # Add AZ field
                        "power_watts": power_watts,
                        "co2_kg_per_hour": co2_per_hour,
                        "estimated_cost_per_hour": cost_per_hour,
                        "launch_time": launch_time,
                        "tags": tags,
                    }

                    if not estimate_only:
                        # Get additional metrics from CloudWatch
                        instance_data.update(self._get_ec2_metrics(instance_id))

                    instances.append(instance_data)
                    total_co2_per_hour += co2_per_hour
                    total_cost_per_hour += cost_per_hour

            return {
                "service": "ec2",
                "region": self.region,
                "total_instances": len(instances),
                "instances": instances,
                "co2_kg_per_hour": total_co2_per_hour,
                "estimated_cost_usd": total_cost_per_hour,
                "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except ClientError as e:
            logger.error(f"AWS API error in EC2 audit: {e}")
            return {
                "service": "ec2",
                "region": self.region,
                "error": f"AWS API error: {str(e)}",
                "total_instances": 0,
                "instances": [],
                "co2_kg_per_hour": 0,
                "estimated_cost_usd": 0,
                "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Unexpected error in EC2 audit: {e}")
            return {
                "service": "ec2",
                "region": self.region,
                "error": f"Unexpected error: {str(e)}",
                "total_instances": 0,
                "instances": [],
                "co2_kg_per_hour": 0,
                "estimated_cost_usd": 0,
                "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def audit_rds(self, estimate_only: bool = False) -> Dict[str, Any]:
        """Audit RDS instances for CO2 emissions."""
        rds = self.session.client("rds")

        try:
            response = rds.describe_db_instances()

            instances = []
            total_co2_per_hour = 0
            total_cost_per_hour = 0

            for db_instance in response["DBInstances"]:
                if db_instance["DBInstanceStatus"] == "available":
                    instance_class = db_instance["DBInstanceClass"]
                    instance_id = db_instance["DBInstanceIdentifier"]

                    # Estimate power consumption (RDS instances typically use more power)
                    base_power = self.INSTANCE_POWER_CONSUMPTION.get(
                        instance_class.replace("db.", ""), 60
                    )
                    power_watts = base_power * 1.2  # RDS overhead
                    power_kwh = power_watts / 1000

                    # Calculate CO2 emissions
                    co2_per_hour = power_kwh * self.carbon_intensity

                    # Estimate cost
                    cost_per_hour = self._estimate_rds_cost(instance_class)

                    instance_data = {
                        "db_instance_identifier": instance_id,
                        "db_instance_class": instance_class,
                        "engine": db_instance["Engine"],
                        "power_watts": power_watts,
                        "co2_kg_per_hour": co2_per_hour,
                        "estimated_cost_per_hour": cost_per_hour,
                        "instance_create_time": db_instance.get("InstanceCreateTime"),
                    }

                    instances.append(instance_data)
                    total_co2_per_hour += co2_per_hour
                    total_cost_per_hour += cost_per_hour

            return {
                "service": "rds",
                "region": self.region,
                "total_instances": len(instances),
                "instances": instances,
                "co2_kg_per_hour": total_co2_per_hour,
                "estimated_cost_usd": total_cost_per_hour,
                "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except ClientError as e:
            logger.error(f"AWS API error in RDS audit: {e}")
            raise

    def audit_lambda(self, estimate_only: bool = False) -> Dict[str, Any]:
        """Audit Lambda functions for CO2 emissions."""
        lambda_client = self.session.client("lambda")

        try:
            response = lambda_client.list_functions()

            functions = []
            total_co2_per_hour = 0
            total_cost_per_hour = 0

            for function in response["Functions"]:
                function_name = function["FunctionName"]
                memory_mb = function["MemorySize"]

                # Estimate power consumption based on memory allocation
                # Lambda pricing is based on GB-seconds, approximate power usage
                power_watts = (memory_mb / 1024) * 2  # Rough estimate
                power_kwh = power_watts / 1000

                # Calculate CO2 emissions (assuming average execution)
                co2_per_hour = (
                    power_kwh * self.carbon_intensity * 0.1
                )  # 10% utilization assumption

                # Estimate cost (very rough)
                cost_per_hour = (
                    (memory_mb / 1024) * 0.0000166667 * 3600 * 0.1
                )  # 10% utilization

                function_data = {
                    "function_name": function_name,
                    "memory_mb": memory_mb,
                    "runtime": function["Runtime"],
                    "power_watts": power_watts,
                    "co2_kg_per_hour": co2_per_hour,
                    "estimated_cost_per_hour": cost_per_hour,
                    "last_modified": function["LastModified"],
                }

                functions.append(function_data)
                total_co2_per_hour += co2_per_hour
                total_cost_per_hour += cost_per_hour

            return {
                "service": "lambda",
                "region": self.region,
                "total_functions": len(functions),
                "functions": functions,
                "co2_kg_per_hour": total_co2_per_hour,
                "estimated_cost_usd": total_cost_per_hour,
                "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except ClientError as e:
            logger.error(f"AWS API error in Lambda audit: {e}")
            raise

    def audit_s3(self, estimate_only: bool = False) -> Dict[str, Any]:
        """Audit S3 storage for CO2 emissions."""
        s3 = self.session.client("s3")
        cloudwatch = self.session.client("cloudwatch")

        try:
            response = s3.list_buckets()

            buckets = []
            total_co2_per_hour = 0
            total_cost_per_hour = 0

            for bucket in response["Buckets"]:
                bucket_name = bucket["Name"]

                try:
                    # Get bucket size from CloudWatch
                    bucket_size_bytes = self._get_s3_bucket_size(
                        bucket_name, cloudwatch
                    )
                    bucket_size_gb = bucket_size_bytes / (1024**3)

                    # Estimate power consumption for storage
                    # S3 uses approximately 0.5W per TB stored
                    power_watts = (bucket_size_gb / 1024) * 0.5
                    power_kwh = power_watts / 1000

                    # Calculate CO2 emissions
                    co2_per_hour = power_kwh * self.carbon_intensity

                    # Estimate cost
                    cost_per_hour = (
                        bucket_size_gb * 0.023 / (24 * 30)
                    )  # Rough S3 standard pricing

                    bucket_data = {
                        "bucket_name": bucket_name,
                        "size_gb": bucket_size_gb,
                        "power_watts": power_watts,
                        "co2_kg_per_hour": co2_per_hour,
                        "estimated_cost_per_hour": cost_per_hour,
                        "creation_date": bucket["CreationDate"],
                    }

                    buckets.append(bucket_data)
                    total_co2_per_hour += co2_per_hour
                    total_cost_per_hour += cost_per_hour

                except Exception as e:
                    logger.warning(f"Could not get size for bucket {bucket_name}: {e}")
                    # Add bucket with zero values
                    buckets.append(
                        {
                            "bucket_name": bucket_name,
                            "size_gb": 0,
                            "power_watts": 0,
                            "co2_kg_per_hour": 0,
                            "estimated_cost_per_hour": 0,
                            "creation_date": bucket["CreationDate"],
                            "error": str(e),
                        }
                    )

            return {
                "service": "s3",
                "region": self.region,
                "total_buckets": len(buckets),
                "buckets": buckets,
                "co2_kg_per_hour": total_co2_per_hour,
                "estimated_cost_usd": total_cost_per_hour,
                "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except ClientError as e:
            logger.error(f"AWS API error in S3 audit: {e}")
            raise

    def _get_ec2_metrics(self, instance_id: str) -> Dict[str, Any]:
        """Get CloudWatch metrics for EC2 instance."""
        cloudwatch = self.session.client("cloudwatch")

        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=1)

            # Get CPU utilization
            cpu_response = cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Average"],
            )

            cpu_avg = 0
            if cpu_response["Datapoints"]:
                cpu_avg = cpu_response["Datapoints"][0]["Average"]

            return {"cpu_utilization_avg": cpu_avg, "metrics_period": "1_hour"}

        except Exception as e:
            logger.warning(f"Could not get metrics for instance {instance_id}: {e}")
            return {}

    def _get_s3_bucket_size(self, bucket_name: str, cloudwatch) -> float:
        """Get S3 bucket size from CloudWatch."""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=2)

            response = cloudwatch.get_metric_statistics(
                Namespace="AWS/S3",
                MetricName="BucketSizeBytes",
                Dimensions=[
                    {"Name": "BucketName", "Value": bucket_name},
                    {"Name": "StorageType", "Value": "StandardStorage"},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Average"],
            )

            if response["Datapoints"]:
                return response["Datapoints"][0]["Average"]
            return 0

        except Exception as e:
            logger.warning(f"Could not get size for bucket {bucket_name}: {e}")
            return 0

    def _estimate_instance_cost(self, instance_type: str) -> float:
        """Estimate hourly cost for EC2 instance type."""
        # Rough cost estimates (USD per hour) - these should be updated with current pricing
        cost_estimates = {
            "t2.nano": 0.0058,
            "t2.micro": 0.0116,
            "t2.small": 0.023,
            "t2.medium": 0.046,
            "t3.nano": 0.0052,
            "t3.micro": 0.0104,
            "t3.small": 0.0208,
            "t3.medium": 0.0416,
            "m5.large": 0.096,
            "m5.xlarge": 0.192,
            "m5.2xlarge": 0.384,
            "c5.large": 0.085,
            "c5.xlarge": 0.17,
            "c5.2xlarge": 0.34,
            "r5.large": 0.126,
            "r5.xlarge": 0.252,
            "r5.2xlarge": 0.504,
        }
        return cost_estimates.get(instance_type, 0.1)  # Default estimate

    def _estimate_rds_cost(self, instance_class: str) -> float:
        """Estimate hourly cost for RDS instance class."""
        # Remove 'db.' prefix and estimate based on EC2 equivalent
        ec2_equivalent = instance_class.replace("db.", "")
        base_cost = self._estimate_instance_cost(ec2_equivalent)
        return base_cost * 1.5  # RDS typically costs ~50% more than EC2
