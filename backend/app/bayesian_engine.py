from app.models import Customer

def update_customer_bayesian_prior(customer: Customer, paid_on_time: bool) -> Customer:
    """
    Beta-Binomial Bayesian Update:
    When a payment event resolves:
    if paid_on_time: alpha += 1
    else: beta += 1
    on_time_probability = (alpha) / (alpha + beta)
    """
    if paid_on_time:
        customer.alpha += 1
    else:
        customer.beta += 1

    total_obs = customer.alpha + customer.beta
    customer.on_time_probability = round(customer.alpha / max(1, total_obs), 3)
    
    # Adjust expected delay days dynamically
    if not paid_on_time:
        customer.average_delay_days = round(customer.average_delay_days * 1.2 + 2.0, 1)

    return customer
