import matplotlib.pyplot as plt
import numpy as np

background_color = '#dce5f2'


class Derivative:
    """
    Base class for a financial derivative.

    Attributes:
        payoff (function): Payoff function that computes the derivative's
        payoff at a given asset price S.

        maturity (float): Derivative's maturity (for European style derivatives
        this is when the payoff is realised).
    """
    def __init__(self, payoff, maturity, name=None, alpha=1):
        self.payoff = payoff
        self.maturity = maturity
        self.name = name
        self.alpha = alpha

    def __repr__(self):
        return f'Custom {self.name} (maturity = {self.maturity})'


class Call(Derivative):
    """
    Represents a European Call Option.

    A call option gives the holder the right (but not the obligation) to
    buy an asset at maturity a specified strike price.

    Attributes:
        strike (float): The strike price of the call option.
        maturity (float): Option's maturity.
    """
    def __init__(self, strike, maturity, alpha=1):
        self.strike = strike
        self.payoff = lambda S: max(S - self.strike, 0)
        self.maturity = maturity
        self.alpha = alpha

    def __repr__(self):
        return f'Call (strike = {self.strike}, maturity = {self.maturity})'


class Put(Derivative):
    """
    Represents a European Put Option.

    A put option gives the holder the right (but not the obligation) to
    sell an asset at maturity at a specified strike price.

    Attributes:
        strike (float): The strike price of the call option.
        maturity (float): Option's maturity.
    """
    def __init__(self, strike, maturity, alpha=1):
        self.strike = strike
        self.payoff = lambda S: max(self.strike - S, 0)
        self.maturity = maturity
        self.alpha = alpha

    def __repr__(self):
        return f'Put (strike = {self.strike}, maturity = {self.maturity})'


class Forward(Derivative):
    """
    Represents a Forward Contract (Lond).

    A long forward contract is an agreement to buy an asset at a specified
    price at maturity.

    Attributes:
        strike (float): The agreed-upon price of the forward contract.
        maturity (float): When forward contract is settled.
    """
    def __init__(self, strike, maturity, alpha=1):
        self.strike = strike
        self.payoff = lambda S: S - self.strike
        self.maturity = maturity
        self.alpha = alpha

    def __repr__(self):
        return f'Forward (strike = {self.strike}, maturity = {self.maturity})'


class Portfolio:
    """
    Represents a portfolio of derivatives.

    The Portfolio class allows users to manage and analyze multiple derivative
    payoffs with different maturities.

    Attributes:
        derivatives (list): List of Derivative objects held in the portfolio.

        position (list): List of long/short positions.

        maturities (list): Unique maturities of the derivatives in the
        portfolio.

        low (dict): Lower bounds of the asset price range for each maturity
        for payoff plotting.

        high (dict): Upper bounds of the asset price range for each maturity
        for payoff plotting.
    """
    def __init__(self, derivatives, position=None):
        self.derivatives = derivatives
        if position:
            self.position = position
        else:
            self.position = ['+'] * len(self.derivatives)

        self.maturities = list(set([d.maturity for d in self.derivatives]))
        self.low = {m: 0 for m in self.maturities}
        self.high = {m: 200 for m in self.maturities}

        self.range_points = 1000

    def __add__(self, other_derivatives):
        """
        Adds a list of derivatives to the portfolio in long position.

        Args:
            other_derivatives (list): A list of Derivative objects to be added.
        """
        for derivative in other_derivatives:
            self.derivatives.append(derivative)
            self.position.append('+')

            if derivative.maturity not in self.maturities:
                self.maturities.append(derivative.maturity)
                self.low[derivative.maturity] = 0
                self.high[derivative.maturity] = 200

    def __sub__(self, other_derivatives):
        """
        Adds a list of derivatives to the portfolio in short position.

        Args:
            other_derivatives (list): A list of Derivative objects to be added.
        """
        for derivative in other_derivatives:
            self.derivatives.append(derivative)
            self.position.append('-')

            if derivative.maturity not in self.maturities:
                self.maturities.append(derivative.maturity)
                self.low[derivative.maturity] = 0
                self.high[derivative.maturity] = 200

    def remove(self, index):
        """
        Removes a derivative from the portfolio by its index.

        Args:
            index (int): Index of the derivative to remove from the portfolio's
            derivative attribute.
        """
        to_remove = self.derivatives[index]
        del self.derivatives[index]
        del self.position[index]

        maturity_to_remove = to_remove.maturity
        self.maturities = list(set([d.maturity for d in self.derivatives]))
        if maturity_to_remove not in self.maturities:
            del self.low[maturity_to_remove]
            del self.high[maturity_to_remove]

        self.derivatives

    def range(self, low, high, maturity=None):
        """
        Sets the price range (low and high) for plotting the payoff of
        derivatives at a specific maturity or all maturities.

        Args:
            low (float): The lower bound of the price range.
            high (float): The upper bound of the price range.
            maturity (float, optional): The maturity for which to set the
            range. If None, sets range for all maturities.
        """
        if maturity:
            self.low[maturity] = low
            self.high[maturity] = high
        else:
            for m in self.maturities:
                self.low[m] = low
                self.high[m] = high

    def payoff(self, maturity_list=None, grid=False, suptitle=None):
        """
        Plots the payoff profile for all derivatives in the portfolio at
        specific maturities.

        Args:
            maturity_list (list, optional): A list of maturities to plot the
            payoff profiles for. If None, plots for all maturities.
        """
        if not maturity_list:
            maturity_list = self.maturities

        plt.figure(figsize=(9, int(7 * len(maturity_list))),
                   facecolor=background_color)
        if suptitle:
            plt.suptitle(f'Payoff Profiles: {suptitle}')
        else:
            plt.suptitle('Payoff Profiles')

        for idx, maturity in enumerate(maturity_list):
            m_total = np.zeros(self.range_points)
            plot_range = np.linspace(self.low[maturity],
                                     self.high[maturity], self.range_points)

            plt.subplot(len(maturity_list), 1, idx+1)
            if grid:
                plt.grid(color=background_color, alpha=0.6)
            plt.title(f'Maturity {maturity}')
            plt.xlabel(f'Underlying Asset Value at Maturity {maturity}')
            plt.ylabel('Payoff')

            mature_derivatives = []
            mature_positions = []
            for i, der in enumerate(self.derivatives):
                if der.maturity == maturity:
                    mature_derivatives.append(der)
                    mature_positions.append(self.position[i])

            for i, derivative in enumerate(mature_derivatives):
                if mature_positions[i] == '+':
                    values = np.array([derivative.payoff(v)
                                       for v in plot_range])
                else:
                    values = np.array([-derivative.payoff(v)
                                       for v in plot_range])

                m_total += values
                plt.plot(plot_range, values, label=derivative.__repr__(),
                         alpha=derivative.alpha)

            plt.plot(plot_range, m_total, lw=6, color='red', alpha=0.5,
                     label='Total Portfolio Payoff')
            plt.legend(loc=(0.7, 1.02))

        plt.tight_layout()
        plt.show()
