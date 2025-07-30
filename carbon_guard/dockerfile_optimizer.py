"""Dockerfile optimization module for reducing carbon footprint."""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class DockerfileOptimizer:
    """Optimizes Dockerfiles to reduce carbon footprint."""
    
    # Base image recommendations (smaller, more efficient alternatives)
    BASE_IMAGE_ALTERNATIVES = {
        'ubuntu:latest': 'ubuntu:22.04-slim',
        'ubuntu:20.04': 'ubuntu:20.04-slim',
        'ubuntu:18.04': 'ubuntu:18.04-slim',
        'debian:latest': 'debian:bullseye-slim',
        'debian:bullseye': 'debian:bullseye-slim',
        'python:latest': 'python:3.11-slim',
        'python:3.11': 'python:3.11-slim',
        'python:3.10': 'python:3.10-slim',
        'python:3.9': 'python:3.9-slim',
        'node:latest': 'node:18-alpine',
        'node:18': 'node:18-alpine',
        'node:16': 'node:16-alpine',
        'openjdk:latest': 'openjdk:17-jre-slim',
        'openjdk:17': 'openjdk:17-jre-slim',
        'openjdk:11': 'openjdk:11-jre-slim',
        'nginx:latest': 'nginx:alpine',
        'redis:latest': 'redis:alpine',
        'postgres:latest': 'postgres:alpine',
    }
    
    # Package manager optimizations
    PACKAGE_MANAGER_OPTIMIZATIONS = {
        'apt-get': [
            'apt-get update && apt-get install -y --no-install-recommends',
            'rm -rf /var/lib/apt/lists/*'
        ],
        'apk': [
            'apk add --no-cache'
        ],
        'yum': [
            'yum install -y',
            'yum clean all'
        ]
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Dockerfile optimizer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def analyze_dockerfile(self, dockerfile_path: str) -> Dict[str, Any]:
        """Analyze a Dockerfile for optimization opportunities.
        
        Args:
            dockerfile_path: Path to the Dockerfile
            
        Returns:
            Dictionary containing analysis results
        """
        dockerfile_path = Path(dockerfile_path)
        if not dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found: {dockerfile_path}")
        
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        analysis = {
            'total_lines': len(lines),
            'layer_count': 0,
            'base_image': None,
            'issues': [],
            'optimization_opportunities': [],
            'estimated_size_mb': 0
        }
        
        # Analyze each line
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Count layers (instructions that create layers)
            if self._creates_layer(line):
                analysis['layer_count'] += 1
            
            # Extract base image
            if line.upper().startswith('FROM'):
                analysis['base_image'] = self._extract_base_image(line)
            
            # Check for issues
            issues = self._check_line_issues(line, i)
            analysis['issues'].extend(issues)
        
        # Check for optimization opportunities
        analysis['optimization_opportunities'] = self._identify_optimizations(content)
        
        # Estimate image size
        analysis['estimated_size_mb'] = self._estimate_image_size(analysis)
        
        return analysis
    
    def generate_optimizations(self, dockerfile_path: str, strategy: str = 'all') -> List[Dict[str, Any]]:
        """Generate optimization recommendations for a Dockerfile.
        
        Args:
            dockerfile_path: Path to the Dockerfile
            strategy: Optimization strategy ('size', 'layers', 'cache', 'all')
            
        Returns:
            List of optimization recommendations
        """
        analysis = self.analyze_dockerfile(dockerfile_path)
        optimizations = []
        
        if strategy in ['size', 'all']:
            optimizations.extend(self._generate_size_optimizations(analysis))
        
        if strategy in ['layers', 'all']:
            optimizations.extend(self._generate_layer_optimizations(analysis))
        
        if strategy in ['cache', 'all']:
            optimizations.extend(self._generate_cache_optimizations(analysis))
        
        # Sort by impact (highest first)
        optimizations.sort(key=lambda x: x.get('co2_reduction_percent', 0), reverse=True)
        
        return optimizations
    
    def apply_optimizations(self, dockerfile_path: str, optimizations: List[Dict[str, Any]]) -> str:
        """Apply optimizations to a Dockerfile.
        
        Args:
            dockerfile_path: Path to the original Dockerfile
            optimizations: List of optimizations to apply
            
        Returns:
            Optimized Dockerfile content
        """
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Apply each optimization
        for optimization in optimizations:
            if optimization.get('auto_apply', False):
                content = self._apply_optimization(content, optimization)
        
        return content
    
    def estimate_savings(self, optimizations: List[Dict[str, Any]]) -> float:
        """Estimate total CO2 reduction percentage from optimizations.
        
        Args:
            optimizations: List of optimizations
            
        Returns:
            Estimated CO2 reduction percentage
        """
        # Simple additive model (in reality, optimizations may have diminishing returns)
        total_reduction = sum(opt.get('co2_reduction_percent', 0) for opt in optimizations)
        return min(total_reduction, 80)  # Cap at 80% reduction
    
    def _creates_layer(self, line: str) -> bool:
        """Check if a Dockerfile instruction creates a new layer."""
        layer_instructions = ['RUN', 'COPY', 'ADD', 'WORKDIR', 'USER', 'VOLUME', 'EXPOSE']
        return any(line.upper().startswith(inst) for inst in layer_instructions)
    
    def _extract_base_image(self, from_line: str) -> str:
        """Extract base image from FROM instruction."""
        parts = from_line.split()
        if len(parts) >= 2:
            return parts[1]
        return ""
    
    def _check_line_issues(self, line: str, line_number: int) -> List[str]:
        """Check a single line for common issues."""
        issues = []
        line_upper = line.upper()
        
        # Check for inefficient base images
        if line_upper.startswith('FROM'):
            base_image = self._extract_base_image(line)
            if base_image in self.BASE_IMAGE_ALTERNATIVES:
                issues.append(f"Line {line_number}: Consider using {self.BASE_IMAGE_ALTERNATIVES[base_image]} instead of {base_image}")
        
        # Check for inefficient package installation
        if 'apt-get install' in line and '--no-install-recommends' not in line:
            issues.append(f"Line {line_number}: Add --no-install-recommends to apt-get install")
        
        if 'apt-get update' in line and 'apt-get install' not in line:
            issues.append(f"Line {line_number}: Combine apt-get update with install in same RUN command")
        
        # Check for missing cleanup
        if 'apt-get install' in line and 'rm -rf /var/lib/apt/lists/*' not in line:
            issues.append(f"Line {line_number}: Missing apt cache cleanup")
        
        # Check for COPY/ADD inefficiencies
        if line_upper.startswith('COPY') and '.' in line:
            issues.append(f"Line {line_number}: Avoid copying entire context, be specific about files")
        
        # Check for multiple RUN commands that could be combined
        if line_upper.startswith('RUN') and len(line.split('&&')) == 1:
            issues.append(f"Line {line_number}: Consider combining with adjacent RUN commands")
        
        return issues
    
    def _identify_optimizations(self, content: str) -> List[str]:
        """Identify high-level optimization opportunities."""
        opportunities = []
        lines = content.split('\n')
        
        # Count RUN instructions
        run_count = sum(1 for line in lines if line.strip().upper().startswith('RUN'))
        if run_count > 3:
            opportunities.append(f"Consider combining {run_count} RUN instructions to reduce layers")
        
        # Check for multi-stage build opportunity
        if 'FROM' in content and content.count('FROM') == 1:
            if any(keyword in content.lower() for keyword in ['gcc', 'make', 'build', 'compile']):
                opportunities.append("Consider using multi-stage build to reduce final image size")
        
        # Check for .dockerignore
        opportunities.append("Ensure .dockerignore file exists to exclude unnecessary files")
        
        return opportunities
    
    def _estimate_image_size(self, analysis: Dict[str, Any]) -> float:
        """Estimate Docker image size in MB."""
        base_sizes = {
            'ubuntu': 72,
            'ubuntu:slim': 28,
            'debian': 124,
            'debian:slim': 69,
            'python': 885,
            'python:slim': 122,
            'python:alpine': 45,
            'node': 993,
            'node:alpine': 110,
            'alpine': 5,
            'scratch': 0
        }
        
        base_image = analysis.get('base_image', '').lower()
        base_size = 100  # Default estimate
        
        for image, size in base_sizes.items():
            if image in base_image:
                base_size = size
                break
        
        # Add estimated size for layers
        layer_size = analysis['layer_count'] * 10  # Rough estimate
        
        return base_size + layer_size
    
    def _generate_size_optimizations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate size-focused optimizations."""
        optimizations = []
        
        # Base image optimization
        base_image = analysis.get('base_image', '')
        if base_image in self.BASE_IMAGE_ALTERNATIVES:
            optimizations.append({
                'type': 'base_image',
                'description': f"Replace {base_image} with {self.BASE_IMAGE_ALTERNATIVES[base_image]}",
                'impact': 'High',
                'co2_reduction_percent': 25,
                'auto_apply': True,
                'original': base_image,
                'replacement': self.BASE_IMAGE_ALTERNATIVES[base_image]
            })
        
        # Multi-stage build recommendation
        if analysis['estimated_size_mb'] > 500:
            optimizations.append({
                'type': 'multi_stage',
                'description': "Implement multi-stage build to reduce final image size",
                'impact': 'High',
                'co2_reduction_percent': 40,
                'auto_apply': False,
                'details': "Use separate build and runtime stages"
            })
        
        return optimizations
    
    def _generate_layer_optimizations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate layer-focused optimizations."""
        optimizations = []
        
        if analysis['layer_count'] > 10:
            optimizations.append({
                'type': 'layer_reduction',
                'description': f"Reduce {analysis['layer_count']} layers by combining RUN instructions",
                'impact': 'Medium',
                'co2_reduction_percent': 15,
                'auto_apply': True,
                'current_layers': analysis['layer_count'],
                'target_layers': max(5, analysis['layer_count'] // 2)
            })
        
        return optimizations
    
    def _generate_cache_optimizations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate cache-focused optimizations."""
        optimizations = []
        
        optimizations.append({
            'type': 'copy_optimization',
            'description': "Optimize COPY instructions for better layer caching",
            'impact': 'Medium',
            'co2_reduction_percent': 10,
            'auto_apply': False,
            'details': "Copy dependency files before source code"
        })
        
        optimizations.append({
            'type': 'package_cache',
            'description': "Add package manager cache cleanup",
            'impact': 'Low',
            'co2_reduction_percent': 5,
            'auto_apply': True,
            'details': "Remove package manager caches after installation"
        })
        
        return optimizations
    
    def _apply_optimization(self, content: str, optimization: Dict[str, Any]) -> str:
        """Apply a single optimization to Dockerfile content."""
        opt_type = optimization.get('type')
        
        if opt_type == 'base_image':
            # Replace base image
            original = optimization['original']
            replacement = optimization['replacement']
            content = re.sub(
                rf'FROM\s+{re.escape(original)}',
                f'FROM {replacement}',
                content,
                flags=re.IGNORECASE
            )
        
        elif opt_type == 'layer_reduction':
            # Combine consecutive RUN instructions
            content = self._combine_run_instructions(content)
        
        elif opt_type == 'package_cache':
            # Add cache cleanup to package installations
            content = self._add_package_cleanup(content)
        
        return content
    
    def _combine_run_instructions(self, content: str) -> str:
        """Combine consecutive RUN instructions."""
        lines = content.split('\n')
        result_lines = []
        run_buffer = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.upper().startswith('RUN'):
                # Extract the command part
                command = stripped[3:].strip()
                run_buffer.append(command)
            else:
                # Flush run buffer if we have accumulated commands
                if run_buffer:
                    if len(run_buffer) > 1:
                        combined = 'RUN ' + ' && \\\n    '.join(run_buffer)
                        result_lines.append(combined)
                    else:
                        result_lines.append(f'RUN {run_buffer[0]}')
                    run_buffer = []
                result_lines.append(line)
        
        # Handle any remaining run commands
        if run_buffer:
            if len(run_buffer) > 1:
                combined = 'RUN ' + ' && \\\n    '.join(run_buffer)
                result_lines.append(combined)
            else:
                result_lines.append(f'RUN {run_buffer[0]}')
        
        return '\n'.join(result_lines)
    
    def _add_package_cleanup(self, content: str) -> str:
        """Add package manager cleanup commands."""
        lines = content.split('\n')
        result_lines = []
        
        for line in lines:
            result_lines.append(line)
            stripped = line.strip()
            
            # Add cleanup after apt-get install
            if 'apt-get install' in stripped and 'rm -rf /var/lib/apt/lists/*' not in stripped:
                if not stripped.endswith('\\'):
                    # Single line install, add cleanup
                    result_lines[-1] = stripped + ' && rm -rf /var/lib/apt/lists/*'
            
            # Add cleanup after apk add
            elif 'apk add' in stripped and '--no-cache' not in stripped:
                result_lines[-1] = stripped.replace('apk add', 'apk add --no-cache')
        
        return '\n'.join(result_lines)
    
    def create_optimized_dockerfile_template(self, base_image: str = 'python:3.11-slim',
                                           app_type: str = 'python') -> str:
        """Create an optimized Dockerfile template.
        
        Args:
            base_image: Base image to use
            app_type: Type of application ('python', 'node', 'java', 'go')
            
        Returns:
            Optimized Dockerfile template content
        """
        templates = {
            'python': f'''# Multi-stage build for Python application
FROM {base_image} as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM {base_image}

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
WORKDIR /app
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Update PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

EXPOSE 8000
CMD ["python", "app.py"]
''',
            
            'node': f'''# Multi-stage build for Node.js application
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Production stage
FROM node:18-alpine

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

WORKDIR /app

# Copy node_modules from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .

USER nextjs

EXPOSE 3000
CMD ["node", "server.js"]
''',
            
            'java': f'''# Multi-stage build for Java application
FROM openjdk:17-jdk-slim as builder

WORKDIR /app
COPY . .
RUN ./gradlew build --no-daemon

# Production stage
FROM openjdk:17-jre-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy JAR from builder
COPY --from=builder /app/build/libs/*.jar app.jar

USER appuser

EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
'''
        }
        
        return templates.get(app_type, templates['python'])
