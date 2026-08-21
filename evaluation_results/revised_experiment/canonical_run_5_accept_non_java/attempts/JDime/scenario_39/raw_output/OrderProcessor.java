
public class OrderProcessor {
  private 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
  LoyaltyManager
=======
  SubscriptionManager
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
   
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
  loyaltyManager
=======
  subscriptionManager
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
  ;

  private BillingManager billingManager;

  public OrderProcessor() {
    this.subscriptionManager = new SubscriptionManager();
    this.
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    loyaltyManager
=======
    billingManager
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
     = new 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    LoyaltyManager
=======
    BillingManager
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
    ();
  }

  public double processCustomerOrder(Customer customer, Order order) {
    if (
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    "GOLD".equals(customer.getTier()) && order.getAmount() > 100
=======
    order.getAmount() > 500 && "BASIC".equals(customer.getSubscriptionType())
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
    ) {

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
      order
=======
      customer
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
      .
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
      setPriority("HIGH")
=======
      upgradeSubscription("STANDARD")
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
      ;
    } else {
      if (order.getAmount() > 1000 && "STANDARD".equals(customer.getSubscriptionType())) {
        customer.upgradeSubscription("PREMIUM");
      }
    }
    double discount = customer.calculateDiscount(order.getAmount());
    double total = order.calculateTotal() - discount;

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    int
=======
    double
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
     
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    pointsEarned = loyaltyManager.calculatePointsEarned(order.getAmount(), customer.getTier())
=======
    creditsUsed = Math.min(customer.getCreditBalance(), total * 0.5)
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
    ;

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    customer.addLoyaltyPoints(pointsEarned);
=======
    if (creditsUsed > 0) {
      customer.useCredit(creditsUsed);
      total -= creditsUsed;
    }
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java

    if (order.isRecurring()) {
      subscriptionManager.setupRecurringBilling(customer, order);
    }
    if (billingManager.processPayment(customer, total, order.getPaymentMethod())) {
      customer.addCredit(order.getAmount() * 0.01);
      customer.addSubscriptionMonth();
      order.processOrder();
    }
    return total;
  }

  public String getOrderSummary(Customer customer, Order order) {
    StringBuilder summary = new StringBuilder();
    summary.append("Order ").append(order.getOrderId()).append(" for ").append(customer.
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    getTier()
=======
    getSubscriptionType()
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
    ).append(
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    " tier customer "
=======
    " subscriber "
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
    ).append(customer.getName()).append(" - Amount: $").append(order.getAmount());
    if (order.
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    isExpressShipping()
=======
    isRecurring()
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
    ) {

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
      summary.append(" (Express Shipping)")
=======
      summary.append(" (Recurring every ").append(order.getBillingCycle()).append(" months)")
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java
      ;
    }
    summary.append(" - Payment: ").append(order.getPaymentMethod());

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/OrderProcessor.java
    if ("HIGH".equals(order.getPriority())) {
      summary.append(" (Priority Processing)");
    }
=======
    if (customer.getCreditBalance() > 0) {
      summary.append(" - Credit Balance: $").append(customer.getCreditBalance());
    }
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/OrderProcessor.java

    return summary.toString();
  }
}