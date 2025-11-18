# Plan: Modeling and Visualizing Escalatory Cycles Between Communities

## Overview

**Goal**: Model the escalatory cycle where Community A accuses a member of Community B, then Community B retaliates by scapegoating a member of Community A, leading to full mutual polarization (A vs B).

**Key Feature**: Community B members will NOT defect when they hear accusations from Community A - they defend their own, leading to symmetric conflict escalation.

## Requirements

### 1. Modified Defection Behavior
- **Current behavior**: B members choose A friends over B scapegoat (defection)
- **New behavior**: B members defend their community member against external accusations
- **Implementation**: Modify contagion rules to check if accusation is cross-community

### 2. Retaliation Mechanism
- After A scapegoats B member, B learns about it
- B retaliates by scapegoating an A member
- Accusation spreads through B → crosses bridge → spreads through A
- Both communities now unified against each other's scapegoat

### 3. Visualization
- Animate the escalation cycle showing:
  - Phase 1: A scapegoats B_victim
  - Phase 2: Information crosses bridge to B
  - Phase 3: B retaliates, scapegoats A_victim
  - Phase 4: Information crosses back to A
  - Final: Mutual polarization (all of A vs all of B)

## Architecture

### Component 1: Modified Simulator with Loyalty Rules

**File**: `src/simulator_with_loyalty.py`

**New Rule**: Community loyalty overrides cross-community friendship
```python
def should_defend_community_member(node, scapegoat, accuser, graph, communities):
    """
    Check if node should defend scapegoat based on community loyalty.

    Returns True if:
    - Node and scapegoat are in same community
    - Accuser is from different community
    - This is a cross-community attack
    """
    node_comm = get_community(node, communities)
    sg_comm = get_community(scapegoat, communities)
    acc_comm = get_community(accuser, communities)

    # Defend if: same community as scapegoat, attacked by outsider
    return (node_comm == sg_comm) and (acc_comm != sg_comm)
```

**Modified Rule 1 (Forced Choice)**:
```python
# Current: Choose friend over scapegoat
# Modified: Check community loyalty first

if should_defend_community_member(node, scapegoat, accuser, graph, communities):
    # DEFEND: Don't flip edge, stay loyal
    return None
else:
    # Original behavior: choose friend over scapegoat
    flip_to_negative(node, scapegoat)
```

### Component 2: Escalation Simulator

**File**: `tests/test_escalation_cycle.py`

**Structure**:
```python
def run_escalation_cycle(
    comm_a_size=6,
    comm_b_size=6,
    bridge_count=1,
    seed=42
):
    """
    Simulate complete escalation cycle.

    Steps:
    1. A0 accuses B0 (initial offense)
    2. Accusation spreads through A
    3. Bridge carries info to B
    4. B hears, defends B0 (loyalty)
    5. B retaliates: B1 accuses A1 (counter-offense)
    6. Accusation spreads through B
    7. Bridge carries counter-accusation to A
    8. A hears, defends A1 (loyalty)
    9. Result: Mutual polarization

    Returns:
    - Phase 1 result (A → B0)
    - Phase 2 result (B → A1)
    - Timeline of decisions
    - Final graph state
    """
```

**Output**:
```python
{
    'phase1': {
        'accuser': 'A0',
        'scapegoat': 'B0',
        'a_accusers': [...],  # All of A
        'b_defenders': [...],  # All of B defend B0
        'final_graph': graph1
    },
    'phase2': {
        'accuser': 'B1',
        'scapegoat': 'A1',
        'b_accusers': [...],  # All of B
        'a_defenders': [...],  # All of A defend A1
        'final_graph': graph2
    },
    'mutual_polarization': {
        'a_hostile_to_b': [...],
        'b_hostile_to_a': [...],
        'bridge_broken': True
    }
}
```

### Component 3: Visualization Script

**File**: `visualize_escalation.py`

**Based on**: `visualize_cascade.py` + `balance-theory` visualization patterns

**Key Features**:

1. **Two-Community Layout**:
```python
def two_community_layout(comm_a, comm_b):
    """
    Position nodes in two semicircles facing each other.

    Community A: Left semicircle
    Community B: Right semicircle
    Bridge: Connects the two
    """
    positions = {}

    # Community A: semicircle on left
    for i, node in enumerate(comm_a):
        angle = math.pi/2 + (math.pi * i / len(comm_a))
        x = -0.5 + 0.8 * math.cos(angle)
        y = 0.8 * math.sin(angle)
        positions[node] = (x, y)

    # Community B: semicircle on right
    for i, node in enumerate(comm_b):
        angle = math.pi/2 - (math.pi * i / len(comm_b))
        x = 0.5 + 0.8 * math.cos(angle)
        y = 0.8 * math.sin(angle)
        positions[node] = (x, y)

    return positions
```

