#!/usr/bin/env python3
"""
Basic test to verify moto mocks work with our Carbon Guard modules.
"""

import pytest
import boto3
from moto import mock_aws
from datetime import datetime
import os

# Import our modules
from carbon_guard.aws_auditor import AWSAuditor


class TestBasicMotoIntegration:
    """Basic tests to verify moto integration works."""
    
    @pytest.fixture
    def aws_credentials(self):
        """Mocked AWS Credentials for moto."""
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    def test_aws_auditor_creation(self, aws_credentials):
        """Test that we can create an AWS auditor."""
        auditor = AWSAuditor(region='us-east-1')
        assert auditor.region == 'us-east-1'
        assert auditor.carbon_intensity == 0.000415  # us-east-1 carbon intensity
    
    @mock_aws
    def test_empty_ec2_audit(self, aws_credentials):
        """Test EC2 audit with no instances (should return empty results)."""
        auditor = AWSAuditor(region='us-east-1')
        
        # This should work even with no instances
        result = auditor.audit_ec2(estimate_only=True)
        
        assert 'total_instances' in result
        assert 'co2_kg_per_hour' in result
        assert 'instances' in result
        assert result['total_instances'] == 0
        assert result['co2_kg_per_hour'] == 0.0
        assert len(result['instances']) == 0
    
    @mock_aws
    def test_single_ec2_instance_basic(self, aws_credentials):
        """Test basic EC2 instance CO2 calculation."""
        # Create EC2 client and launch a test instance
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        response = ec2_client.run_instances(
            ImageId='ami-12345678',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro'
        )
        
        instance_id = response['Instances'][0]['InstanceId']
        
        # Create auditor and test
        auditor = AWSAuditor(region='us-east-1')
        result = auditor.audit_ec2(estimate_only=True)
        
        # Basic assertions
        assert result['total_instances'] == 1
        assert len(result['instances']) == 1
        assert result['co2_kg_per_hour'] > 0
        
        # Check instance details
        instance = result['instances'][0]
        assert instance['instance_id'] == instance_id
        assert instance['instance_type'] == 't2.micro'
        assert instance['state'] == 'running'
        assert instance['power_watts'] > 0
        assert instance['co2_kg_per_hour'] > 0
    
    @mock_aws
    def test_multiple_instances_basic(self, aws_credentials):
        """Test multiple EC2 instances CO2 calculation."""
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        # Launch 3 instances
        response = ec2_client.run_instances(
            ImageId='ami-12345678',
            MinCount=3,
            MaxCount=3,
            InstanceType='t2.micro'
        )
        
        # Create auditor and test
        auditor = AWSAuditor(region='us-east-1')
        result = auditor.audit_ec2(estimate_only=True)
        
        # Should find all 3 instances
        assert result['total_instances'] == 3
        assert len(result['instances']) == 3
        
        # Total CO2 should be 3x individual instance CO2
        individual_co2 = result['instances'][0]['co2_kg_per_hour']
        expected_total = individual_co2 * 3
        assert abs(result['co2_kg_per_hour'] - expected_total) < 1e-10
    
    @mock_aws
    def test_instance_with_tags(self, aws_credentials):
        """Test that instance tags are properly captured."""
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        # Launch instance with tags
        response = ec2_client.run_instances(
            ImageId='ami-12345678',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'test-server'},
                        {'Key': 'Environment', 'Value': 'testing'}
                    ]
                }
            ]
        )
        
        # Create auditor and test
        auditor = AWSAuditor(region='us-east-1')
        result = auditor.audit_ec2(estimate_only=True)
        
        # Check tags are included
        instance = result['instances'][0]
        assert 'tags' in instance
        
        tags_dict = instance['tags']  # Tags are now in dictionary format
        assert tags_dict['Name'] == 'test-server'
        assert tags_dict['Environment'] == 'testing'
    
    def test_carbon_intensity_values(self, aws_credentials):
        """Test that carbon intensity values are correct for different regions."""
        test_regions = [
            ('us-east-1', 0.000415),
            ('us-west-2', 0.000351),
            ('eu-west-1', 0.000316)
        ]
        
        for region, expected_intensity in test_regions:
            auditor = AWSAuditor(region=region)
            assert auditor.carbon_intensity == expected_intensity
    
    def test_instance_power_consumption_values(self, aws_credentials):
        """Test that instance power consumption values are reasonable."""
        auditor = AWSAuditor(region='us-east-1')
        
        # Test some common instance types
        test_instances = [
            ('t2.micro', 10),
            ('t2.small', 20),
            ('m5.large', 80),
            ('c5.xlarge', 140)
        ]
        
        for instance_type, expected_power in test_instances:
            if instance_type in auditor.INSTANCE_POWER_CONSUMPTION:
                actual_power = auditor.INSTANCE_POWER_CONSUMPTION[instance_type]
                assert actual_power == expected_power


def test_moto_basic_functionality():
    """Test that moto itself is working correctly."""
    with mock_aws():
        # Set up credentials
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        # Create EC2 client
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        
        # Launch instance
        response = ec2_client.run_instances(
            ImageId='ami-12345678',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro'
        )
        
        # Verify instance was created
        assert len(response['Instances']) == 1
        instance = response['Instances'][0]
        assert instance['InstanceType'] == 't2.micro'
        # Instance may be pending initially, so check if it's either pending or running
        assert instance['State']['Name'] in ['pending', 'running']
        
        # List instances
        describe_response = ec2_client.describe_instances()
        assert len(describe_response['Reservations']) == 1
        assert len(describe_response['Reservations'][0]['Instances']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
