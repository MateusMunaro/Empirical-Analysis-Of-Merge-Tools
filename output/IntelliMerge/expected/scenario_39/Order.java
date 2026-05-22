public class Order {
    private Long orderId;
    private Long customerId;
    private double amount;
    private String status;
    
    // Combined features from both systems
    private String priority; // From loyalty system
    private boolean expressShipping; // From loyalty system
    private boolean isRecurring; // From subscription system
    private int billingCycle; // From subscription system
    private String paymentMethod; // From subscription system
    
    public Order(Long orderId, Long customerId, double amount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.amount = amount;
        this.status = "PENDING";
        this.priority = "NORMAL";
        this.expressShipping = false;
        this.isRecurring = false;
        this.billingCycle = 1;
        this.paymentMethod = "CREDIT_CARD";
    }
    
    public Long getOrderId() { return orderId; }
    public Long getCustomerId() { return customerId; }
    public double getAmount() { return amount; }
    public String getStatus() { return status; }
    public String getPriority() { return priority; }
    public boolean isExpressShipping() { return expressShipping; }
    public boolean isRecurring() { return isRecurring; }
    public int getBillingCycle() { return billingCycle; }
    public String getPaymentMethod() { return paymentMethod; }
    
    public void setPriority(String priority) {
        this.priority = priority;
    }
    
    public void setExpressShipping(boolean express) {
        this.expressShipping = express;
    }
    
    public void setRecurring(boolean recurring, int cycle) {
        this.isRecurring = recurring;
        this.billingCycle = cycle;
    }
    
    public void setPaymentMethod(String method) {
        this.paymentMethod = method;
    }
    
    public void processOrder() {
        if ("HIGH".equals(priority) && isRecurring) {
            this.status = "FAST_TRACKED_SCHEDULED";
        } else if ("HIGH".equals(priority)) {
            this.status = "FAST_TRACKED";
        } else if (isRecurring) {
            this.status = "SCHEDULED";
        } else {
            this.status = "PROCESSED";
        }
    }
    
    public double calculateTotal() {
        double baseTotal = amount;
        
        // Apply recurring discounts first (from subscription system)
        if (isRecurring) {
            if (billingCycle >= 12) {
                baseTotal *= 0.85; // 15% discount for annual billing
            } else if (billingCycle >= 6) {
                baseTotal *= 0.90; // 10% discount for semi-annual
            } else if (billingCycle >= 3) {
                baseTotal *= 0.95; // 5% discount for quarterly
            }
        }
        
        // Apply priority processing fee (from loyalty system)
        if ("HIGH".equals(priority)) {
            baseTotal += amount * 0.05; // 5% priority fee
        }
        
        // Apply express shipping fee (from loyalty system)
        if (expressShipping) {
            baseTotal += 15.0; // $15 express fee
        }
        
        // Apply payment method fees (from subscription system)
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
        
        // Apply unified tax (compromise between 8% and 12%)
        baseTotal += baseTotal * 0.10; // 10% unified tax
        
        return baseTotal;
    }
}