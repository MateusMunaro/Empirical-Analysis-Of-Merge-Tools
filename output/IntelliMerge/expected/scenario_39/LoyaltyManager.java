public class LoyaltyManager {
    
    public int calculatePointsEarned(double amount, String tier) {
        int basePoints = (int) (amount / 10); // 1 point per $10
        
        // Tier multiplier
        switch (tier) {
            case "GOLD":
                return basePoints * 3;
            case "SILVER":
                return basePoints * 2;
            case "BRONZE":
            default:
                return basePoints;
        }
    }
    
    public boolean canRedeemPoints(Customer customer, int pointsToRedeem) {
        return customer.getLoyaltyPoints() >= pointsToRedeem;
    }
    
    public double convertPointsToDiscount(int points) {
        return points * 0.01; // 1 point = $0.01
    }
    
    // Enhanced method that works with subscription system
    public void processLoyaltyBenefits(Customer customer, Order order) {
        // Grant express shipping for high-tier customers
        if ("GOLD".equals(customer.getTier()) && order.getAmount() > 200) {
            order.setExpressShipping(true);
        }
        
        // Recommend better payment methods for premium subscribers
        if ("PREMIUM".equals(customer.getSubscriptionType()) && "GOLD".equals(customer.getTier())) {
            order.setPaymentMethod("BANK_TRANSFER"); // Lower fees
        }
    }
}