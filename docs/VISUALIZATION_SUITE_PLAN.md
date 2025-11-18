# Visualization Suite Plan: Scapegoating Dynamics

## Overview

Create a comprehensive suite of static and animated visualizations demonstrating:
1. **Fundamental scapegoating process** (small and large networks)
2. **Centrality effects** (hub vs peripheral scapegoats)
3. **Bridge dynamics** (why bridges make bad scapegoats)
4. **Community structures** (escalation, fragmentation, unification)

## Visualization Categories

### Category 1: Basic Scapegoat Process

**Goal**: Show the fundamental contagion mechanism in clean, educational examples

#### Viz 1.1: Small Network (5 nodes) - Complete Success
- **Structure**: 5-node complete graph (all friends)
- **Process**: A accuses B, contagion spreads via BFS
- **Frames**:
  - Initial: All positive edges
  - Step 1: A accuses B (A→B flips red)
  - Step 2: C hears from A (Rule 3), C→B turns red
  - Step 3: D hears, D→B turns red
  - Step 4: E hears, E→B turns red
  - Final: B isolated (all vs one)
- **Layout**: Circular layout, B at center (visually isolated)
- **Output**: `basic_5node_success.gif`

#### Viz 1.2: Small Network (5 nodes) - With Defenders
- **Structure**: 5-node graph with mixed edges (some internal conflicts)
- **Process**: Same accusation, but some nodes defend
- **Outcome**: Partial scapegoating (3 accusers, 1 defender)
- **Output**: `basic_5node_partial.gif`

#### Viz 1.3: Large Network (20 nodes) - Wave Propagation
- **Structure**: 20-node sparse graph (min_degree=3, 70% positive)
- **Process**: BFS wave spreading through network
- **Frames**: Show BFS frontier advancing (color nodes by discovery time)
- **Layout**: Force-directed or circular
- **Key features**:
  - Heat map showing BFS distance from accuser
  - Edges turning red as contagion spreads
  - Final state: accusers (red), defenders (green), scapegoat (dark red)
- **Output**: `basic_20node_wave.gif`

#### Viz 1.4: Comparison Panel - Small vs Large
- **Static image**: 2x2 grid showing initial and final states
  - Top row: 5-node (before/after)
  - Bottom row: 20-node (before/after)
- **Highlights**: Size doesn't change fundamental mechanism
- **Output**: `basic_size_comparison.png`

---

### Category 2: Centrality Effects

**Goal**: Demonstrate Girard's observation that peripheral nodes make better scapegoats

#### Viz 2.1: Star Graph - Hub as Scapegoat (FAILS)
- **Structure**: 1 hub + 5 peripheral nodes (star topology)
- **Scapegoat**: Hub (most central)
- **Accuser**: P1 (peripheral)
- **Process**:
  - P1 accuses Hub
  - P1 becomes isolated (only friend was Hub)
  - Other peripherals never hear (no path)
- **Final**: Only P1 hostile to Hub (catastrophic failure)
- **Layout**: Star layout (hub at center, periphery in circle)
- **Output**: `centrality_hub_fails.gif`

#### Viz 2.2: Star Graph - Peripheral as Scapegoat (SUCCESS)
- **Structure**: Same star graph
- **Scapegoat**: P5 (peripheral)
- **Accuser**: Hub (central)
- **Process**:
  - Hub accuses P5
  - Hub tells all other peripherals (has connections to all)
  - All peripherals join (100% unity)
- **Final**: Perfect unity against P5
- **Layout**: Same star layout
- **Output**: `centrality_peripheral_success.gif`

#### Viz 2.3: Comparison - Hub vs Peripheral
- **Static image**: Side-by-side comparison
  - Left: Hub as scapegoat (1/5 accusers = 20%)
  - Right: Peripheral as scapegoat (5/5 accusers = 100%)
- **Annotations**: Show degree centrality of each node
- **Metrics**: Unity % for each scenario
- **Output**: `centrality_comparison.png`

