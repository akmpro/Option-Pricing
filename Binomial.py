from numpy import exp, sqrt, arange


class BinomialTree:
    def __init__(
        self,
        steps: int,
        time_to_maturity: float,
        strike: float,
        current_price: float,
        volatility: float,
        interest_rate: float,
        dividend_yield: float,
        american_or_european: str,
    ):
        self.steps = steps
        self.delta_time = time_to_maturity / steps
        self.strike = strike
        self.current_price = current_price
        self.volatility = volatility
        self.interest_rate = interest_rate
        self.american_or_european = american_or_european
        self.up, self.down = self.up_down(
            volatility,
            self.delta_time,
        )
        self.risk_neutral_probability = self.risk_neutral_probability(
            interest_rate,
            dividend_yield,
            self.delta_time,
            self.up,
            self.down,
            volatility,
        )

    def up_down(
        self,
        volatility,
        delta_time,
    ):
        up = exp(volatility * sqrt(delta_time))
        down = exp(-volatility * sqrt(delta_time))

        return up, down

    def risk_neutral_probability(
        self, interest_rate, dividend_yield, delta_time, up, down, volatility
    ):
        q = (exp((interest_rate - dividend_yield) * delta_time) - down) / ((up - down))

        # if delta_time > (volatility ** 2) / (interest_rate - q) ** 2:
        #     raise Exception("Time condition not met")

        return q

    def calculate_all_nodes_for_puts(
        self,
        strike,
        current_price,
        up,
        down,
        risk_neutral_probability,
        steps,
        delta_time,
        interest_rate,
    ):
        q = risk_neutral_probability

        # S is the price
        S = {}

        # S[i, j] is defined as S[time,(step - amount of ups)]
        S[0, 0] = current_price

        for i in range(1, steps + 1):
            for j in range(0, i + 1):
                if j > 0:
                    S[i, j] = S[i - 1, j - 1] * up
                else:
                    S[i, 0] = S[i - 1, 0] * down

        # P-alive vs P-exercise
        P = {}
        exercise = {}
        for i in arange(steps, -1, -1):
            for j in range(0, i + 1):
                if i == steps:
                    P[i, j] = max(strike - S[i, j], 0)
                else:
                    P[i, j] = exp(-interest_rate * delta_time) * (
                        q * P[i + 1, j + 1] + (1 - q) * P[i + 1, j]
                    )
                P[i, j] = max(P[i, j], 0)
                if P[i, j] > (strike - S[i, j]):
                    exercise[i, j] = "no"
                else:
                    exercise[i, j] = "yes"
                if self.american_or_european == "A":
                    P[i, j] = max(P[i, j], (strike - S[i, j]))

        return S, P, exercise

    def calculate_all_nodes_for_calls(
        self,
        strike,
        current_price,
        up,
        down,
        risk_neutral_probability,
        steps,
        delta_time,
        interest_rate,
    ):
        q = risk_neutral_probability

        # S is the price
        S = {}

        # S[i, j] is defined as S[time,(step - amount of ups)]
        S[0, 0] = current_price

        for i in range(1, steps + 1):
            for j in range(0, i + 1):
                if j > 0:
                    S[i, j] = S[i - 1, j - 1] * up
                else:
                    S[i, 0] = S[i - 1, 0] * down

        # P-alive vs P-exercise
        P = {}
        exercise = {}
        for i in arange(steps, -1, -1):
            for j in range(0, i + 1):
                if i == steps:
                    P[i, j] = max(S[i, j] - strike, 0)
                else:
                    P[i, j] = exp(-interest_rate * delta_time) * (
                        q * P[i + 1, j + 1] + (1 - q) * P[i + 1, j]
                    )
                P[i, j] = max(P[i, j], 0)
                if P[i, j] > (S[i, j] - strike):
                    exercise[i, j] = "no"
                else:
                    exercise[i, j] = "yes"
                if self.american_or_european == "A":
                    P[i, j] = max(P[i, j], (S[i, j] - strike))

        return S, P, exercise

    def run(self):
        self.put_S, self.put_P, self.put_exercise = self.calculate_all_nodes_for_puts(
            self.strike,
            self.current_price,
            self.up,
            self.down,
            self.risk_neutral_probability,
            self.steps,
            self.delta_time,
            self.interest_rate,
        )
        (
            self.call_S,
            self.call_P,
            self.call_exercise,
        ) = self.calculate_all_nodes_for_calls(
            self.strike,
            self.current_price,
            self.up,
            self.down,
            self.risk_neutral_probability,
            self.steps,
            self.delta_time,
            self.interest_rate,
        )


if __name__ == "__main__":
    steps = 4
    time_to_maturity = 2
    strike = 90
    current_price = 100
    volatility = 0.2
    interest_rate = 0.05
    dividend_yield = 0.0
    american_or_european = "E"

    # Binomial Tree
    BT = BinomialTree(
        steps=steps,
        time_to_maturity=time_to_maturity,
        strike=strike,
        current_price=current_price,
        volatility=volatility,
        interest_rate=interest_rate,
        dividend_yield=dividend_yield,
        american_or_european=american_or_european,
    )
    BT.run()
    for i in BT.put_P:
        print(i, ":", BT.put_P[i])
