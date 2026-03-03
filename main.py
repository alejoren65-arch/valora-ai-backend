from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

app = FastAPI()

class InputData(BaseModel):
    fcf: float
    growth: float
    beta: float
    debt: float

def monte_carlo(fcf, growth, wacc, sims=5000):
    results = []
    for _ in range(sims):
        g = np.random.normal(growth, 0.02)
        r = np.random.normal(wacc, 0.01)
        flujo = fcf
        pv = 0
        for i in range(1,11):
            flujo *= (1+g)
            pv += flujo/((1+r)**i)
        results.append(pv)
    return np.mean(results), np.std(results)

@app.get("/")
def root():
    return {"status":"Backend running"}

@app.post("/analyze")
def analyze(data: InputData):

    rf = 0.04
    mrp = 0.06
    cost_equity = rf + data.beta * mrp
    wacc = cost_equity

    flujo = data.fcf
    pv = 0

    for i in range(1,11):
        flujo *= (1+data.growth)
        pv += flujo/((1+wacc)**i)

    terminal = (flujo*1.02)/(wacc-0.02)
    pv += terminal/((1+wacc)**10)

    enterprise_value = pv
    equity_value = enterprise_value - data.debt

    mc_mean, mc_std = monte_carlo(data.fcf, data.growth, wacc)

    risk = "High" if data.beta>1.3 else "Moderate" if data.beta>1 else "Low"

    return {
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "montecarlo_mean": mc_mean,
        "montecarlo_std": mc_std,
        "risk": risk
    }