#### Viz 2.4: Degree Centrality Heatmap
- **Structure**: 20-node network
- **Visualization**: Nodes colored by degree centrality
  - Red (high degree) = bad scapegoats
  - Green (low degree) = good scapegoats
- **Show**: Try scapegoating 3 different nodes (high/medium/low centrality)
- **Results**: Unity achievement % correlates inversely with centrality
- **Output**: `centrality_heatmap.png`

---

### Category 3: Bridge Dynamics

**Goal**: Show why bridge nodes make terrible scapegoats (network fragmentation)

#### Viz 3.1: Simple Bridge (3-node chain)
- **Structure**: A — B — C (linear chain)
- **Scapegoat**: B (bridge connecting A and C)
- **Accuser**: A
- **Process**:
  - A accuses B
  - A→B flips red
  - C is now unreachable (only path was through B)
  - C never hears
- **Final**: A hostile to B, C unaware (50% unity)
- **Layout**: Linear horizontal layout
- **Annotation**: Show "Information barrier" where bridge was
- **Output**: `bridge_3node_chain.gif`

#### Viz 3.2: Two Communities Bridge
- **Structure**: Two 3-node communities (ABC and DEF) connected only via bridge C↔D
- **Scapegoat**: C (bridge node)
- **Accuser**: A (in community ABC)
- **Process**:
  - A accuses C
  - B hears from A, joins
  - Community ABC united against C (local success)
  - Community DEF never hears (C was only connector)
- **Final**: 2/5 accusers (community ABC), 0/3 in DEF
- **Layout**: Two clusters, bridge highlighted
- **Annotation**: "Network fragmented - information cannot cross"
- **Output**: `bridge_two_communities.gif`

#### Viz 3.3: Bridge Scapegoat vs Non-Bridge Scapegoat
- **Structure**: Same two-community graph
- **Comparison**:
  - Left: Bridge C as scapegoat (fails globally, 33% unity)
  - Right: Non-bridge B as scapegoat (succeeds, 100% unity)
- **Layout**: Side-by-side
- **Output**: `bridge_comparison.png`

#### Viz 3.4: Bridge Betweenness Visualization
- **Structure**: 15-node network with clear bridge nodes
- **Visualization**: Edge thickness = betweenness centrality
  - Thick edges = critical paths (many shortest paths go through)
  - Thin edges = redundant (many alternate paths)
- **Show**: Scapegoating node on thick edge → fragmentation
- **Show**: Scapegoating node on thin edge → unity
- **Output**: `bridge_betweenness.png`

---

### Category 4: Graph Requirements

**Goal**: Illustrate the min_degree ≥ 2 requirement

#### Viz 4.1: Dead End Problem (Degree 1 Node)
- **Structure**: Simple graph where one node has only scapegoat as friend
- **Example**: A — B — C — S (S is scapegoat, C only friends with S)
- **Process**:
  - A accuses S
  - B hears from A, joins
  - C hears from B, must choose between B (new info) and S (only friend)
  - C joins accusers (Rule 1)
  - C now isolated (degree 0)
  - If there were more nodes beyond C, they'd never hear
- **Annotation**: Highlight "Dead end - degree 1 after joining"
- **Output**: `requirements_dead_end.gif`

#### Viz 4.2: Ring Graph (Min Degree = 2 Works)
- **Structure**: 8-node ring (each node has exactly 2 friends)
- **Scapegoat**: Any node
- **Process**: Contagion propagates both directions around ring
- **Key**: After any node joins, still has 1 friend for propagation
- **Final**: 100% unity
- **Layout**: Circular ring
- **Output**: `requirements_ring_success.gif`

#### Viz 4.3: Degree Distribution and Unity
- **Structure**: Multiple graphs with different min_degree values
- **Grid**:
  - min_degree=1: Sometimes fails (show example)
  - min_degree=2: Always succeeds (show example)
  - min_degree=3: Always succeeds (show example)
- **Metrics**: Success rate for each degree threshold
- **Output**: `requirements_degree_comparison.png`

