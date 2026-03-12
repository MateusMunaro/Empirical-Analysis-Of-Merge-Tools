public class SubscriptionManager {
    
    public void setupRecurringBilling(Customer customer, Order order) {
        // Logic to setup recurring billing based on both subscription type and tier
        switch (customer.getSubscriptionType()) {
            case "PREMIUM":
                // Premium customers get priority processing
                order.setPaymentMethod("BANK_TRANSFER"); // Lower fees
                // Premium customers with high tier get best terms
                if ("GOLD".equals(customer.getTier())) {
                    order.setRecurring(true, 12); // Annual for best discount
                }
                break;
            case "STANDARD":
                // Standard customers get automatic renewals
                if (order.getBillingCycle() < 3) {
                    order.setRecurring(true, 3); // Upgrade to quarterly
                }
                break;
            case "BASIC":
            default:
                // Basic customers keep current settings but benefit from tier
                if ("SILVER".equals(customer.getTier()) || "GOLD".equals(customer.getTier())) {
                    order.setRecurring(true, 3); // Upgrade based on loyalty
                }
                break;
        }
    }
    
    public boolean canUpgradeSubscription(Customer customer, String newType) {
        return customer.getSubscriptionMonths() >= 3 || 
               customer.getCreditBalance() >= 100 ||
               customer.getLoyaltyPoints() >= 500; // Include loyalty points
    }
    
    public double getSubscriptionDiscount(String subscriptionType, int months, String tier) {
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
        
        // Tier bonus on subscription discount
        if ("GOLD".equals(tier)) {
            baseDiscount += 0.02; // 2% bonus for gold tier
        } else if ("SILVER".equals(tier)) {
            baseDiscount += 0.01; // 1% bonus for silver tier
        }
        
        return baseDiscount;
    }
}