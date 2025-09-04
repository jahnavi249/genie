class TokenCostCalculator:
    """
    Calculate token cost in EUR based on accurate input/output pricing.
    """
    
    MODEL_PRICING = {
        "gpt-4o": {"input": 0.0025, "output": 0.0050},    # per 1K tokens
        "o3_mini": {"input": 0.00015, "output": 0.0006},
    }

    USD_TO_EUR_RATE = 0.94
    EUR_TO_INR_RATE = 88.3
    EUR_TO_USD_RATE = 1 / USD_TO_EUR_RATE

    def __init__(self, model_name):
        self.model_name = model_name
        self.pricing = self.MODEL_PRICING.get(model_name, {"input": 0.0, "output": 0.0})

    def calculate_cost(self, prompt_tokens, completion_tokens):
        cost_input = (prompt_tokens / 1000) * self.pricing["input"]
        cost_output = (completion_tokens / 1000) * self.pricing["output"]
        total_cost_usd = cost_input + cost_output
        total_cost_eur = total_cost_usd * self.USD_TO_EUR_RATE
        return round(total_cost_eur, 4)

    @staticmethod
    def convert_cost(cost_in_eur, currency="USD"):
        cost_in_eur = float(cost_in_eur)
        if currency == "USD":
            return round(cost_in_eur * TokenCostCalculator.EUR_TO_USD_RATE, 4)
        elif currency == "INR":
            return round(cost_in_eur * TokenCostCalculator.EUR_TO_INR_RATE, 2)
        elif currency == "EUR":
            return round(cost_in_eur, 4)
        else:
            raise ValueError(f"Unsupported currency: {currency}")


# # Example usage
# def main():
#     """
#     Main function to demonstrate the usage of the TokenCostCalculator class.
#     """
#     print("Testing TokenCostCalculator...")

#     # Define test cases
#     test_cases = [
#         {"model_name": "gpt-4o", "prompt_tokens": 1500, "completion_tokens": 500, "currency": "USD"},
#         {"model_name": "o1", "prompt_tokens": 1000, "completion_tokens": 2000, "currency": "EUR"},
#         {"model_name": "o3_mini", "prompt_tokens": 500, "completion_tokens": 500, "currency": "INR"},
#         {"model_name": "o3_mini", "prompt_tokens": 1000, "completion_tokens": 1000, "currency": "USD"},
#     ]

#     # Process each test case
#     for case in test_cases:
#         calculator = TokenCostCalculator(case["model_name"])
#         cost_in_eur = TokenCostCalculator.calculate_cost(
#             case["prompt_tokens"], case["completion_tokens"], calculator.cost_per_1000_tokens
#         )
#         converted_cost = calculator.convert_cost(cost_in_eur, case["currency"])
#         print(
#             f"Model: {case['model_name']}, Prompt Tokens: {case['prompt_tokens']}, "
#             f"Completion Tokens: {case['completion_tokens']}, Currency: {case['currency']}, "
#             f"Cost: {converted_cost} {case['currency']}"
#         )


# if __name__ == "__main__":
#     main()