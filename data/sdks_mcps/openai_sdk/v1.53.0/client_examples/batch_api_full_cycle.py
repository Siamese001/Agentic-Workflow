"""OpenAI v1.53.0 - Batch API Full Cycle Implementation
Production client for processing large volumes of resume extractions.
"""

import os
import time
import json
from typing import List, Dict, object, Optional
from openai import OpenAI
from openai.types.batches import Batch


class BatchProcessor:
    """Handles OpenAI Batch API operations for resume processing."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.endpoint = "https://api.openai.com/v1/chat/completions"
    
    def create_batch_file(
        self, 
        requests: List[Dict[str, object]], 
        output_path: str
    ) -> str:
        """Create JSONL batch file for submission.
        
        Args:
            requests: List of completion requests
            output_path: Path to save batch file
            
        Returns:
            Path to created batch file
        """
        with open(output_path, 'w') as f:
            for req in requests:
                json.dump(req, f)
                f.write('\n')
        return output_path
    
    def upload_batch_file(self, file_path: str) -> str:
        """Upload batch file to OpenAI storage.
        
        Args:
            file_path: Path to batch file
            
        Returns:
            File ID from OpenAI
        """
        with open(file_path, 'rb') as f:
            response = self.client.files.create(
                file=f,
                purpose="batch"
            )
        return response.id
    
    def submit_batch(
        self, 
        file_id: str, 
        description: Optional[str] = None,
        completion_window: str = "24h"
    ) -> Batch:
        """Submit batch for processing.
        
        Args:
            file_id: Uploaded file ID
            description: Optional batch description
            completion_window: Processing time window
            
        Returns:
            Batch object
        """
        return self.client.batches.create(
            input_file_id=file_id,
            endpoint=self.endpoint,
            completion_window=completion_window,
            metadata={"description": description} if description else None
        )
    
    def wait_for_completion(
        self, 
        batch_id: str, 
        poll_interval: int = 30,
        timeout: int = 3600
    ) -> Batch:
        """Wait for batch completion with polling.
        
        Args:
            batch_id: Batch ID to monitor
            poll_interval: Seconds between polls
            timeout: Maximum wait time
            
        Returns:
            Completed batch object
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            batch = self.client.batches.retrieve(batch_id)
            
            if batch.status in ["completed", "failed", "cancelled", "expired"]:
                return batch
            
            print(f"Batch {batch_id} status: {batch.status} - {batch.request_counts.completed}/{batch.request_counts.total} completed")
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Batch {batch_id} did not complete within {timeout} seconds")
    
    def download_results(self, batch: Batch, output_path: str) -> List[Dict[str, object]]:
        """Download and parse batch results.
        
        Args:
            batch: Completed batch object
            output_path: Path to save results
            
        Returns:
            List of completion results
        """
        if batch.status != "completed":
            raise ValueError(f"Batch not completed: {batch.status}")
        
        # Download result file
        result_content = self.client.files.content(batch.output_file_id)
        results = []
        
        for line in result_content.text.split('\n'):
            if line.strip():
                results.append(json.loads(line))
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def full_batch_cycle(
        self, 
        requests: List[Dict[str, object]],
        batch_name: str = "resume_batch"
    ) -> Dict[str, object]:
        """Execute complete batch processing cycle.
        
        Args:
            requests: List of completion requests
            batch_name: Name for batch files
            
        Returns:
            Results dictionary with metadata
        """
        # Create batch file
        batch_file = f"{batch_name}_requests.jsonl"
        self.create_batch_file(requests, batch_file)
        
        # Upload file
        file_id = self.upload_batch_file(batch_file)
        print(f"Uploaded batch file: {file_id}")
        
        # Submit batch
        batch = self.submit_batch(file_id, f"Resume processing batch - {batch_name}")
        print(f"Submitted batch: {batch.id}")
        
        # Wait for completion
        completed_batch = self.wait_for_completion(batch.id)
        print(f"Batch completed with status: {completed_batch.status}")
        
        # Download results
        results_file = f"{batch_name}_results.json"
        results = self.download_results(completed_batch, results_file)
        
        return {
            "batch_id": completed_batch.id,
            "status": completed_batch.status,
            "requests_count": len(requests),
            "results_count": len(results),
            "results": results,
            "file_id": file_id,
            "output_file_id": completed_batch.output_file_id
        }


def create_resume_requests(resumes: List[str]) -> List[Dict[str, object]]:
    """Create batch requests for resume extraction.
    
    Args:
        resumes: List of resume texts
        
    Returns:
        List of formatted batch requests
    """
    requests = []
    
    for i, resume in enumerate(resumes):
        request = {
            "custom_id": f"resume_{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-2024-08-06",
                "messages": [
                    {
                        "role": "system",
                        "content": "Extract key information from the resume. Return JSON with name, email, experience, and education."
                    },
                    {
                        "role": "user",
                        "content": f"Extract information from: {resume}"
                    }
                ],
                "response_format": {"type": "json_object"},
                "max_tokens": 1000,
                "temperature": 0.1
            }
        }
        requests.append(request)
    
    return requests


if __name__ == "__main__":
    # Example usage
    sample_resumes = [
        "Jane Smith\nSoftware Engineer at ABC Corp\nBS Computer Science, MIT",
        "John Doe\nData Scientist at XYZ Inc\nPhD Statistics, Stanford"
    ]
    
    processor = BatchProcessor()
    
    # Create batch requests
    requests = create_resume_requests(sample_resumes)
    
    # Execute full batch cycle
    try:
        results = processor.full_batch_cycle(requests, "test_resume_batch")
        print(f"Batch completed: {results['status']}")
        print(f"Processed {results['requests_count']} requests")
        print(f"Generated {results['results_count']} results")
    except Exception as e:
        print(f"Batch processing failed: {e}")
