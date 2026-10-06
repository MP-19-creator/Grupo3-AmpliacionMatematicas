# Problema de Kepler

Este paquete contiene el código del problema de Kepler de los hitos, separado del de la PEI 1 (`src/dinamica_actitud/`). De momento solo tiene la capa física, en `fisica/`.

Para usarlo desde un script hay que añadir `src/` a la ruta de Python:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))  # desde hitos/hito_N/scripts/

from kepler.fisica import kepler_rhs, kepler_jacobian, specific_energy, angular_momentum
```
