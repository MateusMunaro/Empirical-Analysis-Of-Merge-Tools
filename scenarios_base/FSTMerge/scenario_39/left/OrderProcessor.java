public class OrderProcessor {
    private LoyaltyManager loyaltyManager;
    
    public OrderProcessor() {
        this.loyaltyManager = new LoyaltyManager();
    }
    
    public double processCustomerOrder(Customer customer, Order order) {
        // Apply tier-based priority
        if ("GOLD".equals(customer.getTier()) && order.getAmount() > 100) {
            order.setPriority("HIGH");
        }
        
        double discount = customer.calculateDiscount(order.getAmount());
        double total = order.calculateTotal() - discount;
        
        // Award loyalty points based on purchase
        int pointsEarned = loyaltyManager.calculatePointsEarned(order.getAmount(), customer.getTier());
        customer.addLoyaltyPoints(pointsEarned);
        
        order.processOrder();
        return total;
    }
    
    public String getOrderSummary(Customer customer, Order order) {
        StringBuilder summary = new StringBuilder();
        summary.append("Order ").append(order.getOrderId())
               .append(" for ").append(customer.getTier()).append(" tier customer ")
               .append(customer.getName())
               .append(" - Amount: $").append(order.getAmount());
        
        if (order.isExpressShipping()) {
            summary.append(" (Express Shipping)");
        }
        
        if ("HIGH".equals(order.getPriority())) {
            summary.append(" (Priority Processing)");
        }
        
        return summary.toString();
    }
}