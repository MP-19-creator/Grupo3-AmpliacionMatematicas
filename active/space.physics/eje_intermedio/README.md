# Física del eje intermedio

Esta es la física de la PEI 1: la rotación libre de un satélite rígido, sin pares exteriores, en ejes principales de inercia con I₁ < I₂ < I₃. El estado es la velocidad angular en ejes cuerpo, U = ω = (ω₁, ω₂, ω₃).

La carpeta está vacía todavía. Aquí irán, igual que en [`kepler/`](../kepler/):

- El campo F(U, t), que son las ecuaciones de Euler:

  ```text
  dω₁/dt = (I₂ − I₃)/I₁ · ω₂ω₃
  dω₂/dt = (I₃ − I₁)/I₂ · ω₃ω₁
  dω₃/dt = (I₁ − I₂)/I₃ · ω₁ω₂
  ```

- El Jacobiano exacto J(ω).
- Las dos magnitudes que se conservan:

  ```text
  2T = I₁ω₁² + I₂ω₂² + I₃ω₃²          energía cinética de rotación
  L² = I₁²ω₁² + I₂²ω₂² + I₃²ω₃²       módulo del momento angular
  ```

El Jacobiano completo y la estabilidad de los tres giros puros están en [`PEI1/README.md`](../../../PEI1/README.md).
