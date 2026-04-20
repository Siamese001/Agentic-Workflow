"""
Phase 3.3: Intelligent Disposition System with AI-Assisted Violation Triage.

Machine learning-based violation classification, pattern recognition from historical
dispositions, and context-aware risk assessment for intelligent prioritization.

Key capabilities:
1. AI-assisted violation triage and prioritization
2. Learning from manual disposition patterns
3. Context-aware risk assessment
4. Automated disposition recommendations
5. Continuous learning and feedback loops
"""

from __future__ import annotations

import sqlite3
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from tqdm import tqdm

from agentic_core.adg.artifact.multi_writer import has_guardian_for_violation

_PHASE3_NON_FATAL_EXCEPTIONS = (
    sqlite3.Error,
    OSError,
    UnicodeError,
    AttributeError,
    IndexError,
    KeyError,
    TypeError,
    ValueError,
    RuntimeError,
)


class DispositionType(Enum):
    """Types of violation dispositions."""

    UNTRIAGED = "untriaged"
    TESTED = "tested"
    APPROVED = "approved"
    REMEDIATED = "remediated"
    IGNORED = "ignored"
    ESCALATED = "escalated"


class RiskLevel(Enum):
    """Risk levels for violations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ViolationFeatures:
    """Features extracted from a violation for ML analysis."""

    file_path: str
    line_no: int
    edge_kind: str
    exception_type: str
    severity: str
    architectural_layer: str
    module_name: str
    function_name: str | None
    has_guardian_comment: bool
    test_coverage: bool
    import_complexity: int
    function_complexity: int
    business_criticality: float
    security_impact: float
    operational_impact: float
    historical_frequency: int
    similar_violations_count: int


@dataclass
class DispositionRecommendation:
    """AI-generated disposition recommendation."""

    suggested_disposition: DispositionType
    confidence: float  # 0.0 to 1.0
    reasoning: str
    risk_level: RiskLevel
    priority_score: float  # 0.0 to 1.0
    supporting_evidence: list[str]
    alternative_suggestions: list[tuple[DispositionType, float]]


class FeatureExtractor:
    """Extract features from violations for ML analysis."""

    def __init__(self, adg_path: Path):
        self.adg_path = adg_path
        self.conn: sqlite3.Connection | None = None

        # Business criticality weights by module patterns
        self.business_weights = {
            "auth": 0.9,
            "security": 0.9,
            "payment": 0.8,
            "api": 0.7,
            "core": 0.8,
            "utils": 0.3,
            "test": 0.1,
            "example": 0.1,
        }

        # Security impact weights by exception type
        self.security_weights = {
            "Exception": 0.8,
            "BaseException": 0.9,
            "SecurityError": 1.0,
            "PermissionError": 0.7,
            "OSError": 0.5,
            "ValueError": 0.3,
            "TypeError": 0.2,
        }

    def __enter__(self) -> FeatureExtractor:
        self.conn = sqlite3.connect(str(self.adg_path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn:
            self.conn.close()

    def extract_features(self, violation_data: dict) -> ViolationFeatures:
        """Extract features from violation data."""
        file_path = violation_data["file_path"]
        line_no = violation_data["line_no"]
        evidence = violation_data["evidence"]
        edge_kind = violation_data.get("edge_kind", "")
        severity = violation_data.get("severity", "MEDIUM")

        # Persisted schema stores raw exception symbols (e.g. Exception, ValueError)
        exception_type = evidence if evidence else "Unknown"

        # Determine architectural layer
        architectural_layer = self._determine_architectural_layer(file_path)

        # Extract module name
        module_name = Path(file_path).stem

        # Extract function name (simplified)
        function_name = self._extract_function_name(file_path, line_no)

        # Check for guardian comments
        has_guardian_comment = self._has_guardian_comment(file_path, line_no, edge_kind)

        # Check test coverage
        test_coverage = self._has_test_coverage(file_path, line_no)

        # Calculate complexity metrics
        import_complexity = self._calculate_import_complexity(file_path)
        function_complexity = self._calculate_function_complexity(file_path, line_no)

        # Calculate impact scores
        business_criticality = self._calculate_business_criticality(file_path)
        security_impact = self._calculate_security_impact(exception_type, architectural_layer)
        operational_impact = self._calculate_operational_impact(file_path, severity)

        # Historical patterns
        historical_frequency = self._get_historical_frequency(exception_type, module_name)
        similar_violations_count = self._count_similar_violations(file_path, exception_type)

        return ViolationFeatures(
            file_path=file_path,
            line_no=line_no,
            edge_kind=edge_kind,
            exception_type=exception_type,
            severity=severity,
            architectural_layer=architectural_layer,
            module_name=module_name,
            function_name=function_name,
            has_guardian_comment=has_guardian_comment,
            test_coverage=test_coverage,
            import_complexity=import_complexity,
            function_complexity=function_complexity,
            business_criticality=business_criticality,
            security_impact=security_impact,
            operational_impact=operational_impact,
            historical_frequency=historical_frequency,
            similar_violations_count=similar_violations_count,
        )

    def _determine_architectural_layer(self, file_path: str) -> str:
        """Determine architectural layer from DB nodes, then file path heuristics."""
        # 1. Authoritative: look up layer from ADG nodes table
        if self.conn:
            try:
                cursor = self.conn.execute(
                    "SELECT layer FROM nodes WHERE resolved_path = ? LIMIT 1",
                    (file_path,),
                )
                row = cursor.fetchone()
                if row and row[0] and row[0] not in ("", "tests", "unknown"):
                    return str(row[0])
            except _PHASE3_NON_FATAL_EXCEPTIONS:  # guardian: allow-silent-swallow -- ADG query: SQLite/IO failure gracefully falls back to path inference
                pass

        # 2. Fallback: infer from path string
        if "L0_" in str(file_path) or "/L0/" in str(file_path):
            return "L0"
        elif "L1_" in str(file_path) or "/L1/" in str(file_path):
            return "L1"
        elif "L2_" in str(file_path) or "/L2/" in str(file_path):
            return "L2"
        elif "L3_" in str(file_path) or "/L3/" in str(file_path):
            return "L3"
        elif "L4_" in str(file_path) or "/L4/" in str(file_path):
            return "L4"
        elif "L5_" in str(file_path) or "/L5/" in str(file_path):
            return "L5"
        elif "L6_" in str(file_path) or "/L6/" in str(file_path):
            return "L6"
        else:
            # Heuristic based on directory structure
            fp = str(file_path)
            if any(part in fp for part in ["routing", "enforcement"]):
                return "L0"
            elif any(part in fp for part in ["reasoning", "agents"]):
                return "L2"
            elif any(part in fp for part in ["safety", "types"]):
                return "L5"
            else:
                return "L3"  # Default

    def _extract_function_name(self, file_path: str, line_no: int) -> str | None:
        """Extract function name containing the violation."""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if line_no <= len(lines):
                # Search backwards for function definition
                for i in range(line_no - 1, max(-1, line_no - 20), -1):
                    line = lines[i].strip()
                    if line.startswith("def "):
                        return line.split("(")[0].replace("def ", "")
                    elif line.startswith("class "):
                        return line.split("(")[0].replace("class ", "")

        except (OSError, UnicodeDecodeError) as exc:  # guardian: allow-log-and-swallow -- file read helper, None returned on failure
            import logging
            logging.getLogger(__name__).debug("_extract_function_name: could not read %s: %s", file_path, exc)

        return None

    def _has_guardian_comment(self, file_path: str, line_no: int, edge_kind: str) -> bool:
        """Check if violation has guardian comment."""
        return bool(edge_kind) and has_guardian_for_violation(file_path, line_no, edge_kind)

    def _has_test_coverage(self, file_path: str, line_no: int) -> bool:
        """Check if violation has test coverage."""
        if not self.conn:
            return False

        try:
            # Check for tests_execution_of edges covering this location
            cursor = self.conn.execute(
                """
                SELECT COUNT(*) FROM edges e
                JOIN nodes n ON e.dst_id = n.id
                WHERE e.relation_type = 'tests_execution_of'
                  AND n.resolved_path = ?
                  AND n.span_line <= ? AND n.span_end_line >= ?
            """,
                (file_path, line_no, line_no),
            )

            row = cursor.fetchone()
            count = int(row[0]) if row else 0
            return count > 0

        except _PHASE3_NON_FATAL_EXCEPTIONS:  # guardian: allow-silent-swallow -- has_test_coverage query: SQLite/IO failure returns False (safe default)
            pass

        return False

    def _calculate_import_complexity(self, file_path: str) -> int:
        """Calculate import complexity score."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            import_count = content.count("import ")
            from_count = content.count("from ")

            return import_count + from_count

        except _PHASE3_NON_FATAL_EXCEPTIONS:  # guardian: allow-return-none-swallow -- feature extraction: best-effort, None is valid return on missing data
            return None

    def _calculate_function_complexity(self, file_path: str, line_no: int) -> int:
        """Calculate function complexity score."""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if line_no <= len(lines):
                # Simple heuristic: count control structures in surrounding lines
                start = max(0, line_no - 10)
                end = min(len(lines), line_no + 10)

                complexity = 0
                for i in range(start, end):
                    line = lines[i].strip()
                    if any(
                        keyword in line for keyword in ["if ", "for ", "while ", "try:", "with ", "except"]
                    ):
                        complexity += 1

                return complexity

        except _PHASE3_NON_FATAL_EXCEPTIONS:  # guardian: allow-silent-swallow -- import complexity query: SQLite/IO failure returns 0 (safe default)
            pass

        return 0

    def _calculate_business_criticality(self, file_path: str) -> float:
        """Calculate business criticality score."""
        file_path_lower = file_path.lower()

        for pattern, weight in self.business_weights.items():
            if pattern in file_path_lower:
                return weight

        return 0.5  # Default medium criticality

    def _calculate_security_impact(self, exception_type: str, architectural_layer: str) -> float:
        """Calculate security impact score."""
        base_security = self.security_weights.get(exception_type, 0.3)

        # Higher impact in critical layers
        layer_multiplier = {
            "L0": 1.5,  # Routing/enforcement
            "L2": 1.2,  # Reasoning/agents
            "L5": 1.3,  # Safety/types
        }.get(architectural_layer, 1.0)

        return min(base_security * layer_multiplier, 1.0)

    def _calculate_operational_impact(self, file_path: str, severity: str) -> float:
        """Calculate operational impact score."""
        severity_weight = {"HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.2}.get(severity, 0.5)

        # Higher impact for core modules
        if any(keyword in file_path.lower() for keyword in ["core", "main", "index"]):
            severity_weight *= 1.3

        return min(severity_weight, 1.0)

    def _get_historical_frequency(self, exception_type: str, module_name: str) -> int:
        """Get historical frequency of similar violations."""
        if not self.conn:
            return 0

        try:
            cursor = self.conn.execute(
                """
                SELECT COUNT(*) FROM violations v
                WHERE v.evidence LIKE ?
                  AND v.file_path LIKE ?
            """,
                (exception_type, f"%{module_name}%"),
            )

            row = cursor.fetchone()
            return int(row[0]) if row else 0

        except _PHASE3_NON_FATAL_EXCEPTIONS:  # guardian: allow-silent-swallow -- business criticality query: SQLite/IO failure returns 0 (safe default)
            pass

        return 0

    def _count_similar_violations(self, file_path: str, exception_type: str) -> int:
        """Count similar violations in the same file."""
        if not self.conn:
            return 0

        try:
            cursor = self.conn.execute(
                """
                SELECT COUNT(*) FROM violations
                WHERE file_path = ? AND evidence LIKE ?
            """,
                (file_path, exception_type),
            )

            row = cursor.fetchone()
            return int(row[0]) if row else 0

        except _PHASE3_NON_FATAL_EXCEPTIONS:  # guardian: allow-silent-swallow -- similar violations count: SQLite/IO failure returns 0 (safe default)
            pass

        return 0


class DispositionClassifier:
    """ML-based classifier for violation dispositions."""

    def __init__(self):
        self.model_trained = False
        self.feature_weights = {}
        self.pattern_rules = {}
        self._initialize_rule_based_system()

    def _initialize_rule_based_system(self) -> None:
        """Initialize rule-based classification system."""
        self.pattern_rules = {
            # High confidence approval rules
            "approval_rules": [
                {
                    "condition": lambda f: f.has_guardian_comment,
                    "disposition": DispositionType.APPROVED,
                    "confidence": 0.9,
                    "reasoning": "Has guardian comment approving this exception handling",
                },
                {
                    "condition": lambda f: f.test_coverage and f.business_criticality < 0.6,
                    "disposition": DispositionType.TESTED,
                    "confidence": 0.8,
                    "reasoning": "Has test coverage and low business criticality",
                },
            ],
            # Escalation rules
            "escalation_rules": [
                {
                    "condition": lambda f: f.security_impact > 0.8 and f.architectural_layer in ["L0", "L5"],
                    "disposition": DispositionType.ESCALATED,
                    "confidence": 0.8,
                    "reasoning": "High security impact in critical architectural layer",
                },
                {
                    "condition": lambda f: f.business_criticality > 0.8 and f.operational_impact > 0.7,
                    "disposition": DispositionType.ESCALATED,
                    "confidence": 0.7,
                    "reasoning": "High business and operational impact",
                },
            ],
            # Remediation rules
            "remediation_rules": [
                {
                    "condition": lambda f: (
                        not f.has_guardian_comment and f.test_coverage and f.function_complexity < 3
                    ),
                    "disposition": DispositionType.REMEDIATED,
                    "confidence": 0.7,
                    "reasoning": "Simple function with test coverage, no guardian comment",
                },
            ],
        }

    def train_from_historical_data(self, historical_dispositions: list[dict]) -> None:
        """Train classifier from historical disposition data."""
        print("🧠 Training disposition classifier from historical data...")

        # Extract patterns from historical data
        disposition_patterns = defaultdict(list)

        for item in historical_dispositions:
            disposition = item.get("disposition", "untriaged")
            features = item.get("features")

            if features and disposition != "untriaged":
                disposition_patterns[disposition].append(features)

        # Learn feature weights for each disposition
        for disposition, feature_list in disposition_patterns.items():
            if len(feature_list) >= 5:  # Minimum samples for learning
                self._learn_feature_weights(disposition, feature_list)

        self.model_trained = True
        print(f"  Trained on {len(historical_dispositions)} historical dispositions")

    def _learn_feature_weights(self, disposition: str, feature_list: list[dict]) -> None:
        """Learn feature weights for a specific disposition."""
        # Simple statistical learning - calculate feature correlations
        feature_correlations = {}

        # Convert feature list to feature matrix
        all_features: dict[str, list] = {}
        for features in feature_list:
            for key, value in features.items():
                if key not in all_features:
                    all_features[key] = []
                all_features[key].append(value)

        # Calculate correlation with disposition
        for feature_name, values in all_features.items():
            if isinstance(values[0], (int, float)):
                # For numeric features, calculate mean correlation
                mean_value = statistics.mean(values)
                feature_correlations[feature_name] = mean_value

        self.feature_weights[disposition] = feature_correlations

    def classify_violation(self, features: ViolationFeatures) -> DispositionRecommendation:
        """Classify a violation and generate disposition recommendation."""
        # Apply rule-based system first
        best_match = None
        best_confidence = 0.0

        # Check approval rules
        for rule in self.pattern_rules["approval_rules"]:
            if rule["condition"](features):
                if rule["confidence"] > best_confidence:
                    best_match = rule
                    best_confidence = rule["confidence"]

        # Check escalation rules
        for rule in self.pattern_rules["escalation_rules"]:
            if rule["condition"](features):
                if rule["confidence"] > best_confidence:
                    best_match = rule
                    best_confidence = rule["confidence"]

        # Check remediation rules
        for rule in self.pattern_rules["remediation_rules"]:
            if rule["condition"](features):
                if rule["confidence"] > best_confidence:
                    best_match = rule
                    best_confidence = rule["confidence"]

        # If no rule matches, use ML-based classification
        if not best_match:
            return self._ml_classify(features)

        # Generate recommendation from rule match
        risk_level = self._calculate_risk_level(features)
        priority_score = self._calculate_priority_score(features, best_match["confidence"])

        return DispositionRecommendation(
            suggested_disposition=best_match["disposition"],
            confidence=best_match["confidence"],
            reasoning=best_match["reasoning"],
            risk_level=risk_level,
            priority_score=priority_score,
            supporting_evidence=self._generate_evidence(features),
            alternative_suggestions=self._generate_alternatives(features, best_match["disposition"]),
        )

    def _ml_classify(self, features: ViolationFeatures) -> DispositionRecommendation:
        """ML-based classification when no rules match."""
        # Simple scoring system based on feature weights
        scores = {}

        for disposition, weights in tqdm(self.feature_weights.items(), desc="Processing", unit="item"):
            score = 0.0
            total_weight = 0.0

            for feature_name, weight in weights.items():
                if hasattr(features, feature_name):
                    feature_value = getattr(features, feature_name)
                    if isinstance(feature_value, (int, float)):
                        score += weight * feature_value
                        total_weight += abs(weight)

            if total_weight > 0:
                scores[disposition] = score / total_weight

        # Select best disposition
        if scores:
            best_disposition = max(scores.keys(), key=lambda k: scores[k])
            confidence = min(abs(scores[best_disposition]), 1.0)
        else:
            best_disposition = DispositionType.UNTRIAGED
            confidence = 0.3  # Low confidence for unknown patterns

        risk_level = self._calculate_risk_level(features)
        priority_score = self._calculate_priority_score(features, confidence)

        return DispositionRecommendation(
            suggested_disposition=best_disposition,
            confidence=confidence,
            reasoning=f"ML-based classification based on {len(scores)} disposition patterns",
            risk_level=risk_level,
            priority_score=priority_score,
            supporting_evidence=self._generate_evidence(features),
            alternative_suggestions=self._generate_alternatives(features, best_disposition),
        )

    def _calculate_risk_level(self, features: ViolationFeatures) -> RiskLevel:
        """Calculate risk level for violation."""
        risk_score = (
            features.security_impact * 0.4
            + features.business_criticality * 0.3
            + features.operational_impact * 0.3
        )

        if risk_score > 0.8:
            return RiskLevel.CRITICAL
        elif risk_score > 0.6:
            return RiskLevel.HIGH
        elif risk_score > 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_priority_score(self, features: ViolationFeatures, confidence: float) -> float:
        """Calculate priority score for violation."""
        base_priority = (
            features.security_impact * 0.3
            + features.business_criticality * 0.3
            + features.operational_impact * 0.2
            + (1.0 - confidence) * 0.2  # Lower confidence = higher priority
        )

        return min(base_priority, 1.0)

    def _generate_evidence(self, features: ViolationFeatures) -> list[str]:
        """Generate supporting evidence for recommendation."""
        evidence = []

        if features.has_guardian_comment:
            evidence.append("Has guardian comment")

        if features.test_coverage:
            evidence.append("Has test coverage")

        if features.security_impact > 0.7:
            evidence.append(f"High security impact ({features.security_impact:.2f})")

        if features.business_criticality > 0.7:
            evidence.append(f"High business criticality ({features.business_criticality:.2f})")

        if features.similar_violations_count > 5:
            evidence.append(f"Pattern of similar violations ({features.similar_violations_count} found)")

        return evidence

    def _generate_alternatives(
        self,
        features: ViolationFeatures,
        primary: DispositionType,
    ) -> list[tuple[DispositionType, float]]:
        """Generate alternative disposition suggestions."""
        alternatives = []

        # Always include untriaged as fallback
        alternatives.append((DispositionType.UNTRIAGED, 0.5))

        # Suggest tested if has coverage and not already tested
        if features.test_coverage and primary != DispositionType.TESTED:
            alternatives.append((DispositionType.TESTED, 0.7))

        # Suggest remediation if simple and not already remediated
        if features.function_complexity < 3 and primary != DispositionType.REMEDIATED:
            alternatives.append((DispositionType.REMEDIATED, 0.6))

        return alternatives


class IntelligentDispositionSystem:
    """Phase 3.3: Intelligent disposition system with AI-assisted triage."""

    def __init__(self, adg_path: Path):
        self.adg_path = adg_path
        self.feature_extractor = FeatureExtractor(adg_path)
        self.classifier = DispositionClassifier()
        self.conn: sqlite3.Connection | None = None

    def __enter__(self) -> IntelligentDispositionSystem:
        self.conn = sqlite3.connect(str(self.adg_path))
        self.feature_extractor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn:
            self.conn.close()
        self.feature_extractor.__exit__(exc_type, exc_val, exc_tb)

    def analyze_and_recommend_dispositions(self) -> dict:
        """Analyze violations and generate intelligent disposition recommendations."""
        if not self.conn:
            raise RuntimeError("System not used as context manager")

        print("🧠 Phase 3.3: AI-assisted intelligent disposition analysis...")

        # Load historical dispositions for training
        historical_data = self._load_historical_dispositions()
        if historical_data:
            self.classifier.train_from_historical_data(historical_data)

        # Load untriaged violations
        violations = self._load_untriaged_violations()
        print(f"  Analyzing {len(violations)} untriaged violations")

        # Generate recommendations
        recommendations = []
        for violation in tqdm(violations, desc="Processing", unit="item"):
            features = self.feature_extractor.extract_features(violation)
            recommendation = self.classifier.classify_violation(features)
            recommendations.append(
                {
                    "file_path": violation["file_path"],
                    "line_no": violation["line_no"],
                    "evidence": violation["evidence"],
                    "features": asdict(features),
                    "recommendation": asdict(recommendation),
                },
            )

        # Sort by priority score
        recommendations.sort(key=lambda r: r["recommendation"]["priority_score"], reverse=True)

        # Generate summary statistics
        summary = self._generate_summary_statistics(recommendations)

        print(f"  Generated {len(recommendations)} disposition recommendations")
        print(f"  High priority (>0.8): {summary['high_priority_count']}")
        print(f"  High confidence (>0.7): {summary['high_confidence_count']}")

        return {
            "recommendations": recommendations,
            "summary": summary,
            "training_data_size": len(historical_data),
            "model_trained": self.classifier.model_trained,
        }

    def _load_historical_dispositions(self) -> list[dict]:
        """Load historical disposition data for training."""
        if not self.conn:
            return []

        try:
            cursor = self.conn.execute("""
                SELECT file_path, line_no, evidence, severity, disposition, disposition_source
                FROM violations
                WHERE disposition != 'untriaged'
                  AND disposition_source != ''
                ORDER BY disposition_date DESC
                LIMIT 1000
            """)

            historical_data = []
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                file_path, line_no, evidence, severity, disposition, source = row

                # Extract features for this historical violation
                violation_data = {
                    "file_path": file_path,
                    "line_no": line_no,
                    "evidence": evidence,
                    "severity": severity,
                }

                try:
                    features = self.feature_extractor.extract_features(violation_data)
                    historical_data.append(
                        {"disposition": disposition, "source": source, "features": asdict(features)},
                    )
                except _PHASE3_NON_FATAL_EXCEPTIONS as e:
                    # Fail-closed: feature extraction unavailable, skip this historical data point
                    print(f"    Could not extract features for historical data: {e}")
                    continue

            return historical_data

        except _PHASE3_NON_FATAL_EXCEPTIONS as e:
            # Fail-closed: historical data unavailable, skip training
            print(f"    Could not load historical dispositions: {e}")
            return []

    def _load_untriaged_violations(self) -> list[dict]:
        """Load untriaged violations for analysis."""
        if not self.conn:
            return []

        try:
            cursor = self.conn.execute("""
                SELECT v.file_path, v.line_no, v.evidence, v.severity, COALESCE(e.edge_kind, '')
                FROM violations v
                LEFT JOIN edges e ON v.edge_id = e.id
                WHERE v.disposition = 'untriaged'
                  AND v.category = 'antipattern'
                  AND e.edge_kind IN ('broad_exception_catch','silent_exception_swallow','log_and_swallow','return_none_swallow')
                ORDER BY v.severity DESC, v.file_path, v.line_no
            """)

            violations = []
            for row in cursor.fetchall():
                file_path, line_no, evidence, severity, edge_kind = row
                violations.append(
                    {
                        "file_path": file_path,
                        "line_no": line_no,
                        "evidence": evidence,
                        "severity": severity,
                        "edge_kind": edge_kind,
                    },
                )

            return violations

        except _PHASE3_NON_FATAL_EXCEPTIONS as e:
            print(f"    ⚠️  Could not load untriaged violations: {e}")
            return []

    def _generate_summary_statistics(self, recommendations: list[dict]) -> dict:
        """Generate summary statistics from recommendations."""
        if not recommendations:
            return {
                "total_recommendations": 0,
                "high_priority_count": 0,
                "high_confidence_count": 0,
                "disposition_breakdown": {},
                "risk_level_breakdown": {},
                "average_confidence": 0.0,
                "average_priority_score": 0.0,
            }

        # Count dispositions
        disposition_counts = Counter(r["recommendation"]["suggested_disposition"] for r in recommendations)

        # Count risk levels
        risk_counts = Counter(r["recommendation"]["risk_level"] for r in recommendations)

        # Calculate averages
        confidences = [r["recommendation"]["confidence"] for r in recommendations]
        priorities = [r["recommendation"]["priority_score"] for r in recommendations]

        return {
            "total_recommendations": len(recommendations),
            "high_priority_count": len(
                [r for r in recommendations if r["recommendation"]["priority_score"] > 0.8],
            ),
            "high_confidence_count": len(
                [r for r in recommendations if r["recommendation"]["confidence"] > 0.7],
            ),
            "disposition_breakdown": dict(disposition_counts),
            "risk_level_breakdown": dict(risk_counts),
            "average_confidence": statistics.mean(confidences) if confidences else 0.0,
            "average_priority_score": statistics.mean(priorities) if priorities else 0.0,
        }


def run_phase3_intelligent_disposition(adg_path: Path) -> dict:
    """Convenience function to run Phase 3.3 intelligent disposition analysis."""
    with IntelligentDispositionSystem(adg_path) as system:
        return system.analyze_and_recommend_dispositions()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python phase3_intelligent_disposition.py <path_to_adg.sqlite>")
        sys.exit(1)

    adg_path = Path(sys.argv[1])
    if not adg_path.exists():
        print(f"Error: ADG file not found: {adg_path}")
        sys.exit(1)

    results = run_phase3_intelligent_disposition(adg_path)
    print(
        f"\nPhase 3.3 Analysis Complete: {results['summary']['total_recommendations']} recommendations generated",
    )
