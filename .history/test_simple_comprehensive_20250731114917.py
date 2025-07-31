#!/usr/bin/env python3
"""
Simple comprehensive test demonstrating moto mocks for EC2 CO2 calculations.
"""

import pytest
import boto3
from moto import mock_aws
from datetime import datetime
import os
import json

from carbon_guard.aws_auditor import AWSAuditor


class TestSimpleComprehensive:
    """Simple comprehensive tests for moto mocks."""
    
    @pytest.fixture
    def aws_credentials(self):
        """Set up mocked AWS credentials."""
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    @mock_aws
    def test_production_scenario(self, aws_credentials):
        """Test a realistic production scenario."""
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        # Launch production-like instances
        instances = [
            {'type': 'm5.large', 'count': 3, 'role': 'web'},
            {'type': 'c5.xlarge', 'count': 2, 'role': 'api'},
            {'type': 'r5.large', 'count': 1, 'role': 'database'}
        ]
        
        total_launched = 0
        for config in instances:
            for i in range(config['count']):
                ec2_client.run_instances(
                    ImageId='ami-12345678',
                    MinCount=1,
                    MaxCount=1,
                    InstanceType=config['type'],
                    TagSpecifications=[{
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Role', 'Value': config['role']},
                            {'Key': 'Environment', 'Value': 'production'}
                        ]
                    }]
                )
                total_launched += 1
        
        # Audit CO2
        auditor = AWSAuditor(region='us-east-1')
        result = auditor.audit_ec2(estimate_only=True)
        
        assert result['total_instances'] == total_launched
        assert result['co2_kg_per_hour'] > 0
        
        # Calculate expected values
        expected_power = (3 * 80) + (2 * 140) + (1 * 200)  # 720W
        expected_co2 = (expected_power / 1000) * auditor.carbon_intensity
        
        assert abs(result['co2_kg_per_hour'] - expected_co2) < 1e-6
        
        print(f"\n🏢 Production Scenario Results:")
        print(f"   Instances: {result['total_instances']}")
        print(f"   Power: {expected_power}W")
        print(f"   CO2: {result['co2_kg_per_hour']:.8f} kg/hour")
        print(f"   Annual CO2: {result['co2_kg_per_hour'] * 24 * 365:.4f} kg/year")
        
        return result
    
    @mock_aws
    def test_multi_region_comparison(self, aws_credentials):
        """Compare CO2 across multiple regions."""
        regions = [
            ('us-east-1', 0.000415),
            ('us-west-2', 0.000351),
            ('eu-west-1', 0.000316)
        ]
        
        results = []
        
        for region, expected_intensity in regions:
            # Launch identical instance in each region
            ec2_client = boto3.client('ec2', region_name=region)
            ec2_client.run_instances(
                ImageId='ami-12345678',
                MinCount=1,
                MaxCount=1,
                InstanceType='m5.large'
            )
            
            # Calculate CO2
            auditor = AWSAuditor(region=region)
            result = auditor.audit_ec2(estimate_only=True)
            
            results.append({
                'region': region,
                'carbon_intensity': auditor.carbon_intensity,
                'co2_per_hour': result['co2_kg_per_hour'],
                'co2_per_year': result['co2_kg_per_hour'] * 24 * 365
            })
            
            # Verify carbon intensity
            assert auditor.carbon_intensity == expected_intensity
        
        # Sort by CO2 (lowest first)
        results.sort(key=lambda x: x['co2_per_hour'])
        
        print(f"\n🌍 Multi-Region Comparison (m5.large):")
        for i, result in enumerate(results):
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            print(f"   {rank} {result['region']}: {result['co2_per_hour']:.8f} kg/hour")
        
        # Calculate savings potential
        best = results[0]
        worst = results[-1]
        savings = worst['co2_per_year'] - best['co2_per_year']
        savings_percent = (savings / worst['co2_per_year']) * 100
        
        print(f"\n💡 Optimization Potential:")
        print(f"   Best region: {best['region']}")
        print(f"   Annual savings: {savings:.4f} kg ({savings_percent:.1f}%)")
        
        return results
    
    @mock_aws
    def test_scaling_impact(self, aws_credentials):
        """Test CO2 impact of scaling instances."""
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        auditor = AWSAuditor(region='us-east-1')
        
        scaling_scenarios = [1, 2, 4, 8]  # Number of instances
        results = []
        
        for instance_count in scaling_scenarios:
            # Launch instances
            instance_ids = []
            for i in range(instance_count):
                response = ec2_client.run_instances(
                    ImageId='ami-12345678',
                    MinCount=1,
                    MaxCount=1,
                    InstanceType='m5.large'
                )
                instance_ids.append(response['Instances'][0]['InstanceId'])
            
            # Calculate CO2
            result = auditor.audit_ec2(estimate_only=True)
            
            results.append({
                'instances': instance_count,
                'co2_per_hour': result['co2_kg_per_hour'],
                'co2_per_day': result['co2_kg_per_hour'] * 24
            })
            
            # Clean up for next scenario
            ec2_client.terminate_instances(InstanceIds=instance_ids)
        
        print(f"\n📈 Scaling Impact Analysis:")
        for result in results:
            print(f"   {result['instances']} instances: {result['co2_per_hour']:.8f} kg/hour")
        
        # Verify linear scaling
        base_co2 = results[0]['co2_per_hour']
        for i, result in enumerate(results):
            expected_co2 = base_co2 * (i + 1)
            assert abs(result['co2_per_hour'] - expected_co2) < 1e-6
        
        return results
    
    @mock_aws
    def test_instance_type_comparison(self, aws_credentials):
        """Compare CO2 emissions across different instance types."""
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        auditor = AWSAuditor(region='us-east-1')
        
        instance_types = [
            ('t2.micro', 10),
            ('t2.small', 20),
            ('m5.large', 80),
            ('c5.xlarge', 140),
            ('r5.large', 200)
        ]
        
        results = []
        
        for instance_type, expected_power in instance_types:
            # Launch instance
            response = ec2_client.run_instances(
                ImageId='ami-12345678',
                MinCount=1,
                MaxCount=1,
                InstanceType=instance_type
            )
            
            instance_id = response['Instances'][0]['InstanceId']
            
            # Calculate CO2
            result = auditor.audit_ec2(estimate_only=True)
            
            if result['total_instances'] > 0:  # Instance found
                instance_data = result['instances'][0]
                
                results.append({
                    'type': instance_type,
                    'power_watts': instance_data['power_watts'],
                    'co2_per_hour': instance_data['co2_kg_per_hour'],
                    'cost_per_hour': instance_data['estimated_cost_per_hour']
                })
                
                # Verify power consumption
                assert instance_data['power_watts'] == expected_power
            
            # Clean up
            ec2_client.terminate_instances(InstanceIds=[instance_id])
        
        print(f"\n⚡ Instance Type Comparison:")
        for result in results:
            print(f"   {result['type']}: {result['power_watts']}W, "
                  f"{result['co2_per_hour']:.8f} kg CO2/hour")
        
        return results


