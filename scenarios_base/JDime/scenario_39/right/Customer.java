public class Customer {
    private Long id;
    private String name;
    private String email;
    private String status;
    private String subscriptionType;
    private int subscriptionMonths;
    private double creditBalance;
    
    public Customer(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.status = "ACTIVE";
        this.subscriptionType = "BASIC";
        this.subscriptionMonths = 0;
        this.creditBalance = 0.0;
    }
    
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getStatus() { return status; }
    public String getSubscriptionType() { return subscriptionType; }
    public int getSubscriptionMonths() { return subscriptionMonths; }
    public double getCreditBalance() { return creditBalance; }
    
    public void setStatus(String status) {
        this.status = status;
    }
    
    public void upgradeSubscription(String newType) {
        this.subscriptionType = newType;
        if ("PREMIUM".equals(newType)) {
            this.creditBalance += 50.0; // Bonus credits for premium
        }
    }
    
    public void addSubscriptionMonth() {
        this.subscriptionMonths++;
        if (subscriptionMonths > 12) {
            // Long-term customer benefits
            this.creditBalance += 10.0;
        }
    }
    
    public void addCredit(double amount) {
        this.creditBalance += amount;
    }
    
    public boolean useCredit(double amount) {
        if (creditBalance >= amount) {
            creditBalance -= amount;
            return true;
        }
        return false;
    }
    
    public double calculateDiscount(double amount) {
        // Subscription-based discount system
        switch (subscriptionType) {
            case "PREMIUM":
                return amount * 0.20; // 20% for premium subscribers
            case "STANDARD":
                return amount * 0.12; // 12% for standard subscribers
            case "BASIC":
            default:
                double discount = amount * 0.05; // 5% base
                // Long-term customer bonus
                if (subscriptionMonths > 6) {
                    discount += amount * 0.03; // Additional 3%
                }
                return discount;
        }
    }
}