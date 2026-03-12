public class BillingManager {
    
    public boolean processPayment(Customer customer, double amount, String paymentMethod) {
        // Simulate payment processing logic
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
        // Bank transfers are more reliable for premium customers
        if ("PREMIUM".equals(customer.getSubscriptionType())) {
            return true; // Always approve for premium
        }
        return amount <= 1000; // Limit for other customers
    }
    
    private boolean processPayPal(Customer customer, double amount) {
        // PayPal has standard limits
        return amount <= 2500;
    }
    
    private boolean processCreditCard(Customer customer, double amount) {
        // Credit card processing with subscription-based limits
        double limit = getCustomerCreditLimit(customer);
        return amount <= limit;
    }
    
    private double getCustomerCreditLimit(Customer customer) {
        switch (customer.getSubscriptionType()) {
            case "PREMIUM":
                return 5000.0;
            case "STANDARD":
                return 2000.0;
            case "BASIC":
            default:
                return 500.0;
        }
    }
    
    public double calculateProcessingFee(double amount, String paymentMethod) {
        switch (paymentMethod) {
            case "BANK_TRANSFER":
                return 0; // No fee
            case "PAYPAL":
                return amount * 0.03; // 3%
            case "CREDIT_CARD":
            default:
                return amount * 0.025; // 2.5%
        }
    }
}