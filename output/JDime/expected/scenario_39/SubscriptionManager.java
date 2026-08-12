public class SubscriptionManager {
    
    public void setupRecurringBilling(Customer customer, Order order) {
        // Logic to setup recurring billing based on subscription type
        switch (customer.getSubscriptionType()) {
            case "PREMIUM":
                // Premium customers get priority processing
                order.setPaymentMethod("BANK_TRANSFER"); // Lower fees
                break;
            case "STANDARD":
                // Standard customers get automatic renewals
                if (order.getBillingCycle() < 3) {
                    order.setRecurring(true, 3); // Upgrade to quarterly
                }
                break;
            case "BASIC":
            default:
                // Basic customers keep current settings
                break;
        }
    }
    
    public boolean canUpgradeSubscription(Customer customer, String newType) {
        return customer.getSubscriptionMonths() >= 3 || customer.getCreditBalance() >= 100;
    }
    
    public double getSubscriptionDiscount(String subscriptionType, int months) {
        double baseDiscount = 0.05;
        
        switch (subscriptionType) {
            case "PREMIUM":
                baseDiscount = 0.20;
                break;
            case "STANDARD":
                baseDiscount = 0.12;
                break;
        }
        
        // Long-term customer bonus
        if (months > 12) {
            baseDiscount += 0.05;
        }
        
        return baseDiscount;
    }
}