2. **Escalation Phases**:
```python
def create_escalation_frame(ax, phase, step, graph_state, communities):
    """
    Draw frame showing current escalation phase.

    Phase markers:
    - Phase 1A: "A0 accuses B0" (highlight accuser, scapegoat)
    - Phase 1B: "Spreads through A" (show A members turning hostile)
    - Phase 1C: "Bridge to B" (highlight bridge edge)
    - Phase 1D: "B defends B0" (show B members staying loyal)
    - Phase 2A: "B1 retaliates against A1" (new accusation)
    - Phase 2B: "Spreads through B"
    - Phase 2C: "Bridge to A"
    - Phase 2D: "A defends A1"
    - Final: "Mutual polarization" (communities unified against each other)
    """

    # Color nodes by role and phase
    node_colors = {}
    for node in graph_state.nodes:
        if phase == '1A' and node == accuser:
            node_colors[node] = 'orange'  # Initial accuser
        elif phase == '1A' and node == scapegoat:
            node_colors[node] = 'red'  # Initial scapegoat
        elif phase == '2A' and node == retaliator:
            node_colors[node] = 'orange'  # Retaliator
        elif phase == '2A' and node == counter_scapegoat:
            node_colors[node] = 'red'  # Counter-scapegoat
        elif node in communities['A']:
            node_colors[node] = 'lightblue'  # Community A
        elif node in communities['B']:
            node_colors[node] = 'lightgreen'  # Community B

    # Draw edges with phase-appropriate highlighting
    # ... (similar to visualize_cascade.py)
```

3. **Animation Sequence**:
```python
def animate_escalation_cycle(escalation_data, output_path, fps=1):
    """
    Create animated GIF showing full escalation cycle.

    Frames:
    1-5: Phase 1A (A accuses B, spreads through A)
    6-10: Phase 1B (Bridge crossing, B defends)
    11-15: Phase 2A (B retaliates, spreads through B)
    16-20: Phase 2B (Bridge crossing back, A defends)
    21-25: Final state (mutual polarization)

    Total: ~25 frames at 1 FPS = 25 second animation
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    frames = []

    # Phase 1: A → B0
    frames.extend(generate_phase1_frames(escalation_data))

    # Phase 2: B → A1
    frames.extend(generate_phase2_frames(escalation_data))

    # Final state
    frames.extend(generate_final_frames(escalation_data))

    # Create animation
    anim = FuncAnimation(
        fig,
        lambda i: draw_frame(ax, frames[i]),
        frames=len(frames),
        interval=1000/fps,
        repeat=True
    )

    # Save
    anim.save(output_path, writer=PillowWriter(fps=fps))
```

4. **Energy/Hostility Metrics**:
```python
def compute_inter_community_hostility(graph, comm_a, comm_b):
    """
    Compute level of cross-community hostility.

    Returns:
    - A→B hostility: % of A members hostile to any B member
    - B→A hostility: % of B members hostile to any A member
    - Mutual hostility score: average of both
    """
    a_hostile_to_b = sum(
        1 for a in comm_a for b in comm_b
        if graph.get_edge(a, b) == -1
    )

    b_hostile_to_a = sum(
        1 for b in comm_b for a in comm_a
        if graph.get_edge(b, a) == -1
    )

    max_possible = len(comm_a) * len(comm_b)

    return {
        'a_to_b': 100 * a_hostile_to_b / max_possible,
        'b_to_a': 100 * b_hostile_to_a / max_possible,
        'mutual': 100 * (a_hostile_to_b + b_hostile_to_a) / (2 * max_possible)
    }
```

### Component 4: Comparison Visualizations

**File**: `generate_escalation_comparison.py`

**Purpose**: Side-by-side comparison of:
- Scenario 1: No loyalty (defection occurs, all-against-one)
- Scenario 2: With loyalty (escalation to mutual polarization)

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  SCENARIO 1: No Loyalty (Defection)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Initial  │→ │ Phase 1  │→ │  Final   │             │
│  │  State   │  │ A→B0     │  │ All vs B0│             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                         │
│  SCENARIO 2: With Loyalty (Escalation)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Initial  │→ │ Phase 1  │→ │ Phase 2  │→ │ Final  ││
│  │  State   │  │ A→B0     │  │ B→A1     │  │ A vs B ││
│  └──────────┘  └──────────┘  └──────────┘  └────────┘│
│                                                         │
│  Hostility Metrics:                                    │
│  Scenario 1: 100% vs B0, 0% community polarization    │
│  Scenario 2: 0% vs individuals, 100% A-B polarization │
└─────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Step 1: Modify Simulator (1-2 hours)
1. Copy `src/simulator.py` → `src/simulator_with_loyalty.py`
2. Add community tracking to `MimeticContagionSimulator.__init__()`
3. Modify Rule 1 to check community loyalty before forced choice
4. Add `should_defend_community_member()` function
5. Test basic loyalty behavior

### Step 2: Create Escalation Test (1-2 hours)
1. Create `tests/test_escalation_cycle.py`
2. Implement `run_escalation_cycle()`
3. Add `detect_retaliation_opportunity()` to find who B should scapegoat
4. Run Phase 1, then Phase 2 with loyalty rules
5. Validate: A defends A members, B defends B members
6. Output JSON with full timeline

