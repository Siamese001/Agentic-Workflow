"""
Outreach Engine CLI
LEVEL 5 - Command-line interface for outreach generation and management
"""

import asyncio
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from apps.outreach_engine.services.pipelines.outreach_pipeline import OutreachPipeline
from apps.outreach_engine.services.pipelines.validation_pipeline import ValidationPipeline
from apps.outreach_engine.workers.outreach_generate_worker import outreach_worker
from apps.outreach_engine.workers.contact_enrich_worker import contact_enrich_worker
from apps.outreach_engine.workers.delivery_worker import delivery_worker

class OutreachEngineCLI:
    """Command-line interface for the Outreach Engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.outreach_pipeline = OutreachPipeline()
        self.validation_pipeline = ValidationPipeline()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('outreach_engine.log')
            ]
        )
    
    async def generate_outreach(
        self,
        recipient_file: str,
        sender_file: str,
        outreach_type: str,
        output_file: str,
        context_file: Optional[str] = None,
        preferences_file: Optional[str] = None
    ):
        """Generate outreach message"""
        try:
            self.logger.info("Starting outreach generation")
            
            # Load input files
            recipient_profile = self._load_json_file(recipient_file)
            sender_profile = self._load_json_file(sender_file)
            context = self._load_json_file(context_file) if context_file else {}
            preferences = self._load_json_file(preferences_file) if preferences_file else {}
            
            # Prepare request data
            request_data = {
                "recipient_profile": recipient_profile,
                "sender_profile": sender_profile,
                "outreach_type": outreach_type,
                "context": context,
                "preferences": preferences
            }
            
            # Execute pipeline
            result = await self.outreach_pipeline.execute(request_data)
            
            # Prepare output
            output_data = {
                "outreach_content": result.outreach_content,
                "metadata": result.metadata,
                "quality_score": result.quality_score,
                "processing_time": result.processing_time,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Save result
            self._save_json_file(output_file, output_data)
            
            # Print summary
            print(f"\n✅ Outreach generated successfully!")
            print(f"📊 Quality Score: {result.quality_score:.2f}")
            print(f"⏱️  Processing Time: {result.processing_time:.2f}s")
            print(f"💾 Output saved to: {output_file}")
            
            # Show preview
            print(f"\n📧 Subject: {result.outreach_content.get('subject', 'N/A')}")
            print(f"📝 Body Preview: {result.outreach_content.get('body', 'N/A')[:200]}...")
            
        except Exception as e:
            self.logger.error(f"Outreach generation failed: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    async def validate_outreach(
        self,
        content_file: str,
        output_file: str,
        validation_level: str = "standard"
    ):
        """Validate outreach message"""
        try:
            self.logger.info(f"Starting outreach validation at level: {validation_level}")
            
            # Load content
            outreach_content = self._load_json_file(content_file)
            
            # Execute validation
            result = await self.validation_pipeline.validate_outreach(
                outreach_content, validation_level=validation_level
            )
            
            # Prepare output
            output_data = {
                "is_valid": result.is_valid,
                "validation_score": result.validation_score,
                "issues_found": result.issues_found,
                "recommendations": result.recommendations,
                "compliance_checks": result.compliance_checks,
                "quality_metrics": result.quality_metrics,
                "metadata": result.metadata
            }
            
            # Save result
            self._save_json_file(output_file, output_data)
            
            # Print summary
            status = "✅ Valid" if result.is_valid else "❌ Invalid"
            print(f"\n{status} - Validation Score: {result.validation_score:.2f}")
            print(f"🔍 Issues Found: {len(result.issues_found)}")
            print(f"💡 Recommendations: {len(result.recommendations)}")
            print(f"💾 Output saved to: {output_file}")
            
            # Show top issues
            if result.issues_found:
                print(f"\n🚨 Top Issues:")
                for issue in result.issues_found[:3]:
                    print(f"  • {issue.get('message', 'Unknown issue')}")
            
            # Show top recommendations
            if result.recommendations:
                print(f"\n💡 Top Recommendations:")
                for rec in result.recommendations[:3]:
                    print(f"  • {rec}")
            
        except Exception as e:
            self.logger.error(f"Outreach validation failed: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    async def start_workers(self, worker_types: list):
        """Start background workers"""
        try:
            self.logger.info(f"Starting workers: {', '.join(worker_types)}")
            
            # Start specified workers
            if "outreach" in worker_types:
                await outreach_worker.start()
                print("✅ Outreach generation worker started")
            
            if "enrichment" in worker_types:
                await contact_enrich_worker.start()
                print("✅ Contact enrichment worker started")
            
            if "delivery" in worker_types:
                await delivery_worker.start()
                print("✅ Delivery worker started")
            
            print(f"\n🚀 Workers started successfully!")
            print("Press Ctrl+C to stop workers...")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping workers...")
                
                # Stop workers
                if "outreach" in worker_types:
                    await outreach_worker.stop()
                if "enrichment" in worker_types:
                    await contact_enrich_worker.stop()
                if "delivery" in worker_types:
                    await delivery_worker.stop()
                
                print("✅ All workers stopped")
            
        except Exception as e:
            self.logger.error(f"Worker management failed: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    async def get_worker_stats(self, worker_type: str):
        """Get worker statistics"""
        try:
            if worker_type == "outreach":
                stats = await outreach_worker.get_worker_stats()
            elif worker_type == "enrichment":
                stats = await contact_enrich_worker.get_worker_stats()
            elif worker_type == "delivery":
                stats = await delivery_worker.get_worker_stats()
            else:
                raise ValueError(f"Unknown worker type: {worker_type}")
            
            # Display stats
            print(f"\n📊 {worker_type.title()} Worker Statistics:")
            print(f"🟢 Status: {'Running' if stats['is_running'] else 'Stopped'}")
            print(f"📋 Active Tasks: {stats['active_tasks']}")
            print(f"📦 Queue Size: {stats['queue_size']}")
            print(f"✅ Completed Tasks: {stats['completed_tasks']}")
            
            if stats.get('uptime_seconds'):
                uptime_minutes = stats['uptime_seconds'] / 60
                print(f"⏱️  Uptime: {uptime_minutes:.1f} minutes")
            
            if stats.get('stats'):
                worker_stats = stats['stats']
                print(f"📈 Tasks Processed: {worker_stats.get('tasks_processed', 0)}")
                print(f"✅ Tasks Completed: {worker_stats.get('tasks_completed', 0)}")
                print(f"❌ Tasks Failed: {worker_stats.get('tasks_failed', 0)}")
                
                if worker_stats.get('average_processing_time'):
                    print(f"⚡ Avg Processing Time: {worker_stats['average_processing_time']:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to get worker stats: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def create_sample_files(self, output_dir: str):
        """Create sample input files"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Sample recipient profile
            recipient_sample = {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "company": "Tech Innovations Inc.",
                "role": "Engineering Manager",
                "industry": "Technology",
                "background": {
                    "experience_years": 8,
                    "education": "BS Computer Science",
                    "skills": ["Leadership", "Project Management", "Software Development"],
                    "achievements": ["Led team of 10 engineers", "Successfully launched 5 products"]
                }
            }
            
            # Sample sender profile
            sender_sample = {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "company": "Digital Solutions LLC",
                "role": "Senior Software Engineer",
                "industry": "Technology",
                "expertise": ["Cloud Architecture", "DevOps", "Python"],
                "background": {
                    "experience_years": 6,
                    "education": "MS Computer Science",
                    "skills": ["Python", "AWS", "Docker", "Kubernetes"],
                    "achievements": ["AWS Certified", "Open source contributor"]
                }
            }
            
            # Sample context
            context_sample = {
                "mutual_connections": ["Mike Johnson", "Sarah Williams"],
                "shared_interests": ["Cloud Computing", "DevOps"],
                "relationship": "professional_network",
                "purpose": "exploring collaboration opportunities",
                "urgency": "medium"
            }
            
            # Sample preferences
            preferences_sample = {
                "tone": "professional",
                "length": "medium",
                "personalization_level": "moderate",
                "include_call_to_action": True
            }
            
            # Save sample files
            self._save_json_file(output_path / "recipient_sample.json", recipient_sample)
            self._save_json_file(output_path / "sender_sample.json", sender_sample)
            self._save_json_file(output_path / "context_sample.json", context_sample)
            self._save_json_file(output_path / "preferences_sample.json", preferences_sample)
            
            print(f"✅ Sample files created in: {output_dir}")
            print("📁 Files created:")
            print("  • recipient_sample.json")
            print("  • sender_sample.json")
            print("  • context_sample.json")
            print("  • preferences_sample.json")
            
        except Exception as e:
            self.logger.error(f"Failed to create sample files: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
    
    def _save_json_file(self, file_path: str, data: Dict[str, Any]):
        """Save JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to save {file_path}: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Outreach Engine CLI - Generate and manage personalized outreach messages"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate outreach message')
    generate_parser.add_argument('--recipient', required=True, help='Recipient profile JSON file')
    generate_parser.add_argument('--sender', required=True, help='Sender profile JSON file')
    generate_parser.add_argument('--type', required=True, choices=['email', 'linkedin', 'cold_call', 'follow_up', 'networking'], help='Outreach type')
    generate_parser.add_argument('--output', required=True, help='Output JSON file')
    generate_parser.add_argument('--context', help='Context JSON file (optional)')
    generate_parser.add_argument('--preferences', help='Preferences JSON file (optional)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate outreach message')
    validate_parser.add_argument('--content', required=True, help='Content JSON file')
    validate_parser.add_argument('--output', required=True, help='Output JSON file')
    validate_parser.add_argument('--level', choices=['basic', 'standard', 'strict'], default='standard', help='Validation level')
    
    # Workers command
    workers_parser = subparsers.add_parser('workers', help='Manage background workers')
    workers_subparsers = workers_parser.add_subparsers(dest='workers_command', help='Worker commands')
    
    start_parser = workers_subparsers.add_parser('start', help='Start workers')
    start_parser.add_argument('types', nargs='+', choices=['outreach', 'enrichment', 'delivery'], help='Worker types to start')
    
    stats_parser = workers_subparsers.add_parser('stats', help='Get worker statistics')
    stats_parser.add_argument('type', choices=['outreach', 'enrichment', 'delivery'], help='Worker type')
    
    # Sample command
    sample_parser = subparsers.add_parser('sample', help='Create sample input files')
    sample_parser.add_argument('--output-dir', required=True, help='Output directory for sample files')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create CLI instance
    cli = OutreachEngineCLI()
    
    # Execute command
    if args.command == 'generate':
        asyncio.run(cli.generate_outreach(
            args.recipient, args.sender, args.type, args.output, args.context, args.preferences
        ))
    elif args.command == 'validate':
        asyncio.run(cli.validate_outreach(args.content, args.output, args.level))
    elif args.command == 'workers':
        if args.workers_command == 'start':
            asyncio.run(cli.start_workers(args.types))
        elif args.workers_command == 'stats':
            asyncio.run(cli.get_worker_stats(args.type))
        else:
            workers_parser.print_help()
            sys.exit(1)
    elif args.command == 'sample':
        cli.create_sample_files(args.output_dir)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
