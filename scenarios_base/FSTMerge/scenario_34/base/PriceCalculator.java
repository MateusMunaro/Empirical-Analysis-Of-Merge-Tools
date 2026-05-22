public class PriceCalculator {
    public double calculateDiscount(double price, String customerType) {
        if (customerType.equals("PREMIUM")) {
            return price * 0.2;
        }
        return price * 0.1;
    }
}