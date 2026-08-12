public class Order {
    private Long orderId;
    private Long customerId;
    private double amount;
    private String status;
    private String priority;
    private boolean expressShipping;
    
    public Order(Long orderId, Long customerId, double amount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.amount = amount;
        this.status = "PENDING";
        this.priority = "NORMAL";
        this.expressShipping = false;
    }
    
    public Long getOrderId() { return orderId; }
    public Long getCustomerId() { return customerId; }
    public double getAmount() { return amount; }
    public String getStatus() { return status; }
    public String getPriority() { return priority; }
    public boolean isExpressShipping() { return expressShipping; }
    
    public void setPriority(String priority) {
        this.priority = priority;
    }
    
    public void setExpressShipping(boolean express) {
        this.expressShipping = express;
    }
    
    public void processOrder() {
        if ("HIGH".equals(priority)) {
            this.status = "FAST_TRACKED";
        } else {
            this.status = "PROCESSED";
        }
    }
    
    public double calculateTotal() {
        double baseTotal = amount;
        
        // Priority processing fee
        if ("HIGH".equals(priority)) {
            baseTotal += amount * 0.05; // 5% priority fee
        }
        
        // Express shipping fee
        if (expressShipping) {
            baseTotal += 15.0; // $15 express fee
        }
        
        // Standard tax
        baseTotal += baseTotal * 0.08; // 8% tax
        
        return baseTotal;
    }
}