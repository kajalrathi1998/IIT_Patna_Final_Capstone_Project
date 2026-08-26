from src.config import config

class CostTracker:
    """
    Tracks token usage and estimates the cost of OpenAI API calls
    """

    def __init__(self):

        self.input_cost = config.COST["input_cost"]
        self.output_cost = config.COST["output_cost"]
        self.currency = config.COST["currency"]
        self.cost_tracking_enabled = config.COST["enabled"]

        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def calculate_cost(self, input_tokens:int, output_tokens:int):

        current_input_cost = (input_tokens / 1_000_000) * self.input_cost
        current_output_cost = (output_tokens / 1_000_000) * self.output_cost

        current_request_cost = current_input_cost + current_output_cost

        self.total_requests += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += current_request_cost

        return{
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "current_input_cost": round(current_input_cost, 6),
            "current_output_cost": round(current_output_cost, 6),
            "current_total_cost": round(current_request_cost, 6),
            "currency": self.currency,
        }

    def summary(self):
        """
        Returns cumulative API usage statistics.
        """

        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": round(self.total_cost, 6),
            "currency": self.currency,
        }

cost_tracker = CostTracker()