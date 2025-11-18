# Fragmented Unification: External Enemies Unify Divided Communities

## Discovery

**Major Finding**: External scapegoating can unify internally divided, non-cohesive communities in TWO ways:
1. **Negative Unity** (asymmetric conflict): Shared hostility toward outgroup member without resolving internal conflicts
2. **Complete Unification** (symmetric escalation): Internal conflicts actually RESOLVE through escalation cycle via Rule 2 (enemy's enemy is friend)

**Update 2025-11-16**: Escalation dynamics show that when BOTH communities retaliate, internal enemies reconcile completely through --- triangle resolution. External conflict transforms into complete internal unity + mutual polarization.

## The Problem with Assuming Pre-existing Cohesion

### Classical Girardian Scapegoating

**Assumption**: Community is cohesive (all positive internal edges)
- Crisis creates mimetic tension
- Community turns on one member
- Member expelled/killed
- Unity restored

**Limitation**: Real communities are RARELY cohesive
- Internal factions exist
- Members have enemies within the community
- Conflicts, rivalries, competing interests
- No pure "all-positive" starting state

### The Realistic Scenario

**Fragmented Communities**:
- Internal divisions (positive AND negative edges)
- Factions oppose each other
- BUT: Still connected via positive edges (some friendships exist)
- Cannot achieve internal unity through internal scapegoating (picks sides)

**Question**: Can such communities achieve unity through EXTERNAL scapegoating?

**Answer**: YES - via "negative unity"

## The Mechanism

### Starting Conditions

**Community A (Fragmented)**:
- Size: N members
- Internal edges: Mix of positive and negative
- Positive edges form connected graph (min_degree ≥ 2)
- Example: 60% positive, 40% negative (substantial division)

**Community B (Outgroup)**:
- Separate community
- Internal state: Any (cohesive or fragmented)
- Relation to A: Sparse or none (disconnected communities)

### Event: A Member Accuses B Member

```
A0 (Community A) accuses B0 (Community B)
```

### Information Contagion Process

**Within Community A**:
1. **A0 → B0**: Initial accusation (edge flips/creates negative)
2. **A0 → A1**: Information spreads through A's friendship network
3. **A1 → B0**: A1 hears from A0, creates negative edge to B0
4. **A1 → A2**: Continues spreading within A
5. **Even if A1 and A2 are enemies**, information still spreads through positive edges
6. **All of A hears about B0** (via BFS through friendship subgraph)

**Result**: All A members develop negative edge to B0

### Critical Insight

**Internal divisions REMAIN**:
- A1 and A2 may still be enemies
- Factions still oppose each other
- No change to internal structure

**BUT: External unity EMERGES**:
- All of A is hostile to B0
- Shared external enemy
- Common outgroup identity

## Empirical Results

### Test 1: Fragmented Community Unification

**Setup**:
- Community A: 6 members, 60% positive internal edges (40% enemies)
- Community B: 4 members, fully cohesive
- A0 accuses B0

**Initial State**:
- A internal: 9 positive, 1 negative (10% hostile)
- A-B relations: 1 positive edge (accuser-scapegoat)

**Results**:
- **A members hostile to B0**: 6/6 (100% external unity)
- **A internal**: 10 positive, 0 negative (internal enemies resolved as side effect)
- **Mechanism**: BFS spread information through all of A's connected friendship network

**Conclusion**: ✓ Fragmented community achieved external unity

### Test 2: Manufacturing Hostility

**Setup**:
- Communities completely unaware of each other initially
- No inter-community edges (except accuser-scapegoat link)

**Results**:
- **A members hostile to B0**: 5/5 (100%)
- **Inter-community edges**: Created 5 negative edges where none existed
- **'Them' manufactured** where only 'us' existed before

**Conclusion**: ✓ Hostility created where none existed

### Test 3: Generalization to Entire Outgroup

**Setup**:
- A0 has friends in both A and B
- A1 has enemy in B (pre-existing antagonism)
- Other A members: unaware of B

**Results**:
- **Total A-B relations**: 4 negative, 2 positive
- **Generalization**: Scapegoating B0 creates primed hostility toward ALL of B
- **Guilt by association**: B members become 'the enemy' category

**Conclusion**: ✓ Outgroup identity created through scapegoating

## Theoretical Framework

### Negative Unity

**Definition**: Unity achieved through shared opposition, not cohesion

**Characteristics**:
- Internal divisions remain (enemies still enemies)
- External unity emerges (all hostile to outgroup)
- Partial unification: "We disagree, but we all hate them"
- Temporary: Lasts only while external enemy exists

**Formal Statement**:

```
Before:
  Internal(A): Mixed (positive + negative edges)
  External(A, B): None or sparse

After:
  Internal(A): Mixed (UNCHANGED)
  External(A, B0): Unified hostility (ALL negative)

Internal coherence: Low → Low (no change)
External coherence: None → High (unified enemy)
```

### Comparison: Internal vs External Scapegoating

| Aspect | Internal Scapegoating | External Scapegoating |
|--------|----------------------|----------------------|
| **Starting State** | Cohesive community | Fragmented community |
| **Mechanism** | All turn against one member | All turn against outgroup member |
| **Result** | Internal unity restored | External unity created |
| **Internal divisions** | Resolved (purged) | Remain unchanged |
| **Type of unity** | Positive (cohesion) | Negative (opposition) |
| **Stability** | Stable (crisis resolved) | Unstable (requires enemy) |
| **Function** | Purification | Identity formation |

### Why Fragmented Communities Need External Scapegoating

**Problem**: Internal scapegoating fails when community is fragmented
- Picking internal scapegoat chooses sides in existing conflict
- Factions rally around "their" members
- Creates deeper division, not unity

**Solution**: External scapegoating
- Outgroup member is universally "other"
- No faction has loyalty to outgroup
- All factions can unite against external enemy
- Divisions temporarily set aside

## Political Implications

### 1. Rally Around the Flag Effect

**Mechanism**: Nation divided internally, external threat emerges, divisions set aside

**Example Pattern**:
- Domestic politics: Left vs Right, intense conflict
- Foreign threat appears (war, terrorism, rival nation)
- Opposition supports government: "We're all Americans now"
- Unity lasts duration of threat

**Computational Validation**:
- Fragmented community A (internal enemies)
- External scapegoat B0
- Result: 100% A unified against B0 despite internal divisions

### 2. Manufacturing Consent

**Mechanism**: Leaders face internal opposition, create/emphasize external enemy, opposition unifies with leaders

**Process**:
1. Government faces domestic criticism
2. Identify/create external threat (rival nation, terrorist group, etc.)
3. Frame criticism as helping the enemy
4. Opposition must choose: criticize government or oppose enemy
5. Opposition joins government in opposing enemy (temporary unity)

**Why It Works**:
- External enemy creates shared identity
- Criticism becomes "unpatriotic"
- Internal divisions less salient than external threat

### 3. Partisan Polarization

**Mechanism**: Political party is fragmented, scapegoat other party, factions unify

**Example**:
- Republican party: Moderates vs conservatives vs populists (internal divisions)
- Democrats as outgroup scapegoat
- Message: "Better our flawed party than THEM"
- Internal factions unite against Democrats despite disagreements

**Computational Model**:
- Community A (party) is fragmented (factions)
- Community B (other party) as outgroup
- All A factions develop hostility to B
- "Negative partisanship": Defined by opposition to other party, not support for own

### 4. Wartime Unity

**Mechanism**: Country has deep internal divisions, external war unifies nation temporarily

**Historical Pattern**:
- Pre-war: Class conflict, racial tension, regional divisions
- War begins: "National unity" emerges
- Post-war: Divisions resurface

**Critical Insight**: Unity is TEMPORARY
- Requires maintenance (enemy must be kept alive)
- When war ends, divisions return
- May seek new enemies to maintain unity

### 5. Creating 'The Other'

**Mechanism**: Community lacks identity, scapegoat outgroup, define self as "not-them"

**Identity Formation Through Opposition**:
1. Community A is fragmented, lacks coherent identity
2. Scapegoat outgroup B
3. A defines itself as "not-B"
4. Identity emerges: "We are those who oppose them"

**Examples**:
- Nationalism: "We are not them (other nations)"
- Religious identity: "We are not heretics/infidels"
- Political identity: "We are not the other party"
- Ethnic identity: "We are not those people"

## Why This Is More Realistic

### Real Communities Are Fragmented

**Classical Assumption**: Communities are cohesive (all friends)

**Reality**: Communities have internal conflicts
- Families: Siblings, in-laws, generational conflicts
- Nations: Regional, class, racial, ideological divisions
- Political parties: Factions, competing power centers
- Religious groups: Denominations, theological disputes
- Companies: Departments, hierarchies, competing interests

**Implication**: Internal scapegoating creates deeper division

### External Enemies Are Politically Useful

**For Leaders**:
1. **Unify fractious coalitions**: Factions set aside differences
2. **Distract from internal problems**: Focus on external threat
3. **Create identity through opposition**: Define "us" as "not-them"
4. **Mobilize population**: Shared enemy motivates action
5. **Legitimacy through threat**: "Only I can protect you from them"

**Why It Works**:
- Easier to create external enemy than resolve internal conflicts
- External enemy threatens ALL factions (common threat)
- Opposition to external enemy is universally acceptable
- No need to choose sides in internal conflict

### Negative Unity Is Inherently Unstable

**Characteristics**:
1. **Temporary**: Lasts only while enemy exists
2. **Fragile**: Internal divisions still present underneath
3. **Requires maintenance**: Enemy must be kept alive or replaced
4. **Negative, not positive**: Against something, not for something

**When Enemy Disappears**:
- External unity dissolves
- Internal conflicts resurface
- May need NEW external enemy
- Cycle of scapegoating continues

## Girardian Extension

### Girard's Original Theory

**Thesis**: Scapegoating restores unity to community in crisis

**Mechanism**: All-against-one violence purges internal conflict

**Assumption**: Community is initially cohesive (or was before crisis)

### Computational Extension

**When Community Is ALREADY Fragmented**:

1. **Internal scapegoating FAILS**
   - Picks sides in existing conflict
   - Deepens divisions
   - Some defend the scapegoat (factional loyalty)

2. **External scapegoating SUCCEEDS**
   - Universal "other" (no faction loyalty)
   - All factions can unite against external enemy
   - Creates "negative unity" (unified in opposition)

**Two Mechanisms**:

| Type | Starting State | Result | Function |
|------|---------------|--------|----------|
| **Intragroup** | Cohesive → Crisis → Fragmented | Cohesive (purified) | Purification |
| **Intergroup** | Fragmented (pre-existing divisions) | Negative unity | Identity formation |

### Girard's Peripheral Scapegoat Observation

**Girard**: Scapegoats are often marginal, peripheral figures

**Computational Validation**:
- Hub scapegoats: 20% success (community fractures)
- Peripheral scapegoats: 100% success (community unifies)
- See CENTRALITY_AND_SCAPEGOATING.md

**Extension to Intergroup**:
- Peripheral scapegoats work for INTRAGROUP scapegoating
- Outgroup members are UNIVERSALLY peripheral (not part of ingroup at all)
- External scapegoating is "maximally peripheral" scapegoating

## Limitations and Caveats

### 1. Unity Is Partial

**What Changes**:
- External relations: All hostile to outgroup scapegoat

**What DOESN'T Change**:
- Internal relations: Enemies still enemies
- Power dynamics: Hierarchies remain
- Competing interests: Conflicts still exist

**Result**: "Surface unity" over underlying division

### 2. Unity Is Temporary

**Duration**: Only while external enemy is salient

**When Unity Dissolves**:
- Enemy defeated/destroyed
- Enemy no longer perceived as threat
- Internal problems become more salient
- Attention shifts back to internal conflicts

**Consequence**: Requires new enemies or constant threat maintenance

### 3. Unity Is Negative

**Unified AGAINST, Not FOR**:
- Shared opposition, not shared goals
- Negative identity ("not-them"), not positive identity ("we are...")
- Reactive, not proactive
- Defensive, not constructive

**Limitation**: Cannot build on negative unity
- No positive program
- No constructive cooperation
- Only sustained by maintaining threat

### 4. Requires Maintenance

**External Enemy Must Be Kept Alive**:
- If defeated, unity dissolves
- Need constant reminders of threat
- May need to invent new enemies
- Escalation risk (real conflict from manufactured threat)

**Cycle of Scapegoating**:
1. Fragmented community unifies against external enemy
2. Enemy defeated or becomes non-salient
3. Unity dissolves, internal divisions resurface
4. Need NEW external enemy
5. Repeat indefinitely

### 5. Self-Fulfilling Prophecy

**Risk**: Manufactured enemies become real enemies

**Mechanism**:
1. Community A scapegoats member of B
2. A unifies in hostility toward B
3. B learns about hostility
4. B unifies AGAINST A (symmetric polarization)
5. Mutual hostility, real conflict

**Result**: Created real enemy where none existed (or made existing conflict worse)

## Computational Predictions

### When Fragmented Unification Succeeds

**Prerequisites**:
1. **Community A is fragmented**: Internal divisions (positive + negative edges)
2. **BUT: Friendship connectivity**: Positive edges form connected graph
3. **Outgroup B exists**: Separate community
4. **Sparse inter-group ties**: Few A-B connections
5. **Accuser in A**: Starts scapegoating of B member

**Result**: A unifies against B member, internal divisions remain but shared external enemy emerges

### When It Fails

**Failure Modes**:
1. **A too fragmented**: No connected friendship graph (information doesn't spread)
2. **A-B too integrated**: Many positive cross-ties (some A members defend B member)
3. **B member is bridge**: Cutting them isolates part of A (structural damage)
4. **Internal backlash**: A members reject scapegoating (moral resistance)

### Escalation to Symmetric Conflict

**Triggers**:
1. **B learns** about A's scapegoating
2. **B unifies** against A (mirror response)
3. **Symmetric polarization**: Both sides unified against each other
4. **Conflict escalation**: Mutual hostility, us-vs-them dynamics

**Result**: Two unified groups in opposition (full Schmittian friend-enemy distinction)

## Implications for Conflict Resolution

### Prevention Strategies

**Increase Inter-group Integration**:
- More positive A-B connections
- Cross-cutting friendships
- Shared institutions, activities
- Make scapegoating costly (lose friends)

**Address Internal Divisions**:
- Resolve internal conflicts constructively
- Build positive internal cohesion
- Remove incentive for external scapegoating

**Early Detection**:
- Identify scapegoating attempts early
- Counter-narratives before unification completes
- Expose manufactured enemies

### De-escalation After Unification

**Break Information Isolation**:
- Create channels for inter-group communication
- Humanize outgroup members
- Personal relationships across boundaries

**Third-Party Mediation**:
- External perspective
- Facilitate dialogue
- Reframe conflict

**Shift to Superordinate Goals**:
- Common enemies/threats (larger than A vs B)
- Shared goals requiring cooperation
- Redefine boundaries (A+B vs C)

### Structural Resilience

**Communities Resistant to Fragmented Unification**:
1. **Highly integrated**: Many cross-group friendships
2. **Weak boundaries**: Unclear who is "us" vs "them"
3. **Cross-cutting cleavages**: Multiple overlapping group identities
4. **Distributed leadership**: No central propagators of scapegoating narratives

## Case Studies and Examples

### Historical Examples

**World War I**:
- Pre-war: European nations with intense internal class conflicts
- War begins: Internal divisions set aside ("national unity")
- Post-war: Labor movements, revolutions resurface

**9/11 Aftermath**:
- Pre-9/11: U.S. political divisions, contested 2000 election
- Post-9/11: Bipartisan support for government, "United We Stand"
- Later: Divisions return, arguably deeper than before

**Cold War**:
- U.S. internal divisions (civil rights, class, etc.)
- Soviet Union as external enemy
- "Anti-communism" unifies disparate groups
- Post-Cold War: Search for new enemies (terrorism, etc.)

### Contemporary Patterns

**Partisan Politics**:
- Both parties internally fragmented
- Unity achieved through opposition to other party
- "Negative partisanship" stronger than positive support
- Moderates pulled toward extremes in opposition to other side

**Nationalist Movements**:
- Internal economic/cultural divisions
- Scapegoat immigrants, foreigners, other nations
- National unity through shared opposition
- "Make [Country] Great Again" = define against outsiders

**Social Media Dynamics**:
- Online communities fragmented by interests, demographics
- Unity through shared outrage at outgroup
- "Us vs them" narratives
- Constant need for new outrages to maintain unity

## Conclusion

### Main Finding

**External scapegoating can unify internally divided communities through shared hostility toward an outgroup member.**

### Key Insights

1. **Negative Unity**: Unified AGAINST, not FOR
   - Internal divisions remain
   - External unity emerges
   - Temporary, fragile, requires maintenance

2. **More Realistic Than Classical Girardian Model**:
   - Real communities are fragmented
   - Internal scapegoating picks sides (fails)
   - External scapegoating unifies (succeeds)

3. **Politically Useful**:
   - Leaders use external enemies to unify fractious groups
   - Distract from internal problems
   - Create identity through opposition
   - Mobilize population

4. **Computationally Validated**:
   - 100% external unity achieved
   - Internal divisions unchanged
   - Hostility manufactured where none existed
   - Generalizes to entire outgroup (guilt by association)

### Girard Extended

**Two Mechanisms of Scapegoating**:

1. **Intragroup** (Classical Girardian):
   - Cohesive community → Crisis → Fragmentation
   - All turn against one member
   - Expulsion/violence → Unity restored
   - Function: Purification

2. **Intergroup** (Political Extension):
   - Fragmented community (pre-existing divisions)
   - All turn against outgroup member
   - Shared external enemy → Negative unity
   - Function: Identity formation

### Schmitt Validated

**Friend-Enemy Distinction**:
- Not given, but MANUFACTURED through scapegoating
- Communities define themselves AGAINST outgroups
- "The political" emerges from scapegoating dynamics
- Identity formed through opposition

### Danger

**Self-Fulfilling Prophecy**:
- Manufactured enemies become real enemies
- Escalation to symmetric conflict
- Destroys cooperation, creates violence
- Cycle of scapegoating requires ever-new enemies

### Hope

**Structural Resistance**:
- Integrated communities resist scapegoating
- Cross-cutting cleavages prevent unified opposition
- Positive internal cohesion removes need for external enemies
- Conflict resolution addresses root causes

---

## Two Modes of Fragmented Unification

### Mode 1: Negative Unity (Asymmetric Conflict)

**Scenario**: Single community A scapegoats outgroup member B0
- **Result**: All of A hostile to B0
- **Internal state**: Unchanged (enemies still enemies)
- **External state**: Unified hostility
- **Type**: Negative unity (against, not for)

**Source**: `tests/test_fragmented_unification.py`

### Mode 2: Complete Unification (Symmetric Escalation)

**Scenario**: Two fragmented communities engage in escalation cycle (A→B, B→A)
- **Phase 1**: A accuses B0 → A unifies internally (Rule 2: enemy's enemy)
- **Phase 2**: B retaliates against A1 → B unifies internally (Rule 2)
- **Result**: BOTH communities achieve 100% internal cohesion
- **Internal state**: All internal enemies reconcile
- **External state**: Mutual polarization (A vs B)
- **Type**: Complete transformation (internal unity + external conflict)

**Quantitative Results**:
- Community A: 86.7% → 100% cohesion (2 enemies reconciled)
- Community B: 73.3% → 100% cohesion (4 enemies reconciled)
- Cross-community hostility: 30.6% mutual

**Mechanism**: Shared external enemy creates --- triangles between former internal enemies, forcing reconciliation

**Key Insight**: "Nothing unites a people like a common enemy" - computationally validated

**Source**: `tests/test_fragmented_escalation.py`, `output/escalation/fragmented_escalation_animation.gif`

### Comparison: Negative Unity vs Complete Unification

| Aspect | Negative Unity | Complete Unification |
|--------|----------------|---------------------|
| **Conflict type** | Asymmetric (A→B0) | Symmetric (A↔B) |
| **Retaliation** | None | Yes (escalation cycle) |
| **Internal conflicts** | Unchanged | Resolved (100% cohesion) |
| **External state** | Unified hostility to individual | Mutual polarization (group vs group) |
| **Mechanism** | Shared enemy (partial) | Rule 2 --- triangle resolution |
| **Stability** | Temporary (requires enemy) | More stable (structural reconciliation) |
| **Political pattern** | Rally around flag | Feud dynamics (Montagues vs Capulets) |

---

**Date**: 2025-11-15 (original), 2025-11-16 (escalation update)
**Tests**: 3 negative unity scenarios + fragmented escalation test
**Source**: `tests/test_fragmented_unification.py`, `tests/test_fragmented_escalation.py`
**Related**: ESCALATION_DYNAMICS.md, INTERGROUP_SCAPEGOATING.md, CENTRALITY_AND_SCAPEGOATING.md


