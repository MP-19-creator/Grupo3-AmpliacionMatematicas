# Enunciado

**Milestone 2: Prototypes to integrate orbits with functions.**

1. Write a function called Euler to integrate one step. The function $F(U, t)$ of the Cauchy problem should be input argument.
2. Write a function called Crank_Nicolson to integrate one step.
3. Write a function called RK4 to integrate one step.
4. Write a function called Inverse_Euler to integrate one step.
5. Write a function to integrate a Cauchy problem. Temporal scheme, initial condition and the function $F(U, t)$ of the Cauchy problem should be input arguments.
6. Write a function to express the force of the Kepler movement. Put emphasis on the way the function of the Cauchy problem is written: $F = [\dot{r},\, -r/|r|^3]$ where $r, \dot{r} \in \mathbb{R}^2$.
7. Integrate an orbit with these latter schemes and explain the results.
8. Increase and decrease the time step and explain the results.