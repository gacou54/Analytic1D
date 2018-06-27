from analytic1d import FonctionAnalytique1D


##################################################
# NOTE : alias for numpy and scipy.constant are important
#        Shoud be:
#           numpy           -> np
#           scipy.constant  -> cte
##################################################
import numpy as np


# Create a 1 dimensional function with the decorator above
# ----------------------------------------------------------

@FonctionAnalytique1D
def a_function(x):
    y = x ** 2
    z = x + (y + 1) ** 2 + y * np.log(x)
    return x + y + z


# Now you can manipulate the function
# ----------------------------------------------------------

# NUMERIC SECTION
print("\nNumeric section")
print("----------------")

# trapeze method
# ---------------
result = a_function.trapeze(1, 2, N=100)

print("Trapeze method: Result is ", round(result, 2))

# simpson method
# ---------------
result = a_function.simpson(1, 2, N=100)

print("Simpson method: Result is ", round(result, 2))

# gaussian quadrative method
# ---------------
result = a_function.quad(1, 2, N=100)

print("Gaussian quadratic method: Result is ", round(result, 2))


# SYMBOLIC SECTION
print("\nSymbolic section")
print("----------------")

# We can ask if the function can be treated as an symbolic expression
# If supported, this method should show the variable and the symbolic function
print("\n\nIntegration")
a_function.ana_information()

# if supported, then you can to a non-definite integral (I put verbeux (verbose)
# to see something for the example)
print("\n\nSymbolic integration\n")
a_function.ana_integration_non_def(verbeux=True)

# Note that the last method returns a FonctionalAnalytique1D object. So you can
# applied the analytique method as long as you want :)
print("\n\nnDouble symbolic integration\n")
a_function.ana_integration_non_def(verbeux=False).ana_integration_non_def(verbeux=True)

# You can also do that with define integral
result = a_function.ana_integration_def(a=1, b=2, verbeux=True)
print("Integrate 1 to 2, but with symbolic resolution: Result is ", round(result, 2))


# Finaly it is possible to derive
print("\n\nDerivative")
a_function.ana_derive(verbeux=True)

# derive at
result = a_function.ana_derive_a(a=2, verbeux=True)
print("Derive at 2, but symbolic resolution: Result is ", round(result, 2))


