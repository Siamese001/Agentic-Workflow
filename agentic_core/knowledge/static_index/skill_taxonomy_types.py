"""
Skill Taxonomy - Professional Skills Categorization

Zero-Ambiguity Standard: Named with _types.py suffix
Category: TYPES (Static knowledge taxonomy)

Provides categorized skills for professional content matching and generation.
"""
from typing import Final
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
SKILL_TAXONOMY: Final[dict[str, list[str]]] = {'AI/ML': ['Machine Learning', 'Deep Learning', 'Natural Language Processing', 'Computer Vision', 'Reinforcement Learning', 'Neural Networks', 'TensorFlow', 'PyTorch', 'Transformers', 'LLMs', 'RAG', 'Vector Databases', 'Embeddings', 'Fine-tuning', 'Prompt Engineering'], 'Backend': ['Python', 'Java', 'Go', 'Rust', 'Node.js', 'FastAPI', 'Django', 'Flask', 'Spring Boot', 'REST APIs', 'GraphQL', 'gRPC', 'Microservices', 'Event-Driven Architecture', 'Message Queues'], 'Frontend': ['React', 'Vue.js', 'Angular', 'TypeScript', 'JavaScript', 'HTML/CSS', 'Tailwind CSS', 'Next.js', 'Svelte', 'Redux', 'Responsive Design', 'Web Components', 'PWA'], 'Cloud': ['AWS', 'GCP', 'Azure', 'Kubernetes', 'Docker', 'Terraform', 'CloudFormation', 'Serverless', 'Lambda', 'EC2', 'S3', 'Cloud Functions', 'CDN', 'Load Balancing'], 'Data': ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Apache Kafka', 'Apache Spark', 'Data Pipelines', 'ETL', 'Data Warehousing', 'BigQuery', 'Snowflake', 'dbt'], 'DevOps': ['CI/CD', 'GitHub Actions', 'Jenkins', 'GitLab CI', 'Ansible', 'Prometheus', 'Grafana', 'ELK Stack', 'Infrastructure as Code', 'Site Reliability Engineering', 'Monitoring', 'Logging', 'Alerting'], 'Security': ['Application Security', 'Penetration Testing', 'OWASP', 'Authentication', 'Authorization', 'OAuth', 'JWT', 'Encryption', 'Zero Trust', 'SAST/DAST', 'Vulnerability Assessment', 'Compliance'], 'Leadership': ['Team Leadership', 'Technical Leadership', 'Project Management', 'Agile/Scrum', 'Stakeholder Management', 'Mentoring', 'Cross-functional Collaboration', 'Strategic Planning', 'Roadmap Development', 'Technical Vision']}
ALL_SKILLS: Final[list[str]] = [skill for skills in SKILL_TAXONOMY.values() for skill in skills]
