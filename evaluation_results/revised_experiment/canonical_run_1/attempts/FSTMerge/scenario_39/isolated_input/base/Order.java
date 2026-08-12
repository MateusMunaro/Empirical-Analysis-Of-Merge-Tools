public class Order {
    private Long orderId;
    private Long customerId;
    private double amount;
    private String status;
    
    public Order(Long orderId, Long customerId, double amount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.amount = amount;
        this.status = "PENDING";
    }
    
    public Long getOrderId() { return orderId; }
    public Long getCustomerId() { return customerId; }
    public double getAmount() { return amount; }
    public String getStatus() { return status; }
    
    public void processOrder() {
        this.status = "PROCESSED";
    }
    
    public double calculateTotal() {
        return amount + (amount * 0.1); // 10% tax
    }
}