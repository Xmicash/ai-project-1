# Emergency response system

Run from the repository root using Python 3. No additional packages are required.

    python run.py Scenarios/Scenario1 --route N1 N2 --roads-only
    python run.py Scenarios/Scenario1 --route N1 N2 --baseline
    python -m unittest -v

With road reports, the first command gives N1 → H1 → N2 (78.60 s). The open-road baseline gives N1 → N2 (51.67 s).

## Road conditions and routing

Road reports are available at time zero and grouped by directed road. For each possible true state, start with its probability given the local weather. Multiply by the probability of each observed report given that state and its source, then normalize across the three states. This assumes reports are conditionally independent given the true status. Without weather evidence, average the weather-specific priors using the supplied weather probabilities.

For planning, use the most probable state. Omit roads classified as blocked. Congested roads take 1.5 times their normal travel time. For an open road, time in seconds is distance in metres divided by speed in metres per second. Exact ties favour blocked, then congested. Uniform-cost search returns the fastest path in this estimated graph.

For N1 → N2 in Scenario1, the probability of blockage is about 52.7%. The model excludes the road even though congestion is also plausible. This illustrates how choosing one state discards uncertainty. The reverse road has its own reports and is classified as congested.

## Traffic forecast

The default mode also reads historical traffic. Each direction has its own sequence ordered by observation number. The HMM starts with the initial distribution. For each reading it weights the current probabilities by the emission likelihoods, normalizes, and applies the transition matrix. After the final reading this gives a one-step forecast. A road without observations uses the initial distribution.

I use travel-time factors of 1.00, 1.15 and 1.35 for low, medium and high traffic. These are assumptions because the dataset provides no measured delay factors. The forecast-weighted average factor scales each available road's storm-adjusted travel time. This treats traffic as an additional delay and could overestimate travel time when a storm report already reflects traffic. The forecast is held fixed during routing because observation numbers have no specified duration in seconds.

    python run.py Scenarios/Scenario2 --route H2 N9 --roads-only
    python run.py Scenarios/Scenario2 --route H2 N9

The first route goes via N8 (48.57 s). With traffic included, the fastest estimated route goes via N7 (54.55 s). Times come from different cost models.

## Generate a response plan

    python run.py Scenarios/Scenario1 --output-dir results/Scenario1

Without an output directory, run.py writes plan.json and statistics.txt in the working directory. The route inspection commands still work.

At each incident release or responder availability event, consider only known, unassigned incidents. Each incident may be skipped or assigned to one free responder with the required capability and a route arriving by its absolute deadline. Backtracking enforces that each responder appears at most once in a simultaneous batch. It maximizes the counts served in priority order (critical, high, medium, low), then minimizes total release-to-arrival time. Exact ties follow input order. After arrival the responder stays at the scene for the service duration and starts subsequent trips there.

This policy optimizes the current dispatch batch. It can miss a better multi-event schedule and its search can be expensive with many simultaneous compatible calls. Deadlines use predicted travel times. The deadline percentage uses all incidents, including unhandled incidents as misses. The average response time includes only handled incidents. All times are in seconds.
