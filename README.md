# A Deceptive Level Generator for Angry Birds

The Angry Birds AI competition has been held over
many years to encourage the development of AI agents that can
play Angry Birds game levels better than human players. Many
different agents with various approaches have been employed
over the competition’s lifetime to solve this task. Even though
the performance of these agents has increased significantly over
the past few years, they still show major drawbacks in playing
deceptive levels. This is because most of the current agents
try to identify the best next shot rather than planning an
effective sequence of shots. In order to encourage advancements
in such agents, we present an automated methodology to generate
deceptive game levels for Angry Birds. Even though there are
many existing content generators for Angry Birds, they do not
focus on generating deceptive levels. In this paper, we propose a
procedure to generate deceptive levels for six deception categories
that can fool the state-of-the-art Angry Birds playing AI agents.
Our results show that generated deceptive levels exhibit similar
characteristics of human-created deceptive levels. Additionally,
we define metrics to measure the stability, solvability, and degree
of deception of the generated levels.

link of the paper: https://ieee-cog.org/2021/assets/papers/paper_155.pdf

## How to run the level generator

1. To run the level generator:<br>
    1. Go to base directory
    2. Run the level generator in the command line providing the deception index as an argument (1:Rolling/falling objects deception, 2:Clearing paths deception, 3: Entity strength analysis deception, 4: Non-greedy actions deception 5: Non-fixed tap time deception 6: TNT deception)
     ```
        python level_generator.py <deception_index>
     ```
    3. Generated game levels will be available in the ```output_levels``` folder
