
public class Order {
  private Long orderId;

  private Long customerId;

  private double amount;

  private String status;

  private String 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Order.java
  priority
=======
  paymentMethod
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Order.java
  ;

  private boolean 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Order.java
  expressShipping
=======
  isRecurring
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Order.java
  ;

  private int billingCycle;

  public Order(Long orderId, Long customerId, double amount) {
    this.orderId = orderId;
    this.customerId = customerId;
    this.amount = amount;
    this.status = "PENDING";
    this.isRecurring = false;

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Order.java
    this.priority = "NORMAL"
=======
    this.billingCycle = 1
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Order.java
    ;

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Order.java
    this.expressShipping = false
=======
    this.paymentMethod = "CREDIT_CARD"
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Order.java
    ;
  }

  public Long getOrderId() {
    return orderId;
  }

  public Long getCustomerId() {
    return customerId;
  }

  public double getAmount() {
    return amount;
  }

  public String getStatus() {
    return status;
  }

  public String getPriority() {
    return priority;
  }

  public boolean isRecurring() {
    return isRecurring;
  }

  public boolean isExpressShipping() {
    return expressShipping;
  }

  public int getBillingCycle() {
    return billingCycle;
  }

  public void setPriority(String priority) {
    this.priority = priority;
  }

  public String getPaymentMethod() {
    return paymentMethod;
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

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Order.java
    if ("HIGH".equals(priority)) {
      this.status = "FAST_TRACKED";
    } else {
      this.status = "PROCESSED";
    }
=======
    if (isRecurring) {
      this.status = "SCHEDULED";
    } else {
      this.status = "PROCESSED";
    }
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Order.java
  }

  public double calculateTotal() {
    double baseTotal = amount;

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Order.java
    if ("HIGH".equals(priority)) {
      baseTotal += amount * 0.05;
    }
=======
    if (isRecurring) {
      if (billingCycle >= 12) {
        baseTotal *= 0.85;
      } else {
        if (billingCycle >= 6) {
          baseTotal *= 0.90;
        } else {
          if (billingCycle >= 3) {
            baseTotal *= 0.95;
          }
        }
      }
    }
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Order.java


<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Order.java
    if (expressShipping) {
      baseTotal += 15.0;
    }
=======
    switch (paymentMethod) {
      case "BANK_TRANSFER":
      break;
      case "PAYPAL":
      baseTotal += baseTotal * 0.03;
      break;
      case "CREDIT_CARD":
      default:
      baseTotal += baseTotal * 0.025;
      break;
    }
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Order.java

    baseTotal += baseTotal * 
<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/left/Order.java
    0.08
=======
    0.12
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_39/right/Order.java
    ;
    return baseTotal;
  }
}