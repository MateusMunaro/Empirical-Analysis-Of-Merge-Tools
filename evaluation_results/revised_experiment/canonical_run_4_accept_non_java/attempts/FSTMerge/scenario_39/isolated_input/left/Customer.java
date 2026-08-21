import javax.persistence.*;

@Entity
@Table(name = "customers")
public class Customer {
    private Long id;
    private String name;
    private String email;
    private String status;
    private int loyaltyPoints;
    private String tier;
    
    public Customer(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.status = "ACTIVE";
        this.loyaltyPoints = 0;
        this.tier = "BRONZE";
    }
    
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getStatus() { return status; }
    public int getLoyaltyPoints() { return loyaltyPoints; }
    public String getTier() { return tier; }
    
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
    
    public double calculateDiscount(double amount) {
        // Tier-based discount system
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
}