# Emergency response system

Run from the repository root using Python 3. No additional packages are required.

    python run.py Scenarios/Scenario1 --route N1 N2
    python run.py Scenarios/Scenario1 --route N1 N2 --baseline
    python -m unittest -v

With road reports, the first command gives N1 → H1 → N2 (78.60 s). The open-road baseline gives N1 → N2 (51.67 s).

## Road conditions and routing

Road reports are available at time zero and grouped by directed road. For each possible true state, start with its probability given the local weather. Multiply by the probability of each observed report given that state and its source, then normalize across the three states. This assumes reports are conditionally independent given the true status. Without weather evidence, average the weather-specific priors using the supplied weather probabilities.

For planning, use the most probable state. Omit roads classified as blocked. Congested roads take 1.5 times their normal travel time. For an open road, time in seconds is distance in metres divided by speed in metres per second. Exact ties favour blocked, then congested. Uniform-cost search returns the fastest path in this estimated graph.

For N1 → N2 in Scenario1, the probability of blockage is about 52.7%. The model excludes the road even though congestion is also plausible. This illustrates how choosing one state discards uncertainty. The reverse road has its own reports and is classified as congested.

Traffic forecasting, responder allocation and final plan generation are pending.
