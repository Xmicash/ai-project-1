# Development record

## First implementation request in this conversation

> make this for me , the task allows ai , make it in parts which i will push on github because ->Het verslag moet ook een link naar jullie coderepository (bv. GitHub) bevatten. so start with first push

ChatGPT (Codex) generated the graph loader, uniform-cost search, command-line entry point and routing tests. The open-road result provides a reference for checking how later estimates change a route. A shortest-time result at this stage only describes travel under normal conditions.

## Bayesian road estimates

Prompt: “alright continue with milestone 2 of the project”

ChatGPT (Codex) implemented a Bayesian update for each directed road and used the most probable status to update route costs. It tested missing evidence, conflicting sources, reverse-direction costs and a real detour. The Scenario1 detour is a model prediction. The supplied reports do not establish the road's true state.
