"""
Resume Engine CLI Runner
LEVEL 5 - Command-line interface for resume generation and management
"""

import asyncio
import json
import argparse
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Import engine components
from ..services.pipelines.resume_pipeline import ResumePipeline
from ..workers.resume_generate_worker import ResumeGenerateWorker, ResumeGenerateTask
from ..workers.enrichment_worker import EnrichmentWorker, EnrichmentTask
from ..services.utils.scoring import ResumeScorer

class ResumeEngineCLI:
    """Command-line interface for resume engine operations"""
    
    def __init__(self):
        self.resume_pipeline = ResumePipeline()
        self.resume_worker = ResumeGenerateWorker()
        self.enrichment_worker = EnrichmentWorker()
        self.resume_scorer = ResumeScorer()
        
        # Default configurations
        self.default_config = {
            "output_dir": "generated_resumes",
            "format": "json",
            "verbose": False
        }
    
    async def generate_resume(
        self,
        profile_file: str,
        job_file: str,
        output_file: str = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate resume from profile and job description"""
        try:
            # Load input files
            user_profile = await self._load_json_file(profile_file)
            job_description = await self._load_json_file(job_file)
            
            if not user_profile or not job_description:
                raise ValueError("Invalid input files")
            
            # Generate resume
            print("🚀 Generating resume...")
            result = await self.resume_pipeline.execute(
                {"user_profile": user_profile, "job_description": job_description},
                preferences or {}
            )
            
            # Save result
            if output_file:
                await self._save_result(result, output_file)
                print(f"✅ Resume saved to: {output_file}")
            
            # Display summary
            print(f"📊 Quality Score: {result.quality_score:.2f}")
            print(f"⏱️  Processing Time: {result.processing_time:.2f}s")
            print(f"📝 Word Count: {result.metadata.get('word_count', 0)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating resume: {e}")
            raise e
    
    async def analyze_resume(
        self,
        resume_file: str,
        job_file: str = None
    ) -> Dict[str, Any]:
        """Analyze resume quality and job alignment"""
        try:
            # Load resume
            resume_content = await self._load_json_file(resume_file)
            
            if not resume_content:
                raise ValueError("Invalid resume file")
            
            # Load job description if provided
            job_description = None
            if job_file:
                job_description = await self._load_json_file(job_file)
            
            print("🔍 Analyzing resume...")
            
            # Calculate comprehensive score
            score_result = await self.resume_scorer.calculate_comprehensive_score(
                resume_content, job_description
            )
            
            # Display results
            print(f"📊 Overall Score: {score_result['overall_score']:.2f} ({score_result['grade']})")
            
            print("\n🎯 Individual Scores:")
            for score_type, result in score_result['individual_scores'].items():
                print(f"  {result.score_type.value}: {result.score:.2f}")
            
            if score_result['strengths']:
                print(f"\n💪 Strengths: {', '.join(score_result['strengths'])}")
            
            if score_result['improvement_areas']:
                print(f"🔧 Improvement Areas: {', '.join(score_result['improvement_areas'])}")
            
            if score_result['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in score_result['recommendations']:
                    print(f"  • {rec}")
            
            return score_result
            
        except Exception as e:
            print(f"❌ Error analyzing resume: {e}")
            raise e
    
    async def enrich_resume(
        self,
        resume_file: str,
        enrichment_type: str,
        job_file: str = None,
        output_file: str = None
    ) -> Dict[str, Any]:
        """Enrich resume with additional data"""
        try:
            # Load resume
            resume_content = await self._load_json_file(resume_file)
            
            if not resume_content:
                raise ValueError("Invalid resume file")
            
            # Load job description if needed
            job_description = None
            if job_file:
                job_description = await self._load_json_file(job_file)
            
            print(f"⚡ Enriching resume ({enrichment_type})...")
            
            # Create enrichment task
            task = EnrichmentTask(
                task_id=f"enrich_{datetime.utcnow().timestamp()}",
                resume_id="cli_resume",
                resume_content=resume_content,
                enrichment_type=enrichment_type,
                job_description=job_description
            )
            
            # Process enrichment
            result = await self.enrichment_worker._perform_enrichment(task)
            
            # Save enriched resume
            if output_file:
                await self._save_result(result['enriched_resume'], output_file)
                print(f"✅ Enriched resume saved to: {output_file}")
            
            # Display summary
            if enrichment_type == "comprehensive":
                print(f"📊 Comprehensive Score: {result['comprehensive_score']:.2f}")
            elif enrichment_type == "ats":
                print(f"🤖 ATS Score: {result['ats_score']:.2f}")
            elif enrichment_type == "alignment":
                print(f"🎯 Alignment Score: {result['alignment_score']:.2f}")
            elif enrichment_type == "skills":
                print(f"🛠️  Expanded Skills: {len(result['expanded_skills'])}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error enriching resume: {e}")
            raise e
    
    async def start_workers(self):
        """Start background workers"""
        print("🚀 Starting resume engine workers...")
        
        # Start workers
        await asyncio.gather(
            self.resume_worker.start_worker(),
            self.enrichment_worker.start_worker()
        )
        
        print("✅ Workers started successfully")
        
        # Display status
        resume_status = await self.resume_worker.get_worker_status()
        enrichment_status = await self.enrichment_worker.get_worker_status()
        
        print(f"\n📊 Resume Worker: {resume_status['queue_size']} tasks queued")
        print(f"📊 Enrichment Worker: {enrichment_status['queue_size']} tasks queued")
    
    async def stop_workers(self):
        """Stop background workers"""
        print("🛑 Stopping resume engine workers...")
        
        await asyncio.gather(
            self.resume_worker.stop_worker(),
            self.enrichment_worker.stop_worker()
        )
        
        print("✅ Workers stopped successfully")
    
    async def _load_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load JSON file"""
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ Error loading file {file_path}: {e}")
            return None
    
    async def _save_result(self, result: Dict[str, Any], output_file: str):
        """Save result to file"""
        try:
            path = Path(output_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
                
        except Exception as e:
            print(f"❌ Error saving result: {e}")
            raise e

def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Resume Engine CLI - Generate and optimize resumes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate resume from profile and job description
  python run_resume_engine.py generate profile.json job.json -o resume.json
  
  # Analyze resume quality
  python run_resume_engine.py analyze resume.json job.json
  
  # Enrich resume for ATS optimization
  python run_resume_engine.py enrich resume.json ats -o enriched.json
  
  # Start background workers
  python run_resume_engine.py workers start
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate resume')
    gen_parser.add_argument('profile', help='User profile JSON file')
    gen_parser.add_argument('job', help='Job description JSON file')
    gen_parser.add_argument('-o', '--output', help='Output file path')
    gen_parser.add_argument('-f', '--format', choices=['json', 'text'], default='json', help='Output format')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze resume')
    analyze_parser.add_argument('resume', help='Resume JSON file')
    analyze_parser.add_argument('job', nargs='?', help='Job description JSON file (optional)')
    
    # Enrich command
    enrich_parser = subparsers.add_parser('enrich', help='Enrich resume')
    enrich_parser.add_argument('resume', help='Resume JSON file')
    enrich_parser.add_argument('type', choices=['skills', 'ats', 'alignment', 'comprehensive'], help='Enrichment type')
    enrich_parser.add_argument('job', nargs='?', help='Job description JSON file (optional)')
    enrich_parser.add_argument('-o', '--output', help='Output file path')
    
    # Workers command
    workers_parser = subparsers.add_parser('workers', help='Manage background workers')
    workers_parser.add_argument('action', choices=['start', 'stop', 'status'], help='Worker action')
    
    # Global options
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    return parser

async def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ResumeEngineCLI()
    
    try:
        if args.command == 'generate':
            preferences = {"format": args.format}
            await cli.generate_resume(args.profile, args.job, args.output, preferences)
        
        elif args.command == 'analyze':
            await cli.analyze_resume(args.resume, args.job)
        
        elif args.command == 'enrich':
            await cli.enrich_resume(args.resume, args.type, args.job, args.output)
        
        elif args.command == 'workers':
            if args.action == 'start':
                await cli.start_workers()
                # Keep running
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping workers...")
                    await cli.stop_workers()
            elif args.action == 'stop':
                await cli.stop_workers()
            elif args.action == 'status':
                resume_status = await cli.resume_worker.get_worker_status()
                enrichment_status = await cli.enrichment_worker.get_worker_status()
                
                print("📊 Worker Status:")
                print(f"  Resume Worker: {'Active' if resume_status['active'] else 'Inactive'}")
                print(f"    Queue: {resume_status['queue_size']} tasks")
                print(f"    Processing: {resume_status['processing_tasks']} tasks")
                print(f"  Enrichment Worker: {'Active' if enrichment_status['active'] else 'Inactive'}")
                print(f"    Queue: {enrichment_status['queue_size']} tasks")
                print(f"    Processing: {enrichment_status['processing_tasks']} tasks")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