---

### Category 5: Advanced Dynamics (From Recent Work)

**Goal**: Show complex multi-community dynamics

#### Viz 5.1: Escalation Cycle (Already Created)
- **Use existing**: `output/escalation/escalation_animation.gif`
- **Shows**: A→B, then B→A retaliation
- **Outcome**: Mutual polarization (A vs B)

#### Viz 5.2: Fragmented Unification (Already Created)
- **Use existing**: `output/escalation/fragmented_escalation_animation.gif`
- **Shows**: Internal enemies reconcile via external conflict
- **Outcome**: Both communities 100% internally unified

#### Viz 5.3: Bridge Contagion (New)
- **Structure**: Two communities connected by single friendship bridge
- **Process**: A0 accuses B0, contagion crosses bridge, both communities turn against B0
- **Key frames**:
  - Initial: Two separate cohesive communities
  - Phase 1: Community A unifies against B0
  - Phase 2: Info crosses bridge (A2→B3)
  - Phase 3: Community B also turns against B0
- **Final**: Both communities hostile to B0 (symmetric targeting)
- **Layout**: Two-community layout (similar to escalation viz)
- **Output**: `advanced_bridge_contagion.gif`

---

## Implementation Plan

### Phase 1: Basic Foundations (4-6 hours)
1. **Viz 1.1-1.4**: Basic scapegoat process (small and large networks)
   - Reuse existing `visualize_cascade.py` framework
   - Add BFS wave coloring for large network
   - Create comparison grid generator

2. **Testing**: Run on generated graphs, verify outputs

### Phase 2: Centrality Effects (3-4 hours)
3. **Viz 2.1-2.4**: Hub vs peripheral scapegoats
   - Create star graph generator
   - Add centrality metric calculations
   - Create heatmap visualization for degree centrality

4. **Testing**: Verify 20% vs 100% unity rates

### Phase 3: Bridge Dynamics (3-4 hours)
5. **Viz 3.1-3.4**: Bridge node scapegoating failures
   - Create chain and two-community graph generators
   - Add betweenness centrality calculations
   - Show fragmentation clearly in visualizations

6. **Testing**: Verify fragmentation patterns

### Phase 4: Requirements & Advanced (3-4 hours)
7. **Viz 4.1-4.3**: Graph structure requirements
   - Create dead-end examples
   - Generate ring graphs
   - Create degree distribution comparison

8. **Viz 5.3**: Bridge contagion (new advanced example)
   - Adapt escalation visualization code
   - Show cross-community information flow

9. **Testing**: Verify all prerequisites

### Phase 5: Documentation & Polish (2-3 hours)
10. **Create index/gallery**: HTML page showing all visualizations
11. **README update**: Add visualization gallery section
12. **Annotations**: Ensure all visualizations have clear titles and explanations

---

## Technical Specifications

### Common Features (All Visualizations)

**Layout Options**:
- Circular: Good for small complete graphs (Viz 1.1, 1.2)
- Force-directed (spring): Good for general graphs (Viz 1.3)
- Star: For hub-and-spoke (Viz 2.1, 2.2)
- Two-community: For intergroup dynamics (Viz 3.2, 5.3)
- Linear: For chains (Viz 3.1)

**Color Scheme**:
- Nodes:
  - Blue: Normal/uninvolved
  - Orange: Accuser (initial)
  - Red: Accusers (joined)
  - Green: Defenders
  - Dark Red: Scapegoat
  - Gray: Unreachable (never heard)
- Edges:
  - Green: Friendship (positive)
  - Red: Hostility (negative)
  - Light gray: Absent/neutral

**Animation Settings**:
- FPS: 2 for small networks, 1 for complex dynamics
- Duration: 0.5s per frame for smooth viewing
- Loop: Infinite for GIFs

**Static Image Settings**:
- DPI: 150 for crisp text
- Size: 10x8 inches for single images, 16x12 for grids
- Font: Readable size (12pt for labels, 14pt for titles)

