# Mastering AI Agents, Agentic Swarms, and Google's A2A Protocol
## Student Reference Guide

---

## Module 1: Foundations of AI Agents

### What is an AI Agent?

An **AI Agent** is an autonomous entity that:
- **Perceives** its environment through sensors
- **Processes** information to make decisions
- **Acts** upon the environment to achieve goals

**Key Properties:**
| Property | Description |
|----------|-------------|
| Autonomy | Operates without direct human intervention |
| Reactivity | Responds to environmental changes |
| Proactiveness | Takes initiative to achieve goals |
| Social Ability | Interacts with other agents |

### Agent Architecture: The Perception-Action Loop

```
Environment → Sensors → Agent (Perceive → Decide → Act) → Actuators → Environment
```

### Agent Types

#### 1. Reactive Agents
- Simple stimulus-response behavior
- No internal state or memory
- Fast but limited reasoning
- Example: Thermostat, simple game AI

```python
class ReactiveAgent:
    def __init__(self, rules):
        self.rules = rules  # condition -> action

    def act(self, percept):
        for condition, action in self.rules.items():
            if condition(percept):
                return action
        return 'idle'
```

#### 2. Deliberative Agents
- Maintain internal world model
- Plan actions to achieve goals
- Slower but more intelligent
- Example: Chess AI, path planners

#### 3. Hybrid Agents
- Combine reactive and deliberative layers
- Reactive layer for immediate responses
- Deliberative layer for planning
- Example: Autonomous vehicles

### BDI Architecture (Beliefs, Desires, Intentions)

A cognitive model for rational agents:

- **Beliefs**: Agent's knowledge about the world (may be incomplete/incorrect)
- **Desires**: Goals the agent wants to achieve
- **Intentions**: Committed plans of action

```python
class BDIAgent:
    def __init__(self):
        self.beliefs = {}      # Current world state
        self.desires = []      # Goal states
        self.intentions = []   # Active plans

    def deliberate(self):
        self.update_beliefs()
        options = self.generate_options()
        self.filter_intentions(options)
        self.execute_intention()
```

### Environment Properties (PEAS Framework)

**P**erformance, **E**nvironment, **A**ctuators, **S**ensors

| Property | Options | Example |
|----------|---------|---------|
| Observability | Fully / Partially | Chess vs Poker |
| Determinism | Deterministic / Stochastic | Calculator vs Weather |
| Episodic | Episodic / Sequential | Classifier vs Game |
| Dynamics | Static / Dynamic | Puzzle vs Trading |
| Agents | Single / Multi | Crossword vs Auction |

---

## Module 2: Swarm Intelligence

### Biological Inspiration

| System | Mechanism | Emergent Behavior |
|--------|-----------|-------------------|
| Ant Colonies | Pheromone trails | Shortest path finding |
| Bee Swarms | Waggle dance | Collective decision-making |
| Bird Flocks | Local rules | Coordinated movement |
| Fish Schools | Neighbor alignment | Predator avoidance |

### Core Principles

1. **Decentralization**: No central controller
2. **Self-Organization**: Order from local interactions
3. **Emergence**: Complex behavior from simple rules
4. **Stigmergy**: Indirect communication via environment

### Boids Algorithm (Reynolds, 1986)

Three simple rules create realistic flocking:

| Rule | Description | Formula |
|------|-------------|---------|
| **Separation** | Avoid crowding | `steer away from nearby boids` |
| **Alignment** | Match velocity | `steer toward average heading` |
| **Cohesion** | Move to center | `steer toward average position` |

```python
def update_boid(boid, neighbors, weights):
    separation = avoid_neighbors(boid, neighbors) * weights['sep']
    alignment = match_velocity(boid, neighbors) * weights['ali']
    cohesion = seek_center(boid, neighbors) * weights['coh']

    boid.velocity += separation + alignment + cohesion
    boid.velocity = limit_speed(boid.velocity, MAX_SPEED)
    boid.position += boid.velocity
```

### Stigmergy

**Definition**: Agents communicate by modifying the environment rather than direct messaging.

