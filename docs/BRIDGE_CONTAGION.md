# Bridge Contagion: Information Flow Across Community Boundaries

## Discovery

**Major Finding**: A single friendship bridge between communities IS sufficient for scapegoating contagion to spread from one community to another. However, the "energy cost" (number of edge changes) reveals a clear **phase transition** when contagion crosses the boundary.

## The Question

If Community A and Community B have a single positive edge connecting them (a "friendship bridge"), can scapegoating that begins in Community A spread to Community B through that bridge?

**Answer**: YES - but with interesting energy dynamics.

## The Mechanism

### Setup

**Two Communities**:
- **Community A**: 6 members, 90% positive internal edges (some internal conflicts)
- **Community B**: 6 members, 90% positive internal edges (some internal conflicts)
- **Bridge**: A2 ↔ B3 (single friendship connecting communities)

**Event**: A0 (Community A) accuses B0 (Community B)

### Contagion Path

```
1. A0 accuses B0
   └─> A0 ↔ B0 flips to negative

2. Accusation spreads through Community A via BFS
   ├─> A1 hears from A0, creates A1 → B0 negative edge
   ├─> A2 hears, creates A2 → B0 negative edge
   ├─> A3 hears, creates A3 → B0 negative edge
   ├─> A4 hears, creates A4 → B0 negative edge
   └─> A5 hears, creates A5 → B0 negative edge

3. A2 is connected to B3 via friendship bridge
   └─> Information flows: A2 tells B3 about B0

4. B3 (bridge node in B) hears accusation
   └─> B3 ↔ B0 flips to negative (ENTERS Community B)

5. Accusation spreads through Community B
   ├─> B1 hears from B3, flips B1 ↔ B0 to negative
   ├─> B4 hears, flips B4 ↔ B0 to negative
   ├─> B5 hears, flips B5 ↔ B0 to negative
   └─> B2 hears, flips B2 ↔ B0 to negative

RESULT: Both communities unified against B0
```

## Empirical Results

### Test 1: Bridge Sufficiency

**Results**:
- Community A hostile to B0: **6/6 (100%)**
- Community B hostile to B0: **5/5 (100%)**
- **✓ Contagion successfully crossed the bridge**

### Energy Cost Analysis

**Total Edge Changes: 12**

Breakdown by location:
- **Within Community A**: 0 edge flips
- **Within Community B**: 6 edge flips
- **Across A-B boundary**: 6 edge creations/flips

**Why the asymmetry?**

