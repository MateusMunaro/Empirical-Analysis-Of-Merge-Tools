
public class PriceCalculator {
  private static final double MAX_DISCOUNT = 100.0;

  public double calculateDiscount(double price, String customerType) {
    double discount;
    if (customerType.equals("PREMIUM")) {

<<<<<<< ./senarios_merge_base/JDime/scenario_34/left/priceCalculator.java
      if (price > 1000) {
        return price * 0.3;
      }
=======
      discount = price * 0.2;
>>>>>>> ./senarios_merge_base/JDime/scenario_34/right/priceCalculator.java

      if (price > 500) {
        return price * 0.25;
      }
    } else {
      discount = price * 0.1;
    }
    return Math.min(discount, MAX_DISCOUNT);
  }
}