**Ant Colony Example:**
1. Ant finds food source
2. Deposits pheromone on return path
3. Other ants follow stronger trails
4. More ants = more pheromone = stronger trail
5. Shortest path emerges naturally

```python
class PheromoneGrid:
    def deposit(self, x, y, amount):
        self.grid[x, y] += amount

    def evaporate(self, rate=0.1):
        self.grid *= (1 - rate)

    def get_probability(self, x, y, alpha=1):
        return self.grid[x, y] ** alpha
```

---

## Module 3: Multi-Agent Systems Architecture

### System Topologies

| Topology | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Centralized** | Easy management | Single point of failure | Small systems |
| **Decentralized** | Fault tolerant | Complex coordination | Robust systems |
| **Hierarchical** | Scalable | Rigid structure | Large organizations |
| **Mesh** | Flexible | Network overhead | Dynamic systems |

### Communication Patterns

#### 1. Direct Messaging (Point-to-Point)
```python
agent_b.receive(sender=agent_a, message=msg)
```

#### 2. Publish-Subscribe (Decoupled)
```python
broker.publish(topic="prices", data=update)
# All subscribers to "prices" receive update
```

#### 3. Blackboard (Shared Memory)
```python
blackboard.post(key="partial_solution", value=data)
# All agents can read and contribute
```

### Contract Net Protocol

A task allocation protocol:

1. **Manager** broadcasts Call For Proposals (CFP)
2. **Contractors** evaluate and submit bids
3. **Manager** evaluates bids and awards contract
4. **Winner** executes task and reports results

### FIPA Standards

Foundation for Intelligent Physical Agents defines:
- Agent Communication Language (ACL)
- Performatives: REQUEST, INFORM, PROPOSE, ACCEPT, REJECT
- Message structure and protocols

---

## Module 4: Google's A2A Protocol

### Overview

**Agent-to-Agent (A2A)** is Google's open protocol for agent interoperability.

**Key Features:**
- Framework agnostic
- HTTP(S) + JSON-RPC 2.0
- Capability discovery via Agent Cards
- Task delegation and streaming
- Opaque collaboration (internal details hidden)

### Agent Card Schema

```json
{
    "name": "DataAnalysisAgent",
    "description": "Analyzes datasets",
    "url": "https://agent.example.com/a2a",
    "version": "1.0.0",
    "capabilities": {
        "streaming": true,
        "pushNotifications": false
    },
    "skills": [
        {
            "id": "analyze",
            "name": "Data Analysis",
            "inputSchema": {...},
            "outputSchema": {...}
        }
    ],
    "authentication": {"type": "bearer"}
}
```

### Task Lifecycle

```
PENDING → RUNNING → COMPLETED
                  ↘ FAILED
    ↓ (cancel)     ↓ (cancel)
CANCELED ←←←←←←←←←←
```

### A2A vs MCP Comparison

| Feature | A2A | MCP (Model Context Protocol) |
|---------|-----|------------------------------|
| Focus | Agent-to-agent | Model-to-tool |
| Transport | HTTP + JSON-RPC | Stdio/SSE |
| Discovery | Agent Cards | Tool manifests |
| Use Case | Agent networks | LLM tool use |

### Implementation Checklist

- [ ] Expose `/.well-known/agent.json` endpoint
- [ ] Implement JSON-RPC 2.0 endpoint at `/a2a`
- [ ] Handle `tasks/create`, `tasks/get`, `tasks/cancel`
- [ ] Define skills with input/output schemas
- [ ] Implement authentication
- [ ] Support streaming for long tasks (optional)

---

## Module 5: Advanced Agent Development

### Memory Architecture

| Type | Duration | Capacity | Use Case |
|------|----------|----------|----------|
| **Short-term** | Session | Limited (5-10 items) | Current context |
| **Long-term** | Persistent | Large (vector DB) | Knowledge base |
| **Episodic** | Persistent | Structured events | Past experiences |