### Step 3: Basic Visualization (2-3 hours)
1. Create `visualize_escalation.py`
2. Implement `two_community_layout()`
3. Add phase-based coloring and highlighting
4. Create static frames for each phase
5. Test with matplotlib.pyplot.show()

### Step 4: Animation (2-3 hours)
1. Add `animate_escalation_cycle()` function
2. Generate frame sequence with phase transitions
3. Add phase labels and annotations
4. Export as GIF using PillowWriter
5. Test animation playback

### Step 5: Comparison Visualization (1-2 hours)
1. Create `generate_escalation_comparison.py`
2. Run both scenarios (with/without loyalty)
3. Create side-by-side layout
4. Add metrics comparison
5. Export comparison figure

### Step 6: Documentation (1 hour)
1. Create `ESCALATION_DYNAMICS.md`
2. Document findings
3. Add theoretical interpretation (Schmitt, Girard, feud dynamics)
4. Include images and examples

## Expected Outputs

### 1. Test Results
```
escalation_cycle_data.json
├── phase1: {accuser, scapegoat, decisions, graph_state}
├── phase2: {retaliator, counter_scapegoat, decisions, graph_state}
└── metrics: {hostility, polarization, bridge_status}
```

### 2. Visualizations
```
output/escalation/
├── escalation_animation.gif          # Full cycle animation
├── phase1_static.png                 # A → B0 static
├── phase2_static.png                 # B → A1 static
├── final_polarization.png            # Final A vs B
├── comparison_defection_vs_loyalty.png
└── hostility_timeline.png            # Metrics over time
```

### 3. Key Metrics to Track
- **Phase 1**: % of A hostile to B0, % of B defending B0
- **Phase 2**: % of B hostile to A1, % of A defending A1
- **Final**: % inter-community hostility (A↔B negative edges)
- **Bridge status**: Maintained, weakened, or broken

## Theoretical Insights Expected

### 1. Loyalty Prevents Total Scapegoating
- With loyalty: Communities defend their members
- Without loyalty: Defection → all-against-one
- **Finding**: Community solidarity is protective

### 2. Escalation Creates Symmetric Polarization
- Phase 1: Asymmetric (A → B0)
- Phase 2: Symmetric (A ↔ B)
- **Finding**: Retaliation equalizes conflict

### 3. Bridge Becomes Fault Line
- Initially: Connection between communities
- During escalation: Conduit for hostility
- Finally: May break entirely (communities separate)
- **Finding**: Bridges enable but also suffer from escalation

### 4. Schmittian Friend-Enemy Distinction
- Start: Individuals with relationships
- End: Two unified camps (A vs B)
- **Finding**: Conflict creates political identities

### 5. Feud Dynamics (Montagues vs Capulets)
- Classic feud pattern: escalating retaliation
- Each side defends own, attacks other
- No resolution without external intervention
- **Finding**: Validates historical feud patterns

## Success Criteria

1. ✅ Modified simulator correctly implements loyalty rules
2. ✅ B members defend B0 instead of defecting
3. ✅ B successfully retaliates against A member
4. ✅ Final state shows mutual polarization (A vs B)
5. ✅ Animation clearly shows escalation phases
6. ✅ Comparison shows difference between defection and loyalty scenarios
7. ✅ Metrics confirm symmetric polarization

## Extensions (Future Work)

### 1. Multi-Round Escalation
- Not just 2 phases, but 3, 4, 5...
- Each side keeps retaliating
- Track escalation intensity over time

### 2. De-escalation Mechanisms
- Third-party mediation
- Breaking the bridge (isolation)
- Internal peace-makers who refuse to retaliate

### 3. Asymmetric Escalation
- Community A has more members (power imbalance)
- One side escalates more than the other
- Structural factors in escalation

### 4. Multiple Bridges
- What if there are 3 bridges between A and B?
- Does it accelerate or slow escalation?
- Redundancy effects

### 5. Three-Community Dynamics
- A vs B, then C joins
- Alliance formation (A+C vs B)
- Shifting coalitions

## Timeline Estimate

- **Step 1** (Simulator modification): 1-2 hours
- **Step 2** (Escalation test): 1-2 hours
- **Step 3** (Basic visualization): 2-3 hours
- **Step 4** (Animation): 2-3 hours
- **Step 5** (Comparison): 1-2 hours
- **Step 6** (Documentation): 1 hour

**Total**: 8-13 hours of focused work

**Realistic**: 2-3 days with breaks and testing

## Next Steps

1. **Immediate**: Create `src/simulator_with_loyalty.py`
2. **Then**: Build `tests/test_escalation_cycle.py`
3. **Validate**: Run test, confirm loyalty behavior
4. **Visualize**: Create basic static frames
5. **Animate**: Full cycle GIF
6. **Document**: Write up findings

---

**Ready to proceed with implementation?**
