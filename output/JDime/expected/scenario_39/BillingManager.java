public class BillingManager {
    
    public boolean processPayment(Customer customer, double amount, String paymentMethod) {
        // Simulate payment processing logic with enhanced customer tier consideration
        if (amount <= 0) {
            return false;
        }
        
        switch (paymentMethod) {
            case "BANK_TRANSFER":
                return processBankTransfer(customer, amount);
            case "PAYPAL":
                return processPayPal(customer, amount);
            case "CREDIT_CARD":
            default:
                return processCreditCard(customer, amount);
        }
    }
    
    private boolean processBankTransfer(Customer customer, double amount) {
        // Bank transfers are more reliable for premium customers and high-tier customers
        if ("PREMIUM".equals(customer.getSubscriptionType()) || "GOLD".equals(customer.getTier())) {
            return true; // Always approve for premium/gold
        }
        return amount <= 1000; // Limit for other customers
    }
    
    private boolean processPayPal(Customer customer, double amount) {
        // PayPal has enhanced limits for loyal customers
        double limit = 2500;
        if ("SILVER".equals(customer.getTier()) || "GOLD".equals(customer.getTier())) {
            limit = 5000; // Higher limit for tier customers
        }
        return amount <= limit;
    }
    
    private boolean processCreditCard(Customer customer, double amount) {
        // Credit card processing with combined subscription and tier limits
        double limit = getCustomerCreditLimit(customer);
        return amount <= limit;
    }
    
    private double getCustomerCreditLimit(Customer customer) {
        double baseLimit;
        
        // Base limit from subscription
        switch (customer.getSubscriptionType()) {
            case "PREMIUM":
                baseLimit = 5000.0;
                break;
            case "STANDARD":
                baseLimit = 2000.0;
                break;
            case "BASIC":
            default:
                baseLimit = 500.0;
                break;
        }
        
        // Tier bonus on credit limit
        switch (customer.getTier()) {
            case "GOLD":
                baseLimit *= 2.0; // Double limit for gold
                break;
            case "SILVER":
                baseLimit *= 1.5; // 50% bonus for silver
                break;
            case "BRONZE":
            default:
                // No bonus for bronze
                break;
        }
        
        return baseLimit;
    }
    
    public double calculateProcessingFee(double amount, String paymentMethod, String tier) {
        double baseFee;
        
        switch (paymentMethod) {
            case "BANK_TRANSFER":
                baseFee = 0; // No fee
                break;
            case "PAYPAL":
                baseFee = amount * 0.03; // 3%
                break;
            case "CREDIT_CARD":
            default:
                baseFee = amount * 0.025; // 2.5%
                break;
        }
        
        // Tier discount on processing fees
        if ("GOLD".equals(tier)) {
            baseFee *= 0.5; // 50% discount for gold tier
        } else if ("SILVER".equals(tier)) {
            baseFee *= 0.75; // 25% discount for silver tier
        }
        
        return baseFee;
    }
}