def test_generate_sample_data():
    """Generate comprehensive sample data for testing."""
    with mock_aws():
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        # Create diverse sample instances
        sample_configs = [
            {'type': 't2.micro', 'name': 'dev-test', 'env': 'development'},
            {'type': 't2.small', 'name': 'staging-web', 'env': 'staging'},
            {'type': 'm5.large', 'name': 'prod-web-1', 'env': 'production'},
            {'type': 'm5.large', 'name': 'prod-web-2', 'env': 'production'},
            {'type': 'c5.xlarge', 'name': 'prod-api', 'env': 'production'},
            {'type': 'r5.large', 'name': 'prod-db', 'env': 'production'}
        ]
        
        launched = []
        for config in sample_configs:
            response = ec2_client.run_instances(
                ImageId='ami-12345678',
                MinCount=1,
                MaxCount=1,
                InstanceType=config['type'],
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': config['name']},
                        {'Key': 'Environment', 'Value': config['env']},
                        {'Key': 'Purpose', 'Value': 'sample-data'}
                    ]
                }]
            )
            
            instance = response['Instances'][0]
            launched.append({
                'instance_id': instance['InstanceId'],
                'instance_type': instance['InstanceType'],
                'name': config['name'],
                'environment': config['env']
            })
        
        # Generate CO2 analysis
        auditor = AWSAuditor(region='us-east-1')
        co2_result = auditor.audit_ec2(estimate_only=True)
        
        # Create sample dataset
        sample_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'region': 'us-east-1',
                'carbon_intensity': auditor.carbon_intensity,
                'purpose': 'moto-mock-demonstration'
            },
            'instances': launched,
            'co2_analysis': co2_result,
            'summary': {
                'total_instances': len(launched),
                'total_power_watts': sum(inst['power_watts'] for inst in co2_result['instances']),
                'total_co2_kg_per_hour': co2_result['co2_kg_per_hour'],
                'total_co2_kg_per_year': co2_result['co2_kg_per_hour'] * 24 * 365,
                'environments': {
                    'development': len([i for i in launched if i['environment'] == 'development']),
                    'staging': len([i for i in launched if i['environment'] == 'staging']),
                    'production': len([i for i in launched if i['environment'] == 'production'])
                }
            }
        }
        
        # Save to file
        with open('moto_sample_ec2_data.json', 'w') as f:
            json.dump(sample_data, f, indent=2, default=str)
        
        print(f"\n📊 Generated Sample EC2 Data:")
        print(f"   Total instances: {sample_data['summary']['total_instances']}")
        print(f"   Total power: {sample_data['summary']['total_power_watts']}W")
        print(f"   Annual CO2: {sample_data['summary']['total_co2_kg_per_year']:.4f} kg")
        print(f"   Environments: {sample_data['summary']['environments']}")
        print(f"   Saved to: moto_sample_ec2_data.json")
        
        return sample_data


if __name__ == '__main__':
    print("🧪 Simple Comprehensive Moto Mock Tests")
    print("=" * 50)
    
    # Generate sample data first
    sample_data = test_generate_sample_data()
    
    # Run tests
    print("\n🚀 Running tests...")
    pytest.main([__file__, '-v', '-s'])
