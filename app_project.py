import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime
import streamlit as st

class GBM():
    def __init__(self,maturity,n_scenarios,risk_free,sigma,steps_per_year,s_0):
        self.maturity = maturity
        self.n_scenarios = n_scenarios
        self.sigma = sigma
        self.steps_per_year = steps_per_year
        self.s_0 = s_0
        self.risk_free = risk_free
    
    def monte_carlo(self,z=None):
        dt = 1/self.steps_per_year
        n_steps = int(self.maturity*self.steps_per_year)
        if z is None:
            z = np.random.normal(size=(n_steps, self.n_scenarios))
        
        rets = np.exp(((self.risk_free - 0.5*self.sigma**2))*dt + self.sigma*np.sqrt(dt)*z)
        rets = pd.concat([pd.DataFrame(np.ones((1, self.n_scenarios))),pd.DataFrame((rets))],ignore_index=True)
        return self.s_0 * rets.cumprod()
    
    def european_pricing(self,strike,option_type,z=None):
        paths = self.monte_carlo(z=z)
        s_T = paths.iloc[-1]
        
        if option_type == 'call':
            payoff = np.maximum(0,s_T-strike)

        elif option_type == 'put':
            payoff = np.maximum(0,strike - s_T)
        else:
            raise ValueError('This is not a valid option type')

        return np.exp(-self.risk_free*self.maturity)*payoff.mean()
    
    def knock_out_option(self,strike,barrier,option_type,z=None):
        paths = self.monte_carlo(z=z)
        s_T = paths.iloc[-1]

        if option_type == 'PDO':
            hit = (paths <= barrier).any(axis=0)
            not_hit = ~hit
            payoff = not_hit * np.maximum(strike - s_T , 0)
        elif option_type == 'PUO':
            hit = (paths >= barrier).any(axis=0)
            not_hit = ~hit
            payoff = not_hit * np.maximum(strike - s_T , 0)
        elif option_type == 'CUO':
            hit = (paths >= barrier).any(axis=0)
            not_hit = ~hit
            payoff = not_hit * np.maximum(s_T - strike, 0)
        elif option_type == 'CDO':
            hit = (paths <= barrier).any(axis=0)
            not_hit = ~hit
            payoff = not_hit * np.maximum(s_T -strike , 0)
        else:
            raise ValueError('This is not a valid option type')
        
        return np.exp(-self.risk_free*self.maturity)*payoff.mean()
    
    def knock_in_option(self,strike,barrier,option_type,z=None):
        paths = self.monte_carlo(z=z)
        s_T = paths.iloc[-1]

        if option_type == 'PDI':
            hit = (paths <= barrier).any(axis=0)
            payoff = hit * np.maximum(strike - s_T , 0)
        elif option_type == 'PUI':
            hit = (paths >= barrier).any(axis=0)
            payoff = hit * np.maximum(strike - s_T , 0)
        elif option_type == 'CUI':
            hit = (paths >= barrier).any(axis=0)
            payoff = hit * np.maximum(s_T - strike, 0)
        elif option_type == 'CDI':
            hit = (paths <= barrier).any(axis=0)
            payoff = hit * np.maximum(s_T -strike , 0)
        else:
            raise ValueError('This is not a valid option type')
        
        return np.exp(-self.risk_free*self.maturity)*payoff.mean()
    
    def Bonus_Steps_Certificate(self,barrier1,barrier2,coupon,product_type,notional,z=None):
        paths = self.monte_carlo(z=z)
        s_T = paths.iloc[-1]
        coupon = coupon*notional
        
        if barrier1>=barrier2:
            raise ValueError('Barrier1 should be stricly lower than Barrier2')
        
        if product_type == 'American':
            itm_proba = (paths >= barrier1).any(axis=0).mean() + (paths >= barrier2).any(axis=0).mean()
            price = np.exp(-self.risk_free*self.maturity)*itm_proba*coupon
        elif product_type == 'European':
            itm_proba = (s_T >= barrier1).mean() + (s_T >= barrier2).mean()
            price = np.exp(-self.risk_free*self.maturity)*itm_proba*coupon
        else:
            raise ValueError('Not a valid product_type')
        
        return price
    
    def range_accrual(self, range_down, range_up,coupon,notional,z=None):
        
        paths = self.monte_carlo(z=z)
        coupon = coupon*notional
        in_range = ((paths >= range_down) & (paths <= range_up)).iloc[1:]
        accrual_fraction = in_range.mean()
        expected_accrual = accrual_fraction.mean()
        price = np.exp(-self.risk_free*self.maturity)*expected_accrual*coupon
        return price

        
    
    def price_product(self, product,z=None, **kwargs):
        if product == "Vanilla Option":
            return self.european_pricing(
                strike=kwargs["strike"],
                option_type=kwargs["option_type"],
                z=z
            )

        elif product == "Knock-In Option":
            return self.knock_in_option(
                strike=kwargs["strike"],
                barrier=kwargs["barrier"],
                option_type=kwargs["option_type"],
                z=z
            )

        elif product == "Knock-Out Option":
            return self.knock_out_option(
                strike=kwargs["strike"],
                barrier=kwargs["barrier"],
                option_type=kwargs["option_type"],
                z=z
            )

        elif product == "Bonus Steps Certificate":
            return self.Bonus_Steps_Certificate(
                barrier1=kwargs["barrier1"],
                barrier2=kwargs["barrier2"],
                coupon=kwargs["coupon"],
                product_type=kwargs["product_type"],
                notional=kwargs["notional"],
                z=z
            )

        elif product == "Range Accrual":
            return self.range_accrual(
                range_down=kwargs["range_down"],
                range_up=kwargs["range_up"],
                coupon=kwargs["coupon"],
                notional=kwargs["notional"],
                z=z
            )
        

        else:
            raise ValueError("Unknown product")
    
    def delta(self, product, bump=0.01, **kwargs):
        s_up = self.s_0 * (1 + bump)
        s_down = self.s_0 * (1 - bump)
        n_steps = int(self.maturity*self.steps_per_year)
        z = np.random.normal(size=(n_steps, self.n_scenarios))
        model_up = GBM(self.maturity, self.n_scenarios, self.risk_free, self.sigma, self.steps_per_year, s_up)
        model_down = GBM(self.maturity, self.n_scenarios, self.risk_free, self.sigma, self.steps_per_year, s_down)

        p_up = model_up.price_product(product,z=z, **kwargs)
        p_down = model_down.price_product(product,z=z, **kwargs)

        return (p_up - p_down) / (s_up - s_down)
    
    def gamma(self, product, bump=0.01, **kwargs):
        s_up = self.s_0 * (1 + bump)
        s_mid = self.s_0
        s_down = self.s_0 * (1 - bump)

        n_steps = int(self.maturity*self.steps_per_year)
        z = np.random.normal(size=(n_steps, self.n_scenarios))

        model_up = GBM(self.maturity, self.n_scenarios, self.risk_free, self.sigma, self.steps_per_year, s_up)
        model_mid = GBM(self.maturity, self.n_scenarios, self.risk_free, self.sigma, self.steps_per_year, s_mid)
        model_down = GBM(self.maturity, self.n_scenarios, self.risk_free, self.sigma, self.steps_per_year, s_down)

        p_up = model_up.price_product(product,z=z, **kwargs)
        p_mid = model_mid.price_product(product,z=z, **kwargs)
        p_down = model_down.price_product(product,z=z, **kwargs)

        ds = self.s_0 * bump
        return (p_up - 2 * p_mid + p_down) / (ds ** 2)


    def vega(self, product, bump=0.01, **kwargs):
        vol_up = self.sigma + bump
        vol_down = max(1e-6, self.sigma - bump)

        n_steps = int(self.maturity*self.steps_per_year)
        z = np.random.normal(size=(n_steps, self.n_scenarios))

        model_up = GBM(self.maturity, self.n_scenarios, self.risk_free, vol_up, self.steps_per_year, self.s_0)
        model_down = GBM(self.maturity, self.n_scenarios, self.risk_free, vol_down, self.steps_per_year, self.s_0)

        p_up = model_up.price_product(product,z=z, **kwargs)
        p_down = model_down.price_product(product,z=z, **kwargs)

        return (p_up - p_down) / (vol_up - vol_down)
    

    
    
