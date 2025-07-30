#!/usr/bin/env python3
"""
Comprehensive Moto Mock Tests for Carbon Guard CLI
Tests AWS EC2 CO2 calculations using moto mocking library.
"""

import os
import json
import boto3
import pytest
from datetime import datetime
from moto import mock_aws
from carbon_guard.aws_auditor import AWSAuditor


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


class TestComprehensiveMoto:
    """Comprehensive test suite using moto for AWS mocking."""
    
    @mock_aws
    def test_basic_ec2_audit(self, aws_credentials):
        """Test basic EC2 audit functionality with moto."""
        # Create EC2 client
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        # Launch test instances
        response = ec2_client.run_instances(
            ImageId='ami-12345678',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro'
        )
        
        # Perform audit
        auditor = AWSAuditor(region='us-east-1')
        result = auditor.audit_ec2(estimate_only=True)
        
        # Verify results
        assert result['total_instances'] == 1
        assert result['co2_kg_per_hour'] > 0
        assert 'instances' in result
        
        print(f"\\nBasic EC2 Audit Results:")
        print(f"  Instances: {result['total_instances']}")
        print(f"  CO2: {result['co2_kg_per_hour']:.8f} kg/hour")
        
        return result
    
    @mock_aws
    def test_multiple_instance_types(self, aws_credentials):
        """Test audit with multiple instance types."""
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        # Launch different instance types
        instance_types = ['t2.micro', 't2.small', 'm5.large']
        
        for instance_type in instance_types:
            ec2_client.run_instances(
                ImageId='ami-12345678',
                MinCount=1,
                MaxCount=1,
                InstanceType=instance_type
            )
        
        # Perform audit
        auditor = AWSAuditor(region='us-east-1')
        result = auditor.audit_ec2(estimate_only=True)
        
        # Verify results
        assert result['total_instances'] == 3
        assert result['co2_kg_per_hour'] > 0
        
        print(f"\\nMultiple Instance Types Results:")
        print(f"  Total instances: {result['total_instances']}")
        print(f"  Total CO2: {result['co2_kg_per_hour']:.8f} kg/hour")
        
        return result


def test_sample_data_generation():
    """Generate sample EC2 data for testing."""
    with mock_aws():
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        # Create sample instances
        sample_instances = [
            {'type': 't2.micro', 'name': 'test-1'},
            {'type': 'm5.large', 'name': 'test-2'}
        ]
        
        launched_instances = []
        
        for config in sample_instances:
            response = ec2_client.run_instances(
                ImageId='ami-12345678',
                MinCount=1,
                MaxCount=1,
                InstanceType=config['type'],
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': config['name']}]
                }]
            )
            
            instance = response['Instances'][0]
            launched_instances.append({
                'instance_id': instance['InstanceId'],
                'instance_type': instance['InstanceType'],
                'name': config['name']
            })
        
        # Perform CO2 audit
        auditor = AWSAuditor(region='us-east-1')
        result = auditor.audit_ec2(estimate_only=True)
        
        print(f"\\nSample Data Generation:")
        print(f"  Instances created: {len(launched_instances)}")
        print(f"  Total CO2: {result['co2_kg_per_hour']:.8f} kg/hour")
        
        return result


if __name__ == '__main__':
    print("🧪 Clean Moto Mock Test")
    print("=" * 40)
    
    # Run the sample data generation
    test_sample_data_generation()
    
    print("\\n✅ Test completed successfully!")
