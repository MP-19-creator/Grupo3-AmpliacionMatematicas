from numpy import array, zeros, max, dot 

def  Gauss(A, b):
  N = len(b);  x = zeros(N) 
# forward elimination
  for k, _ in enumerate(A): 
    pivoting_row_swapping(A, b, k, N)
# elimination for all rows below pivot
    for i in range(k+1, N):  
      c = A[i, k] / A[k, k]  
      A[i, k:N] = A[i, k:N] - c * A[k, k:N] 
      b[i] = b[i] - c * b[k] 
# back substitution
    for i in range(N-1, -1, -1):
      x[i] = (b[i] - dot(A[i, i:N], x[i:N]))/ A[i, i]
    return x 

def pivoting_row_swapping(A, b, k, N): 
  s = zeros(N);
# s[i] largest element of row i
  for i in range(k, N):
    s[i] = max(abs(A[i, k:N])) 
      
# find row with largest pivoting element
    pivot = abs(A[k, k] / s[k])
    l = k
    for j in range(k, N): 
      if abs(A[j, k] / s[j]) > pivot: 
        pivot = abs(A[j, k] / s[j])
        l = j

# Check singular matrix
    if pivot == 0.0: print("The matrix is singular"); exit()
       
# pivoting if needed
    if l != k: 
      A[[k, l] , k:N] = A[[l, k], k:N]  
      (b[k], b[l]) = (b[l], b[k])

if __name__ == "__main__":
  import doctest
  doctest.testmod(verbose = True)