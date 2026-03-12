
public class OrderProcessor {
  private 
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
  LoyaltyManager
=======
  SubscriptionManager
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
   
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
  loyaltyManager
=======
  subscriptionManager
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
  ;

  private BillingManager billingManager;

  public OrderProcessor() {
    this.subscriptionManager = new SubscriptionManager();
    this.
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    loyaltyManager
=======
    billingManager
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
     = new 
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    LoyaltyManager
=======
    BillingManager
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
    ();
  }

  public double processCustomerOrder(Customer customer, Order order) {
    if (
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    "GOLD".equals(customer.getTier()) && order.getAmount() > 100
=======
    order.getAmount() > 500 && "BASIC".equals(customer.getSubscriptionType())
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
    ) {

<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
      order
=======
      customer
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
      .
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
      setPriority("HIGH")
=======
      upgradeSubscription("STANDARD")
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
      ;
    } else {
      if (order.getAmount() > 1000 && "STANDARD".equals(customer.getSubscriptionType())) {
        customer.upgradeSubscription("PREMIUM");
      }
    }
    double discount = customer.calculateDiscount(order.getAmount());
    double total = order.calculateTotal() - discount;

<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    int
=======
    double
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
     
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    pointsEarned = loyaltyManager.calculatePointsEarned(order.getAmount(), customer.getTier())
=======
    creditsUsed = Math.min(customer.getCreditBalance(), total * 0.5)
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
    ;

<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    customer.addLoyaltyPoints(pointsEarned);
=======
    if (creditsUsed > 0) {
      customer.useCredit(creditsUsed);
      total -= creditsUsed;
    }
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java

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
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    getTier()
=======
    getSubscriptionType()
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
    ).append(
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    " tier customer "
=======
    " subscriber "
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
    ).append(customer.getName()).append(" - Amount: $").append(order.getAmount());
    if (order.
<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    isExpressShipping()
=======
    isRecurring()
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
    ) {

<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
      summary.append(" (Express Shipping)")
=======
      summary.append(" (Recurring every ").append(order.getBillingCycle()).append(" months)")
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java
      ;
    }
    summary.append(" - Payment: ").append(order.getPaymentMethod());

<<<<<<< ./senarios_merge_base/JDime/scenario_39/left/OrderProcessor.java
    if ("HIGH".equals(order.getPriority())) {
      summary.append(" (Priority Processing)");
    }
=======
    if (customer.getCreditBalance() > 0) {
      summary.append(" - Credit Balance: $").append(customer.getCreditBalance());
    }
>>>>>>> ./senarios_merge_base/JDime/scenario_39/right/OrderProcessor.java

    return summary.toString();
  }
}