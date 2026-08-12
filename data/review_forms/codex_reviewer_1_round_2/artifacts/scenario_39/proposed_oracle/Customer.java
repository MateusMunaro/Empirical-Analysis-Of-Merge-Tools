public class Customer {
    private Long id;
    private String name;
    private String email;
    private String status;
    private int loyaltyPoints;
    private String tier;
    private String subscriptionType;
    private int subscriptionMonths;
    private double creditBalance;
    
    public Customer(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.status = "ACTIVE";
        this.loyaltyPoints = 0;
        this.tier = "BRONZE";
        this.subscriptionType = "BASIC";
        this.subscriptionMonths = 0;
        this.creditBalance = 0.0;
    }
    
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getStatus() { return status; }
    public int getLoyaltyPoints() { return loyaltyPoints; }
    public String getTier() { return tier; }
    public String getSubscriptionType() { return subscriptionType; }
    public int getSubscriptionMonths() { return subscriptionMonths; }
    public double getCreditBalance() { return creditBalance; }
    
    public void setStatus(String status) {
        this.status = status;
    }

    public void addLoyaltyPoints(int points) {
        this.loyaltyPoints += points;
        updateTier();
    }

    private void updateTier() {
        if (loyaltyPoints >= 1000) {
            this.tier = "GOLD";
        } else if (loyaltyPoints >= 500) {
            this.tier = "SILVER";
        } else {
            this.tier = "BRONZE";
        }
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
        // Resolve the competing policies without stacking discounts: retain
        // the larger discount explicitly defined by either branch.
        return Math.max(
            calculateTierDiscount(amount),
            calculateSubscriptionDiscount(amount)
        );
    }

    private double calculateTierDiscount(double amount) {
        switch (tier) {
            case "GOLD":
                return amount * 0.15;
            case "SILVER":
                return amount * 0.10;
            case "BRONZE":
            default:
                return amount * 0.05;
        }
    }

    private double calculateSubscriptionDiscount(double amount) {
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
