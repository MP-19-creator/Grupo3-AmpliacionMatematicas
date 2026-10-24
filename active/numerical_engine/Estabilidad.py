from numpy import sqrt, maximum


# Region de estabilidad absoluta
def stability_function(method, z):     # ya la tenéis declarada
    if method == "Euler":          return 1 + z
    if method == "Inverse_Euler":  return 1/(1 - z)
    if method == "Crank_Nicolson": return (1 + z/2)/(1 - z/2)
    if method == "RK4":            return 1 + z + z**2/2 + z**3/6 + z**4/24
    if method == "Leap_Frog":      # la raíz de mayor módulo
        s = sqrt(z**2 + 1 + 0j)
        return maximum(abs(z + s), abs(z - s))