```python
class AgentMemory:
    def __init__(self):
        self.short_term = deque(maxlen=10)
        self.long_term = VectorStore()
        self.episodic = []

    def remember(self, text, memory_type="short"):
        if memory_type == "short":
            self.short_term.append(text)
        elif memory_type == "long":
            self.long_term.add(text)

    def recall(self, query, k=3):
        return self.long_term.similarity_search(query, k=k)
```

### Fault Tolerance Patterns

#### Retry with Exponential Backoff
```python
@retry(max_attempts=3, backoff=2)
def risky_operation():
    # May fail temporarily
    pass
```

#### Circuit Breaker
```python
class CircuitBreaker:
    def __init__(self, threshold=5, timeout=60):
        self.failures = 0
        self.threshold = threshold
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
```

### State Management

```python
class AgentState(Enum):
    IDLE = auto()
    PERCEIVING = auto()
    REASONING = auto()
    ACTING = auto()
    WAITING = auto()
    ERROR = auto()
```

### Best Practices Checklist

- [ ] Implement proper error handling
- [ ] Add retry logic for transient failures
- [ ] Use circuit breakers for external services
- [ ] Persist state for recovery
- [ ] Log all state transitions
- [ ] Implement health checks
- [ ] Set timeouts on all operations

---

## Module 6: Frameworks and Tools

### Framework Comparison

| Framework | Best For | Scale | Language |
|-----------|----------|-------|----------|
| **Mesa** | Agent-based modeling | Single machine | Python |
| **PySwarm** | PSO optimization | Single machine | Python |
| **Ray** | Distributed computing | Cluster | Python |
| **RLlib** | Multi-agent RL | Cluster | Python |

### Mesa Quick Start

```python
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

class MyAgent(Agent):
    def step(self):
        # Agent behavior
        pass

class MyModel(Model):
    def __init__(self, n_agents):
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(10, 10, True)
        for i in range(n_agents):
            agent = MyAgent(i, self)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()
```

### Ray Quick Start

```python
import ray

ray.init()

@ray.remote
class DistributedAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id

    def compute(self, data):
        return process(data)

# Create and use distributed agents
agents = [DistributedAgent.remote(i) for i in range(10)]
futures = [a.compute.remote(data) for a in agents]
results = ray.get(futures)
```

---

## Module 7: Swarm Optimization

### Particle Swarm Optimization (PSO)

**Algorithm:**
1. Initialize particles with random positions and velocities
2. Evaluate fitness of each particle
3. Update personal best (pBest) and global best (gBest)
4. Update velocity: `v = w*v + c1*r1*(pBest-x) + c2*r2*(gBest-x)`
5. Update position: `x = x + v`
6. Repeat until convergence

**Parameters:**
- `w`: Inertia weight (0.4-0.9)
- `c1`: Cognitive coefficient (1.5-2.0)
- `c2`: Social coefficient (1.5-2.0)

### Ant Colony Optimization (ACO)

**Algorithm:**
1. Initialize pheromone trails
2. Each ant constructs a solution probabilistically
3. Evaluate solutions
4. Update pheromones (deposit on good paths, evaporate)
5. Repeat until convergence

**Probability formula:**
```
P(i→j) = [τ(i,j)]^α * [η(i,j)]^β / Σ[τ(i,k)]^α * [η(i,k)]^β
```
- τ: pheromone level
- η: heuristic information (e.g., 1/distance)
- α, β: influence parameters

### Consensus Algorithms

#### Raft vs Paxos

| Feature | Raft | Paxos |
|---------|------|-------|
| Understandability | Easy | Complex |
| Leader | Single leader | Multiple proposers |
| Phases | 2 (election, replication) | 2 (prepare, accept) |
| Implementation | Straightforward | Challenging |

### Byzantine Fault Tolerance

Handles malicious nodes (up to f faulty nodes with 3f+1 total).

**PBFT (Practical BFT):**
1. Request → Primary
2. Pre-prepare → All replicas
3. Prepare → All replicas
4. Commit → All replicas
5. Reply → Client

---

## Module 8: Real-World Applications

### Warehouse Automation (Kiva/Amazon)

**Architecture:**
- 1000s of robots per warehouse
- Decentralized path planning (A*)
- Hungarian algorithm for task assignment
- Virtual highways for traffic flow

