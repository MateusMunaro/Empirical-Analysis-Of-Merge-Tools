public class Customer {
    private Long id;
    private String name;
    private String email;
    private String status;
    
    // Combined loyalty and subscription system
    private int loyaltyPoints;
    private String tier; // BRONZE, SILVER, GOLD
    private String subscriptionType; // BASIC, STANDARD, PREMIUM
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
            // Auto-upgrade subscription for high-tier customers
            if ("BASIC".equals(subscriptionType)) {
                upgradeSubscription("STANDARD");
            }
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
            addLoyaltyPoints(50); // Cross-system rewards
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
        // Hybrid discount system: combine both tier and subscription benefits
        double tierDiscount = getTierDiscount(amount);
        double subscriptionDiscount = getSubscriptionDiscount(amount);
        
        // Take the better of the two discounts, plus a small bonus for having both
        double bestDiscount = Math.max(tierDiscount, subscriptionDiscount);
        
        // Bonus for customers with both high tier and premium subscription
        if ("GOLD".equals(tier) && "PREMIUM".equals(subscriptionType)) {
            bestDiscount += amount * 0.05; // Additional 5% bonus
        }
        
        return bestDiscount;
    }
    
    private double getTierDiscount(double amount) {
        switch (tier) {
            case "GOLD":
                return amount * 0.15; // 15% for gold
            case "SILVER":
                return amount * 0.10; // 10% for silver
            case "BRONZE":
            default:
                return amount * 0.05; // 5% for bronze
        }
    }
    
    private double getSubscriptionDiscount(double amount) {
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