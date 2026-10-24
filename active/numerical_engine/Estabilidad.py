from numpy import sqrt, maximum

# Region de estabilidad absoluta
def stability_function(method, w):
    if method == "Euler":          return 1 + w
    if method == "Inverse_Euler":  return 1/(1 - w)
    if method == "Crank_Nicolson": return (1 + w/2)/(1 - w/2)
    if method == "RK4":            return 1 + w + w**2/2 + w**3/6 + w**4/24
    if method == "Leap_Frog":      # la raíz de mayor módulo
        s = sqrt(w**2 + 1 + 0j)
        return maximum(abs(w + s), abs(w - s))