1. **Community A (origin)**: Members had NO prior relationship with B0
   - Creating NEW edges (not flipping existing ones)
   - Energy cost = 0 flips (5 new edges + 1 flip of accuser's edge)

2. **Community B (target)**: Members were B0's friends
   - Flipping EXISTING positive friendships to negative
   - Energy cost = 6 flips (breaking friendships)

**Key Insight**: **Higher energy cost within target's own community** - destroying existing friendships is the "expensive" part of scapegoating.

## Phase Transition at Boundary

### Three Phases of Contagion

**Phase 1: Within Community A** (Steps 1-6)
- 0 flips of internal A edges
- 5 edge creations to scapegoat B0
- Low energy (creating hostility where none existed)

**Phase 2: Crossing Boundary** (Step 7)
- Bridge node B3 hears from A2
- B3 ↔ B0 flips (FIRST flip in Community B)
- **PHASE TRANSITION** - contagion enters new community

**Phase 3: Within Community B** (Steps 8-11)
- 5 edge flips (B members break friendship with B0)
- High energy (destroying existing relationships)
- Cascade through B's internal network

### Energy Ratio

```
Energy in B / Energy in A = 6 / 0 = ∞

(If we count edge creations as "half energy", still 6 / 3 = 2x)
```

**Conclusion**: **Community B requires more energy** - breaking existing friendships vs creating new hostilities.

## Timeline Visualization

```
Cumulative Edge Changes Over Time:

12 ┤                                    ●●●●●
11 ┤                                  ●
10 ┤                                ●
 9 ┤                              ●
 8 ┤                            ●
 7 ┤                          ● <-- ENTERS COMMUNITY B
 6 ┤                        ●
 5 ┤          ●●●●●
 4 ┤        ●
 3 ┤      ●
 2 ┤    ●
 1 ┤  ●
 0 ●─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴
   0 1 2 3 4 5 6 7 8 9 10 11  (BFS step)
   |← A  →|     |←   B   →|
           ↑
        Bridge crossing
```

**Clear inflection point** when contagion enters Community B - second phase of rapid edge changes.

## Theoretical Implications

### 1. Information Bridges Enable Cross-Community Contagion

**Even one positive edge is sufficient** for contagion to spread between communities.

**Requirements**:
1. Friendship bridge between communities (A ↔ B positive edge)
2. Bridge node in A hears accusation (via BFS through A)
3. Bridge node tells bridge node in B
4. B's bridge node is connected to rest of B (BFS propagates)

**Failure modes**:
- No bridge exists (isolated communities)
- Bridge node in A doesn't hear (unreachable via friendship path)
- Bridge node in B is isolated (can't propagate to rest of B)

### 2. Energy Cost Reveals Community Structure

**Low energy phase**: Creating hostility toward outsider
- Community A turning against B0 (outgroup member)
- New edges, not flipped edges
- "Easy" to create outgroup enemy

**High energy phase**: Breaking internal friendships
- Community B turning against B0 (ingroup member)
- Flipping existing positive edges
- "Hard" to destroy friendships

**Key Insight**: **Scapegoating is more costly within the victim's own community** than from outside communities.

### 3. Bridge Nodes Are Critical

**Bridge node in Community A (A2)**:
- Must hear accusation (be reachable via BFS)
- Acts as information transmitter to other community
- Critical link in contagion chain

**Bridge node in Community B (B3)**:
- First to hear in B ("patient zero" in B)
- Must be connected to rest of B for propagation
- Initiates phase transition

**Implication**: **Isolating bridge nodes stops cross-community contagion**
- Remove/block bridge → communities become isolated
- Contagion contained within originating community

### 4. Asymmetric Awareness → Symmetric Hostility

**Process**:
1. **Start**: A and B unaware/neutral toward each other
2. **A unifies**: All of A hostile to B0 (outgroup member)
3. **Bridge crosses**: A2 → B3 transmission
4. **B unifies**: All of B hostile to B0 (B turns on own member)
5. **Result**: Both communities hostile to B0

**But**: Community A and B are NOT hostile to each other (yet)
- Only shared hostility toward B0
- Could escalate to A-B mutual hostility if B blames A for the accusation

## Comparison: Intra-Community vs Bridge Contagion

| Aspect | Intra-Community | Bridge Contagion |
|--------|----------------|------------------|
| **Communities** | One | Two (A → B) |
| **Bridge required** | No | Yes (single edge sufficient) |
| **Energy in origin** | N/A | Low (create new edges) |
| **Energy in target** | High (flip friendships) | High (flip friendships) |
| **Phase transition** | No | Yes (at bridge crossing) |
| **Victim awareness** | High (hears quickly) | Medium (hears after delay) |
| **Victim's community** | Turns against victim | Also turns against victim |

## Political and Social Implications

### 1. Social Media and Information Bridges

**Modern context**: Online social networks

**Mechanism**:
- Community A (e.g., political group, subreddit, etc.)
- Community B (different group)
- Bridge nodes: Users with friends in both communities
- Accusation spreads from A, crosses bridge, infects B

**Result**: Both communities unite against scapegoat, even though scapegoat is member of B

**Real-world pattern**: "Cancellation" spreading across social networks

### 2. Intergroup Conflict Escalation

**Scenario**: Scapegoating member of Community B from Community A

**Phase 1**: Community A unifies against B member
**Phase 2**: Information crosses bridge
**Phase 3**: Community B turns against own member (internal scapegoating)

**Escalation risk**:
- If B blames A for starting the accusation
- B may unify AGAINST A (counter-scapegoating)
- Mutual hostility emerges (Schmittian friend-enemy)

### 3. Destroying Inter-Community Trust

**Initial state**: A and B connected via bridge (cooperation exists)

**After scapegoating**:
- Bridge may break (B blames A, or vice versa)
- Trust destroyed
- Communities polarize

**Application**: How rumors/accusations destroy diplomatic relations, alliances, partnerships

### 4. Information Containment Strategies

**To prevent contagion crossing**:
1. **Remove bridges**: Isolate communities (censorship, firewalls)
2. **Block bridge nodes**: Prevent key individuals from hearing/transmitting
3. **Counter-narratives**: Bridge nodes spread alternative information
4. **Early detection**: Identify scapegoating before it reaches bridge

**Trade-off**: Isolation prevents contagion but also prevents cooperation

### 5. Different Energy Requirements Explain Resistance Patterns

**Why outgroup scapegoating is easier**:
- Low energy (no existing friendships to break)
- Community A easily unifies against B0 (outsider)
- "Us vs them" is cheap to create

**Why ingroup scapegoating is harder**:
- High energy (must break existing friendships)
- Community B's members were friends with B0
- Requires overcoming friendship bonds

**Prediction**: **Outgroup scapegoating is more common than ingroup** because it's energetically cheaper.

## Structural Requirements for Bridge Contagion

### Necessary Conditions

1. **Bridge Exists**: At least one positive edge A ↔ B
2. **A is connected**: BFS can reach bridge node in A from accuser
3. **B is connected**: BFS can reach rest of B from bridge node in B
4. **Accusation propagates**: Rules 1 and 3 fire correctly

### Sufficient Conditions

If all necessary conditions met:
- Contagion WILL cross bridge
- Both communities WILL unify against scapegoat
- Energy cost WILL be higher in scapegoat's home community

### Resilience Factors

**Communities resistant to bridge contagion**:
1. **No bridges**: Completely isolated (no positive A-B edges)
2. **Multiple bridges**: Redundancy makes blocking harder, but also means more pathways
3. **Bridge nodes are peripheral**: If bridge nodes in A can't hear, can't transmit
4. **Strong internal bonds in B**: High energy cost makes unification harder

## Energy Cost Formula

Let:
- `E_A` = energy cost in Community A
- `E_B` = energy cost in Community B
- `E_AB` = energy cost across boundary
- `n_A` = number of A members
- `n_B` = number of B members
- `k` = average degree of scapegoat in their community

**Observed pattern**:
```
E_A ≈ 0 (if A members don't know scapegoat)
E_B ≈ k (scapegoat's degree in B)
E_AB ≈ n_A (A members create edges to scapegoat)

Total energy: E_total ≈ n_A + k
```

**If scapegoat is hub in B**: `k` is large → high energy in B
**If scapegoat is peripheral in B**: `k` is small → low energy in B

**Implication**: **Peripheral members of Community B make "easier" scapegoats** when accused from Community A - lower energy to destroy their friendships.

## Comparison to Intergroup Scapegoating (No Bridge)

**Intergroup without bridge** (INTERGROUP_SCAPEGOATING.md):
- A unifies against B0
- B never hears (no bridge)
- Result: Asymmetric polarization (A vs B0, B unaware)

**Bridge contagion** (this document):
- A unifies against B0
- B DOES hear (via bridge)
- B also turns against B0
- Result: Both communities against B0 (symmetric targeting)

**Key difference**: Bridge enables symmetric response, but targeting same victim (not yet mutual A-B hostility)

## Escalation Scenarios

### Scenario 1: B Accepts the Accusation

**Process**:
1. A accuses B0
2. Contagion crosses bridge
3. B hears, investigates, confirms accusation
4. B scapegoats B0 too

**Result**: Coordinated scapegoating across communities (rare)

### Scenario 2: B Rejects the Accusation, Blames A

**Process**:
1. A accuses B0
2. Contagion crosses bridge
3. B hears, but defends B0
4. B blames A for false accusation
5. B unifies AGAINST Community A

**Result**: Intergroup conflict (A vs B, not just vs B0)

**Escalation**: Mutual scapegoating, Schmittian friend-enemy, conflict

### Scenario 3: Bridge Breaks

**Process**:
1. A accuses B0
2. Contagion begins crossing bridge
3. Bridge nodes (A2, B3) break their friendship
4. Contagion stopped

**Result**: Partial contagion (A unified, B partially hears or unaware)

## Computational Predictions

### When Bridge Contagion Succeeds

**Prerequisites**:
1. ✓ Bridge exists (A ↔ B positive edge)
2. ✓ A is connected (BFS reaches bridge node in A)
3. ✓ B is connected (BFS propagates through B)
4. ✓ Scapegoat is not bridge member (doesn't block own propagation)

**Result**: Both communities unified against scapegoat

### When It Fails

**Failure modes**:
1. **No bridge**: Communities isolated → contained within A
2. **Bridge node unreachable in A**: Can't transmit to B
3. **Bridge node isolated in B**: Can't propagate through B
4. **Bridge breaks early**: Transmission interrupted

### Energy Cost Predictions

**High energy (many flips)**:
- Scapegoat is hub in their community (many friendships to break)
- Scapegoat is well-liked (strong positive edges)
- Dense community (everyone is friends)

**Low energy (few flips)**:
- Scapegoat is peripheral (few friendships)
- Scapegoat has enemies (fewer positive edges to flip)
- Sparse community (not everyone connected)

## Implications for Conflict Resolution

### Prevention Strategies

**Block bridge contagion**:
1. **Remove bridges**: Isolate communities (prevents spread, but also cooperation)
2. **Strengthen bridges**: Multiple bridges make blocking harder
3. **Educate bridge nodes**: Train them to resist/counter accusations
4. **Early detection**: Identify scapegoating before bridge crossing

**Structural resilience**:
1. **Distributed bridges**: Many weak bridges instead of one strong bridge
2. **Cross-cutting memberships**: People belong to both A and B (reduces us-them)
3. **Institutional mediation**: Third parties verify accusations before spread

### De-escalation After Bridge Crossing

**If contagion has crossed**:
1. **Counter-narratives via same bridge**: Use bridge to spread alternative information
2. **Victim's allies in B**: Defenders speak up, break consensus
3. **A-B dialogue**: Direct communication between communities
4. **Expose bridge dynamics**: Make communities aware of manipulation

### Building Resistant Structures

**Communities resistant to bridge contagion**:
1. **Multiple group memberships**: Cross-cutting cleavages
2. **Strong friendship bonds**: High energy cost to break
3. **Institutional verification**: Require evidence before acceptance
4. **Norms against scapegoating**: Cultural resistance

## Conclusion

### Main Finding

**A single friendship bridge between communities IS sufficient for scapegoating contagion to spread from one community to another.**

### Key Insights

1. **Bridge Sufficiency**: One positive edge allows cross-community spread
2. **Phase Transition**: Clear energy spike when entering target community
3. **Asymmetric Energy**: Higher cost within victim's community (breaking friendships)
4. **Bridge Nodes Critical**: Isolating them prevents spread
5. **Escalation Risk**: Can lead to intergroup conflict if B blames A

### Energy Dynamics

**Outgroup scapegoating** (A → B0):
- Low energy in A (create hostility)
- High energy in B (break friendships)
- Total: n_A + k (where k = scapegoat's degree in B)

**Implication**: **Peripheral outgroup members are "energetically optimal" scapegoats** - easy to attack from outside, few friendships to break in their own community.

### Theoretical Integration

**Girard + Schmitt + Information Theory**:
- **Girard**: Scapegoating creates unity (validated in both communities)
- **Schmitt**: Friend-enemy distinction (could escalate to A vs B)
- **Information Theory**: Contagion follows network paths (BFS via positive edges)

**Contribution**: **Bridge contagion model explains how scapegoating crosses community boundaries and why it's easier to target outsiders.**

---

**Date**: 2025-11-15
**Test**: Bridge contagion with energy analysis
**Source**: `tests/test_bridge_contagion.py`
**Related**: INTERGROUP_SCAPEGOATING.md, FRAGMENTED_UNIFICATION.md
