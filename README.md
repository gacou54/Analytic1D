# Analytic1D

This module aims to facilitate derivatives and integrations, both analytic and numeric, for one dimension system. It should be used as a python decorator. I implemented few numeric methods and I tried to nicely wrap derivate/integrate symbolic capabilities of Sympy. For examples, look at examples.py.


Example


    >>> @FonctionAnalytique1D
    ... def a_function(x):
    ...     y = x**2
    ...     z = x + (y + 1)**2 + y * np.log(x)
    ...     return x + y + z


Numeric example


    >>> a_function.trapeze(a=1, b=2, N=1000)
    18.270617851431115


Symbolic example


    >>> a_function.ana_integration_def(a=1, b=2, verbeux=True)
    La fonction est la suivante :
    x + (x ** 2) + (x + ((x ** 2) + 1) ** 2 + (x ** 2) * sm.log(x))

    Le résultat de l'intégrale non définie est :
      ⎛ 4    2             2        ⎞
      ⎜x    x ⋅log(x)   8⋅x         ⎟
    x⋅⎜── + ───────── + ──── + x + 1⎟
      ⎝5        3        9          ⎠

    Le résultat de l'intégrale définie est :
    8⋅log(2)   739
    ──────── + ───
       3        45
    18.27061470371541

    >>> a_function.ana_integration_def(a=1, b=2)
    18.27061470371541


Supported integration methods are: trapeze, Simpson, Gaussian quadratic. The others are not implemented yet. You might want to see scipy methods, they should be better than mines. The cool thing about this module is the symbolic part. It relies on Sympy (symbolic operations are made with the Sympy module).

NOTE: I do not maintain this project, it was part of a school homework and I do not have the time to work on it.


TODO If you have spare time you could:

    - Rewrite all comments in english.
    - Finish few parts (some methods are not implemented. They should be mark with a TODO note).
    - Add functionalities


