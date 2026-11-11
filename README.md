# Emergency response system

The first milestone computes the fastest route for one responder assuming every road is open. It uses Python 3 and the standard library.

Run from the repository root:

    python run.py Scenarios/Scenario1 --route H1 N3
    python -m unittest -v

The first command should print `H1 -> N3 (37.70 s)`. The scenario gives this road a length of 1131 metres and a speed of 30 metres per second.

The graph keeps each road direction supplied in the data. Uniform-cost search expands the node with the lowest known travel time. Since all travel times are nonnegative, the first time the destination is removed from the queue its cost is optimal. The predecessor map reconstructs the route.

This baseline ignores storm reports and historical traffic. Later milestones will estimate road conditions with Bayesian inference and traffic levels with a hidden Markov model, then use the resulting route costs for constraint-based incident allocation. The final simulation will produce plan.json and statistics.txt.
