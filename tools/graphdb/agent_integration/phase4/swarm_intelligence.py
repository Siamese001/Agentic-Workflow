"""Swarm Intelligence - Distributed architectural coordination and emergent behavior.

This module provides swarm intelligence capabilities that enable
distributed agent coordination with emergent collective intelligence.
"""

from __future__ import annotations

import logging
import time
import math
import random
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np
from datetime import datetime, timedelta

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from ..phase3.ecosystem_intelligence import EcosystemIntelligenceEngine

logger = logging.getLogger(__name__)


class SwarmRole(Enum):
    """Roles within the swarm."""

    EXPLORER = "explorer"  # Explores architectural space
    EXPLOITER = "exploiter"  # Exploits known good solutions
    SCOUT = "scout"  # Scouts for new opportunities
    COORDINATOR = "coordinator"  # Coordinates swarm activities
    OBSERVER = "observer"  # Observes and learns


class SwarmBehavior(Enum):
    """Types of swarm behaviors."""

    FORAGING = "foraging"  # Searching for architectural solutions
    NEST_BUILDING = "nest_building"  # Constructing architectural structures
    TASK_ALLOCATION = "task_allocation"  # Distributing architectural tasks
    COLLECTIVE_DECISION = "collective_decision"  # Making collective decisions
    ADAPTIVE_RESPONSE = "adaptive_response"  # Responding to changes


@dataclass
class SwarmAgent:
    """Represents an individual agent in the swarm."""

    agent_id: str
    role: SwarmRole
    position: np.ndarray  # Multi-dimensional position
    velocity: np.ndarray
    fitness: float
    personal_best: np.ndarray
    personal_best_fitness: float
    neighbors: List[str]
    memory: List[Dict[str, Any]]
    energy: float = 1.0
    age: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SwarmState:
    """Represents the overall state of the swarm."""

    swarm_id: str
    agents: Dict[str, SwarmAgent]
    global_best: np.ndarray
    global_best_fitness: float
    collective_fitness: float
    swarm_cohesion: float
    swarm_diversity: float
    convergence_rate: float
    behavior: SwarmBehavior
    iteration: int = 0


@dataclass
class SwarmCoordinationResult:
    """Result of swarm coordination."""

    coordination_id: str
    swarm_state: SwarmState
    collective_decision: Dict[str, Any]
    emergent_patterns: List[str]
    coordination_efficiency: float
    convergence_achieved: bool
    execution_time_seconds: float = 0.0


