#!/usr/bin/env python3
"""
Example: Batch connectivity analysis for multiple workspaces
"""

import subprocess
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# List of workspaces to analyze
WORKSPACES = [
    {
        "name": "prod-ai-hub",
        "resource_group": "prod-rg",
        "hub_type": "azure-ai-foundry"
    },
    {
        "name": "dev-ml-workspace",
        "resource_group": "dev-rg",
        "hub_type": "azure-ml"
    },
    {
        "name": "test-ai-hub",
        "resource_group": "test-rg",
        "hub_type": "azure-ai-foundry"
    }
]

def analyze_workspace(workspace):
    """Run connectivity analysis for a single workspace"""
    print(f"\n{'='*60}")
    print(f"Analyzing {workspace['hub_type']}: {workspace['name']}")
    print(f"{'='*60}")
    
    cmd = [
        "python", "main.py",
        "--hub-type", workspace['hub_type'],
        "--workspace-name", workspace['name'],
        "--resource-group", workspace['resource_group'],
        "--action", "analyze-connectivity"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Analysis completed successfully")
            
            # Find and parse the JSON report
            report_dir = Path("connectivity-reports")
            if report_dir.exists():
                json_files = [f for f in report_dir.glob("*.json") 
                             if f.name.startswith(workspace['name'])]
                
                if json_files:
                    # Get the most recent file
                    latest_json = max(json_files, key=lambda f: f.stat().st_ctime)
                    
                    try:
                        with open(latest_json, 'r') as f:
                            analysis_data = json.load(f)
                        
                        # Extract key metrics
                        connected_resources = analysis_data.get('connected_resources', {})
                        security_summary = connected_resources.get('security_summary', {})
                        network_config = analysis_data.get('network_configuration', {})
                        
                        security_score = security_summary.get('average_security_score', 0)
                        total_resources = connected_resources.get('total_resources', 0)
                        network_type = network_config.get('configuration_type', 'unknown')
                        
                        # Count private endpoints
                        resources = connected_resources.get('resources', [])
                        private_endpoint_count = sum(1 for r in resources if r.get('has_private_endpoint', False))
                        
                        print(f"   Security Score: {security_score}/100")
                        print(f"   Total Resources: {total_resources}")
                        print(f"   Network Type: {network_type}")
                        print(f"   Private Endpoints: {private_endpoint_count}/{total_resources}")
                        
                        return {
                            "workspace": workspace['name'],
                            "hub_type": workspace['hub_type'],
                            "resource_group": workspace['resource_group'],
                            "status": "success",
                            "security_score": security_score,
                            "total_resources": total_resources,
                            "network_type": network_type,
                            "private_endpoint_count": private_endpoint_count,
                            "report_file": str(latest_json)
                        }
                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        print(f"   ⚠️  Report generated but couldn't parse: {e}")
                        return {
                            "workspace": workspace['name'],
                            "status": "partial_success",
                            "error": f"Report parsing failed: {e}"
                        }
                else:
                    print(f"   ⚠️  Analysis completed but no JSON report found")
                    return {
                        "workspace": workspace['name'],
                        "status": "partial_success",
                        "error": "No JSON report found"
                    }
            else:
                print(f"   ⚠️  No reports directory found")
                return {
                    "workspace": workspace['name'],
                    "status": "partial_success",
                    "error": "No reports directory"
                }
        else:
            print(f"❌ Analysis failed: {result.stderr}")
            return {
                "workspace": workspace['name'],
                "status": "failed",
                "error": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        print(f"❌ Analysis timed out after 5 minutes")
        return {
            "workspace": workspace['name'],
            "status": "timeout",
            "error": "Analysis timed out"
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "workspace": workspace['name'],
            "status": "error",
            "error": str(e)
        }

def generate_security_report(results):
    """Generate a security-focused summary report"""
    successful = [r for r in results if r['status'] == 'success']
    
    if not successful:
        return
    
    print(f"\n{'='*60}")
    print("🛡️  SECURITY SUMMARY REPORT")
    print(f"{'='*60}")
    
    # Overall statistics
    total_resources = sum(r.get('total_resources', 0) for r in successful)
    total_private_endpoints = sum(r.get('private_endpoint_count', 0) for r in successful)
    avg_security_score = sum(r.get('security_score', 0) for r in successful) / len(successful)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Resources Analyzed: {total_resources}")
    print(f"   Total Private Endpoints: {total_private_endpoints}")
    print(f"   Average Security Score: {avg_security_score:.1f}/100")
    print(f"   Private Endpoint Coverage: {(total_private_endpoints/total_resources*100):.1f}%" if total_resources > 0 else "   Private Endpoint Coverage: N/A")
    
    # Security scoring breakdown
    high_security = [r for r in successful if r.get('security_score', 0) >= 80]
    medium_security = [r for r in successful if 60 <= r.get('security_score', 0) < 80]
    low_security = [r for r in successful if r.get('security_score', 0) < 60]
    
    print(f"\n🔒 Security Score Distribution:")
    print(f"   High Security (80-100): {len(high_security)} workspaces")
    print(f"   Medium Security (60-79): {len(medium_security)} workspaces")
    print(f"   Low Security (0-59): {len(low_security)} workspaces")
    
    # Top recommendations
    print(f"\n⚡ Key Recommendations:")
    if low_security:
        print(f"   🔴 URGENT: {len(low_security)} workspace(s) need immediate security attention")
        for workspace in low_security:
            print(f"      - {workspace['workspace']}: {workspace.get('security_score', 0)}/100")
    
    if medium_security:
        print(f"   🟡 MEDIUM: {len(medium_security)} workspace(s) need security improvements")
    
    if total_resources > total_private_endpoints:
        missing_pe = total_resources - total_private_endpoints
        print(f"   🔗 Enable private endpoints for {missing_pe} remaining resources")
    
    print(f"   📋 Review individual reports for detailed recommendations")

def main():
    """Run batch analysis"""
    print("🚀 Starting batch connectivity analysis")
    print(f"   Analyzing {len(WORKSPACES)} workspaces")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ensure reports directory exists
    os.makedirs("connectivity-reports", exist_ok=True)
    
    results = []
    for workspace in WORKSPACES:
        result = analyze_workspace(workspace)
        results.append(result)
    
    # Generate summary report
    print(f"\n{'='*60}")
    print("📊 BATCH ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] not in ['success', 'partial_success']]
    partial = [r for r in results if r['status'] == 'partial_success']
    
    print(f"\nTotal Workspaces: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Partial Success: {len(partial)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        avg_score = sum(r.get('security_score', 0) for r in successful) / len(successful)
        print(f"\nAverage Security Score: {avg_score:.1f}/100")
        
        print("\nWorkspace Security Scores:")
        for r in sorted(successful, key=lambda x: x.get('security_score', 0), reverse=True):
            score = r.get('security_score', 0)
            emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            print(f"  {emoji} {r['workspace']}: {score}/100")
    
    if partial:
        print("\nPartial Success (check manually):")
        for r in partial:
            print(f"  ⚠️  {r['workspace']}: {r.get('error', 'Unknown issue')}")
    
    if failed:
        print("\nFailed Analyses:")
        for r in failed:
            print(f"  ❌ {r['workspace']}: {r.get('error', 'Unknown error')}")
    
    # Generate security report
    generate_security_report(results)
    
    # Save summary
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_file = f"connectivity-reports/batch_summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_workspaces": len(results),
            "successful": len(successful),
            "partial": len(partial),
            "failed": len(failed),
            "results": results
        }, f, indent=2)
    
    print(f"\n📄 Batch summary saved to: {summary_file}")
    
    # Exit with appropriate code
    if failed:
        print(f"\n⚠️  Batch analysis completed with {len(failed)} failures")
        sys.exit(1)
    elif partial:
        print(f"\n⚠️  Batch analysis completed with {len(partial)} partial successes")
        sys.exit(2)
    else:
        print(f"\n✅ Batch analysis completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main() 