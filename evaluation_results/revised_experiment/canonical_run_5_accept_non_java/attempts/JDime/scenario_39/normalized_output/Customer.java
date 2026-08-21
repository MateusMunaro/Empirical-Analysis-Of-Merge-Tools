import javax.persistence.*;

@Entity @Table(name = "customers") public class Customer {
  private Long id;

  private String name;

  private String email;

  private String status;

  private int 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
  loyaltyPoints
=======
  subscriptionMonths
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
  ;

  private String 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
  tier
=======
  subscriptionType
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
  ;

  private double creditBalance;

  public Customer(Long id, String name, String email) {
    this.id = id;
    this.name = name;
    this.email = email;
    this.status = "ACTIVE";
    this.subscriptionType = "BASIC";
    this.
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
    loyaltyPoints
=======
    subscriptionMonths
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
     = 0;

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
    this.tier = "BRONZE"
=======
    this.creditBalance = 0.0
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
    ;
  }

  public Long getId() {
    return id;
  }

  public String getName() {
    return name;
  }

  public String getEmail() {
    return email;
  }

  public String getStatus() {
    return status;
  }

  public int getLoyaltyPoints() {
    return loyaltyPoints;
  }

  public String getSubscriptionType() {
    return subscriptionType;
  }

  public String getTier() {
    return tier;
  }

  public int getSubscriptionMonths() {
    return subscriptionMonths;
  }

  public double getCreditBalance() {
    return creditBalance;
  }

  public void setStatus(String status) {
    this.status = status;
  }

  public void addLoyaltyPoints(int points) {
    this.loyaltyPoints += points;
    updateTier();
  }

  public void upgradeSubscription(String newType) {
    this.subscriptionType = newType;
    if ("PREMIUM".equals(newType)) {
      this.creditBalance += 50.0;
    }
  }

  private void updateTier() {
    if (loyaltyPoints >= 1000) {
      this.tier = "GOLD";
    } else {
      if (loyaltyPoints >= 500) {
        this.tier = "SILVER";
      } else {
        this.tier = "BRONZE";
      }
    }
  }

  public void addSubscriptionMonth() {
    this.subscriptionMonths++;
    if (subscriptionMonths > 12) {
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
    switch (
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
    tier
=======
    subscriptionType
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
    ) {
      case 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
      "GOLD"
=======
      "PREMIUM"
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
      :
      return amount * 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
      0.15
=======
      0.20
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
      ;
      case 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
      "SILVER"
=======
      "STANDARD"
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
      :
      return amount * 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
      0.10
=======
      0.12
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
      ;
      case 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
      "BRONZE"
=======
      "BASIC"
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
      :
      default:
      double discount = amount * 0.05;
      if (subscriptionMonths > 6) {
        discount += amount * 0.03;
      }
      return 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Customer.java
      amount * 0.05
=======
      discount
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Customer.java
      ;
    }
  }
}