### File Organization

```
output/
├── basic/
│   ├── 5node_success.gif
│   ├── 5node_partial.gif
│   ├── 20node_wave.gif
│   └── size_comparison.png
├── centrality/
│   ├── hub_fails.gif
│   ├── peripheral_success.gif
│   ├── comparison.png
│   └── heatmap.png
├── bridge/
│   ├── 3node_chain.gif
│   ├── two_communities.gif
│   ├── comparison.png
│   └── betweenness.png
├── requirements/
│   ├── dead_end.gif
│   ├── ring_success.gif
│   └── degree_comparison.png
├── advanced/
│   ├── bridge_contagion.gif
│   ├── escalation_cycle.gif (existing)
│   └── fragmented_unification.gif (existing)
└── gallery.html (index of all visualizations)
```

### Code Structure

**New Files**:
1. `visualize_basic.py` - Generate basic process visualizations (Category 1)
2. `visualize_centrality.py` - Generate centrality visualizations (Category 2)
3. `visualize_bridge.py` - Generate bridge visualizations (Category 3)
4. `visualize_requirements.py` - Generate requirement visualizations (Category 4)
5. `visualize_advanced.py` - Generate advanced visualizations (Category 5)
6. `generate_gallery.py` - Create HTML gallery index

**Reusable Components** (shared library):
```python
# viz_utils.py
def create_layout(graph, layout_type='circular', **kwargs):
    """Generate node positions for different layout types."""

def animate_contagion(graph, decisions, layout, output_path, fps=2):
    """Create animated GIF of contagion process."""

def create_comparison_grid(images, titles, output_path):
    """Create side-by-side comparison of multiple scenarios."""

def add_metrics_overlay(ax, accusers, defenders, total):
    """Add text overlay showing unity metrics."""
```

---

## Success Criteria

### Educational Value
- [ ] Clearly demonstrates fundamental scapegoat mechanism
- [ ] Shows why centrality matters (Girard validation)
- [ ] Illustrates bridge fragmentation problem
- [ ] Explains graph structure requirements

### Technical Quality
- [ ] All animations smooth and clear
- [ ] Color scheme consistent across suite
- [ ] Annotations readable and informative
- [ ] No visual clutter

### Completeness
- [ ] All 4 categories fully implemented
- [ ] Static and animated versions where appropriate
- [ ] Comparison visualizations show contrasts clearly
- [ ] Gallery provides easy navigation

### Documentation
- [ ] Each visualization has accompanying explanation
- [ ] Gallery HTML is clear and organized
- [ ] README updated with visualization links
- [ ] Code is well-commented

---

## Timeline Estimate

**Total Time**: 15-21 hours

Breakdown:
- Phase 1 (Basic): 4-6 hours
- Phase 2 (Centrality): 3-4 hours
- Phase 3 (Bridge): 3-4 hours
- Phase 4 (Requirements & Advanced): 3-4 hours
- Phase 5 (Documentation): 2-3 hours

**Recommended Approach**: Implement in phases, testing thoroughly before moving to next phase.

---

## Dependencies

**Required Libraries**:
- `matplotlib` - Plotting and animation
- `numpy` - Numerical operations
- `networkx` (optional) - Graph layouts and centrality calculations

**Existing Code to Reuse**:
- `visualize_cascade.py` - Animation framework
- `visualize_escalation.py` - Two-community layout
- `src/simulator.py` - Contagion simulation
- `src/graph.py` - Graph data structure

---

## Notes

1. **Modular Design**: Each category can be developed independently
2. **Reusability**: Create shared utilities to avoid duplication
3. **Testing**: Generate test cases for each visualization before creating final versions
4. **Iteration**: First pass for functionality, second pass for aesthetics
5. **Gallery**: Build incrementally as visualizations are completed

---

**Date**: 2025-11-16
**Purpose**: Comprehensive visualization suite for scapegoating dynamics
**Scope**: 15+ visualizations covering all major findings