**Results:**
- 4x faster order fulfillment
- 50% less floor space
- Near-zero collisions

### Smart City Traffic Control

**Agents:**
- Intersection controllers
- Vehicle agents
- Emergency vehicles (priority)

**Techniques:**
- Reinforcement learning for signal timing
- V2I (Vehicle-to-Infrastructure) communication
- Swarm-based congestion avoidance

### Financial Trading

**Agent Types:**
- Market makers
- Trend followers
- Mean reversion
- Arbitrageurs

**Considerations:**
- Latency sensitivity
- Risk management
- Regulatory compliance

---

## Module 9: Monitoring and Troubleshooting

### Key Metrics

| Level | Metrics |
|-------|---------|
| **Agent** | Response time, success rate, resource usage |
| **System** | Throughput, latency, convergence time |
| **Network** | Message rate, queue depth, errors |

### Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Deadlock** | Agents frozen | Timeout + retry |
| **Livelock** | Busy but no progress | Randomization |
| **Starvation** | Some agents never run | Fair scheduling |
| **Message loss** | Missing responses | Acknowledgments + retry |

### Debugging Tips

1. Add correlation IDs to all messages
2. Log state transitions
3. Use distributed tracing (Jaeger, Zipkin)
4. Implement health check endpoints
5. Create visualization dashboards

---

## Module 10: Ethics and Future

### Ethical Framework

1. **Accountability**: Clear responsibility chain
2. **Transparency**: Explainable decisions
3. **Safety**: Bounded autonomy, kill switches
4. **Privacy**: Data minimization, consent
5. **Fairness**: Avoid bias, equal treatment

### Emerging Technologies

| Technology | Potential Impact |
|------------|-----------------|
| **LLM Agents** | Natural language reasoning |
| **Neuromorphic** | Low-power, real-time learning |
| **Quantum** | Faster optimization |
| **Edge AI** | Distributed intelligence |

---

## Module 11: Capstone Guidelines

### Project Requirements

**Technical:**
- Minimum 5 agents
- A2A protocol communication
- At least 2 agent types
- Visualization dashboard
- Monitoring/logging

**Deliverables:**
- Working code (GitHub)
- Architecture documentation
- Performance analysis
- 10-minute demo
- Lessons learned

### Evaluation Rubric

| Criteria | Weight |
|----------|--------|
| Functionality | 40% |
| Code Quality | 20% |
| Documentation | 20% |
| Presentation | 20% |

---

## Quick Reference: Python Code Snippets

### Basic Agent Template
```python
class Agent:
    def perceive(self, env): pass
    def decide(self, percepts): pass
    def act(self, action, env): pass

    def run(self, env):
        while True:
            p = self.perceive(env)
            a = self.decide(p)
            self.act(a, env)
```

### Message Format (A2A)
```python
message = {
    "jsonrpc": "2.0",
    "method": "tasks/create",
    "params": {"skillId": "analyze", "input": {...}},
    "id": 1
}
```

### PSO Update
```python
v = w*v + c1*r1*(pbest-x) + c2*r2*(gbest-x)
x = x + v
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Agent** | Autonomous entity that perceives and acts |
| **BDI** | Beliefs, Desires, Intentions architecture |
| **Emergence** | Complex behavior from simple rules |
| **Stigmergy** | Indirect communication via environment |
| **A2A** | Google's Agent-to-Agent protocol |
| **PSO** | Particle Swarm Optimization |
| **ACO** | Ant Colony Optimization |
| **MAS** | Multi-Agent System |
| **FIPA** | Foundation for Intelligent Physical Agents |

---

## Further Reading

1. Russell & Norvig - "Artificial Intelligence: A Modern Approach"
2. Wooldridge - "An Introduction to MultiAgent Systems"
3. Kennedy & Eberhart - "Swarm Intelligence"
4. Google A2A Specification: https://github.com/google/A2A
5. Mesa Documentation: https://mesa.readthedocs.io/
6. Ray Documentation: https://docs.ray.io/