class SwarmIntelligenceEngine:
    """Swarm intelligence engine for distributed architectural coordination."""

    def __init__(self, ecosystem_engine: EcosystemIntelligenceEngine):
        """Initialize swarm intelligence engine.

        Args:
            ecosystem_engine: Ecosystem intelligence engine for context
        """
        self.ecosystem_engine = ecosystem_engine

        # Swarm configuration
        self.swarm_config = {
            "swarm_size": 20,
            "max_iterations": 100,
            "convergence_threshold": 0.95,
            "diversity_threshold": 0.1,
            "neighborhood_radius": 0.3,
            "inertia_weight": 0.7,
            "cognitive_weight": 1.5,
            "social_weight": 1.5,
            "energy_decay_rate": 0.99,
        }

        # Active swarms
        self.active_swarms: Dict[str, SwarmState] = {}

        # Swarm algorithms
        self.swarm_algorithms = {
            SwarmBehavior.FORAGING: self._particle_swarm_optimization,
            SwarmBehavior.NEST_BUILDING: self._ant_colony_optimization,
            SwarmBehavior.TASK_ALLOCATION: self._bee_algorithm,
            SwarmBehavior.COLLECTIVE_DECISION: self._consensus_algorithm,
            SwarmBehavior.ADAPTIVE_RESPONSE: self._adaptive_swarm_algorithm,
        }

        logger.info("SwarmIntelligenceEngine initialized")

    def coordinate_swarm(
        self,
        context: ArchitecturalContext,
        behavior: SwarmBehavior = SwarmBehavior.FORAGING,
        swarm_size: Optional[int] = None,
    ) -> SwarmCoordinationResult:
        """Coordinate swarm intelligence for architectural decision making.

        Args:
            context: Architectural context for coordination
            behavior: Type of swarm behavior to use
            swarm_size: Optional swarm size override

        Returns:
            SwarmCoordinationResult with coordination outcomes
        """
        start_time = time.time()

        logger.info(
            "Starting swarm coordination for %s using %s behavior", context.action_type, behavior.value
        )

        # Initialize swarm
        swarm_id = f"swarm_{context.session_id}_{int(time.time())}"
        swarm_size = swarm_size or self.swarm_config["swarm_size"]

        swarm_state = self._initialize_swarm(swarm_id, context, behavior, swarm_size)
        self.active_swarms[swarm_id] = swarm_state

        # Run swarm algorithm
        algorithm_func = self.swarm_algorithms[behavior]
        final_state = algorithm_func(swarm_state, context)

        # Generate collective decision
        collective_decision = self._generate_collective_decision(final_state, context)

        # Identify emergent patterns
        emergent_patterns = self._identify_emergent_patterns(final_state)

        # Calculate coordination efficiency
        coordination_efficiency = self._calculate_coordination_efficiency(final_state)

        # Check convergence
        convergence_achieved = final_state.convergence_rate > self.swarm_config["convergence_threshold"]

        result = SwarmCoordinationResult(
            coordination_id=swarm_id,
            swarm_state=final_state,
            collective_decision=collective_decision,
            emergent_patterns=emergent_patterns,
            coordination_efficiency=coordination_efficiency,
            convergence_achieved=convergence_achieved,
            execution_time_seconds=time.time() - start_time,
        )

        logger.info(
            "Swarm coordination completed in %.3f seconds with efficiency %.3f",
            result.execution_time_seconds,
            coordination_efficiency,
        )

        return result

    def analyze_swarm_dynamics(self, swarm_id: str) -> Dict[str, Any]:
        """Analyze dynamics of a specific swarm.

        Args:
            swarm_id: ID of the swarm to analyze

        Returns:
            Swarm dynamics analysis
        """
        if swarm_id not in self.active_swarms:
            return {"error": f"Swarm {swarm_id} not found"}

        swarm_state = self.active_swarms[swarm_id]

        dynamics = {
            "swarm_id": swarm_id,
            "swarm_size": len(swarm_state.agents),
            "behavior": swarm_state.behavior.value,
            "iteration": swarm_state.iteration,
            "global_best_fitness": swarm_state.global_best_fitness,
            "collective_fitness": swarm_state.collective_fitness,
            "swarm_cohesion": swarm_state.swarm_cohesion,
            "swarm_diversity": swarm_state.swarm_diversity,
            "convergence_rate": swarm_state.convergence_rate,
            "role_distribution": self._analyze_role_distribution(swarm_state),
            "spatial_distribution": self._analyze_spatial_distribution(swarm_state),
            "energy_levels": self._analyze_energy_levels(swarm_state),
            "communication_network": self._analyze_communication_network(swarm_state),
        }

        return dynamics

    def optimize_with_swarm(
        self, context: ArchitecturalContext, objective_function: callable, dimensions: int = 5
    ) -> Dict[str, Any]:
        """Optimize architectural parameters using swarm intelligence.

        Args:
            context: Architectural context
            objective_function: Function to optimize
            dimensions: Number of dimensions for optimization

        Returns:
            Optimization results
        """
        logger.info("Starting swarm optimization with %d dimensions", dimensions)

        # Create swarm for optimization
        swarm_id = f"opt_swarm_{int(time.time())}"
        swarm_state = self._initialize_optimization_swarm(swarm_id, dimensions)

        best_solution = None
        best_fitness = float("-inf")
        fitness_history = []

        # Run optimization iterations
        for iteration in range(self.swarm_config["max_iterations"]):
            # Update agent positions
            for agent in swarm_state.agents.values():
                # PSO update equations
                r1, r2 = random.random(), random.random()

                # Update velocity
                agent.velocity = (
                    self.swarm_config["inertia_weight"] * agent.velocity
                    + self.swarm_config["cognitive_weight"] * r1 * (agent.personal_best - agent.position)
                    + self.swarm_config["social_weight"] * r2 * (swarm_state.global_best - agent.position)
                )

                # Update position
                agent.position = agent.position + agent.velocity

                # Evaluate fitness
                fitness = objective_function(agent.position)
                agent.fitness = fitness

                # Update personal best
                if fitness > agent.personal_best_fitness:
                    agent.personal_best = agent.position.copy()
                    agent.personal_best_fitness = fitness

                # Update global best
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = agent.position.copy()
                    swarm_state.global_best = agent.position.copy()
                    swarm_state.global_best_fitness = fitness

            # Calculate swarm metrics
            swarm_state.collective_fitness = np.mean([agent.fitness for agent in swarm_state.agents.values()])
            swarm_state.swarm_diversity = self._calculate_diversity(swarm_state)
            swarm_state.convergence_rate = 1.0 - swarm_state.swarm_diversity

            fitness_history.append(best_fitness)

            # Check convergence
            if swarm_state.convergence_rate > self.swarm_config["convergence_threshold"]:
                logger.info("Swarm optimization converged at iteration %d", iteration)
                break

        optimization_result = {
            "best_solution": best_solution.tolist() if best_solution is not None else None,
            "best_fitness": best_fitness,
            "fitness_history": fitness_history,
            "iterations": iteration + 1,
            "convergence_achieved": swarm_state.convergence_rate > self.swarm_config["convergence_threshold"],
            "final_diversity": swarm_state.swarm_diversity,
            "swarm_size": len(swarm_state.agents),
        }

        return optimization_result

    def simulate_collective_behavior(
        self, context: ArchitecturalContext, simulation_steps: int = 50
    ) -> List[Dict[str, Any]]:
        """Simulate collective behavior of swarm over time.

        Args:
            context: Architectural context
            simulation_steps: Number of simulation steps

        Returns:
            Time series of swarm behavior
        """
        logger.info("Simulating collective behavior for %d steps", simulation_steps)

        behavior_history = []

        # Initialize swarm
        swarm_id = f"sim_swarm_{int(time.time())}"
        swarm_state = self._initialize_swarm(swarm_id, context, SwarmBehavior.ADAPTIVE_RESPONSE)

        for step in range(simulation_steps):
            # Update swarm state
            self._update_swarm_step(swarm_state, context, step)

            # Record current state
            step_data = {
                "step": step,
                "timestamp": (datetime.now() + timedelta(seconds=step)).isoformat(),
                "collective_fitness": swarm_state.collective_fitness,
                "swarm_cohesion": swarm_state.swarm_cohesion,
                "swarm_diversity": swarm_state.swarm_diversity,
                "convergence_rate": swarm_state.convergence_rate,
                "active_agents": len([a for a in swarm_state.agents.values() if a.energy > 0.1]),
                "emergent_behavior": self._detect_emergent_behavior(swarm_state),
            }

            behavior_history.append(step_data)

        return behavior_history

    def _initialize_swarm(
        self, swarm_id: str, context: ArchitecturalContext, behavior: SwarmBehavior, swarm_size: int
    ) -> SwarmState:
        """Initialize swarm with agents."""
        agents = {}

        # Create agents with different roles
        role_distribution = {
            SwarmRole.EXPLORER: 0.3,
            SwarmRole.EXPLOITER: 0.3,
            SwarmRole.SCOUT: 0.2,
            SwarmRole.COORDINATOR: 0.1,
            SwarmRole.OBSERVER: 0.1,
        }

        dimensions = max(len(context.target_modules), 5)  # At least 5 dimensions

        for i in range(swarm_size):
            # Assign role based on distribution
            rand_val = random.random()
            cumulative = 0.0
            role = SwarmRole.EXPLORER

            for r, prob in role_distribution.items():
                cumulative += prob
                if rand_val <= cumulative:
                    role = r
                    break

            # Initialize agent position randomly
            position = np.random.uniform(-1, 1, dimensions)
            velocity = np.random.uniform(-0.1, 0.1, dimensions)

            agent = SwarmAgent(
                agent_id=f"agent_{swarm_id}_{i}",
                role=role,
                position=position,
                velocity=velocity,
                fitness=0.0,
                personal_best=position.copy(),
                personal_best_fitness=0.0,
                neighbors=[],
                memory=[],
                energy=1.0,
                age=0,
            )

            agents[agent.agent_id] = agent

        # Initialize swarm state
        swarm_state = SwarmState(
            swarm_id=swarm_id,
            agents=agents,
            global_best=np.zeros(dimensions),
            global_best_fitness=float("-inf"),
            collective_fitness=0.0,
            swarm_cohesion=0.0,
            swarm_diversity=1.0,
            convergence_rate=0.0,
            behavior=behavior,
        )

        return swarm_state

    def _initialize_optimization_swarm(self, swarm_id: str, dimensions: int) -> SwarmState:
        """Initialize swarm for optimization."""
        agents = {}

        for i in range(self.swarm_config["swarm_size"]):
            position = np.random.uniform(-1, 1, dimensions)
            velocity = np.random.uniform(-0.1, 0.1, dimensions)

            agent = SwarmAgent(
                agent_id=f"opt_agent_{i}",
                role=SwarmRole.EXPLORER,
                position=position,
                velocity=velocity,
                fitness=0.0,
                personal_best=position.copy(),
                personal_best_fitness=0.0,
                neighbors=[],
                memory=[],
                energy=1.0,
                age=0,
            )

            agents[agent.agent_id] = agent

        swarm_state = SwarmState(
            swarm_id=swarm_id,
            agents=agents,
            global_best=np.zeros(dimensions),
            global_best_fitness=float("-inf"),
            collective_fitness=0.0,
            swarm_cohesion=0.0,
            swarm_diversity=1.0,
            convergence_rate=0.0,
            behavior=SwarmBehavior.FORAGING,
        )

        return swarm_state

    def _particle_swarm_optimization(
        self, swarm_state: SwarmState, context: ArchitecturalContext
    ) -> SwarmState:
        """Run Particle Swarm Optimization algorithm."""
        for iteration in range(self.swarm_config["max_iterations"]):
            # Update neighbors
            self._update_neighbors(swarm_state)

            # Update each agent
            for agent in swarm_state.agents.values():
                # PSO update
                r1, r2 = random.random(), random.random()

                agent.velocity = (
                    self.swarm_config["inertia_weight"] * agent.velocity
                    + self.swarm_config["cognitive_weight"] * r1 * (agent.personal_best - agent.position)
                    + self.swarm_config["social_weight"] * r2 * (swarm_state.global_best - agent.position)
                )

                agent.position = agent.position + agent.velocity

                # Evaluate fitness
                fitness = self._evaluate_fitness(agent.position, context)
                agent.fitness = fitness

                # Update personal best
                if fitness > agent.personal_best_fitness:
                    agent.personal_best = agent.position.copy()
                    agent.personal_best_fitness = fitness

                # Update global best
                if fitness > swarm_state.global_best_fitness:
                    swarm_state.global_best = agent.position.copy()
                    swarm_state.global_best_fitness = fitness

            # Update swarm metrics
            self._update_swarm_metrics(swarm_state)
            swarm_state.iteration = iteration

            # Check convergence
            if swarm_state.convergence_rate > self.swarm_config["convergence_threshold"]:
                break

        return swarm_state

    def _ant_colony_optimization(self, swarm_state: SwarmState, context: ArchitecturalContext) -> SwarmState:
        """Run Ant Colony Optimization algorithm."""
        # Simplified ACO for architectural optimization
        pheromone_trails = np.ones((len(context.target_modules), len(context.target_modules))) * 0.1

        for iteration in range(self.swarm_config["max_iterations"]):
            for agent in swarm_state.agents.values():
                if agent.role == SwarmRole.EXPLORER:
                    # Ant explores solution space
                    solution = self._construct_solution(pheromone_trails, context)
                    fitness = self._evaluate_fitness(solution, context)

                    # Update pheromones
                    self._update_pheromones(pheromone_trails, solution, fitness)

                    agent.fitness = fitness
                    agent.memory.append({"solution": solution, "fitness": fitness})

            # Update swarm metrics
            self._update_swarm_metrics(swarm_state)
            swarm_state.iteration = iteration

            if swarm_state.convergence_rate > self.swarm_config["convergence_threshold"]:
                break

        return swarm_state

    def _bee_algorithm(self, swarm_state: SwarmState, context: ArchitecturalContext) -> SwarmState:
        """Run Bee Algorithm for task allocation."""
        # Simplified bee algorithm
        for iteration in range(self.swarm_config["max_iterations"]):
            # Employed bee phase
            for agent in swarm_state.agents.values():
                if agent.role == SwarmRole.EXPLOITER:
                    # Exploit current solution
                    new_solution = agent.position + np.random.uniform(-0.1, 0.1, len(agent.position))
                    fitness = self._evaluate_fitness(new_solution, context)

                    if fitness > agent.fitness:
                        agent.position = new_solution
                        agent.fitness = fitness
                        agent.personal_best = new_solution.copy()
                        agent.personal_best_fitness = fitness

            # Onlooker bee phase
            best_agents = sorted(swarm_state.agents.values(), key=lambda a: a.fitness, reverse=True)[
                : len(swarm_state.agents) // 2
            ]

            for agent in best_agents:
                # Recruit onlookers to best solutions
                for other_agent in swarm_state.agents.values():
                    if other_agent.role == SwarmRole.SCOUT:
                        # Explore around best solution
                        exploration = agent.position + np.random.uniform(-0.2, 0.2, len(agent.position))
                        fitness = self._evaluate_fitness(exploration, context)

                        if fitness > other_agent.fitness:
                            other_agent.position = exploration
                            other_agent.fitness = fitness

            # Update swarm metrics
            self._update_swarm_metrics(swarm_state)
            swarm_state.iteration = iteration

            if swarm_state.convergence_rate > self.swarm_config["convergence_threshold"]:
                break

        return swarm_state

    def _consensus_algorithm(self, swarm_state: SwarmState, context: ArchitecturalContext) -> SwarmState:
        """Run consensus algorithm for collective decision."""
        for iteration in range(self.swarm_config["max_iterations"]):
            # Agents share information and move toward consensus
            consensus_position = np.zeros_like(swarm_state.global_best)

            for agent in swarm_state.agents.values():
                if agent.role == SwarmRole.COORDINATOR:
                    # Coordinators aggregate opinions
                    consensus_position += agent.position * agent.energy
                else:
                    # Other agents move toward consensus
                    agent.position = 0.7 * agent.position + 0.3 * swarm_state.global_best

            # Update global best based on consensus
            consensus_fitness = self._evaluate_fitness(consensus_position, context)

            if consensus_fitness > swarm_state.global_best_fitness:
                swarm_state.global_best = consensus_position.copy()
                swarm_state.global_best_fitness = consensus_fitness

            # Update swarm metrics
            self._update_swarm_metrics(swarm_state)
            swarm_state.iteration = iteration

            if swarm_state.convergence_rate > self.swarm_config["convergence_threshold"]:
                break

        return swarm_state

    def _adaptive_swarm_algorithm(self, swarm_state: SwarmState, context: ArchitecturalContext) -> SwarmState:
        """Run adaptive swarm algorithm."""
        for iteration in range(self.swarm_config["max_iterations"]):
            # Adaptive behavior based on swarm state
            if swarm_state.swarm_diversity > 0.5:
                # High diversity - explore more
                exploration_rate = 0.8
            else:
                # Low diversity - exploit more
                exploration_rate = 0.2

            for agent in swarm_state.agents.values():
                # Adaptive movement
                if random.random() < exploration_rate:
                    # Explore
                    agent.velocity = np.random.uniform(-0.2, 0.2, len(agent.position))
                else:
                    # Exploit
                    agent.velocity = 0.9 * agent.velocity + 0.1 * (swarm_state.global_best - agent.position)

                agent.position = agent.position + agent.velocity

                # Evaluate fitness
                fitness = self._evaluate_fitness(agent.position, context)
                agent.fitness = fitness

                # Update personal best
                if fitness > agent.personal_best_fitness:
                    agent.personal_best = agent.position.copy()
                    agent.personal_best_fitness = fitness

                # Update global best
                if fitness > swarm_state.global_best_fitness:
                    swarm_state.global_best = agent.position.copy()
                    swarm_state.global_best_fitness = fitness

                # Update energy
                agent.energy *= self.swarm_config["energy_decay_rate"]

            # Update swarm metrics
            self._update_swarm_metrics(swarm_state)
            swarm_state.iteration = iteration

            if swarm_state.convergence_rate > self.swarm_config["convergence_threshold"]:
                break

        return swarm_state

    def _evaluate_fitness(self, position: np.ndarray, context: ArchitecturalContext) -> float:
        """Evaluate fitness of agent position."""
        # Simplified fitness function
        # In practice, would use more sophisticated architectural fitness evaluation

        # Base fitness from position magnitude
        fitness = 1.0 / (1.0 + np.linalg.norm(position))

        # Adjust based on context
        if context.action_type in ["analyze_code", "read_file"]:
            fitness *= 1.2  # Bonus for analysis actions
        elif context.action_type in ["delete_file", "modify_module"]:
            fitness *= 0.8  # Penalty for risky actions

        # Add randomness for exploration
        fitness += random.uniform(-0.1, 0.1)

        return max(0.0, min(1.0, fitness))

    def _update_neighbors(self, swarm_state: SwarmState) -> None:
        """Update neighbor relationships in swarm."""
        for agent_id, agent in swarm_state.agents.items():
            agent.neighbors = []

            for other_id, other_agent in swarm_state.agents.items():
                if agent_id != other_id:
                    distance = np.linalg.norm(agent.position - other_agent.position)

                    if distance < self.swarm_config["neighborhood_radius"]:
                        agent.neighbors.append(other_id)

    def _update_swarm_metrics(self, swarm_state: SwarmState) -> None:
        """Update swarm-level metrics."""
        if not swarm_state.agents:
            return

        # Collective fitness
        fitnesses = [agent.fitness for agent in swarm_state.agents.values()]
        swarm_state.collective_fitness = np.mean(fitnesses)

        # Swarm cohesion
        if len(swarm_state.agents) > 1:
            positions = [agent.position for agent in swarm_state.agents.values()]
            center = np.mean(positions, axis=0)
            distances = [np.linalg.norm(pos - center) for pos in positions]
            swarm_state.swarm_cohesion = 1.0 / (1.0 + np.mean(distances))
        else:
            swarm_state.swarm_cohesion = 1.0

        # Swarm diversity
        swarm_state.swarm_diversity = self._calculate_diversity(swarm_state)

        # Convergence rate
        swarm_state.convergence_rate = 1.0 - swarm_state.swarm_diversity

    def _calculate_diversity(self, swarm_state: SwarmState) -> float:
        """Calculate diversity of swarm positions."""
        if len(swarm_state.agents) < 2:
            return 1.0

        positions = [agent.position for agent in swarm_state.agents.values()]
        positions_array = np.array(positions)

        # Calculate average pairwise distance
        total_distance = 0.0
        count = 0

        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                distance = np.linalg.norm(positions[i] - positions[j])
                total_distance += distance
                count += 1

        if count > 0:
            avg_distance = total_distance / count
            diversity = min(1.0, avg_distance / 2.0)  # Normalize to 0-1
        else:
            diversity = 0.0

        return diversity

    def _generate_collective_decision(
        self, swarm_state: SwarmState, context: ArchitecturalContext
    ) -> Dict[str, Any]:
        """Generate collective decision from swarm."""
        # Weight agents by fitness and role
        agent_weights = {}

        for agent in swarm_state.agents.values():
            weight = agent.fitness

            # Role-based weighting
            if agent.role == SwarmRole.COORDINATOR:
                weight *= 1.5
            elif agent.role == SwarmRole.EXPLORER:
                weight *= 1.2
            elif agent.role == SwarmRole.OBSERVER:
                weight *= 0.8

            agent_weights[agent.agent_id] = weight

        # Weighted average of positions
        total_weight = sum(agent_weights.values())
        if total_weight > 0:
            weighted_position = (
                sum(
                    swarm_state.agents[agent_id].position * weight
                    for agent_id, weight in agent_weights.items()
                )
                / total_weight
            )
        else:
            weighted_position = swarm_state.global_best

        # Generate decision
        decision = {
            "recommended_action": context.action_type,
            "confidence": swarm_state.convergence_rate,
            "collective_position": weighted_position.tolist(),
            "participating_agents": len(swarm_state.agents),
            "consensus_level": swarm_state.swarm_cohesion,
            "diversity_level": swarm_state.swarm_diversity,
            "decision_rationale": self._generate_decision_rationale(swarm_state),
        }

        return decision

    def _identify_emergent_patterns(self, swarm_state: SwarmState) -> List[str]:
        """Identify emergent patterns in swarm behavior."""
        patterns = []

        # Check for clustering
        if swarm_state.swarm_cohesion > 0.8:
            patterns.append("Strong clustering behavior detected")

        # Check for exploration vs exploitation balance
        explorers = sum(1 for agent in swarm_state.agents.values() if agent.role == SwarmRole.EXPLORER)
        exploiters = sum(1 for agent in swarm_state.agents.values() if agent.role == SwarmRole.EXPLOITER)

        if explorers > exploiters * 2:
            patterns.append("Exploration-dominant behavior")
        elif exploiters > explorers * 2:
            patterns.append("Exploitation-dominant behavior")
        else:
            patterns.append("Balanced exploration-exploitation")

        # Check for convergence patterns
        if swarm_state.convergence_rate > 0.9:
            patterns.append("Rapid convergence achieved")
        elif swarm_state.convergence_rate < 0.3:
            patterns.append("High diversity maintained")

        # Check for energy patterns
        avg_energy = np.mean([agent.energy for agent in swarm_state.agents.values()])
        if avg_energy < 0.3:
            patterns.append("Swarm fatigue detected")

        return patterns

    def _calculate_coordination_efficiency(self, swarm_state: SwarmState) -> float:
        """Calculate coordination efficiency of swarm."""
        # Efficiency based on convergence, cohesion, and fitness
        efficiency = (
            swarm_state.convergence_rate * 0.4
            + swarm_state.swarm_cohesion * 0.3
            + swarm_state.collective_fitness * 0.3
        )

        return efficiency

    def _analyze_role_distribution(self, swarm_state: SwarmState) -> Dict[str, int]:
        """Analyze distribution of roles in swarm."""
        role_counts = defaultdict(int)

        for agent in swarm_state.agents.values():
            role_counts[agent.role.value] += 1

        return dict(role_counts)

    def _analyze_spatial_distribution(self, swarm_state: SwarmState) -> Dict[str, float]:
        """Analyze spatial distribution of swarm."""
        if not swarm_state.agents:
            return {}

        positions = [agent.position for agent in swarm_state.agents.values()]
        positions_array = np.array(positions)

        return {
            "mean_distance_from_center": float(np.mean([np.linalg.norm(pos) for pos in positions])),
            "position_variance": float(np.var(positions)),
            "max_distance": float(np.max([np.linalg.norm(pos) for pos in positions])),
            "min_distance": float(np.min([np.linalg.norm(pos) for pos in positions])),
        }

    def _analyze_energy_levels(self, swarm_state: SwarmState) -> Dict[str, float]:
        """Analyze energy levels in swarm."""
        energies = [agent.energy for agent in swarm_state.agents.values()]

        return {
            "average_energy": np.mean(energies),
            "min_energy": np.min(energies),
            "max_energy": np.max(energies),
            "energy_std": np.std(energies),
            "active_agents": len([e for e in energies if e > 0.1]),
        }

    def _analyze_communication_network(self, swarm_state: SwarmState) -> Dict[str, Any]:
        """Analyze communication network in swarm."""
        network = {
            "total_connections": 0,
            "average_connections": 0.0,
            "max_connections": 0,
            "isolated_agents": 0,
        }

        connections = []
        for agent in swarm_state.agents.values():
            connections.append(len(agent.neighbors))
            network["total_connections"] += len(agent.neighbors)

        if connections:
            network["average_connections"] = np.mean(connections)
            network["max_connections"] = np.max(connections)
            network["isolated_agents"] = sum(1 for c in connections if c == 0)

        return network

    def _construct_solution(self, pheromone_trails: np.ndarray, context: ArchitecturalContext) -> np.ndarray:
        """Construct solution using pheromone trails."""
        # Simplified solution construction
        n = len(context.target_modules)
        solution = np.zeros(n)

        for i in range(n):
            # Choose next module based on pheromones
            probabilities = pheromone_trails[i] / np.sum(pheromone_trails[i])
            next_module = np.random.choice(n, p=probabilities)
            solution[i] = next_module

        return solution

    def _update_pheromones(self, pheromone_trails: np.ndarray, solution: np.ndarray, fitness: float) -> None:
        """Update pheromone trails."""
        # Evaporation
        pheromone_trails *= 0.9

        # Deposit pheromones
        for i in range(len(solution)):
            j = int(solution[i]) % len(solution)
            pheromone_trails[i, j] += fitness * 0.1

    def _update_swarm_step(self, swarm_state: SwarmState, context: ArchitecturalContext, step: int) -> None:
        """Update swarm for one simulation step."""
        # Simple update for simulation
        for agent in swarm_state.agents.values():
            # Random walk with drift
            agent.velocity = 0.9 * agent.velocity + np.random.uniform(-0.05, 0.05, len(agent.position))
            agent.position = agent.position + agent.velocity

            # Update fitness
            agent.fitness = self._evaluate_fitness(agent.position, context)

            # Update energy
            agent.energy *= 0.99
            agent.age += 1

        # Update swarm metrics
        self._update_swarm_metrics(swarm_state)
        swarm_state.iteration = step

    def _detect_emergent_behavior(self, swarm_state: SwarmState) -> str:
        """Detect emergent behavior in swarm."""
        if swarm_state.swarm_cohesion > 0.8 and swarm_state.convergence_rate > 0.7:
            return "collective_convergence"
        elif swarm_state.swarm_diversity > 0.7:
            return "exploratory_swarm"
        elif swarm_state.collective_fitness > 0.8:
            return "high_performance_swarm"
        else:
            return "adaptive_swarm"

    def _generate_decision_rationale(self, swarm_state: SwarmState) -> str:
        """Generate rationale for collective decision."""
        rationale_parts = []

        if swarm_state.convergence_rate > 0.8:
            rationale_parts.append("High convergence indicates strong consensus")

        if swarm_state.swarm_cohesion > 0.7:
            rationale_parts.append("Good swarm cohesion promotes coordinated action")

        if swarm_state.collective_fitness > 0.6:
            rationale_parts.append("Collective fitness supports decision quality")

        if not rationale_parts:
            rationale_parts.append("Decision based on swarm consensus")

        return "; ".join(rationale_parts)

    def get_swarm_statistics(self) -> Dict[str, Any]:
        """Get swarm intelligence statistics."""
        return {
            "active_swarms": len(self.active_swarms),
            "total_agents": sum(len(swarm.agents) for swarm in self.active_swarms.values()),
            "available_behaviors": [b.value for b in SwarmBehavior],
            "available_roles": [r.value for r in SwarmRole],
            "swarm_config": self.swarm_config,
        }
