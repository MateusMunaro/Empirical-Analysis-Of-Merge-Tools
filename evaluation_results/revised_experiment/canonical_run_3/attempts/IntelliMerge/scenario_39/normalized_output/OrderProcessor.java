public class OrderProcessor {

    private SubscriptionManager subscriptionManager;
    private BillingManager billingManager;
    
    private LoyaltyManager loyaltyManager;
    
    public OrderProcessor() {
        this.subscriptionManager = new SubscriptionManager();
        this.billingManager = new BillingManager();
    }
    
    public double processCustomerOrder(Customer customer, Order order) {
<<<<<<< ours
        // Apply tier-based priority
        if ("GOLD".equals(customer.getTier()) && order.getAmount() > 100) {
            order.setPriority("HIGH");
=======
        // Auto-upgrade subscription based on order volume
        if (order.getAmount() > 500 && "BASIC".equals(customer.getSubscriptionType())) {
            customer.upgradeSubscription("STANDARD");
        } else if (order.getAmount() > 1000 && "STANDARD".equals(customer.getSubscriptionType())) {
            customer.upgradeSubscription("PREMIUM");
>>>>>>> theirs
        }
            
        double discount = customer.calculateDiscount(order.getAmount());
        double total = order.calculateTotal() - discount;
            
<<<<<<< ours
        // Award loyalty points based on purchase
        int pointsEarned = loyaltyManager.calculatePointsEarned(order.getAmount(), customer.getTier());
        customer.addLoyaltyPoints(pointsEarned);
            
=======
        // Try to use customer credits first
        double creditsUsed = Math.min(customer.getCreditBalance(), total * 0.5); // Max 50% from credits
        if (creditsUsed > 0) {
            customer.useCredit(creditsUsed);
            total -= creditsUsed;
        }
            
        // Setup recurring billing if applicable
        if (order.isRecurring()) {
            subscriptionManager.setupRecurringBilling(customer, order);
        }
            
        // Process payment
        if (billingManager.processPayment(customer, total, order.getPaymentMethod())) {
            // Award credits for future use (1% cashback)
            customer.addCredit(order.getAmount() * 0.01);
            customer.addSubscriptionMonth();
>>>>>>> theirs
        order.processOrder();
        }
            
        return total;
    }
    
    public String getOrderSummary(Customer customer, Order order) {
        StringBuilder summary = new StringBuilder();
        summary.append("Order ").append(order.getOrderId())
<<<<<<< ours
               .append(" for ").append(customer.getTier()).append(" tier customer ")
               .append(customer.getName())
               .append(" - Amount: $").append(order.getAmount());
            
        if (order.isExpressShipping()) {
            summary.append(" (Express Shipping)");
        }
            
        if ("HIGH".equals(order.getPriority())) {
            summary.append(" (Priority Processing)");
=======
               .append(" for ").append(customer.getSubscriptionType()).append(" subscriber ")
               .append(customer.getName())
               .append(" - Amount: $").append(order.getAmount());
            
        if (order.isRecurring()) {
            summary.append(" (Recurring every ").append(order.getBillingCycle()).append(" months)");
        }
            
        summary.append(" - Payment: ").append(order.getPaymentMethod());
            
        if (customer.getCreditBalance() > 0) {
            summary.append(" - Credit Balance: $").append(customer.getCreditBalance());
>>>>>>> theirs
        }
            
        return summary.toString();
    }
}