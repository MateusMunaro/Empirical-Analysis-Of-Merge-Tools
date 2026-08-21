
public class PriceCalculator {
  private static final double MAX_DISCOUNT = 100.0;

  public double calculateDiscount(double price, String customerType) {
    double discount;
    if (customerType.equals("PREMIUM")) {

<<<<<<< /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_34/left/PriceCalculator.java
      if (price > 1000) {
        return price * 0.3;
      }
=======
      discount = price * 0.2;
>>>>>>> /workspaces/Empirical-Analysis-Of-Merge-Tools/scenarios_base/JDime/scenario_34/right/PriceCalculator.java

      if (price > 500) {
        return price * 0.25;
      }
    } else {
      discount = price * 0.1;
    }
    return Math.min(discount, MAX_DISCOUNT);
  }
}