#!usr/bin/env python
# author: gabriel couture
import copy
import numpy as np
import sympy as sm
import inspect
import scipy.constants as cte
import matplotlib.pyplot as plt


ERREUR_ARRONDI_C = 1e-16  # erreur d'arrondi (notée C)


class FonctionAnalytique1D:
    """
    Cette classe permet, si elle reçoit en argument une fonction de format adéquat,
    d'ajouter à cette fonction des méthodes pour la traitée (plusieurs méthodes
    d'intégraiton et de dérivation sont disponibles, que ce soit des méthodes
    numériques ou symboliques (traitements analytiques))
    La classe peut être utilisée comme un décorateur (recommandé)
    La fonction doit être analytique, et en une seule dimension
    (elle doit donc n'avoir qu'un seul argument)
    Voici un exemple d'utilisation recommandée :
    -------------------------------------------------------------
    >>> @FonctionAnalytique1D
    ... def ma_fonction(x):
    ...     y = x**2
    ...     z = x + (y + 1)**2 + y * np.log(x)
    ...     return x + y + z
    Attributs :
        fonc : function
                La fonction cible à traitée
    NOTE IMPORTANTE :
        L'alias des importation peut être important pour faire foncitonner
        la partie analytique de des fonctions. Voici ceux qui sont recommandés:
        SI ALIAS POUR LES IMPORTATIONS:
            numpy as np
            scipy.constant as cte
        L'implémentation de la classe est toujours en progression. Les fonctions
        qui dépendent d'une autre fonction implémentée par l'utilisateur ne
        supportent pas les opérations symboliques (traitement analytique).
        TODO : implémenter cette fonctionnalité
    """
    def __init__(self, fonc):
        """
        La méthode __init__ permet d'initialisé les attributs et de découvrir si
        les méthodes analytiques (symboliques) sont disponibles pour la fonction
        Paramètres
        ===========
            fonc : function
                    La fonction cible à traitée
        """
        # Attributs
        self.fonc = fonc  # objet function

        # une liste des différentes chaines de caractères qu'il nous est possible de
        # rencontrer (on veut éventuellement les changer par sm.[ ... ])
        # TODO : stratégie à changer
        self.possible_import = ['log', 'ln', 'log10', 'exp', 'pi', 'sin', 'cos', 'tan',
                               'sinh', 'cosh', 'tanh', 'asin', 'acos','atan', 'asinh',
                               'acosh', 'atanh', 'cot', 'acot', 'sec', 'asec', 'srqt',
                               'power', 'csc', 'acsc', 'sinc', 'sech', 'asech', 'csch',
                               'acsch', 'coth', 'acoth']

        self.__ana_variable = []  # liste : contient une string de la
                                  # variable ou reste vide

        self.__ana_fonction = []  # liste : contient une string de la
                                  # variable ou reste vide

        self.__ana = self.__si_analytique()  # Booleen : si la fonction peut être traitée
                                             # de façon analytique

        self.fonc_originel = True  # Booleen : permet de savoir s'il s'agit de l'objet
                                   #           originel. Certaines méthodes retourne un
                                   #           objet FonctionAnalytique1D, dans ce cas
                                   #           cet attribut est posé à False

        # fonction de la dérivée analytique, est fixée si elle est dérivable
        # à la première fois qu'on demande une dérivation
        self.fonc_deriv = None

        # fonction de l'intégrale analytique, est fixée si elle est intégrale
        # à la première fois qu'on demande une intégration
        self.fonc_inte = None

    def __si_analytique(self):
        """
        ------------------------------------------------
        Méthode qui vise à déterminer si la fonction
        peut être traité de façon analytique
        ------------------------------------------------
        Retourne
        ============
        résultat : bool
            Résultat de si la fonction peut être traitée comme
            une fonction analytique
        """
        source = inspect.getsourcelines(self.fonc)[0]  # code source

        # on retire tout les espaces blancs sur les contours
        for i in range(len(source)):
            source[i] = source[i].strip()

        # on trouve où commence la fonction def (il pourait y avoir plusieurs décorateurs)
        for i in range(len(source)):
            if source[i][:3] == 'def':
                source = source[i:]
                break

        try:
            # Détection des variables
            #--------------------------------------------------
            variable = source[0].split('(')[1]
            indice_fin_variable = 0
            for i in range(len(variable)):
                if variable[i] == ')' or variable[i] == ',':
                    indice_fin_variable = i
                    break

            if indice_fin_variable == 0:
                raise TypeError('Erreur dans la détection des variables')

            # notre variable
            variable = variable[:indice_fin_variable]

            # la variable est stocké

            self.__ana_variable.append(variable)

            # Détection de la fonction
            # --------------------------------------------------
            if len(source) == 2:
                # Pour les fonctions à deux lignes
                # manipulation de la chaine de caratere
                fonction = source[1].split('return ')[1]
                fonction = fonction.replace('np.', 'sm.')
                fonction = fonction.replace('numpy.', 'sm.')
                for i in self.possible_import:
                    string_temp = i + '('
                    if (string_temp in fonction) and not ('.'+string_temp in fonction):
                        fonction = fonction.replace(string_temp, 'sm.'+string_temp)
                self.__ana_fonction.append(fonction)
            else:
                # Pour les fonctions à plusieurs lignes
                # manipulation de la chaine de caractères
                elements_temp = []
                for i in source[:-1]:
                    if '=' in i:
                        element_temp = i.split('=')
                        if len(element_temp) == 2:
                            if not '(' in element_temp:
                                element_1 = element_temp[0].strip()
                                element_2 = element_temp[1].strip()
                                elements_temp.append([element_1, '('+element_2+')'])

                elements_temp = elements_temp[::-1]
                fonction = source[-1].split('return ')[1]
                for i in elements_temp:
                    if i[0] in fonction:
                        fonction = fonction.replace(i[0], i[1])
                fonction = fonction.replace('np.', 'sm.')
                fonction = fonction.replace('numpy.', 'sm.')
                # si la fonction a des dépendance de d'autre fonctions
                # implémentées
                elements_charges = globals().keys()
                elements_barrieres = ['+', '-', '*', '/', '%', ' ']
                elements_presents = []
                for i in elements_charges:
                    for j in elements_barrieres:
                        if j+i+'('+variable+')' in fonction:
                            print(i)
                            if type(eval(i)) == FonctionAnalytique1D:
                                fonction = fonction.replace((i+'({0})'.format(variable),
                                                            eval(i).__ana_fonction))

                # une liste des différentes chaines de caractères qu'il
                # nous est possible de
                # rencontrer (on veut éventuellement les changer par sm.[ ... ])
                for i in self.possible_import:
                    string_temp = i + '('
                    if (string_temp in fonction) and not ('.'+string_temp in fonction):
                        fonction = fonction.replace(string_temp, 'sm.'+string_temp)

                self.__ana_fonction.append(fonction)

            # on test différentes combinaisons pour voir si la fonction
            # peut être évaluée (au cas où l'utilisateur retourne des
            # choses étranges)
            vrai_ou_faux = True
            valeurs_test = [0.4, 0, 1, -1, -0.4]
            for valeur_test in valeurs_test:
                try:
                    exec("{0} = {1}".format(self.__ana_variable[0], valeur_test))
                    complex(eval(self.__ana_fonction[0]))
                    vrai_ou_faux = True
                    break
                except:
                    vrai_ou_faux = False
            return vrai_ou_faux

        except:
            return False

    def ana_information(self):
        """
        ------------------------------------------------
        Affiche l'information trouvée pour la section
        analytique de la fonction
        ------------------------------------------------
        """
        if self.__ana:
            print('Variable : ', self.__ana_variable[0])
            print('Fonction : ', self.__ana_fonction[0])
            return self.__ana_fonction[0]
        else:
            print('Variable trouvée : ', self.__ana_variable[0])
            print('Fonction trouvée : ', self.__ana_fonction[0])
            self.si_analytique()

    def si_analytique(self):
        """
        ------------------------------------------------
        Méthode faisant l'affichage de si oui ou non la
        fonction est manipulable par des méthodes
        analytiques
        ------------------------------------------------
        Retourne
        ============
        résultat : bool
                    Résultat sur si oui ou non la fonction peut
                    être traitée comme une fonction analytique
        """
        if not self.__ana:
            print('La fonction ne supporte pas les méthodes analytiques')
            print('Formatage de inadéquat de la fonction :')
            print(inspect.getsource(self.fonc))
            print('\nLa fonction doit être de la forme suivante')
            print('Ex : def ma_fonction(x):')
            print('\t  y = x**2')
            print('\t  return y + x')
            return False
        else:
            print('La fonction supporte les méthodes analytiques')
            return True

    def ana_derive(self, verbeux=False, latex=False):
        """
        ------------------------------------------------
        ------- Méthode de dérivation analytique -------
        Méthode permettant la dérivation analytique
        de la fonction
        ------------------------------------------------
        Paramètres
        ============
        verbeux : bool
            default : False
            True si l'utilisateur veut l'affichage
            d'information sur la dérivation
        latex : bool
            default : False
            True si l'utilisateur veut retourner une
            chaine de caractère en latex de l'expression
            dérivée
        Retourne
        ============
        résultat : si latex=False | FonctionAnalytique1D
                                    Nouvel objet, mais avec la fonction intégrée
                 : si latex=True  | string
                                    Résultat de la dérivée
                                    sous la forme d'une chaine de caractère latex
                 : si l'attribut  | self.__ana = False | None
                                    Retroune l'objet None
        Exemple
        ============
        >>> @FonctionAnalytique1D
        ... def ma_fonction(x):
        ...     return x**2
        TODO
        """
        # si la fonction ne supporte pas le traitement analytique
        if not self.__ana:
            self.si_analytique()
            return None
        # instance de la variable symbolique
        exec("{0} = sm.Symbol('{0}')".format(self.__ana_variable[0]))
        variable = eval('{0}'.format(self.__ana_variable[0]))

        try:
            # derivation
            expression = eval(self.__ana_fonction[0])
            resultat_derive = sm.simplify(expression.diff(variable))
            self.fonc_deriv = sm.lambdify(variable, resultat_derive)

            if verbeux:
                print("Le résultat de sa dérivée est : ")
                sm.pprint(resultat_derive)

            if latex:
                return sm.latex(resultat_derive)
            else:
                # retourne un objet FonctionAnalytique1D avec la fonction
                # dérivée comme attribut self.fonc et self.__ana_fonction
                nouveau = copy.deepcopy(self)
                nouveau.fonc = sm.lambdify(variable, resultat_derive)
                fonction_string = str(resultat_derive)
                for i in self.possible_import:
                    if i in fonction_string:
                        fonction_string = fonction_string.replace(i, 'sm.'+i)
                nouveau.__ana_fonction[0] = fonction_string
                nouveau.fonc_originel = False
                return nouveau
        except NameError:
            raise NameError('Échec de l\'opération. '
                            'Peut être que la fonction à un argument en trop '
                            '(NON SUPPORTÉ)')

    def ana_integration_non_def(self, verbeux=False, latex=False):
        """
        ------------------------------------------------
        ------- Méthode d'intégration analytique -------
        Méthode permettant l'intégration analytique non
        définie de la fonction
        ------------------------------------------------
        Paramètres
        ============
        verbeux : bool
            default : False
            True si l'utilisateur veut l'affichage
            d'information sur l'intégration
        latex : bool
            default : False
            True si l'utilisateur veut retourner une
            chaine de caractère en latex de l'expression
            intégrée
        Retourne
        ============
        résultat : si latex=False | FonctionAnalytique1D
                                    Nouvel objet, mais avec la fonction intégrée
                 : si latex=True  | string
                                    Résultat de l'intégrale non définie
                                    sous la forme d'une chaine de caractère latex
                 : si l'attribut  | self.__ana = False | None
                                    Retroune l'objet None
        Exemple
        ============
        >>> @FonctionAnalytique1D
            def ma_fonction(x):
                return x**2
        TODO
        """
        # si la fonction ne supporte pas le traitement analytique
        if not self.__ana:
            self.si_analytique()
            return None
        # instance de la variable symbolique
        exec("{0} = sm.Symbol('{0}')".format(self.__ana_variable[0]))
        variable = eval('{0}'.format(self.__ana_variable[0]))

        try:
            # integration non definie
            expression = eval(self.__ana_fonction[0])
            resultat_inte = sm.simplify(sm.integrate(expression, variable))
            self.fonc_inte = sm.lambdify(variable, resultat_inte)

            if verbeux:
                print("Le résultat de l'intégrale non définie est : ")
                sm.pprint(resultat_inte)

            if latex:
                # retourne le code sous forme de code latex
                return sm.latex(resultat_inte)
            else:
                # retourne un objet FonctionAnalytique1D avec la fonction
                # intégrée comme attribut self.fonc et self.__ana_fonction
                nouveau = copy.deepcopy(self)
                nouveau.fonc = sm.lambdify(variable, resultat_inte)
                fonction_string = str(resultat_inte)
                for i in self.possible_import:
                    if i in fonction_string:
                        fonction_string = fonction_string.replace(i, 'sm.'+i)
                nouveau.__ana_fonction[0] = fonction_string
                nouveau.fonc_originel = False
                return nouveau

        except NameError:
            raise NameError('Échec de l\'opération. '
                            'Peut être que la fonction à un argument en trop '
                            '(NON SUPPORTÉ)')

    def ana_derive_a(self, a, verbeux=False):
        """
        ------------------------------------------------
        ------- Méthode de dérivation analytique -------
        Méthode permettant la dérivation analytique
        de la fonction. La fonction dérivé est ensuite
        évaluée à a
        ------------------------------------------------
        Paramètres
        ============
        a : float
            Valeur à laquelle la fonction dérivée est
            évaluée
        verbeux : bool
            default : False
            True si l'utilisateur veut l'affichage
            d'informations concernant l'opération
        Retourne
        ============
        résultat : complex ou float
            Résultat de la fonction dérivée évaluée à a
        Exemple
        ============
        >>> @FonctionAnalytique1D
            def ma_fonction(x):
                return x**2
        TODO
        """
        # si la fonction ne supporte pas le traitement analytique
        if not self.__ana:
            self.si_analytique()
            return None

        elif self.fonc_deriv is not None and not verbeux:
            return self.fonc_deriv(a)

        try:
            # instance de la variable symbolique
            exec("{0} = sm.Symbol('{0}')".format(self.__ana_variable[0]))
            variable = eval('{0}'.format(self.__ana_variable[0]))

            # derivation
            expression = eval(self.__ana_fonction[0])
            resultat_derive = sm.simplify(expression.diff(variable))
            self.fonc_deriv = sm.lambdify(variable, resultat_derive)

            if verbeux:
                print('La fonction est la suivante :')
                sm.pprint(self.__ana_fonction[0])
                print("\nLe résultat de la dérivée non évaluée est : ")
                sm.pprint(resultat_derive)

            # résultat de la dérivée définie
            resultat_derive_evaluee = resultat_derive.subs(variable, a)

            # affichage d'étape de calcul
            if verbeux:
                print("\nLe résultat de la dérivée évaluée est : ")
                sm.pprint(resultat_derive_evaluee)

            # si le résultat est un complex, retourne un complex
            # sinon retourne un float
            try:
                resultat = complex(resultat_derive_evaluee.evalf())
                assert resultat.imag
                return resultat
            except:
                return float(resultat_derive_evaluee.evalf())
        except NameError:
            raise NameError('Échec de l\'opération. '
                            'Peut être que la fonction à un argument en trop '
                            '(NON SUPPORTÉ)')


    def ana_integration_def(self, a, b, verbeux=False):
        """
        ------------------------------------------------
        ------- Méthode d'intégration analytique -------
        Méthode permettant l'intégration analytique
        définie de la fonction entre les bornes a et b
        ------------------------------------------------
        Paramètres
        ============
        a : float
            Borne inférieure de l'intégrale
        b : float
            Borne supérieure de l'intégrale
        verbeux : bool
            default : False
            True si l'utilisateur veut l'affichage
            d'information sur l'intégration
        Retourne
        ============
        résultat : complex ou float
            Résultat de l'intégrale définie entre a et b
        Exemple TODO
        ============
        >>> @FonctionAnalytique1D
            def ma_fonction(x):
                return x**2
        >>> ma_fonction.ana_integration_def()
        TODO
        """
        # si la fonction ne supporte pas le traitement analytique
        if not self.__ana:
            self.si_analytique()
            return None

        elif self.fonc_inte is not None and not verbeux:
            return self.fonc_inte(b) - self.fonc_inte(a)

        try:
            # instance de la variable symbolique
            exec("{0} = sm.Symbol('{0}')".format(self.__ana_variable[0]))
            variable = eval('{0}'.format(self.__ana_variable[0]))

            # integration non definie
            expression = eval(self.__ana_fonction[0])
            resultat_inte = sm.simplify(sm.integrate(expression, variable))
            self.fonc_inte = sm.lambdify(variable, resultat_inte)

            if verbeux:
                print('La fonction est la suivante :')
                sm.pprint(self.__ana_fonction[0])
                print("\nLe résultat de l'intégrale non définie est : ")
                sm.pprint(resultat_inte)

            # résultat de l'intégrale définie
            borne_inf_inte_definie = resultat_inte.subs(variable, a)
            borne_sup_inte_definie = resultat_inte.subs(variable, b)
            resultat_integrale_definie = borne_sup_inte_definie - borne_inf_inte_definie

            # affichage d'étape de calcul
            if verbeux:
                print("\nLe résultat de l'intégrale définie est : ")
                sm.pprint(resultat_integrale_definie)

            # si le résultat est un complex, retourne un complex
            # sinon retourne un float
            resultat = complex(resultat_integrale_definie.evalf())
            if resultat.imag == 0.0:
                return float(resultat_integrale_definie.evalf())
            return resultat
        except NameError:
            raise NameError('Échec de l\'opération. '
                            'Peut être que la fonction à un argument en trop '
                            '(NON SUPPORTÉ)')

    def trapeze(self, a, b, N=100):
        """
        ------------------------------------------------
        ------- Méthode d'intégration numérique --------
        Méthode permettant l'intégration d'une fonction
        avec la méthode du trapèze
        ------------------------------------------------
        Paramètres
        ============
        a : float
            Borne inférieure du domaine à intégrer
        b : float
            Borne supérieure du domaine à intégrer
        N : int
            default : 100
            Nombre de trapèzes utilisé pour l'intégration
        Retourne
        ============
        résultat : float
            Résultat de l'intégrale par la méthode du trapèze
        Exemple
        ============
        >>> @FonctionAnalytique1D
        >>> def ma_fonction(x):
                return x**2
        >>> ma_fonction.trapeze(a=1.24, b=2, N=1000)
        2.031125406495998
        """
        # Paramètres
        N = int(N)
        h = (b - a) / N  # largeur de chaque division
        resultat_sum = 0  # variable sur laquelle toute les aires sont additionnées

        # Sommation
        for i in range(1, N+1):
            resultat_sum += self.fonc(a + h * (i-1)) + self.fonc(a + h * i)

        return h / 2 * resultat_sum

    def simpson(self, a, b, N=100):
        """
        ------------------------------------------------
        ------- Méthode d'intégration numérique --------
        Méthode permettant l'intégration d'une fonction
        avec la méthode de Simpson
        ------------------------------------------------
        Paramètres
        ============
        a : float
            Borne inférieure du domaine à intégrer
        b : float
            Borne supérieure du domaine à intégrer
        N : int
            default : 100
            Nombre de sous-divisions utilisé pour l'intégration
        Retourne
        ============
        résultat : float
            Résultat de l'intégrale par la méthode de Simpson
        Exemple
        =============
        >>> import numpy as np
        >>> @FonctionAnalytique1D
        >>> def funcgaus(x):
                return np.e**(-x**2))  #fonction gausienne
        >>> funcgauss.simpson(-1000, 1000, 10000)
        1.7724538509055208
        ----------------------------------------------
        La réponse exacte étant racine de pi soit 1.77245385091 arrondie.
        """
        # Paramètres
        N = int(N)
        h = (b - a) / N  # Largeur des subdivisions
        somme_paire = 0  # Sommation paire
        somme_impaire = 0  # Sommation impaire

        # Sommation paire
        for i in range(2, N, 2):
            somme_paire += self.fonc(a + i*h)

        # Sommation impaire
        for i in range(1, N, 2):
            somme_impaire += self.fonc(a + i*h)

        return (h / 3) * (self.fonc(a) + 2 * somme_paire +\
                4 * somme_impaire + self.fonc(b))

    def romberg_naive(self, a, b, n, m):
        """
        ------------------------------------------------
        ------- Méthode d'intégration numérique --------
        Fonction de l'implémentation naive de la méthode
        d'intégration de Romberg
        ATTENTION : Méthode récursive, ell peut utiliser
                    une grande quantté de mémoire vive
        ------------------------------------------------
        Paramètres
        ============
        fonc : function
            Fonction à intégrer
        a : float
            Borne inférieure du domaine à intégrer
        b : float
            Borne supérieure du domaine à intégrer
        Retourne
        ============
        résultat : float
            Résultat de l'intégrale définie par la borne a et b
        """
        # Paramètres
        h = (b - a) / 2**n  # largeur des subdivisions

        if n == 0 and m == 0:
            return h * (self.fonc(a) + self.fonc(b))
        elif m == 0:
            res_somme = 0
            for i in range(1, 2**(n-1) + 1):
                res_somme += self.fonc(a + h * (2*i - 1))
            return 1/2 * self.romberg_naive(a, b, n - 1, 0) + h * res_somme
        else:
            element_recursif_1 = 4**m * self.romberg_naive(a, b, n, m-1)
            element_recursif_2 = self.romberg_naive(a, b, n-1, m-1)
            return (element_recursif_1 - element_recursif_2) / (4**m - 1)

    @staticmethod
    def gaussxw(N):
        """
        ######################################################################
        #
        # Functions to calculate integration points and weights for Gaussian
        # quadrature
        #
        # x,w = gaussxw(N) returns integration points x and integration
        #           weights w such that sum_i w[i]*f(x[i]) is the Nth-order
        #           Gaussian approximation to the integral int_{-1}^1 f(x) dx
        # x,w = gaussxwab(N,a,b) returns integration points and weights
        #           mapped to the interval [a,b], so that sum_i w[i]*f(x[i])
        #           is the Nth-order Gaussian approximation to the integral
        #           int_a^b f(x) dx
        #
        # This code finds the zeros of the nth Legendre polynomial using
        # Newton's method, starting from the approximation given in Abramowitz
        # and Stegun 22.16.6.  The Legendre polynomial itself is evaluated
        # using the recurrence relation given in Abramowitz and Stegun
        # 22.7.10.  The function has been checked against other sources for
        # values of N up to 1000.  It is compatible with version 2 and version
        # 3 of Python.
        #
        # Written by Mark Newman <mejn@umich.edu>, June 4, 2011
        # modified by Gabriel Couture
        # You may use, share, or modify this file freely
        #
        ######################################################################
        """
        # Initial approximation to roots of the Legendre polynomial
        a = np.linspace(3, 4*N-1, N) / (4 * N+2)
        x = np.cos(np.pi*a + 1/(8 * N * N * np.tan(a)))

        # Find roots using Newton's method
        epsilon = 1e-15
        delta = 1.0
        while delta > epsilon:
            p0 = np.ones(N, float)
            p1 = np.copy(x)
            for k in range(1, N):
                p0, p1 = p1, ((2*k + 1)*x*p1 - k*p0)/(k + 1)

            dp = (N+1)*(p0-x*p1)/(1-x*x)
            dx = p1/dp
            x -= dx
            delta = max(abs(dx))

        # Calculate the weights
        w = 2*(N+1)*(N+1)/(N*N*(1-x*x)*dp*dp)

        return x, w

    @staticmethod
    def gaussxwab(a, b, N):
        """
        ######################################################################
        #
        # Functions to calculate integration points and weights for Gaussian
        # quadrature
        #
        # x,w = gaussxw(N) returns integration points x and integration
        #           weights w such that sum_i w[i]*f(x[i]) is the Nth-order
        #           Gaussian approximation to the integral int_{-1}^1 f(x) dx
        # x,w = gaussxwab(a,b,N) returns integration points and weights
        #           mapped to the interval [a,b], so that sum_i w[i]*f(x[i])
        #           is the Nth-order Gaussian approximation to the integral
        #           int_a^b f(x) dx
        #
        # This code finds the zeros of the nth Legendre polynomial using
        # Newton's method, starting from the approximation given in Abramowitz
        # and Stegun 22.16.6.  The Legendre polynomial itself is evaluated
        # using the recurrence relation given in Abramowitz and Stegun
        # 22.7.10.  The function has been checked against other sources for
        # values of N up to 1000.  It is compatible with version 2 and version
        # 3 of Python.
        #
        # Written by Mark Newman <mejn@umich.edu>, June 4, 2011
        # modified by Gabriel Couture
        # You may use, share, or modify this file freely
        #
        ######################################################################
        """
        x, w = FonctionAnalytique1D.gaussxw(N)
        return 0.5*(b-a)*x + 0.5*(b+a), 0.5*(b-a)*w

    def quad(self, a, b, N):
        """
        ------------------------------------------------
        ------- Méthode d'intégrarion numérique  -------
        Méthode utilisant l'implémentation de Newman
        (voir gaussxwab) qui retourne le résultat de
        l'intégrale
        ------------------------------------------------
        Paramètres
        ============
        a : float
            Valeur de la borne inférieure de l'intégration
        b : float
            Valeur de la borne supérieure de l'intégration
        N: int
            Nombre de séparation effectué pour l'intégration
        Retourne
        ============
        résultat : float
                    Retourne la valeur numérique de l'intégrale borné
                    entre a et b
        """
        x, w = FonctionAnalytique1D.gaussxwab(a, b, N)
        return sum([w_i * self.fonc(x_i) for x_i, w_i in zip(x, w)])

    def derivee(self, a):
        """
        ------------------------------------------------
        ------- Méthode de dérivation numérique  -------
        Méthode permettant la dérivation numérique
        de la fonction
        ------------------------------------------------
        Paramètres
        ============
        a : float
            Valeur à laquelle la dérivée est évaluée
        Retourne
        ============
        résultat : float
                    Retourne la valeur numérique de la dérivée évalué en a
        """
        # Paramètres
        # -----------------------------------------------
        h = ERREUR_ARRONDI_C**(1/3)  # valeur approximative de h (le pas pour
                                     # dérivée) qui minimise l'erreur fait
                                     # sur la dérivée

        return (self.fonc(a + h/2) - self.fonc(a - h/2))/h

    def integrate(self, a, b, ana=False):
        """
        TODO
        """
        # TODO

        if self.fonc_inte is not None:
            return self.fonc_inte(b) - self.fonc_inte(a)


        print('Pas encore implémenté')
        return None

    def __call__(self, *args):
        if len(args) == 0:
            return self.fonc()

        elif len(args) > 1:
            print('Attention, la fonction contient trop'
                    'd\'arguments pour être une fonction analytique en 1D')
            string_a_exec = "self.fonc("
            for i in range(len(args)-1):
                string_a_exec += str(args[i]) + ','

            return eval(string_a_exec + str(args[-1]) + ')')
        else:
            return self.fonc(args[0])

    def __eq__(self, autre_fonction):
        return self.fonc == autre_fonction

    def __name__(self):
        return self.fonc.__name__


