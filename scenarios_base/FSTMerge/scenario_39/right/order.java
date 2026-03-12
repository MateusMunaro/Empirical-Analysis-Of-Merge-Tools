public class Order {
    private Long orderId;
    private Long customerId;
    private double amount;
    private String status;
    private boolean isRecurring;
    private int billingCycle; // in months
    private String paymentMethod;
    
    public Order(Long orderId, Long customerId, double amount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.amount = amount;
        this.status = "PENDING";
        this.isRecurring = false;
        this.billingCycle = 1;
        this.paymentMethod = "CREDIT_CARD";
    }
    
    public Long getOrderId() { return orderId; }
    public Long getCustomerId() { return customerId; }
    public double getAmount() { return amount; }
    public String getStatus() { return status; }
    public boolean isRecurring() { return isRecurring; }
    public int getBillingCycle() { return billingCycle; }
    public String getPaymentMethod() { return paymentMethod; }
    
    public void setRecurring(boolean recurring, int cycle) {
        this.isRecurring = recurring;
        this.billingCycle = cycle;
    }
    
    public void setPaymentMethod(String method) {
        this.paymentMethod = method;
    }
    
    public void processOrder() {
        if (isRecurring) {
            this.status = "SCHEDULED";
        } else {
            this.status = "PROCESSED";
        }
    }
    
    public double calculateTotal() {
        double baseTotal = amount;
        
        // Recurring order discount
        if (isRecurring) {
            if (billingCycle >= 12) {
                baseTotal *= 0.85; // 15% discount for annual billing
            } else if (billingCycle >= 6) {
                baseTotal *= 0.90; // 10% discount for semi-annual
            } else if (billingCycle >= 3) {
                baseTotal *= 0.95; // 5% discount for quarterly
            }
        }
        
        // Payment method fees
        switch (paymentMethod) {
            case "BANK_TRANSFER":
                // No additional fee
                break;
            case "PAYPAL":
                baseTotal += baseTotal * 0.03; // 3% PayPal fee
                break;
            case "CREDIT_CARD":
            default:
                baseTotal += baseTotal * 0.025; // 2.5% credit card fee
                break;
        }
        
        // Service tax
        baseTotal += baseTotal * 0.12; // 12% service tax
        
        return baseTotal;
    }
}