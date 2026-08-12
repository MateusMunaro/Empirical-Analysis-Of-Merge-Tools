public class Order {
    private Long orderId;
    private Long customerId;
    private double amount;
    private String status;
    private String priority;
    private boolean expressShipping;
    private boolean isRecurring;
    private int billingCycle; // in months
    private String paymentMethod;
    
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
        if ("HIGH".equals(priority)) {
            this.status = "FAST_TRACKED";
        } else if (isRecurring) {
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

        // Priority processing fee from the loyalty branch.
        if ("HIGH".equals(priority)) {
            baseTotal += amount * 0.05;
        }

        // Express shipping fee from the loyalty branch.
        if (expressShipping) {
            baseTotal += 15.0;
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
        
        // Retain the subscription branch's explicit service-tax decision.
        baseTotal += baseTotal * 0.12; // 12% service tax
        
        return baseTotal;
    }
}
