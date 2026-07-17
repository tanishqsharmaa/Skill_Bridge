---
name: system-design-doc
description: Design systems, services, and architectures. Trigger with "design a system for", "how should we architect", "system design for", "what's the right architecture for", or when the user needs help with API design, data modeling, or service boundaries.
---

# System Design

Help design systems and evaluate architectural decisions.

## Framework

### 1. Requirements Gathering
- Functional requirements (what it does)
- Non-functional requirements (scale, latency, availability, cost)
- Constraints (team size, timeline, existing tech stack)

### 2. High-Level Design
- Component diagram
- Data flow
- API contracts
- Storage choices

### 3. Deep Dive
- Data model design
- API endpoint design (REST, GraphQL, gRPC)
- Caching strategy
- Scaling approach (horizontal vs vertical)
- Failure modes and resiliency

### 4. Tradeoffs
- CAP theorem considerations
- Consistency vs availability
- Build vs buy vs open source
- Complexity vs maintainability

## Output Format

Provide a structured design with:
1. **Requirements summary** - confirm understanding
2. **Architecture diagram** - ASCII or Mermaid
3. **Component descriptions** - what each does and why
4. **Key decisions** - with rationale and alternatives
5. **Open questions** - uncertainties to resolve
